"""Create all tables. Switch to migrations once the schema changes under real data."""

from app.db import Base, engine
from app import models  # noqa: F401 — registers models on Base.metadata


def main():
    Base.metadata.create_all(engine)
    print("Tables created:", ", ".join(Base.metadata.tables.keys()))


if __name__ == "__main__":
    main()
