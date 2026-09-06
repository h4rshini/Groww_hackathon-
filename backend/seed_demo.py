"""Seed a demo account for local use: python seed_demo.py [email]

The account must already exist (register it in the app first). On hosted
deploys the same seeding runs on startup instead — see app/demo_seed.py.
"""

import sys

from app.db import SessionLocal
from app.demo_seed import SYMBOLS, seed_demo_account


def main():
    email = sys.argv[1] if len(sys.argv) > 1 else "founder@signal.app"
    session = SessionLocal()
    if seed_demo_account(session, email, create_user=False):
        print(f"Seeded {email}: watching {', '.join(SYMBOLS)}, 2 example flags.")
    else:
        print(f"No user {email}. Register in the app first.")
    session.close()


if __name__ == "__main__":
    main()
