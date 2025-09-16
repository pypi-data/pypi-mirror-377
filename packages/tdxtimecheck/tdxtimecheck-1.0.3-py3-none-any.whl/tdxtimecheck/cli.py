#!/usr/bin/env python3
from datetime import datetime, timedelta
import sys

def main():
    if len(sys.argv) > 2:
        try:
            print(f"\nTarget hours is {sys.argv[2]} hours")
            if ":" in sys.argv[2]:
                h, m = map(int, sys.argv[2].split(":"))
                target_hours = h + m / 60
            else:
                target_hours = float(sys.argv[2])
        except ValueError:
            print(f"❌ Invalid target hours format: {sys.argv[2]}")
            sys.exit(1)
        worked_time_str = sys.argv[1]

    elif len(sys.argv) > 1:
        print("\nDefault target hours is 8 hours")
        target_hours = 8
        worked_time_str = sys.argv[1]

    else:
        worked_time_str = input("\nEnter worked time so far (HH, HH:MM, HH:MM:SS): ")
        target_hours = input("\nEnter target hours :")

        if ":" in target_hours:
            try:
                h, m = map(int, target_hours.split(":"))
                target_hours = h + m / 60
            except ValueError:
                print(f"❌ Invalid target hours format: {target_hours}")
                sys.exit(1)
        else:
            try:
                target_hours = float(target_hours)
            except ValueError:
                print(f"❌ Invalid target hours format: {target_hours}")
                sys.exit(1)

        print(f"\nTarget hours is {target_hours} hours")

    parts = worked_time_str.split(":")
    if len(parts) == 2:
        worked_time_str += ":00"
    elif len(parts) == 1:
        worked_time_str += ":00:00"
        print("\nTime changed to", worked_time_str)

    try:
        h, m, s = map(int, worked_time_str.split(":"))
        worked_time = timedelta(hours=h, minutes=m, seconds=s)
    except ValueError:
        print(f"\n❌ Invalid worked time format: {worked_time_str}")
        print("Examples:\n 06:10:02  # HH:MM:SS\n 06:10    # HH:MM\n 06       # Hours\n")
        sys.exit(1)

    target_time = timedelta(hours=target_hours)
    current_time = datetime.now()

    if worked_time >= target_time:
        print(f"\nWorked Hours: {worked_time}")
        print("✅ Times up, go home man!")
    else:
        remaining_time = target_time - worked_time
        finish_time = current_time + remaining_time + timedelta(minutes=1)

        print(f"\nWorked Hours: {worked_time}")
        print(f"You need to work for: {remaining_time}")
        print(f"\nCurrent Time: {current_time.strftime('%d-%m-%Y, %I:%M %p')}")
        print(f"Finish Time: {finish_time.strftime('%d-%m-%Y, %I:%M %p')}\n")
