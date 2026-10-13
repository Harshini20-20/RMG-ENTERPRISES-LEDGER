
import getpass

from app.db import init_db, db_conn
from app.security import hash_pw


def main():
    init_db()

    with db_conn() as c:
        if c.execute(
            "SELECT 1 FROM users WHERE role='admin' LIMIT 1"
        ).fetchone():
            print("Admin already exists; unchanged.")
            return

        name = input("Admin username: ").strip()

        while not name:
            name = input("Username required: ").strip()

        while True:
            password = getpass.getpass("Password (8+ characters): ")
            confirm = getpass.getpass("Confirm password: ")

            if password != confirm:
                print("Passwords do not match.")
            elif len(password) < 8:
                print("Password too short.")
            else:
                break

        c.execute(
            """
            INSERT INTO users (username, password_hash, role)
            VALUES (?, ?, 'admin')
            """,
            (name, hash_pw(password)),
        )

    print("Admin created.")


if __name__ == "__main__":
    main()
