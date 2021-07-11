import sys
import os
import BackEnd.actions as act


if __name__ == '__main__':
    # ~~~~~~~ Logging ~~~~~~~
    import logging.config
    format = '%(msecs)dms %(name)s %(levelname)s line %(lineno)d %(funcName)s %(message)s'
    formatter = logging.Formatter(format)
    logging.basicConfig(
        filename=os.path.join(act.settings.DATA_DIR, "backend.log"),
        format=format,
        filemode="w",
        datefmt='%H:%M:%S',
        level=logging.DEBUG
    )
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(formatter)
    logging.getLogger().addHandler(sh)



    mock_secret = os.urandom(18)
    packages, sinfo = act.split_secret_into_share_packages("MySecret", mock_secret, 3, threshold=2)

    packages = packages[0:-1]

    mock_secret_reconstructed = act.recover_secret_from_packages(packages, sinfo)