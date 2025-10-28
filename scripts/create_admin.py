#!/usr/bin/env python3
"""Create or update an admin user for AUBEVENTS local DB.

Run from project root: python scripts/create_admin.py
"""
import os
import sys
import bcrypt

# Ensure project root is on sys.path so local packages like `database` can be imported
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(THIS_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from database.database import (
    get_user, create_user, update_password, update_is_verified, update_is_admin
)

EMAIL = "faa86@aub.edu.lb"
PASSWORD = "Fafe&6666"

def main():
    user = get_user(EMAIL)
    pw_hash = bcrypt.hashpw(PASSWORD.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    if user:
        print(f"User {EMAIL} exists - updating password, verified, and admin flag.")
        update_password(EMAIL, pw_hash)
        update_is_verified(EMAIL, True)
        update_is_admin(EMAIL, True)
    else:
        print(f"Creating user {EMAIL} and setting verified/admin flags.")
        create_user(EMAIL, pw_hash)
        update_is_verified(EMAIL, True)
        update_is_admin(EMAIL, True)
    print("Done.")

if __name__ == '__main__':
    main()
