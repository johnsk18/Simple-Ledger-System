from constants import Currency, Error_Message, Filename, SQL_Statement, Table, Transaction 
from pprint import pprint
from threading import Lock
import sqlite3

'''
Stores in-memory calcualtion of user balances
'''
balance_cache: dict[int, dict[Currency, float]] = {}

'''
Mutex lock when accessing the balance cache
'''
cache_mutex: Lock = Lock()

'''
Database filenames. Implemented to resolve unit testing overwrite bugs.

TODO:  Improve on solution to discrimiante based on when live or testing. 
On first glance, it seems redundant.
'''
db_files: dict[Table, Filename] = {Table.USERS: Filename.USERS_DB_FILENAME,
                                   Table.TRANSACTIONS: Filename.TRANSACTIONS_DB_FILENAME}


'''
Creates a table in the SQLite database using the provided filename and SQL statement.

Parameters:
- filename (str): The name of the SQLite database file.
- sql_statement (str): The SQL statement to create the table.
'''
def create_table(filename: str, sql_statement: str):
    try:
        with sqlite3.connect(filename) as connection:
            cursor = connection.cursor()
            cursor.execute(sql_statement)
            connection.commit()
    except sqlite3.Error as e:
        print(e)

'''
Drops a table from the SQLite database using the provided filename and SQL statement.

Parameters:
- filename (str): The name of the SQLite database file.
- sql_statement (str): The SQL statement to drop the table.
'''
def drop_table(filename: str, sql_statement: str):
    try:
        with sqlite3.connect(filename) as connection:
            cursor = connection.cursor()
            cursor.execute(sql_statement)
    except sqlite3.Error as e:
        print(e)

'''
Inserts a new user into the users database with the provided username and email.

Parameters:
- username (str): The username of the new user.
- email (str): The email of the new user.

Returns:
- tuple[int, str]: A tuple containing the user id and a potential error message.
'''
def insert_user(username: str, email: str) -> tuple[int, str]:
    id: int = None
    msg: str = None

    try:
        with sqlite3.connect(db_files[Table.USERS]) as connection:
            cursor = connection.cursor()
            cursor.execute(SQL_Statement.USERS_INSERT, (username, email))
            connection.commit()
            id = cursor.lastrowid

        with cache_mutex:
            balance_cache[id] = {currency: 0 for currency in Currency}

        print("Cache:")
        pprint(balance_cache)
    except Exception as e:
        print(e)
        msg = str(e)
        
    return id, msg

'''
Deposit a transaction for a user. Store operation in the transactions database.

Parameters:
- user_id (int): The user id for the transaction.
- amount (float): The amount to deposit.
- currency_type (Currency): The type of currency for the deposit.

Returns:
- tuple[int, str]: A tuple containing the transaction id and a potential error message.
'''
def deposit_transaction(user_id: int, amount: float, currency_type: Currency) -> tuple[int, str]:
    id: int = None
    msg: str = None

    try:
        with cache_mutex:
            if user_id not in balance_cache:
                raise Exception(Error_Message.INVALID_SOURCE_USER)
            
            with sqlite3.connect(db_files[Table.TRANSACTIONS]) as connection:
                cursor = connection.cursor()
                cursor.execute(SQL_Statement.TRANSACTIONS_DEPOSIT, (user_id, amount, currency_type))
                connection.commit()
                id = cursor.lastrowid

            balance_cache[user_id][currency_type] = balance_cache[user_id].get(currency_type, 0) + amount

        print("Cache:")
        pprint(balance_cache)
    except Exception as e:
        print(e)
        msg = str(e)
        
    return id, msg

'''
Transfer a transaction between two users in the database. Store operation in the transactions database.

Parameters:
- source_id (int): The user id of the source user.
- target_id (int): The user id of the target user.
- amount (float): The amount to transfer.
- currency_type (Currency): The type of currency for the transfer.

Returns:
- tuple[int, str]: A tuple containing the transaction id and a potential error message.
'''
def transfer_transaction(source_id: int, target_id: int, amount: float, currency_type: Currency) -> tuple[int, str]:
    id: int = None
    msg: str = None

    try:
        with cache_mutex:
            if source_id not in balance_cache:
                raise Exception(Error_Message.INVALID_SOURCE_USER)
            if target_id not in balance_cache:
                raise Exception(Error_Message.INVALID_TARGET_USER)

            current_balance = balance_cache[source_id][currency_type]

            if current_balance < amount:
                raise Exception(Error_Message.INSUFFICIENT_FUNDS_TRANSFER)
            
            with sqlite3.connect(db_files[Table.TRANSACTIONS]) as connection:
                cursor = connection.cursor()
                cursor.execute(SQL_Statement.TRANSACTIONS_TRANSFER, (source_id, target_id, amount, currency_type))
                connection.commit()
                id = cursor.lastrowid

            balance_cache[source_id][currency_type] = balance_cache[source_id].get(currency_type, 0) - amount
            balance_cache[target_id][currency_type] = balance_cache[target_id].get(currency_type, 0) + amount

        print("Cache:")
        pprint(balance_cache)
    except Exception as e:
        print(e)
        msg = str(e)
        
    return id, msg

