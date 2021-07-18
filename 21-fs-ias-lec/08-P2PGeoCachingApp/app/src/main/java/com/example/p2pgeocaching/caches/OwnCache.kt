package com.example.p2pgeocaching.caches

import android.content.Context
import com.example.p2pgeocaching.RSA.RSA
import com.example.p2pgeocaching.inputValidator.InputValidator.Companion.checkUserNameForIllegalCharacters
import java.util.Objects.hash

/**
 * [OwnCache] is the [Cache] subclass used when creating one's own [Cache].
 * For details on the inputs, see [Cache].
 */
class OwnCache(
    title: String,
    desc: String,
    creator: String,
    id: Int,
    pubKey: String?,
    prvKey: String?,
    hallOfFame: MutableSet<String>,
    plainTextHOF: String
) : Cache(title, desc, creator, id, pubKey, prvKey, hallOfFame, plainTextHOF) {


    /**
     * Here, with the inputs provided, we set the rest of the fields.
     * Used to generate new caches.
     */
    constructor(title: String, desc: String, creator: String, context: Context) : this(
        title,
        desc,
        creator,
        -1,
        null,
        null,
        mutableSetOf<String>(),
        ""
    ) {
        // This checks if the arguments contain an illegal character, which it should not
        checkUserNameForIllegalCharacters(creator)

        // Here we fabricate the string we want to hash by concatenating [title], ';' and [desc]
        val stringToHash = "$title;$desc"

        // The hash is saved to [id], which serves as the unique identifier of the cache
        id = hash(stringToHash)

        // The key pair is created and saved to [pubKey] and [prvKey]
        val keyPair: String = RSA.generateKeys()
        pubKey = RSA.getPublicKey(keyPair)
        prvKey = RSA.getPrivateKey(keyPair)

        // Here we encrypt [creator] and add it to [hallOfFame] and update [plainTextHOF]
        val encryptedCreator: String = RSA.encode(creator, prvKey)

        // This is where the updates and inserts happen
        addPersonToHOF(encryptedCreator)
    }
}