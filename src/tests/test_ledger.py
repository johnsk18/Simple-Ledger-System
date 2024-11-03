from client.database import create_transactions_table, create_users_table, drop_users_table, drop_transactions_table, populate_balance_cache
from constants import API_Query, Currency, Error_Message
from flask import Flask
from flask.testing import FlaskClient
from server.app import app as app
from typing import Generator
import pytest


class Amount(float):
    ONE = 36
    TWO = 1337.37
    THREE = 342.65
    FOUR = 37
    FIVE = 337.98
    SIX = 12.05
    SEVEN = 4.5
    EIGHT = 10.04

@pytest.fixture(scope="session")
def test_app() -> Generator[Flask, None, None]:
    app.config.update({"TESTING": True})

    # Setup
    create_users_table(testing=True)
    create_transactions_table(testing=True)
    populate_balance_cache()

    yield app

    # Clear Resources
    drop_users_table()
    drop_transactions_table()

@pytest.fixture(scope="session")
def client(test_app: Flask) -> FlaskClient:
    return test_app.test_client()

def verify_create_user_response(user_response_json: dict[str, str], name: str, email: str):
    assert user_response_json[API_Query.NAME] == name
    assert user_response_json[API_Query.EMAIL] == email

    assert API_Query.USER_ID in user_response_json

def verify_new_user(user_response_json: dict[str, str], name: str, email: str):
    verify_create_user_response(user_response_json, name, email)

    from client.database import balance_cache
    user_id = user_response_json[API_Query.USER_ID]
    assert user_id in balance_cache
    assert len(balance_cache[user_id]) == len(Currency)

    for currency in Currency:
        assert balance_cache[user_id][currency] == 0

def test_create_user1(client: FlaskClient):
    name = "test1"
    email = "test1@email.com"

    response = client.get(f"/create?{API_Query.NAME}={name}&{API_Query.EMAIL}={email}")
    
    verify_new_user(response.json, name, email)

def test_create_user2(client: FlaskClient):
    name = "test2"
    email = "test2@email.com"

    response = client.get(f"/create?{API_Query.NAME}={name}&{API_Query.EMAIL}={email}")
    
    verify_new_user(response.json, name, email)

def test_create_user3(client: FlaskClient):
    name = "test3"
    email = "test3@email.com"

    response = client.get(f'/create?{API_Query.NAME}={name}&{API_Query.EMAIL}={email}')
    
    verify_new_user(response.json, name, email)

def verify_amount(user_id: int, amount: float, currency_type: Currency):
    from client.database import balance_cache
    assert balance_cache[user_id][currency_type] == amount

def verify_deposit_response(user_response_json: dict[str, str], user_id: int, amount: float, currency_type: Currency):
    assert user_response_json[API_Query.USER_ID] == user_id
    assert user_response_json[API_Query.AMOUNT] == amount
    assert user_response_json[API_Query.CURRENCY_TYPE] == currency_type

def test_one_deposit(client: FlaskClient):
    user_id = 1
    amount = Amount.ONE
    currency_type = Currency.BITCOIN

    verify_amount(user_id, 0, currency_type)
    verify_amount(user_id, 0, Currency.ETHEREUM)
    verify_amount(user_id, 0, Currency.MATIC)

    response = client.get(f'/deposit?{API_Query.USER_ID}={user_id}&{API_Query.AMOUNT}={amount}&{API_Query.CURRENCY_TYPE}={currency_type}')

    verify_amount(user_id, amount, currency_type)
    verify_amount(user_id, 0, Currency.ETHEREUM)
    verify_amount(user_id, 0, Currency.MATIC)

    verify_deposit_response(response.json, user_id, amount, currency_type)

