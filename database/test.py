from database import (
    create_user, get_user, get_password, get_is_verified, get_verification_token,
    get_verification_token_expiry, get_reset_code, get_reset_code_expiry,
    update_password, update_is_verified, update_verification_token,
    update_reset_code, delete_user, update_is_admin
)
from database import (
    create_event, get_title, get_description, get_date, get_location,
    get_capacity, get_available_seats, get_organizers, get_speakers, update_title, update_description, update_date, update_location,
    update_capacity, update_available_seats, delete_event, update_organizers, update_speakers
)

from database import(
    register_user_to_event, unregister_user_from_event, get_user_events, get_event_users, print_all_events
)

from datetime import datetime, timedelta

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

#user = create_user("mkk40@mail.aub.edu", "randomPassword123")

#update_is_admin("mkk40@mail.aub.edu", True)
#update_password("mkk40@mail.aub.edu", "newpassword")
#update_is_verified("mkk40@mail.aub.edu", True)
#update_verification_token("mkk40@mail.aub.edu", "newtoken", datetime.now() + timedelta(seconds=3600))
#update_reset_code("mkk40@mail.aub.edu", "newcode", datetime.now() + timedelta(seconds=3600))

#print("Password:", get_password("mkk40@mail.aub.edu"))
#print("Is Verified:", get_is_verified("mkk40@mail.aub.edu"))
#print("Verification Token:", get_verification_token("mkk40@mail.aub.edu"))
#print("Verification Token Expiry:", get_verification_token_expiry("mkk40@mail.aub.edu"))
#print("Reset Code:", get_reset_code("mkk40@mail.aub.edu"))
#print("Reset Code Expiry:", get_reset_code_expiry("mkk40@mail.aub.edu"))

#delete_user("test2@example.com")

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

#event = create_event(title="Sample Event", description="This is a sample event.", date=datetime(2025, 9, 28, 18, 59), location="AUB", capacity=100, available_seats=100, speakers=["Dr X", "Prof Y", "Prof Z"], organizers=["Dept A", "Dep B"])
#event = create_event(title="Sample Event 2", description="This is a sample event.", date=datetime(2025, 9, 28, 18, 59), location="AUB", capacity=150, available_seats=150, speakers=["Dr K", "Prof L", "Prof M"], organizers=["Dept C", "Dep D"])

#update_title(1, "Updated Event Title")
#update_description(1, "Updated description for the event.")
#update_date(1, datetime(2023, 12, 31, 20, 0))
#update_location(1, "New Location")
#update_capacity(1, 150)
#update_available_seats(1, 150)
#update_organizers(1, ["Organizer 1", "Organizer 2"])
#update_speakers(1, ["Speaker 1", "Speaker 2"])

print("Title:", get_title(1))
print("Description:", get_description(1))
print("Date:", get_date(1))
print("Location:", get_location(1))
print("Capacity:", get_capacity(1))#print("Available Seats:", get_available_seats(1))
print("Organizers:", get_organizers(1))
print("Speakers:", get_speakers(1))

#delete_event(1)

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

#register_user_to_event("mkk40@mail.aub.edu", 1)
#register_user_to_event("mkk40@mail.aub.edu", 2)
#register_user_to_event("mkk41@mail.aub.edu", 2)
#register_user_to_event("mkk42@mail.aub.edu", 1)

#unregister_user_from_event("mkk40@mail.aub.edu", 1)

#print("Events registered: ", get_user_events("mkk40@mail.aub.edu"))
#print("Users registered: ", get_event_users(1))

#print_all_events()