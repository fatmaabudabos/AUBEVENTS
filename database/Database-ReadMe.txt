1-  To access the database, you need to have these downloaded:

    -python:
        https://www.python.org/downloads/
        (in the install process, make sure you tick "pip", and "Add python to environment variables")
        To make sure it was successful, go to terminal and run these codes:
            python --version
            pip --version

    -SQLModel and PyMySQL:
        Go to terminal and run these commands:
            pip install sqlmodel
            pip install PyMySQL


2-  To keep the database safe, the URL is saved in a separate file
    named DB_Password.py, which will be sent privately. What you need
    to do is place this file in the same folder as database.py file. 
    Do NOT push this file to github.


3-  Importing database functions:

    - To create, update, delete or read any data from the database, you need to import them to you file using:

        from database.database import (
        create_user, get_user, get_password, get_is_admin, get_is_verified, get_verification_token,
        get_verification_token_expiry, get_reset_code, get_reset_code_expiry,
        update_password, update_is_admin, update_is_verified, update_verification_token,
        update_reset_code, delete_user
        )

4-  Using database functions:  

    -create_user(email, password_hash)

    -get_user(email) -> (returns user object)

    -get_password(email) -> (returns string)
    -get_is_admin(email) -> (returns boolean)
    -get_is_verified(email) -> (returns boolean)
    -get_verification_token(email) -> (returns string)
    -get_verification_token_expiry(email) -> (returns datetime)
    -get_reset_code(email) -> (returns string)
    -get_reset_code_expiry(email) -> (returns datetime)

    -update_password(email, password_hash)
    -update_is_admin(email, state)
    -update_is_verified(email, state)
    -update_verification_token(email, token, expiry)
    -update_reset_code(email, code, expiry)

    -delete_user(email)


    Argument types:
        email: string
        password_hash: string
        state: boolean
        token/code: string
        expiry: datetime