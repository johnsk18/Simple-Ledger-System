from constants import API_Query, Currency
from client.database import insert_user, deposit_transaction, transfer_transaction, balance_transaction, withdraw_transaction
from flask import request
from server.app import app

'''
Landing Page.

Returns:
    dict: Landing page response.
'''
@app.route('/')
def landingPage():
    return {"message": "Welcome!"}

'''
Create User Endpoint, to create a new user.

Returns:
    dict: Response containing user_id, name, and email.
'''
@app.route('/create')
def createUser():
    name = request.args.get(API_Query.NAME, None, str)
    email = request.args.get(API_Query.EMAIL, None, str)

    user_id, message = insert_user(name, email)
    if user_id is None:
        return {API_Query.ERROR: message}
    
    print("Create:", (user_id, name, email))

    return {API_Query.USER_ID: user_id, API_Query.NAME: name, API_Query.EMAIL: email}

'''
Deposit Endpoint, to deposit money to a user's account.

Returns:
    dict: Response containing transaction_id, user_id, amount, and currency_type.
'''
@app.route('/deposit')
def deposit():
    user_id = request.args.get(API_Query.USER_ID, None, int)
    amount = request.args.get(API_Query.AMOUNT, None, float)
    currency_type = request.args.get(API_Query.CURRENCY_TYPE, None, Currency)

    transaction_id, message = deposit_transaction(user_id, amount, currency_type)
    if transaction_id is None:
        return {API_Query.ERROR: message}
    
    print("Deposit:", (transaction_id, user_id, amount, currency_type))
    
    return {API_Query.TRANSACTION_ID: transaction_id, API_Query.USER_ID: user_id, API_Query.AMOUNT: amount, API_Query.CURRENCY_TYPE: currency_type}

'''
Transfer Endpoint, to transfer money between two users' account.

Returns:
    dict: Response containing transaction_id, source_user_id, target_user_id, amount, and currency_type.
'''
@app.route('/transfer')
def transfer():
    source_id = request.args.get(API_Query.SOURCE_USER_ID, None, int)
    target_id = request.args.get(API_Query.TARGET_USER_ID, None, int)
    amount = request.args.get(API_Query.AMOUNT, None, float)
    currency_type = request.args.get(API_Query.CURRENCY_TYPE, None, Currency)

    transaction_id, message = transfer_transaction(source_id, target_id, amount, currency_type)
    if transaction_id is None:
        return {API_Query.ERROR: message}
    
    print("Transfer:", (transaction_id, source_id, target_id, amount, currency_type))

    return {API_Query.TRANSACTION_ID: transaction_id, API_Query.SOURCE_USER_ID: source_id, API_Query.TARGET_USER_ID: target_id, API_Query.AMOUNT: amount, API_Query.CURRENCY_TYPE: currency_type}

'''
Balance Endpoint, to show the current balance of a given currency for a user's account.

Returns:
    dict: Response containing user_id and balance based on currency. If no currency provided, show all currency balances.
'''
@app.route('/balance')
def getBalances():
    user_id = request.args.get(API_Query.USER_ID, None, int)
    currency_type = request.args.get(API_Query.CURRENCY_TYPE, None, Currency)

    map, msessage = balance_transaction(user_id, currency_type)
    if map is None:
        return {API_Query.ERROR: msessage}
    
    response = {API_Query.USER_ID: user_id}
    response.update(map)

    return response

'''
Withdraw Endpoint, to withdraw money from a user's account.

Returns:
    dict: Response containing transaction_id, user_id, amount, and currency_type.
'''
@app.route('/withdraw')
def withdraw():
    user_id = request.args.get(API_Query.USER_ID, None, int)
    amount = request.args.get(API_Query.AMOUNT, None, float)
    currency_type = request.args.get(API_Query.CURRENCY_TYPE, None, Currency) 

    transaction_id, message = withdraw_transaction(user_id, amount, currency_type)
    if transaction_id is None:
        return {API_Query.ERROR: message}
    
    print("Withdraw:", (transaction_id, user_id, amount, currency_type))
    
    return {API_Query.TRANSACTION_ID: transaction_id, API_Query.USER_ID: user_id, API_Query.AMOUNT: amount, API_Query.CURRENCY_TYPE: currency_type}
