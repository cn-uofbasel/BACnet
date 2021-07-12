package com.example.p2pgeocaching.ownbacnet

import com.example.p2pgeocaching.caches.OwnCache
import com.example.p2pgeocaching.constants.Constants.Companion.CACHE_ENTRY
import com.example.p2pgeocaching.data.CacheDataParser
import com.example.p2pgeocaching.data.Serializer

/**
 * This subclass of [Entry] represents a Cache in the BaCNet-Feed.
 * Its content is a serialized Cache object.
 * The Caches are saved as DataCaches of Type transfer, meaning they do not contain the privateKey.
 */
class CacheEntry(
    timestamp: Long,
    id: Int,
    signedPreviousSignature: String,
    content: String,
    signature: String
) : Entry(timestamp, id, signedPreviousSignature, content, CACHE_ENTRY, signature) {

    companion object {

        /**
         * This method lets us create a CacheEntry with an [ownCache] object.
         * It also needs a [ownFeed] to determine the current position in the feed.
         */
        fun newCacheEntry(ownCache: OwnCache, ownFeed: OwnFeed): CacheEntry {
            val timestamp = System.currentTimeMillis()
            val id = ownFeed.getNextID()
            val previousSignature = ownFeed.getLastSignature()
            val signedPreviousSignature = ownFeed.getOwnPublisher().sign(previousSignature)

            // It is important we concatenate the type as well, to get the correct signature
            val type = CACHE_ENTRY

            // Now we strip the ownCache of its privateKey and save it as a transferCache
            // TODO: replace double function call with simple function in CacheDataParser:
            //  ownToTransfer()
            val dataCache = CacheDataParser.cacheToTransfer(ownCache)
            val transferCache = CacheDataParser.dataToCache(dataCache)
            val content = Serializer.serializeCacheToString(transferCache)

            val concatenatedString: String =
                timestamp.toString() + id.toString() + signedPreviousSignature + type + content
            val hashString = concatenatedString.hashCode().toString()
            val signature = ownFeed.getOwnPublisher().sign(hashString)
            return CacheEntry(timestamp, id, signedPreviousSignature, content, signature)
        }
    }
}