'''
Get the balance of a user and currency type, or all currencies.

Parameters:
- user_id (int): The user id for whom the balance is retrieved.
- currency_type (Currency | None): The type of currency for which the balance is retrieved. If None, retrieves balances for all currency types.

Returns:
- tuple[dict[Currency, float], str]: A tuple containing the balance data, and a potential error message.
''' 
def balance_transaction(user_id: int, currency_type: Currency | None) -> tuple[dict[Currency, float], str]:
    with cache_mutex:
        if user_id not in balance_cache:
            return None, Error_Message.INVALID_SOURCE_USER
        if currency_type is None:
            return balance_cache[user_id], None
        return {currency_type: balance_cache[user_id][currency_type]}, None

'''
Withdraws a transaction for a user. Store operation in the transactions database.

Parameters:
- user_id (int): The user id for the transaction.
- amount (float): The amount to withdraw.
- currency_type (Currency): The type of currency for the withdrawal.

Returns:
- tuple[int, str]: A tuple containing the transaction id and a potential error message.
'''
def withdraw_transaction(user_id: int, amount: float, currency_type: Currency) -> tuple[int, str]:
    id: int = None
    msg: str = None

    try:
        with cache_mutex:
            if user_id not in balance_cache:
                raise Exception(Error_Message.INVALID_SOURCE_USER)

            current_balance = balance_cache[user_id][currency_type]

            if current_balance < amount:
                raise Exception(Error_Message.INSUFFICIENT_FUNDS_WITHDRAW)
            
            with sqlite3.connect(db_files[Table.TRANSACTIONS]) as connection:            
                cursor = connection.cursor()
                cursor.execute(SQL_Statement.TRANSACTIONS_DEPOSIT, (user_id, amount, currency_type))
                connection.commit()
                id = cursor.lastrowid

            balance_cache[user_id][currency_type] = balance_cache[user_id].get(currency_type, 0) - amount

        print("Cache:")
        pprint(balance_cache)
    except Exception as e:
        print(e)
        msg = str(e)
        
    return id, msg

'''
Creates the users table.

Parameters:
- testing (bool): A flag indicating whether the function is being used for testing purposes. Defaults to False.
'''
def create_users_table(testing: bool = False):
    if testing:
        db_files[Table.USERS] = Filename.TEST_USERS_DB_FILENAME
    create_table(db_files[Table.USERS], SQL_Statement.USERS_CREATE_TABLE)

'''
Creates the transacations table.

Parameters:
- testing (bool): A flag indicating whether the function is being used for testing purposes. Defaults to False.
'''
def create_transactions_table(testing: bool = False):
    if testing:
        db_files[Table.TRANSACTIONS] = Filename.TEST_TRANSACTIONS_DB_FILENAME
    create_table(db_files[Table.TRANSACTIONS], SQL_Statement.TRANSACTIONS_CREATE_TABLE)

'''
Drops the users table.
'''
def drop_users_table():
    drop_table(db_files[Table.USERS], SQL_Statement.USERS_DROP_TABLE)

'''
Drops the transacations table.
'''
def drop_transactions_table():
    drop_table(db_files[Table.TRANSACTIONS], SQL_Statement.TRANSACTIONS_DROP_TABLE)

'''
Populates the balance cache with transaction data from the transactions database.
'''
def populate_balance_cache():
    rows = []

    try:
        with cache_mutex:
            with sqlite3.connect(db_files[Table.USERS]) as connection:
                cursor = connection.cursor()
                cursor.execute(SQL_Statement.USERS_SELECT)
                rows = cursor.fetchall()
                
                for row in rows:
                    user_id = int(row[0])
                    balance_cache[user_id] = {currency: 0 for currency in Currency}
                

            with sqlite3.connect(db_files[Table.TRANSACTIONS]) as connection:
                cursor = connection.cursor()
                cursor.execute(SQL_Statement.TRANSACTIONS_SELECT)
                rows = cursor.fetchall()

                for transaction_id, source_id, target_id, transaction_type, amount, currency_type in rows:
                    transaction_id = int(transaction_id)
                    source_id = int(source_id)
                    if target_id is not None:
                        target_id = int(target_id)
                    amount = float(amount)

                    print(transaction_id, source_id, target_id, transaction_type, amount, currency_type)

                    if transaction_type == Transaction.DEPOSIT:
                        if source_id not in balance_cache:
                            balance_cache[source_id] = {currency: 0 for currency in Currency}
                        balance_cache[source_id][currency_type] = balance_cache[source_id].get(currency_type, 0) + amount
                    elif transaction_type == Transaction.WITHDRAW:
                        if source_id not in balance_cache:
                            balance_cache[source_id] = {currency: 0 for currency in Currency}
                        balance_cache[source_id][currency_type] = balance_cache[source_id].get(currency_type, 0) - amount
                    elif transaction_type == Transaction.TRANSFER:
                        if source_id not in balance_cache:
                            balance_cache[source_id] = {currency: 0 for currency in Currency}
                        if target_id not in balance_cache:
                            balance_cache[target_id] = {currency: 0 for currency in Currency}
                        balance_cache[source_id][currency_type] = balance_cache[source_id].get(currency_type, 0) - amount
                        balance_cache[target_id][currency_type] = balance_cache[target_id].get(currency_type, 0) + amount

        print("Cache:")
        pprint(balance_cache)
    except Exception as e:
        print(e)

