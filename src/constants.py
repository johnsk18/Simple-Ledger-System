from enum import StrEnum

"""
Enum representing different tables.
"""
class Table(StrEnum):
    USERS = "users"
    TRANSACTIONS = "transactions"

"""
Enum representing different filenames for the tables.
"""
class Filename(StrEnum):
    USERS_DB_FILENAME = "users.db"
    TRANSACTIONS_DB_FILENAME = "transactions.db"
    TEST_USERS_DB_FILENAME = "./tests/test_users.db"
    TEST_TRANSACTIONS_DB_FILENAME = "./tests/test_transactions.db"

"""
Enum representing different SQL statements.
"""
class SQL_Statement(StrEnum):
    USERS_CREATE_TABLE = """CREATE TABLE IF NOT EXISTS users (
    user_id integer primary key,
    user_name text not null,
    email text unique not null)"""
    TRANSACTIONS_CREATE_TABLE = """CREATE TABLE IF NOT EXISTS transactions (
    transaction_id integer primary key,
    source_user_id integer not null,
    target_user_id integer,
    transaction_type text not null,
    amount real not null,
    currency_type text not null)"""
    USERS_DROP_TABLE = """DROP TABLE users"""
    TRANSACTIONS_DROP_TABLE = """DROP TABLE transactions"""
    USERS_SELECT = """SELECT * FROM users"""
    TRANSACTIONS_SELECT = """SELECT * FROM transactions"""
    USERS_INSERT = """INSERT INTO users(user_name, email)
    VALUES(?,?)"""
    TRANSACTIONS_DEPOSIT = """INSERT INTO transactions(source_user_id, transaction_type, amount, currency_type)
    VALUES(?, "deposit", ?, ?)"""
    TRANSACTIONS_TRANSFER =  """INSERT INTO transactions(source_user_id, target_user_id, transaction_type, amount, currency_type)
    VALUES(?, ?, "transfer", ?, ?)"""
    TRANSACTIONS_BALANCE = """SELECT * FROM transactions
    WHERE (source_user_id = ? AND transaction_type = 'deposit')
    OR (target_user_id = ? AND transaction_type = 'transfer')
    OR (source_user_id = ? AND transaction_type = 'transfer')"""
    TRANSACTIONS_WITHDRAW = """INSERT INTO transactions(source_user_id, transaction_type, amount, currency_type)
    VALUES(?, "withdraw", ?, ?)"""


"""
Enum representing different currencies.
"""
class Currency(StrEnum):
    BITCOIN = "bitcoin"
    ETHEREUM = "ethereum"
    MATIC = "matic"

"""
Enum representing different operations for transactions.
"""
class Transaction(StrEnum):
    DEPOSIT = "deposit"
    TRANSFER = "transfer"
    WITHDRAW = "withdraw"

"""
Enum representing different error messages.
"""
class Error_Message(StrEnum):
    INSUFFICIENT_FUNDS_TRANSFER = "Insufficient funds for transfer."
    INSUFFICIENT_FUNDS_WITHDRAW = "Insufficient funds for withdrawl."
    INVALID_SOURCE_USER = "Source user id not found."
    INVALID_TARGET_USER = "Target user id not found."

"""
Enum representing the parameter names in the API.
"""
class API_Query(StrEnum):
    NAME = "name"
    EMAIL = "email"
    USER_ID = "user_id"
    AMOUNT = "amount"
    CURRENCY_TYPE = "currency_type"
    SOURCE_USER_ID = "source_user_id"
    TARGET_USER_ID = "target_user_id"
    TRANSACTION_ID = "transaction_id"
    ERROR = "error"
