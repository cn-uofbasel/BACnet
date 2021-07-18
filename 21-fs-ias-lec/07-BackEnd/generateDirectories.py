import sys

# add the lib to the module folder
sys.path.append("lib")

import os
import crypto
import feed
import time
import random


def generate(name):  # generates a folder, feed, and key pair for a given person

    # creates a folder 'data' if none exists
    if not os.path.isdir("data"):
        os.mkdir("data")

    # creates a new folder in 'data' with the given name if none exists
    if not os.path.isdir("data/" + name):
        os.mkdir("data/" + name)

    # is used for the encryption
    digestmod = "sha256"
    h, signer = None, None

    # generates a Key if no .key file exists
    if not os.path.isfile("data/" + name + "/" + name + "-secret.key"):
        # for testing: print("Create " + name + "'s key pair at data/" + name + "/" + name + "-secret.key")
        h = crypto.HMAC(digestmod)
        h.create()
        # create a .key file and write the generated key in it
        with open("data/" + name + "/" + name + "-secret.key", "w") as f:
            f.write('{\n  ' + (',\n '.join(h.as_string().split(','))[1:-1]) + '\n}')
            signer = crypto.HMAC(digestmod, h.get_private_key())

    # for testing: print("Read " + name + "'s secret key.")

    # creates the key pair (key 'feed_id' as public key)
    with open("data/" + name + "/" + name + "-secret.key", 'r') as f:
        key = eval(f.read())
        h = crypto.HMAC(digestmod, key["private"], key["feed_id"])
        # compatibility depending on operating systems
        if sys.platform.startswith("linux"):
            signer = crypto.HMAC(digestmod, bytes.fromhex(h.get_private_key()))
        else:
            signer = crypto.HMAC(digestmod, h.get_private_key())

    # for testing: print("Create or load " + name + "'s feed at data/" + name + "/" + name + "-feed.pcap")

    # generate Feed as .pcap file in folder 'Data/Name' with created attributes
    myFeed = feed.FEED(fname="data/" + name + "/" + name + "-feed.pcap", fid=h.get_feed_id(),
                       signer=signer, create_if_notexisting=True, digestmod=digestmod)

    return myFeed, key["feed_id"]


def generate_directories():     # generates directories and connections between the persons
    yasmin, yasmins_id = generate("yasmin")
    esther, esthers_id = generate("esther")
    vera, veras_id = generate("vera")
    pascal, pascals_id = generate("pascal")
    philipp, philipps_id = generate("philipp")
    sebastian, sebastians_id = generate("sebastian")
    aline, alines_id = generate("aline")
    ben, bens_id = generate("ben")
    caroline, carolines_id = generate("caroline")
    david, davids_id = generate("david")
    eveline, evelines_id = generate("eveline")
    fitzgerald, fitzgeralds_id = generate("fitzgerald")
    georgia, georgias_id = generate("georgia")
    henry, henrys_id = generate("henry")
    isabelle, isabelles_id = generate("isabelle")
    julius, julius_id = generate("julius")
    veri, veris_id = generate("veri")

    yasmin.write(["bacnet/following", time.time(), veras_id])  # follow Vera
    yasmin.write(["bacnet/following", time.time(), esthers_id])  # follow Esther
    yasmin.write(["bacnet/following", time.time(), julius_id])  # follow Julius

    vera.write(["bacnet/following", time.time(), esthers_id])  # follow Esther
    vera.write(["bacnet/following", time.time(), yasmins_id])  # follow Yasmin
    vera.write(["bacnet/following", time.time(), sebastians_id])  # follow Sebastian
    vera.write(["bacnet/following", time.time(), pascals_id])  # follow Pascal
    vera.write(["bacnet/following", time.time(), philipps_id])  # follow Phillip

    vera.write(["bacnet/following", time.time(), julius_id])  # follow julius

    esther.write(["bacnet/following", time.time(), yasmins_id])  # follow Yasmin
    esther.write(["bacnet/following", time.time(), veras_id])  # follow Vera
    esther.write(["bacnet/following", time.time(), davids_id])  # follow David

    pascal.write(["bacnet/following", time.time(), sebastians_id])  # follow Sebastian
    pascal.write(["bacnet/following", time.time(), philipps_id])  # follow Phillip

    philipp.write(["bacnet/following", time.time(), sebastians_id])  # follow Sebastian
    philipp.write(["bacnet/following", time.time(), pascals_id])  # follow Pascal

    sebastian.write(["bacnet/following", time.time(), philipps_id])  # follow Phillip
    sebastian.write(["bacnet/following", time.time(), pascals_id])  # follow Pascal

    aline.write(["bacnet/following", time.time(), yasmins_id])  # follow Yasmin
    aline.write(["bacnet/following", time.time(), georgias_id])  # follow Georgia
    aline.write(["bacnet/following", time.time(), henrys_id])  # follow Henry

    julius.write(["bacnet/following", time.time(), alines_id])  # follow Aline
    julius.write(["bacnet/following", time.time(), bens_id])  # follow Ben

    ben.write(["bacnet/following", time.time(), alines_id])  # follow Aline
    ben.write(["bacnet/following", time.time(), veras_id])  # follow Vera
    ben.write(["bacnet/following", time.time(), esthers_id])  # follow Esther
    ben.write(["bacnet/following", time.time(), yasmins_id])  # follow Yasmin


