"""Who has signed in to Creadir. Private — runs locally, never deployed.

    python3 users.py            # one line per person
    python3 users.py --events   # every individual sign-in, oldest first

Reads the append-only login log in Vercel Blob using BLOB_READ_WRITE_TOKEN
from .env. Nothing on the website exposes this.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "api"))
import _lib  # noqa: E402


def main():
    if not _lib.key("BLOB_READ_WRITE_TOKEN"):
        print("BLOB_READ_WRITE_TOKEN missing from .env — can't read the log")
        return
    log = _lib.login_log()
    people, events = log["people"], log["events"]
    if "--events" in sys.argv:
        print("%d sign-ins\n" % len(events))
        for e in events:
            print("  %s  %-34s %s" % (e.get("at", "?"), e.get("email", "?"),
                                      e.get("name", "")))
        return
    if not people:
        print("Nobody has signed in yet.")
        return
    print("%d %s, %d sign-ins total\n" % (
        len(people), "person" if len(people) == 1 else "people", len(events)))
    print("  %-34s %-22s %6s  %s" % ("EMAIL", "NAME", "LOGINS", "LAST SEEN"))
    for p in people:
        print("  %-34s %-22s %6d  %s" % (
            p["email"], (p["name"] or "")[:22], p["logins"],
            (p["last_seen"] or "")[:19].replace("T", " ")))


if __name__ == "__main__":
    main()