def test_two_deposits(client: FlaskClient):
    user_id = 2
    amount1 = Amount.TWO
    currency_type1 = Currency.ETHEREUM

    verify_amount(user_id, 0, currency_type1)
    verify_amount(user_id, 0, Currency.BITCOIN)
    verify_amount(user_id, 0, Currency.MATIC)

    response1 = client.get(f'/deposit?{API_Query.USER_ID}={user_id}&{API_Query.AMOUNT}={amount1}&{API_Query.CURRENCY_TYPE}={currency_type1}')

    verify_amount(user_id, amount1, currency_type1)
    verify_amount(user_id, 0, Currency.BITCOIN)
    verify_amount(user_id, 0, Currency.MATIC)

    verify_deposit_response(response1.json, user_id, amount1, currency_type1)

    amount2 = Amount.THREE
    currency_type2 = Currency.BITCOIN

    response2 = client.get(f'/deposit?{API_Query.USER_ID}={user_id}&{API_Query.AMOUNT}={amount2}&{API_Query.CURRENCY_TYPE}={currency_type2}')

    verify_amount(user_id, amount1, currency_type1)
    verify_amount(user_id, amount2, currency_type2)
    verify_amount(user_id, 0, Currency.MATIC)
    
    verify_deposit_response(response2.json, user_id, amount2, currency_type2)

def test_three_deposits(client: FlaskClient):
    user_id = 3
    amount1 = Amount.FOUR
    currency_type1 = Currency.MATIC

    verify_amount(user_id, 0, currency_type1)
    verify_amount(user_id, 0, Currency.ETHEREUM)
    verify_amount(user_id, 0, Currency.BITCOIN)

    response = client.get(f'/deposit?{API_Query.USER_ID}={user_id}&{API_Query.AMOUNT}={amount1}&{API_Query.CURRENCY_TYPE}={currency_type1}')

    verify_amount(user_id, amount1, currency_type1)
    verify_amount(user_id, 0, Currency.ETHEREUM)
    verify_amount(user_id, 0, Currency.BITCOIN)

    verify_deposit_response(response.json, user_id, amount1, currency_type1)

    amount2 = Amount.FIVE
    currency_type2 = Currency.ETHEREUM

    response2 = client.get(f'/deposit?{API_Query.USER_ID}={user_id}&{API_Query.AMOUNT}={amount2}&{API_Query.CURRENCY_TYPE}={currency_type2}')

    verify_amount(user_id, amount1, currency_type1)
    verify_amount(user_id, amount2, currency_type2)
    verify_amount(user_id, 0, Currency.BITCOIN)
    
    verify_deposit_response(response2.json, user_id, amount2, currency_type2)
    
    amount3 = Amount.SIX
    currency_type3 = Currency.BITCOIN

    response3 = client.get(f'/deposit?{API_Query.USER_ID}={user_id}&{API_Query.AMOUNT}={amount3}&{API_Query.CURRENCY_TYPE}={currency_type3}')

    verify_amount(user_id, amount1, currency_type1)
    verify_amount(user_id, amount2, currency_type2)
    verify_amount(user_id, amount3, currency_type3)
    
    verify_deposit_response(response3.json, user_id, amount3, currency_type3)

def test_additional_deposit(client: FlaskClient):
    user_id = 1
    amount = Amount.SEVEN
    currency_type = Currency.BITCOIN

    verify_amount(user_id, 36, currency_type)
    verify_amount(user_id, 0, Currency.ETHEREUM)
    verify_amount(user_id, 0, Currency.MATIC)

    response = client.get(f'/deposit?{API_Query.USER_ID}={user_id}&{API_Query.AMOUNT}={amount}&{API_Query.CURRENCY_TYPE}={currency_type}')

    verify_amount(user_id, Amount.ONE + amount, currency_type)
    verify_amount(user_id, 0, Currency.ETHEREUM)
    verify_amount(user_id, 0, Currency.MATIC)

    verify_deposit_response(response.json, user_id, amount, currency_type)

def test_invalid_deposit_with_invalid_user(client: FlaskClient):
    user_id = 10
    amount = Amount.SEVEN
    currency_type = Currency.BITCOIN

    response = client.get(f'/deposit?{API_Query.USER_ID}={user_id}&{API_Query.AMOUNT}={amount}&{API_Query.CURRENCY_TYPE}={currency_type}')

    assert API_Query.ERROR in response.json
    assert response.json[API_Query.ERROR] == Error_Message.INVALID_SOURCE_USER
    assert API_Query.USER_ID not in response.json
    assert API_Query.AMOUNT not in response.json
    assert API_Query.CURRENCY_TYPE not in response.json


