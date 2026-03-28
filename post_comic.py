#!/usr/bin/env python3
"""
DailyPeanut - Post today's Peanuts comic to Tumblr
"""

import os
from datetime import datetime, timedelta
import comics
from comics.exceptions import InvalidDateError
import pytumblr


TEMP_PATH = "/tmp/peanuts_today.png"
LOG_FILE = os.path.join(os.path.dirname(__file__), "post_log.csv")


def get_comic():
    """Fetch and download today's comic, falling back up to 7 days if unavailable."""
    today = datetime.today()
    for days_back in range(8):
        date = today - timedelta(days=days_back)
        try:
            comic = comics.search("peanuts", date)
            comic.download(TEMP_PATH)
            if days_back > 0:
                print(f"Today's comic unavailable, using {date.date()} instead.")
            return date
        except InvalidDateError:
            print(f"Comic not available for {date.date()}, trying earlier...")
    raise RuntimeError("Could not find a Peanuts comic in the last 7 days.")


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
