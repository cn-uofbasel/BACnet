package com.example.p2pgeocaching.caches

import com.example.p2pgeocaching.RSA.RSA
import com.example.p2pgeocaching.inputValidator.InputValidator
import com.example.p2pgeocaching.p2pexceptions.CreatorNotInHallOfFameException
import com.example.p2pgeocaching.p2pexceptions.ParametersAreNullException


/**
 * [UnsolvedCache] is the subclass of [Cache] which is used when the user receives a new [Cache]
 * from somebody else.
 * It does not contain a [pubKey] yet.
 * For further documentation, see [Cache].
 */
class UnsolvedCache(
    title: String,
    desc: String,
    creator: String,
    id: Int,
    pubKey: String,
    hallOfFame: MutableSet<String>,
    plainTextHOF: String
) : Cache(title, desc, creator, id, pubKey, null, hallOfFame, plainTextHOF) {


    /**
     * Called when entering new caches that have been transferred from another device.
     * Here we check if the entries are all legal and if the creator is contained in the
     * [hallOfFame]. Then the [hallOfFame] is decrypted and saved in [plainTextHOF].
     */
    constructor(
        title: String,
        desc: String,
        creator: String,
        id: Int,
        pubKey: String,
        hallOfFame: MutableSet<String>
    ) : this(title, desc, creator, id, pubKey, hallOfFame, "") {

        // This checks if the arguments contain an illegal character, which it should not
        InputValidator.checkUserNameForIllegalCharacters(creator)
        InputValidator.checkTextForIllegalCharacters(listOf(title, desc))

        // This checks if the creator is in the [hallOfFame] list
        checkCreatorInHOF()

        // Here we decrypt and save the [hallOfFame] to [plainTextHOF]
        updatePlainTextHOF()
    }


    /**
     * Simple function that checks if the [creator] is in the [hallOfFame].
     * If [creator] is not contained, throws CreatorNotInHallOfFameException.
     */
    private fun checkCreatorInHOF() {
        val stringHOF: String = hallToString()
        if (!stringHOF.contains(creator)) {
            throw CreatorNotInHallOfFameException()
        }
    }


    /**
     * This function takes the name of the [finder] and the [newPrvKey] that was found at the cache.
     * The key pair should already be checked!
     * With the [prvKey], it adds the [finder] to the [hallOfFame].
     * Throws keysDoNotMatchException and stringContainsIllegalCharacterException.
     */
    fun solveCache(finder: String, newPrvKey: String): SolvedCache {

        // Finder cannot contain any illegal characters, can throw exception
        InputValidator.checkUserNameForIllegalCharacters(finder)

        // Assert that all values are not null
        if (pubKey == null) {
            throw ParametersAreNullException()
        }

        // Create the [SolvedCache] object to return
        val solvedCache =
            SolvedCache(title, desc, creator, id, pubKey!!, newPrvKey, hallOfFame, plainTextHOF)

        // Adds the encrypted name to [hallOfFame], if it is null, creates a new one
        val encryptedFinder = RSA.encode(finder, newPrvKey)

        // Here it is inserted into the new solvedCache object
        solvedCache.addPersonToHOF(encryptedFinder)

        return solvedCache
    }
}