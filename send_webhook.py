from pydoc import text
import requests
from bs4 import BeautifulSoup, Tag
import configparser
from discord_webhook import DiscordWebhook, DiscordEmbed

config = configparser.ConfigParser()
config.read('config.ini')

webhook_url = config['DEFAULT']['webhook_url']
search_domain = config['DEFAULT']['search_domain']

def fetch_domain_data(search_domain: str) -> tuple[str, DiscordEmbed]:
    search_url: str = f'https://porkbun.com/auctions?q={search_domain}'
    response: requests.Response = requests.get(search_url)

    if response.status_code != 200:
        embed = DiscordEmbed(
            title='❌ Error',
            description=f'Failed to retrieve auction data for {search_domain}',
            color=0xFF0000,
            url=search_url
        )
        embed.set_timestamp()
        return '', embed

    soup: BeautifulSoup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table', class_='table')

    if table is None or not isinstance(table, Tag):
        embed = DiscordEmbed(
            title='❌ Error',
            description=f'No auction data found for {search_domain}',
            color=0xFF0000,
            url=search_url
        )
        embed.set_timestamp()
        return '@everyone', embed

    tbody = table.find('tbody')
    if tbody is None or not isinstance(tbody, Tag):
        embed = DiscordEmbed(
            title='Error',
            description=f'No auction data found for {search_domain}',
            color=0xFF0000,
            url=search_url
        )
        embed.set_timestamp()
        return '@everyone', embed

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
            embed.set_timestamp()
            return '@everyone', embed

    embed = DiscordEmbed(
        title='⚠️ Not Found',
        description=f'Domain {search_domain} not found in auction results',
        color=0xFFFF00,
        url=search_url
    )
    embed.set_timestamp()
    return '', embed

webhook = DiscordWebhook(url=webhook_url)
content, embed = fetch_domain_data(search_domain)
webhook.content = content
webhook.add_embed(embed)
response = webhook.execute()

print('Message sent successfully.' if response.status_code == 204 
      else f'Failed to send message. Status code: {response.status_code}')