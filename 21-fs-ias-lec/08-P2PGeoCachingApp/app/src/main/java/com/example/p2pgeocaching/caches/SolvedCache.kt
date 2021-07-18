package com.example.p2pgeocaching.caches

/**
 *  This class represents a complete [Cache], which has been solved.
 *  It does not initialize the [plainTextHOF] again.
 */
class SolvedCache(
    title: String,
    desc: String,
    creator: String,
    id: Int,
    pubKey: String,
    prvKey: String,
    hallOfFame: MutableSet<String>,
    plainTextHOF: String
) : Cache(title, desc, creator, id, pubKey, prvKey, hallOfFame, plainTextHOF)