def verify_transfer_response(user_response_json: dict[str, str], source_user_id: int, target_user_id: int, amount: float, currency_type: Currency):
    assert user_response_json[API_Query.SOURCE_USER_ID] == source_user_id
    assert user_response_json[API_Query.TARGET_USER_ID] == target_user_id
    assert user_response_json[API_Query.AMOUNT] == amount
    assert user_response_json[API_Query.CURRENCY_TYPE] == currency_type

def test_transfer(client: FlaskClient):
    source_user_id = 2
    target_user_id = 3
    amount = Amount.EIGHT
    currency_type = Currency.BITCOIN

    verify_amount(source_user_id, Amount.THREE, currency_type)
    verify_amount(target_user_id, Amount.SIX, currency_type)

    response = client.get(f'/transfer?{API_Query.SOURCE_USER_ID}={source_user_id}&{API_Query.TARGET_USER_ID}={target_user_id}&{API_Query.AMOUNT}={amount}&{API_Query.CURRENCY_TYPE}={currency_type}')

    verify_amount(source_user_id, Amount.THREE - amount, currency_type)
    verify_amount(target_user_id, Amount.SIX + amount, currency_type)

    verify_transfer_response(response.json, source_user_id, target_user_id, amount, currency_type)

def test_invalid_transfer_with_insufficient_funds(client: FlaskClient):
    source_user_id = 3
    target_user_id = 1
    amount = Amount.TWO
    currency_type = Currency.MATIC

    verify_amount(source_user_id, Amount.FOUR, currency_type)
    verify_amount(target_user_id, 0, currency_type)

    response = client.get(f'/transfer?{API_Query.SOURCE_USER_ID}={source_user_id}&{API_Query.TARGET_USER_ID}={target_user_id}&{API_Query.AMOUNT}={amount}&{API_Query.CURRENCY_TYPE}={currency_type}')

    verify_amount(source_user_id, Amount.FOUR, currency_type)
    verify_amount(target_user_id, 0, currency_type)

    assert API_Query.ERROR in response.json
    assert response.json[API_Query.ERROR] == Error_Message.INSUFFICIENT_FUNDS_TRANSFER
    assert API_Query.SOURCE_USER_ID not in response.json
    assert API_Query.TARGET_USER_ID not in response.json
    assert API_Query.AMOUNT not in response.json
    assert API_Query.CURRENCY_TYPE not in response.json

def test_invalid_transfer_from_invalid_user(client: FlaskClient):
    source_user_id = 14
    target_user_id = 1
    amount = Amount.TWO
    currency_type = Currency.MATIC

    verify_amount(target_user_id, 0, currency_type)

    response = client.get(f'/transfer?{API_Query.SOURCE_USER_ID}={source_user_id}&{API_Query.TARGET_USER_ID}={target_user_id}&{API_Query.AMOUNT}={amount}&{API_Query.CURRENCY_TYPE}={currency_type}')

    verify_amount(target_user_id, 0, currency_type)

    assert API_Query.ERROR in response.json
    assert response.json[API_Query.ERROR] == Error_Message.INVALID_SOURCE_USER
    assert API_Query.SOURCE_USER_ID not in response.json
    assert API_Query.TARGET_USER_ID not in response.json
    assert API_Query.AMOUNT not in response.json
    assert API_Query.CURRENCY_TYPE not in response.json

def test_invalid_transfer_to_invalid_user(client: FlaskClient):
    source_user_id = 1
    target_user_id = 29
    amount = Amount.TWO
    currency_type = Currency.ETHEREUM

    verify_amount(source_user_id, 0, currency_type)

    response = client.get(f'/transfer?{API_Query.SOURCE_USER_ID}={source_user_id}&{API_Query.TARGET_USER_ID}={target_user_id}&{API_Query.AMOUNT}={amount}&{API_Query.CURRENCY_TYPE}={currency_type}')

    verify_amount(source_user_id, 0, currency_type)

    assert API_Query.ERROR in response.json
    assert response.json[API_Query.ERROR] == Error_Message.INVALID_TARGET_USER
    assert API_Query.SOURCE_USER_ID not in response.json
    assert API_Query.TARGET_USER_ID not in response.json
    assert API_Query.AMOUNT not in response.json
    assert API_Query.CURRENCY_TYPE not in response.json

