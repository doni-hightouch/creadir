"""Who is spending what on Creadir, and approving more. Private — never deployed.

    python3 budget.py                          # this month's spend per person
    python3 budget.py grant <email> 10         # approve $10 more, this month only
    python3 budget.py set <email> 25           # change their standing monthly cap
    python3 budget.py set <email> default      # back to the default cap

Spend is metered in dollars because image generation isn't priced per token and
input tokens cost a fifth of output tokens — a token count wouldn't tell you
what you're actually spending. Budgets reset on the 1st (UTC).
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "api"))
import _lib  # noqa: E402


def show():
    report = _lib.usage_report()
    people = report["people"]
    print("Creadir spend — %s\n" % report["month"])
    if not people:
        print("  Nothing spent yet this month.")
        return
    print("  %-34s %9s %9s %9s %6s" % ("EMAIL", "SPENT", "ALLOWED", "LEFT", "CALLS"))
    total = 0.0
    for p in people:
        total += p["spent_usd"]
        flag = "  ← at limit" if p["left_usd"] <= 0 else ""
        print("  %-34s %8.2f%s %8.2f%s %8.2f%s %6d%s" % (
            p["email"], p["spent_usd"], "", p["allowance_usd"], "",
            p["left_usd"], "", p["calls"], flag))
    print("\n  total this month: $%.2f" % total)
    print("\n  Anyone not listed hasn't spent anything yet (default cap $%.2f/mo)."
          % _lib.DEFAULT_MONTHLY_USD)


def main():
    if not _lib.key("BLOB_READ_WRITE_TOKEN"):
        print("BLOB_READ_WRITE_TOKEN missing from .env — can't read usage")
        return
    args = sys.argv[1:]
    if not args:
        show()
        return
    cmd = args[0]
    if cmd == "grant" and len(args) == 3:
        email, amount = args[1], float(args[2])
        total = _lib.grant_overage(email, amount)
        print("Approved $%.2f more for %s this month. Their cap is now $%.2f."
              % (amount, email, total))
    elif cmd == "set" and len(args) == 3:
        email, raw = args[1], args[2]
        if raw.lower() == "default":
            total = _lib.set_budget(
                email,
                _lib.ADMIN_MONTHLY_USD if email.lower() == _lib.ADMIN_EMAIL
                else _lib.DEFAULT_MONTHLY_USD)
        else:
            total = _lib.set_budget(email, float(raw))
        print("%s now has a $%.2f/month cap." % (email, total))
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
