#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Expiry-date and GitHub access-list checker only."""

import sys
from datetime import datetime, timedelta, timezone
import requests

ACCESS_LIST_URL = (
    "https://raw.githubusercontent.com/ljplodap605-ops/"
    "Demon-access-file-/main/expiry.txt"
)
IST_OFFSET = timedelta(hours=5, minutes=30)
expiry_date = datetime(2027, 10, 19, 23, 59, 59)


def check_telegram_access(user_id: str) -> bool:
    try:
        response = requests.get(ACCESS_LIST_URL, timeout=15)
        response.raise_for_status()

        for line in response.text.splitlines():
            line = line.strip()
            if not line or "," not in line:
                continue

            uid, date_part = line.split(",", 1)
            uid = uid.strip()
            date_part = date_part.strip()

            try:
                access_expiry = datetime.strptime(
                    date_part, "%Y-%m-%d : %H:%M"
                )
            except ValueError:
                continue

            if uid == str(user_id).strip():
                now_ist = datetime.now(timezone.utc).astimezone(
                    timezone(IST_OFFSET)
                ).replace(tzinfo=None)

                if access_expiry > now_ist:
                    remaining = access_expiry - now_ist
                    days = remaining.days
                    hours, rem = divmod(remaining.seconds, 3600)
                    minutes = rem // 60
                    print(f"ACCESS GRANTED — {days}d {hours}h {minutes}m left")
                    return True

                print("ACCESS DENIED: access-list entry has expired.")
                return False

        print("ACCESS DENIED: ID not found in the access list.")
        return False

    except requests.RequestException as exc:
        print(f"Could not fetch access list: {exc}")
        return False


def main():
    now = datetime.now()
    if now > expiry_date:
        print("This file has expired.")
        sys.exit(1)

    print(f"File expiry: {expiry_date:%Y-%m-%d %H:%M:%S}")
    user_id = input("Enter Telegram Chat ID: ").strip()
    if not check_telegram_access(user_id):
        sys.exit(1)

    print("Access check completed successfully.")


if __name__ == "__main__":
    main()
