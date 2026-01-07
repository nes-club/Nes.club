import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone


def main() -> int:
    started_at = datetime.now(timezone.utc)
    deadline = started_at + timedelta(minutes=5)

    while datetime.now(timezone.utc) < deadline:
        result = subprocess.run(
            ["python3", "manage.py", "migrate", "--check"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
        if result.returncode == 0:
            print("Migrations are up to date")
            return 0

        time.sleep(5)

    print("Migrations are not ready after 5 minutes")
    return 1


if __name__ == "__main__":
    sys.exit(main())
