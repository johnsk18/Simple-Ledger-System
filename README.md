# Basic Ledger API
## Description
A simple ledger system with the following capabilities:

1. Creation of users.
2. Deposits for users in any currency*.
3. Transfers between users in any currency*.
4. Listing of balances.
5. Withdrawals by users.

\* Supported currencies are Bitcoin, Ethereum, and Matic; as per database schema spec.


## Table of Contents
- [Installation](#installation)
- [Usage](#usage)
- [Implementation](#implementation)

## Installation
Provide step-by-step instructions on how to install and set up the project. This might include:
1. Cloning the repository
    ```sh
    git clone https://github.com/johnsk18/basic-ledger-exercise.git
    ```
2. Navigate to the project directory.
    ```sh
    cd basic-ledger-exercise
    ```
3. Installing dependencies
    ```sh
    pip install -r requirements.txt
    ```
3. Navigate to the /src/ directory.
    ```sh
    cd src
    ```

## Usage
Only run these commands when you are in the /src/ directory.

Run this command to start the ledger server.
```sh
python main.py
```
Run this command to run the unit tests.
```sh
pytest -v
```

Once started, open this link in your browser: `http://localhost:3000`  
Below are the endpoints to be added to your link to perform the ledger functionalities.
<br><br>

### Create User Endpoint
```sh
/create?name={}&email={}
```
#### Parameters
- name: The user's name
- email: The user's email
#### Response
- user_id: The user id, used for transactional endpoints. <mark> Save this value!</mark>
- name: The user's name
- email: The user's email
#### Effects
- Adds user to users database, to be used for transactions.
---
### Deposit Endpoint
```sh
/deposit?user_id={}&amount={}&currency_type={}
```
#### Parameters
- user_id: The user's id
- amount: The value to deposit
- currency_type: The currency used. Must be bitcoin, ethereum, or matic.
#### Response
- transaction_id: The transaction id
- user_id: The user's id
- amount: The value deposited
- currency_type: The currency used.
#### Effects
- Deposits *value* of *currency_type* into the account associated with *user_id*.
- If insufficient funds, returns error.
- If invalid user, returns error.
---
### Transfer Endpoint
```sh
/transfer?source_user_id={}&target_user_id={}&amount={}&currency_type={}
```
#### Parameters
- source_user_id: The user's id who is sending money.
- target_user_id: The user's id who is receiving money.
- amount: The value to transfer.
- currency_type: The currency used. Must be bitcoin, ethereum, or matic.
#### Response
- transaction_id: The transaction id
- source_user_id: The user's id who is sending money.
- target_user_id: The user's id who is receiving money.
- amount: The value transfered
- currency_type: The currency used.
#### Effects
- Tranfsers *value* of *currency_type* from the account associated with *source_user_id* to the account associated with *target_user_id*.
- If insufficient funds, returns error.
- If invalid user, returns error.
---
### Balance Endpoint
```sh
/balance?user_id={}
/balance?user_id={}&currency_type={}
```
#### Parameters
- user_id: The user's id
- currency_type: Optional. The currency used.
#### Response
- user_id: The user's id
- If currency_type provided, response contains key-value pair of type to balance. Otherwise, balances for all currency types are returned.
---
### Withdraw Endpoint
```sh
/withdraw?user_id={}&amount={}&currency_type={}
```
#### Parameters
- user_id: The user's id
- amount: The value to withdraw
- currency_type: The currency used. Must be bitcoin, ethereum, or matic.
#### Response
- transaction_id: The transaction id
- user_id: The user's id
- amount: The value withdrawn
- currency_type: The currency used.
#### Effects
- Withdraws *value* of *currency_type* into the account associated with *user_id*.
- If insufficient funds, returns error.
- If invalid user, returns error.

## Implementation
To begin, I knew I was going to have to get more familiar with Flask, requests, sqlite3, and multi-threading. I spent some time learning how to use each framework to build each feature; Flask for the server, requests for the API, and sqlite3 for the database.

Using Flask was relatively simple. I turned up a local server and was able to host a simple landing page in JSON. Given more time, I could reasearch frontend web developement to add HTML and CSS for a proper looking webpage. For the purposes of this project, I wanted to make sure to focus on the core features of the project. I was able to create the necessary endpoints that I needed for the features.

Using Python requests proved very useful, pairing with Flask. The library provides easy to use resources to parse the API request from the URL.

There were multiple options for choosing a database library, but sqlite3 proved to be light-weight and efficient in doing its job. For scalability, we can upgrade the database framework that can handle more massive files.

I knew multi-threading was going to be necessary for accessing a database from an API to prevent race conditions. Sqlite3 is defaulted to serialized mode, meaning that any database connection are thread-safe. To avoid deadlock situations for non-databse variables, I implemented a mutex lock for my balance cache. 

The purpose of the cache is to keep a running in-memory total of account balances. The cache is populated with respect to the transaction database before the server goes live. The reason I do not have a databse for balances is because I believe when scaled, this provides an extreme security flaw. By calculating the balances thorugh a calculation of the transactions. To scale this up, there would be a constantly running separate server that hosts this balance cache. Alternatively, this server can have access to a databse to store balances for a user up to a certain date or statement. Memory can be corrupted and a customer may have an enormous amount of transactions, causing the time of calculating the balances to increase. This way, we only need to calculate the transaction up to certain date in the past.

At the moment, this ledger system supports bitcoin, matic, and ethereum; however, it can be scaled to handle more currencies by updating the Currency enumeration in constants.py file. Whether this file should remain a python file or config file is a valid debate topic for design.
