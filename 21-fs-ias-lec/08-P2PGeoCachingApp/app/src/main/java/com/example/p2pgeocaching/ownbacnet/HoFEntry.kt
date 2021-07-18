package com.example.p2pgeocaching.ownbacnet

import com.example.p2pgeocaching.RSA.RSA
import com.example.p2pgeocaching.caches.Cache
import com.example.p2pgeocaching.constants.Constants
import com.example.p2pgeocaching.constants.Constants.Companion.HOF_ENTRY
import com.example.p2pgeocaching.data.CacheDataParser
import com.example.p2pgeocaching.data.FeedDataParser
import com.example.p2pgeocaching.data.Serializer
import java.io.File

/**
 * This [Entry] subclass is created when the [Feed] owner solves a [Cache].
 * Its content represents the encrypted name of the solver.
 */
class HoFEntry(
    timestamp: Long,
    id: Int,
    signedPreviousSignature: String,
    content: String,
    signature: String
) : Entry(timestamp, id, signedPreviousSignature, content, HOF_ENTRY, signature) {

    companion object {

        /**
         * This method lets us create a HoFEntry with a [privateKey] and a [Cache] object
         * It also needs a [ownFeed] to determine the current position in the feed.
         */
        fun newHoFEntry(privateKey: String, cache: Cache, ownFeed: OwnFeed, context: File): HoFEntry {
            val timestamp = System.currentTimeMillis()
            val id = ownFeed.getNextID()
            val previousSignature = ownFeed.getLastSignature()
            val signedPreviousID = ownFeed.getOwnPublisher().sign(previousSignature)
            val content = RSA.encode(ownFeed.getOwnPublisher().name, privateKey)

            val fdp = FeedDataParser()
            val feedNamesFile = File(context, Constants.FEED_NAMES_FILE)
            val feedNameContent = feedNamesFile.readText()
            val feedNameList = feedNameContent.split("\n")
            var sign = ""
            var bool = false
            for (feedName in feedNameList) {
                val feedFile = File(context, feedName)
                val listOfEntries = fdp.feedToEntrylist(feedFile)
                for (entry in listOfEntries) {
                    if(entry.type.equals(Constants.CACHE_ENTRY)) {
                        val cacheEntry = Serializer.deserializeCacheFromString(entry.content)
                        if (cacheEntry.creator.equals(cache.creator) &&
                                cacheEntry.desc.equals(cache.desc) &&
                                cacheEntry.id.equals(cache.id) &&
                                cacheEntry.pubKey.equals(cache.pubKey)) {
                            sign = entry.signature
                            bool = true
                            break
                        }
                    }
                }
                if (bool) {
                    break
                }
            }
            val signature = sign
            return HoFEntry(timestamp, id, previousSignature, content, signature)
        }
    }
}