from db.crud import create_tables, add_user, get_all_users

create_tables()

sample_user = add_user(username="nada_zaki", email="nada.g.zaki.25@gmail.com")
print("Inserted user:", sample_user)

users = get_all_users()
print("All users in database:")
for user in users:
    print(user)
