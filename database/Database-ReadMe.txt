1-  To access the database, you need to have these downloaded:

    -python:
        https://www.python.org/downloads/
        (in the install process, make sure you tick "pip", and "Add python to environment variables")
        To make sure it was successful, go to terminal and run these commands:
            python --version
            pip --version

    -SQLModel and PyMySQL:
        Go to terminal and run these commands:
            pip install sqlmodel
            pip install PyMySQL


2-  To keep the database safe, the URL is saved in a separate file
    named DB_Password.py, which will be sent privately. What you need
    to do is place this file in the same folder as the database.py file. 
    Do NOT push this file to github.


3-  Importing database functions:

    To create, update, delete or read any data from the database, you need to import them to your file using:

        from database.database import (
         # Users
            create_user, get_user, get_password, get_is_admin, get_is_verified, get_verification_token,
            get_verification_token_expiry, get_reset_code, get_reset_code_expiry,
            update_password, update_is_admin, update_is_verified, update_verification_token,
            update_reset_code, delete_user,

        # Events
            create_event, get_title, get_description, get_organizer, get_date, get_location, get_capacity,
            get_available_seats, get_speakers, update_title, update_description, update_organizer,
            update_date, update_location, update_capacity, update_available_seats, update_speakers,
            delete_event,

        # User-Event linking
            register_user_to_event, unregister_user_from_event, get_user_events, get_event_users
        )

        Note: You can also import print_all_events() function that will print all events id/title in the table. Used for testing purposes.


4-  Using database functions:

    -Users:

        create_user(email, password_hash)

        get_user(email) → returns User object
        get_password(email) → returns string
        get_is_admin(email) → returns boolean
        get_is_verified(email) → returns boolean
        get_verification_token(email) → returns string
        get_verification_token_expiry(email) → returns datetime
        get_reset_code(email) → returns string
        get_reset_code_expiry(email) → returns datetime

        update_password(email, password_hash)
        update_is_admin(email, state)
        update_is_verified(email, state)
        update_verification_token(email, token, expiry)
        update_reset_code(email, code, expiry)

        delete_user(email)

        Argument types:
        email - password_hash - token - code: string
        state: boolean
        expiry: datetime


    -Events:

        create_event(title, description, date, location, capacity, available_seats) → returns Event object

        get_title(event_id) → returns string
        get_description(event_id) → returns string
        get_organizer(event_id) → returns string
        get_date(event_id) → returns datetime
        get_location(event_id) → returns string
        get_capacity(event_id) → returns int
        get_available_seats(event_id) → returns int

        update_title(event_id, title)
        update_description(event_id, description)
        update_organizer(event_id, email)
        update_date(event_id, date)
        update_location(event_id, location)
        update_capacity(event_id, capacity)
        update_speakers(event_id, speakers)
        update_available_seats(event_id, seats)

        delete_event(event_id)

        Argument types:
        title - description - location - email - speakers: string
        date: datetime
        event_id - capacity - available_seats: int


    -User–Event linking:

        register_user_to_event(user_email, event_id)
        unregister_user_from_event(user_email, event_id)
        get_user_events(user_email) → returns list of event IDs the user is registered for
        get_event_users(event_id) → returns list of user emails registered to the event

        Argument types:
        user_email: string
        event_id: int
