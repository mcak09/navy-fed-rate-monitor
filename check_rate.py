import requests
import re
import os
from twilio.rest import Client

def get_rate():
    url = "https://www.navyfederal.org/loans-cards/mortgage/mortgage-rates/conventional-fixed-rate-mortgages.html"
    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get(url, headers=headers, timeout=15)
    # Match the 15 Year row rate
    match = re.search(r'15 Year\s*\|?\s*([\d.]+%)', resp.text)
    return match.group(1) if match else None

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

    # Read last known rate
    last_rate = None
    if os.path.exists("last_rate.txt"):
        with open("last_rate.txt") as f:
            last_rate = f.read().strip()

    print(f"Current rate: {rate} | Last rate: {last_rate}")

    if rate != last_rate:
        msg = f"🏠 Navy Federal 15-Year rate changed: {last_rate} → {rate}"
        send_sms(msg)
        print("SMS sent!")
        with open("last_rate.txt", "w") as f:
            f.write(rate)
    else:
        print("No change.")

if __name__ == "__main__":
    main()