def create_random_names(size):      # creates a given number of random composed names (firs & last names)
    firstnames = ["Mia", "Lara", "Emma", "Laura", "Anna", "Sara", "Lea", "Elena", "Lina", "Alina", "Julia", "Emilia",
                  "Lena", "Nina", "Sophia", "Lia", "Elin", "Sophie", "Sofia", "Nora", "Jana", "Mila", "Elina", "Melina",
                  "Livia", "Luana", "Giulia", "Emily", "Chiara", "Valentina", "Noemi", "Lorena", "Selina", "Alessia",
                  "Hanna", "Ronja", "Lynn", "Lisa", "Ella", "Amelie", "Luisa", "Mara", "Sarah", "Elisa", "Jael",
                  "Fiona",
                  "Olivia", "Amelia", "Zoe", "Noah", "Liam", "Luca", "Gabriel", "Leon", "David", "Matteo", "Elias",
                  "Louis",
                  "Levin", "Samuel", "Julian", "Tim", "Jonas", "Robin", "Diego", "Nico", "Leo", "Jan", "Ben", "Leandro",
                  "Dario", "Lukas", "Rafael", "Elia", "Nino", "Simon", "Lenny", "Gian", "Benjamin", "Alessio", "Fabio",
                  "Finn", "Loris", "Aaron", "Daniel", "Lucas", "Livio", "Andrin", "Nevio", "Leonardo", "Alexander",
                  "Nathan", "Lian", "Mattia", "Enzo", "Luis", "Joel", "Raphael"]

    lastnames = ["Amsler", "Amstutz", "Andrist", "Andros", "Ankeney", "Ankeny", "Ankney", "Anliker", "Annen", "Arn",
                 "Arner", "Arnet", "Bally", "Balthis", "Bandi", "Batliner", "Batz", "Batz", "Beachy", "Benziger",
                 "Berlinger", "Berna", "Berna", "Berry", "Bertschy", "Bichsel", "Bieri", "Bryner", "Buchli",
                 "Bullinger",
                 "Buol", "Burckhalter", "Burgi", "Burgin", "Burgy", "Buri", "Burk", "Burkhalter", "Burri", "Burry",
                 "Buser",
                 "Bussinger", "Henggeler", "Herda", "Hilfiker", "Hilty", "Hirschi", "Hirschy", "Hochstedler",
                 "Hochstetler",
                 "Hoesly", "Hoffstetter", "Holdener", "Hopler", "Hostetler", "Hostetter", "Hum", "Hunkler", "Hunziker",
                 "Hurliman", "Inabinett", "Inabnit", "Ingold", "Isch", "Iseli", "Isely", "Jacky", "Jaecks", "Jenni",
                 "Jenny", "Jud", "Kadis", "Kamer", "Schudel", "Schurter", "Sprunger", "Stager", "Staheli", "Sterchi",
                 "Stoecklin", "Struchen", "Stuessy", "Surbeck", "Tanner", "Theiler", "Thoeny", "Torian", "Treichel",
                 "Treichler", "Tresch", "Tritten", "Trollinger", "Troxler", "Truby", "Trumpy", "Tschappat", "Tschoepe",
                 "Tschopp", "Ummel", "Vetsch", "Walliser", "Wehrli", "Wehrly", "Weltner", "Welty", "Weyker", "Wiget",
                 "Willan", "Winzenried", "Wirthlin", "Wurgler", "Wyss"]
    names = []
    while len(names) < size:
        rf = firstnames[random.randint(0, len(firstnames) - 1)]
        rl = lastnames[random.randint(0, len(lastnames) - 1)]

        if rf + "_" + rl not in names:
            names.append(rf + "_" + rl)

    return names


def create_directories_for_random_names(size, max_connections):   # creates the directories for the random created names
    names = create_random_names(size)
    persons = []

    for name in names:
        f, id = generate(name)
        persons.append([f, id])

    for person in persons:
        for i in range(random.randint(1, max_connections)):
            tmp = random.randint(0, len(persons) - 1)
            followPerson = persons[tmp]
            person[0].write((["bacnet/following", time.time(), followPerson[1]]))
