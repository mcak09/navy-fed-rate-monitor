import requests
import re
import os
from datetime import datetime
from twilio.rest import Client

def get_rate():
    url = "https://www.navyfederal.org/loans-cards/mortgage/mortgage-rates/conventional-fixed-rate-mortgages.html"
    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get(url, headers=headers, timeout=15)
    
    # Try multiple patterns to find the 15 Year rate
    patterns = [
        r'15 Year\s*\|?\s*([\d.]+%)',
        r'15 Year.*?([\d]+\.\d+%)',
        r'"15 Year".*?([\d]+\.\d+%)',
        r'15\s*Year[^%]*?([\d]+\.\d+)\s*%',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, resp.text, re.DOTALL)
        if match:
            return match.group(1) if '%' in match.group(1) else match.group(1) + '%'
    
    # Debug: print a snippet around "15 Year" to see what the page actually looks like
    idx = resp.text.find('15 Year')
    if idx != -1:
        print("DEBUG snippet:", resp.text[idx:idx+200])
    else:
        print("DEBUG: '15 Year' not found in page at all")
    
    return None

def send_sms(message):
    client = Client(os.environ["TWILIO_ACCOUNT_SID"], os.environ["TWILIO_AUTH_TOKEN"])
    client.messages.create(
        body=message,
        from_=os.environ["TWILIO_FROM"],
        to=os.environ["TWILIO_TO"]
    )

def main():
    rate = get_rate()
    if not rate:
        print("Could not parse rate.")
        return

    last_rate = None
    if os.path.exists("last_rate.txt"):
        with open("last_rate.txt") as f:
            last_rate = f.read().strip()

    print(f"Current rate: {rate} | Last rate: {last_rate}")

    if rate != last_rate:
        if last_rate:
            msg = f"Navy Federal 15-Year rate changed: {last_rate} -> {rate}"
        else:
            msg = f"Navy Federal 15-Year rate monitor started. Current rate: {rate}"
        send_sms(msg)
        print("SMS sent!")

    with open("last_rate.txt", "w") as f:
        f.write(rate)

    with open("last_checked.txt", "w") as f:
        f.write(f"Last checked: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}\nRate: {rate}\n")

if __name__ == "__main__":
    main()
