#!/usr/bin/env python3
"""
DailyPeanut - Post today's Peanuts comic to Tumblr
"""

import os
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pytumblr


TEMP_PATH = "/tmp/peanuts_today.gif"
LOG_FILE = os.path.join(os.path.dirname(__file__), "post_log.csv")


def get_comic():
    """Fetch and download today's Peanuts comic from ArcaMax."""
    response = requests.get(
        "https://www.arcamax.com/thefunnies/peanuts/",
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=30,
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    img = soup.find("img", src=re.compile(r"resources\.arcamax\.com/newspics/"))
    if not img:
        raise RuntimeError("Could not find Peanuts comic image on ArcaMax")

    date_match = re.search(r"(\d+/\d+/\d{4})", img.get("alt", ""))
    date = datetime.strptime(date_match.group(1), "%m/%d/%Y") if date_match else datetime.today()

    img_response = requests.get(img["src"], timeout=30)
    img_response.raise_for_status()
    with open(TEMP_PATH, "wb") as f:
        f.write(img_response.content)

    return date


def post_to_tumblr(date):
    """Post downloaded comic to Tumblr blog."""
    client = pytumblr.TumblrRestClient(
        os.environ['TUMBLR_CONSUMER_KEY'],
        os.environ['TUMBLR_CONSUMER_SECRET'],
        os.environ['TUMBLR_OAUTH_TOKEN'],
        os.environ['TUMBLR_OAUTH_SECRET'],
    )

    date_str = date.strftime("%B %d, %Y")
    caption = f"Peanuts - {date_str}"

    response = client.create_photo(
        'daily-peanut',
        state="published",
        tags=["DailyPeanut", "peanuts", "comic", "charles schulz", "snoopy", "charlie brown"],
        caption=caption,
        data=TEMP_PATH
    )

    return response


def log_post(date, post_id):
    """Append post info to log file."""
    post_url = f"https://daily-peanut.tumblr.com/post/{post_id}"

    # Create header if file doesn't exist
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w") as f:
            f.write("date,post_url\n")

    with open(LOG_FILE, "a") as f:
        f.write(f"{date.date()},{post_url}\n")

    return post_url


def main():
    print("Fetching Peanuts comic...")
    date = get_comic()
    print(f"Got comic for {date.date()}")

    print("Posting to Tumblr...")
    response = post_to_tumblr(date)

    post_url = log_post(date, response['id'])
    print(f"Done! Post URL: {post_url}")


if __name__ == "__main__":
    main()
