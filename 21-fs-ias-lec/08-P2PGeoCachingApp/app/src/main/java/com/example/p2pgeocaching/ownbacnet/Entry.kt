package com.example.p2pgeocaching.ownbacnet

/**
 * This class represents an entry in a [Feed].
 * It has a [timestamp], which represents when it was created (unix time).
 * The [id] is the number it has in the feed.
 * * [signedPreviousSignature] is the signature of the previous signature.
 * The [content] is specific to what kind of Entry it is: CacheEntry, HoFEntry, LogEntry.
 * The type of entry is saved in [type] as plaintext string (see above).
 * [signature] is the signature of the entry: all fields appended, then hashed
 * and encrypted using the publisher's private key.
 */
@kotlinx.serialization.Serializable
open class Entry(
    val timestamp: Long,
    val id: Int,
    val signedPreviousSignature: String,
    val content: String,
    val type: String,
    val signature: String
) {
}