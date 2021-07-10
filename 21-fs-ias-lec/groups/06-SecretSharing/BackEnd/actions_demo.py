
from os import urandom
import BackEnd.actions as act


if __name__ == '__main__':

    mock_secret = urandom(16)
    packages, sinfo = act.split_secret_into_share_packages("MySecret", mock_secret, 5, "", threshold=2)
    print(sinfo)
    mock_secret_reconstructed = act.recover_secret_from_packages(packages, "", sinfo)

    print("original secret")
    print(mock_secret)
    print("secret reconstructed")
    print(mock_secret_reconstructed)