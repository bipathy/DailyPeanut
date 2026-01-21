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


def get_comic():
    """Fetch and download today's comic, falling back to yesterday if unavailable."""
    today = datetime.today()
    try:
        comic = comics.search("peanuts", today)
        comic.download(TEMP_PATH)
        return today
    except InvalidDateError:
        print("Today's comic not available yet, trying yesterday...")
        yesterday = today - timedelta(days=1)
        comic = comics.search("peanuts", yesterday)
        comic.download(TEMP_PATH)
        return yesterday


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
        tags=["peanuts", "comic", "charles schulz", "snoopy", "charlie brown"],
        caption=caption,
        data=TEMP_PATH
    )

    return response


def main():
    print("Fetching Peanuts comic...")
    date = get_comic()
    print(f"Got comic for {date.date()}")

    print("Posting to Tumblr...")
    response = post_to_tumblr(date)

    print(f"Done! Response: {response}")


if __name__ == "__main__":
    main()
