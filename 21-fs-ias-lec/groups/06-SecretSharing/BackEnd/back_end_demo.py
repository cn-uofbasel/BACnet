import os
import BackEnd.actions as act

if __name__ == '__main__':
    act.setup_logging()

    mock_secret = os.urandom(18)
    packages, sinfo = act.split_secret_into_share_packages("MySecret", mock_secret, 3, threshold=2)

    packages = packages[0:-1]

    mock_secret_reconstructed = act.recover_secret_from_packages(packages, sinfo)