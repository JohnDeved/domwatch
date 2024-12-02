import requests
from bs4 import BeautifulSoup, Tag
import configparser
from discord_webhook import DiscordWebhook, DiscordEmbed

config = configparser.ConfigParser()
config.read('config.ini')

webhook_url = config['DEFAULT']['webhook_url']
search_domain = config['DEFAULT']['search_domain']
porkbun_icon = 'https://porkbun.com/images/favicons/android-icon-192x192.png'

def fetch_domain_data(search_domain: str) -> tuple[str, DiscordEmbed]:
    search_url: str = f'https://porkbun.com/auctions?q={search_domain}'
    response: requests.Response = requests.get(search_url)

    if response.status_code != 200:
        embed = DiscordEmbed(
            title='❌ Error',
            description=f'Failed to retrieve auction data for {search_domain}',
            color=0xFF0000,
            url=search_url,
        )
        embed.footer = {'text': search_domain, 'icon_url': porkbun_icon}
        return '', embed

    soup: BeautifulSoup = BeautifulSoup(response.text, 'html.parser')
    
    # Check for no results message
    no_results = soup.find('h3', string='Your search terms didn\'t return any results.')
    if no_results:
        embed = DiscordEmbed(
            title='⚠️ No Results',
            description=f'No auction results found for search term: {search_domain}',
            color=0xFFFF00,
            url=search_url
        )
        embed.footer = {'text': search_domain, 'icon_url': porkbun_icon}
        return '', embed

    table = soup.find('table', class_='table')

    if table is None or not isinstance(table, Tag):
        embed = DiscordEmbed(
            title='❌ Error',
            description=f'No auction data found for {search_domain}',
            color=0xFF0000,
            url=search_url
        )
        embed.footer = {'text': search_domain, 'icon_url': porkbun_icon}
        return '', embed

    tbody = table.find('tbody')
    if tbody is None or not isinstance(tbody, Tag):
        embed = DiscordEmbed(
            title='Error',
            description=f'No auction data found for {search_domain}',
            color=0xFF0000,
            url=search_url
        )
        embed.footer = {'text': search_domain, 'icon_url': porkbun_icon}
        return '', embed

    rows = tbody.find_all('tr')
    for row in rows:
        cells = row.find_all('td')
        if cells and cells[0].text.strip() == search_domain:
            domain = cells[0].text.strip()
            tld = cells[1].text.strip()
            time_left = cells[2].text.strip()
            starting_price = cells[3].text.strip()
            current_bid = cells[4].text.strip()
            bids = cells[5].text.strip()
            domain_age = cells[6].text.strip()
            
            embed = DiscordEmbed(
                title=f'🎯 Domain Auction Found: {domain}',
                color=0x00FF00,
                url=search_url
            )
            embed.add_embed_field(name='🌐 TLD', value=tld, inline=True)
            embed.add_embed_field(name='⏰ Time Left', value=time_left, inline=True)
            embed.add_embed_field(name='💰 Starting Price', value=starting_price, inline=True)
            embed.add_embed_field(name='💸 Current Bid', value=current_bid, inline=True)
            embed.add_embed_field(name='🔢 Bids', value=bids, inline=True)
            embed.add_embed_field(name='📅 Domain Age', value=domain_age, inline=True)
            embed.footer = {'text': search_domain, 'icon_url': porkbun_icon}
            return '@everyone', embed

    embed = DiscordEmbed(
        title='⚠️ Not Found',
        description=f'Domain {search_domain} not found in auction results',
        color=0xFFFF00,
        url=search_url
    )
    embed.footer = {'text': search_domain, 'icon_url': porkbun_icon}
    return '', embed

webhook = DiscordWebhook(url=webhook_url)
content, embed = fetch_domain_data(search_domain)
webhook.content = content
webhook.add_embed(embed)
response = webhook.execute()

print('Message sent successfully.' if response.status_code == 204 
      else f'Failed to send message. Status code: {response.status_code}')