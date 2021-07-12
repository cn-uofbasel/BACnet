import os
import random
import BackEnd.actions as act
import logging

if __name__ == '__main__':
    # some logging
    act.setup_logging(logging.INFO)

    # any random secret
    mock_secret = os.urandom(18)

    # split it into shares with name, desired number of packages and recovery threshold
    (packages, sinfo) = act.split_secret_into_share_packages("MySecret", mock_secret, 3, threshold=2)

    # now well save the shares in a buffer until they are ready to be sent
    act.push_packages_into_share_buffer(packages, sinfo)

    # we can check on a secret any time, if its ready to be recovered
    if act.secret_can_be_recovered("MySecret"):
        print("Yes we can!")

    # lets simulate getting shares back from a friend
    # first let's delete the buffer,
    # ToDo this shouldn't be done like this, only with the send_shares function in actions
    del act.shareBuffer["MySecret"]

    if not act.secret_can_be_recovered("MySecret"):
        print("No we can't!")

    random.shuffle(packages)

    returned_packages = packages[:-1]

    # so lets put them in the share buffer one by one
    act.push_package_into_share_buffer(returned_packages[0])
    act.push_package_into_share_buffer(returned_packages[1])

    if act.secret_can_be_recovered("MySecret"):
        print("Yes we can!")

    # and recover it
    (packages, sinfo) = act.get_packages_from_share_buffer("MySecret")
    recovered_secret = act.recover_secret_from_packages(packages, sinfo)

    # lets see if they match:

    print(mock_secret)
    print(recovered_secret)

    # lets also save the state

    act.save_state()
