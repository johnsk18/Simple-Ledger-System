from client.database import create_transactions_table, create_users_table, populate_balance_cache
from server.app import app
import sys


def main():
    create_users_table()
    create_transactions_table()
    populate_balance_cache()

    app.run(host='localhost', port=3000)
    return 0

if __name__ == "__main__":
    sys.exit(main())