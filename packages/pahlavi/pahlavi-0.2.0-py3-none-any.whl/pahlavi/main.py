import requests
from bs4 import BeautifulSoup
import re

def get_today_dollar_price() -> float:
    """Get today's USD price in Toman"""
    url = 'https://www.tgju.org/profile/price_dollar_rl'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    price_tag = soup.find('span', {'class': 'value'})
    if price_tag:
        price = "".join(re.findall(r"\d+", price_tag.text.split()[0]))
        return int(price) / 10  # Convert Rial to Toman
    else:
        raise ValueError("Dollar price not found.")

def show_amount_in_dollars(amount_toman: float, dollar_1357: float = 7):
    today_dollar = get_today_dollar_price()  # in Toman
    dollars_today = amount_toman / today_dollar
    dollars_1357 = amount_toman / dollar_1357

    # Format: if <1 use 4 decimals, else 2 decimals
    def format_amount(x):
        return f"{x:.4f}" if x < 1 else f"{x:.2f}"

    print(f"{amount_toman} Toman today equals:")
    print(f"- About {format_amount(dollars_today)} USD today")
    print(f"- About {format_amount(dollars_1357)} USD in 1978 (Pahlavi era)")

