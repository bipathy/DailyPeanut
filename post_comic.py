#!/usr/bin/env python3
"""
DailyPeanut - Post today's Peanuts comic to Tumblr
"""

import os
from datetime import datetime, timedelta
import comics
from comics.exceptions import InvalidDateError
import pytumblr


def get_comic():
    """Fetch today's Peanuts comic, falling back to yesterday if unavailable."""
    today = datetime.today()
    try:
        comic = comics.search("peanuts", today)
        return comic, today
    except InvalidDateError:
        print(f"Today's comic not available yet, trying yesterday...")
        yesterday = today - timedelta(days=1)
        comic = comics.search("peanuts", yesterday)
        return comic, yesterday


def post_to_tumblr(comic, date):
    """Post comic to Tumblr blog."""
    client = pytumblr.TumblrRestClient(
        os.environ['TUMBLR_CONSUMER_KEY'],
        os.environ['TUMBLR_CONSUMER_SECRET'],
        os.environ['TUMBLR_OAUTH_TOKEN'],
        os.environ['TUMBLR_OAUTH_SECRET'],
    )

    # Format date for caption
    date_str = date.strftime("%B %d, %Y")
    caption = f"Peanuts - {date_str}"

    # Download locally then upload (more reliable)
    temp_path = "/tmp/peanuts_today.png"
    comic.download(temp_path)

    response = client.create_photo(
        'daily-peanut',
        state="published",
        tags=["peanuts", "comic", "charles schulz", "snoopy", "charlie brown"],
        caption=caption,
        data=temp_path
    )

    return response


def main():
    print("Fetching Peanuts comic...")
    comic, date = get_comic()
    print(f"Got comic for {date.date()}")

    print("Posting to Tumblr...")
    response = post_to_tumblr(comic, date)

    print(f"Done! Response: {response}")


if __name__ == "__main__":
    main()
