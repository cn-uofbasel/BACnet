package com.example.p2pgeocaching.ownbacnet

/**
 * This class represents the BaCNet-Feed.
 * [entries] contains all the entries of the feed, and [publisher] is the person that the feed
 * belongs to.
 */
open class Feed(val entries: List<Entry>, val publisher: Publisher) {

    /**
     * This function gives back the ID of the last entry.
     */
    fun getLastID(): Int {
        return if (entries.isEmpty()) {
            -1
        } else {
            entries.last().id
        }
    }

    /**
     * This function gives back the ID for a new entry.
     */
    fun getNextID(): Int {
        return this.getLastID() + 1
    }

    /**
     * This function returns the signature of the last entry in [entries].
     */
    fun getLastSignature(): String {
        return if (entries.isEmpty()) {
            ""
        } else {
            entries.last().signature
        }
    }
}