package com.example.p2pgeocaching.constants

/**
 * This class holds all the constants needed in the app.
 * This is so that if it changes in one class, it changes in all others that also
 * utilize it.
 */
class Constants {
    companion object {
        const val U_NAME_FILE = "userName"
        const val CACHE_LIST_FILE = "cacheList"
        const val PERSON_DATA = "personData"
        const val OWN_CACHE_LIST_FILE = "ownCacheListFile"
        const val SOLVED_CACHE_LIST_FILE = "solvedCacheListFile"
        const val PRIVATE_KEY = "private key"
        const val PUBLIC_KEY = "public key"
        const val ID = "id"
        const val USE_DUMMY_LIST = false
        const val DUMMY_LIST_FILE = "raw/dummyCacheList.json"
        const val OWN_CACHE = "OwnCache"
        const val UNSOLVED_CACHE = "UnsolvedCache"
        const val SOLVED_CACHE = "SolvedCache"
        const val TRANSFER_CACHE = "TransferCache"
        const val CACHE = "cache"
        const val HOF_ENTRY = "HoFEntry"
        const val CACHE_ENTRY = "CacheEntry"
        const val LOG_ENTRY = "LogEntry"
        const val FEEDS = "Feeds"
        const val FEED_NAMES_FILE = "feedNames"
        const val FEED_NAME = "FeedName"
        const val USE_DUMMY_FEED_NAME_LIST = false
        const val BUFFERSIZE = 500
    }
}