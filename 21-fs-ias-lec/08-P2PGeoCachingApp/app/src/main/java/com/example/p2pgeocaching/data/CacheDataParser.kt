package com.example.p2pgeocaching.data

import com.example.p2pgeocaching.caches.Cache
import com.example.p2pgeocaching.caches.OwnCache
import com.example.p2pgeocaching.caches.SolvedCache
import com.example.p2pgeocaching.caches.UnsolvedCache
import com.example.p2pgeocaching.constants.Constants.Companion.OWN_CACHE
import com.example.p2pgeocaching.constants.Constants.Companion.SOLVED_CACHE
import com.example.p2pgeocaching.constants.Constants.Companion.TRANSFER_CACHE
import com.example.p2pgeocaching.constants.Constants.Companion.UNSOLVED_CACHE
import com.example.p2pgeocaching.p2pexceptions.CacheDataTypeNotDefinedException
import com.example.p2pgeocaching.p2pexceptions.IllegalCacheTypeException
import com.example.p2pgeocaching.p2pexceptions.ParametersAreNullException

/**
 * This class is used to parse from data objects to real objects and back.
 */
class CacheDataParser {

    companion object {

        /**
         * This is used to create a [Cache] from a [CacheData] object.
         * [data] is the object to be read from.
         */
        fun dataToCache(data: CacheData): Cache {
            return when (data.type) {
                OWN_CACHE -> dataToOwnCache(data)
                SOLVED_CACHE -> dataToSolvedCache(data)
                UNSOLVED_CACHE -> dataToUnsolvedCache(data)
                TRANSFER_CACHE -> dataTransferToUnsolvedCache(data)
                else -> throw CacheDataTypeNotDefinedException()
            }
        }


        /**
         * Simple function that makes a [OwnCache] from a [CacheData] object [data].
         */
        private fun dataToOwnCache(data: CacheData): OwnCache {
            if (data.pubKey != null && data.prvKey != null) {
                return OwnCache(
                    data.title,
                    data.desc,
                    data.creator,
                    data.id,
                    data.pubKey!!,
                    data.prvKey!!,
                    data.hallOfFame,
                    data.plainTextHOF
                )
            } else {
                throw ParametersAreNullException()
            }
        }


        /**
         * Simple function that makes a [SolvedCache] from a [CacheData] object [data].
         */
        private fun dataToSolvedCache(data: CacheData): SolvedCache {
            if (data.pubKey != null && data.prvKey != null) {
                return SolvedCache(
                    data.title,
                    data.desc,
                    data.creator,
                    data.id,
                    data.pubKey!!,
                    data.prvKey!!,
                    data.hallOfFame,
                    data.plainTextHOF
                )
            } else {
                throw ParametersAreNullException()
            }
        }


        /**
         * Simple function that makes an [UnsolvedCache] from a [CacheData] object [data].
         */
        private fun dataToUnsolvedCache(data: CacheData): UnsolvedCache {
            if (data.pubKey != null) {
                return UnsolvedCache(
                    data.title,
                    data.desc,
                    data.creator,
                    data.id,
                    data.pubKey!!,
                    data.hallOfFame,
                    data.plainTextHOF,
                )
            } else {
                throw ParametersAreNullException()
            }
        }


        /**
         * Simple function that makes an [UnsolvedCache] from a [CacheData] object [data] when used
         * to transfer data.
         */
        private fun dataTransferToUnsolvedCache(data: CacheData): UnsolvedCache {
            if (data.pubKey != null) {
                return UnsolvedCache(
                    data.title,
                    data.desc,
                    data.creator,
                    data.id,
                    data.pubKey!!,
                    data.hallOfFame
                )
            } else {
                throw ParametersAreNullException()
            }
        }


        /**
         * This function takes a [Cache] [cache] and transforms it into a [CacheData] object.
         */
        fun cacheToData(cache: Cache): CacheData {
            return when (cache) {
                is OwnCache -> CacheData(
                    cache.title,
                    cache.desc,
                    cache.creator,
                    cache.id,
                    cache.pubKey!!,
                    cache.prvKey!!,
                    cache.hallOfFame,
                    cache.plainTextHOF,
                    OWN_CACHE
                )
                is UnsolvedCache -> CacheData(
                    cache.title,
                    cache.desc,
                    cache.creator,
                    cache.id,
                    cache.pubKey!!,
                    null,
                    cache.hallOfFame,
                    cache.plainTextHOF,
                    UNSOLVED_CACHE
                )
                is SolvedCache -> CacheData(
                    cache.title,
                    cache.desc,
                    cache.creator,
                    cache.id,
                    cache.pubKey!!,
                    cache.prvKey!!,
                    cache.hallOfFame,
                    cache.plainTextHOF,
                    SOLVED_CACHE
                )
                else -> throw IllegalCacheTypeException()
            }
        }


        /**
         * This function is used when creating [CacheData] objects to transfer caches from one device
         * to another. It is effectively equivalent to the object created when using cacheToData
         * with an [UnsolvedCache].
         */
        fun cacheToTransfer(cache: Cache): CacheData {
            return CacheData(
                cache.title,
                cache.desc,
                cache.creator,
                cache.id,
                cache.pubKey!!,
                null,
                cache.hallOfFame,
                TRANSFER_CACHE
            )
        }
    }
}