def verify_balance_response(user_response_json: dict[str, str], user_id: int, currency_type: Currency = None):
    assert user_response_json[API_Query.USER_ID] == user_id

    from client.database import balance_cache
    if currency_type is None:
        for currency in Currency:
            assert currency in user_response_json
            assert balance_cache[user_id][currency] == user_response_json[currency]

    else:
        assert currency_type in user_response_json
        assert balance_cache[user_id][currency_type] == user_response_json[currency_type]

def test_balance_with_currency(client: FlaskClient):
    user_id = 1
    currency_type = Currency.BITCOIN

    response = client.get(f'/balance?{API_Query.USER_ID}={user_id}&{API_Query.CURRENCY_TYPE}={currency_type}')

    verify_balance_response(response.json, user_id, currency_type)

def test_balance_without_currency(client: FlaskClient):
    user_id = 1

    response = client.get(f'/balance?{API_Query.USER_ID}={user_id}')
    
    verify_balance_response(response.json, user_id)

def test_invalid_balance_with_invalid_user(client: FlaskClient):
    user_id = 19

    response = client.get(f'/balance?{API_Query.USER_ID}={user_id}')

    assert API_Query.ERROR in response.json
    assert response.json[API_Query.ERROR] == Error_Message.INVALID_SOURCE_USER
    assert API_Query.USER_ID not in response.json
    
    for currency in Currency:
        assert currency not in response.json
    

def verify_withdraw_response(user_response_json: dict[str, str], user_id: int, amount: float, currency_type: Currency):
    assert user_response_json[API_Query.USER_ID] == user_id
    assert user_response_json[API_Query.AMOUNT] == amount
    assert user_response_json[API_Query.CURRENCY_TYPE] == currency_type
    

def test_withdraw(client: FlaskClient):
    user_id = 1
    amount = Amount.ONE
    currency_type = Currency.BITCOIN

    verify_amount(user_id, amount + Amount.SEVEN, currency_type)

    response = client.get(f'/withdraw?{API_Query.USER_ID}={user_id}&{API_Query.AMOUNT}={amount}&{API_Query.CURRENCY_TYPE}={currency_type}')
    
    verify_amount(user_id, Amount.SEVEN, currency_type)
    verify_withdraw_response(response.json, user_id, amount, currency_type)

def test_invalid_withdraw_with_insufficient_funds1(client: FlaskClient):
    user_id = 1
    amount = Amount.TWO
    currency_type = Currency.BITCOIN

    response = client.get(f'/withdraw?{API_Query.USER_ID}={user_id}&{API_Query.AMOUNT}={amount}&{API_Query.CURRENCY_TYPE}={currency_type}')

    assert API_Query.ERROR in response.json
    assert response.json[API_Query.ERROR] == Error_Message.INSUFFICIENT_FUNDS_WITHDRAW
    assert API_Query.USER_ID not in response.json
    assert API_Query.AMOUNT not in response.json
    assert API_Query.CURRENCY_TYPE not in response.json

def test_invalid_withdraw_with_insufficient_funds2(client: FlaskClient):
    user_id = 2
    amount = Amount.FIVE
    currency_type = Currency.MATIC

    response = client.get(f'/withdraw?{API_Query.USER_ID}={user_id}&{API_Query.AMOUNT}={amount}&{API_Query.CURRENCY_TYPE}={currency_type}')

    assert API_Query.ERROR in response.json
    assert response.json[API_Query.ERROR] == Error_Message.INSUFFICIENT_FUNDS_WITHDRAW
    assert API_Query.USER_ID not in response.json
    assert API_Query.AMOUNT not in response.json
    assert API_Query.CURRENCY_TYPE not in response.json

def test_invalid_withdraw_with_invalid_user(client: FlaskClient):
    user_id = 10
    amount = Amount.SEVEN
    currency_type = Currency.BITCOIN

    response = client.get(f'/withdraw?{API_Query.USER_ID}={user_id}&{API_Query.AMOUNT}={amount}&{API_Query.CURRENCY_TYPE}={currency_type}')

    assert API_Query.ERROR in response.json
    assert response.json[API_Query.ERROR] == Error_Message.INVALID_SOURCE_USER
    assert API_Query.USER_ID not in response.json
    assert API_Query.AMOUNT not in response.json
    assert API_Query.CURRENCY_TYPE not in response.json
