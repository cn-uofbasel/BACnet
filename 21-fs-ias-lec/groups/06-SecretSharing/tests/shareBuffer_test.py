"""Manual tests for file encryption."""
from BackEnd import actions as act
from os import urandom

if __name__ == '__main__':
    secret_one = urandom(16)
    packages = act.split_secret_into_share_packages("SecretOne", secret_one, 10, 10, [])
    act.push_packages_into_share_buffer("SecretOne", packages)
    act.save_state()
    packages = act.get_packages_from_share_buffer("SecretOne")
    secret_rec = act.recover_secret_from_packages("SecretOne", packages)

    print(secret_one)
    print(secret_rec)