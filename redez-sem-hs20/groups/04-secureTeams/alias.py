""" Alias
This script allows the direct mapping of an alias and an id of a user.
Therefore a user can be addressed by its alias by other users and not only by the id.

This file contains the three following functions:
    * add_alias - assigns alias to id
    * get_alias_by_id - returns alias of a user
    * get_id_by_alias - returns id of a user
"""

from json import dump, load


def add_alias(alias: str, id: str) -> bool:
    """
    This function assigns a desired alias of the user to its id.

    Parameters
    ----------
    alias : str
        The alias name of the user
    id : str
        The id of the user
    Returns
    -------
    bool
        True if new alias has been added, otherwise false
    """
    # load all existing alias
    try:
        with open("alias.txt", "r") as f:
            a = load(f)
    except:
        a = []
    # alias already in use -> not possible to choose this alias
    if a.__contains__(alias):
        print("alias already in use, choose something other than", alias)
        return False
    # alias not in use -> try to assign this to id by adding it in file containing all alias
    try:
        with open("alias.txt", "w") as f:
            a.append([alias, id])
            dump(a, f)
            return True
    except:
        return False


def get_alias_by_id(id: str) -> str:
    """
    This function returns the alias of the user by its id.

    Parameters
    ----------
    id : str
        The id of the user
    Returns
    -------
    str
        The alias of the user
    """
    try:
        with open("alias.txt", "r") as f:
            # go through all entries
            for a in load(f):
                # if id matches an entry return matching alias
                if a[1] == id:
                    return a[0]
            return None
    except:
        return id[:6]


def get_id_by_alias(alias: str) -> str:
    """
    This function returns the id of the user by its alias.

    Parameters
    ----------
    alias : str
        The alias of the user
    Returns
    -------
    str
        The id of the user
    """
    try:
        with open("alias.txt", "r") as f:
            # go through all entries
            for a in load(f):
                # if alias matches an entry return matching id
                if a[0] == alias:
                    return a[1]
            return None
    except:
        return None
