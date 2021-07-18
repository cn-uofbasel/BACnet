package com.example.p2pgeocaching.caches

import com.example.p2pgeocaching.constants.Constants
import com.example.p2pgeocaching.data.FeedDataParser
import com.example.p2pgeocaching.data.Serializer
import com.example.p2pgeocaching.ownbacnet.Entry
import java.io.File
import android.util.Log
import com.example.p2pgeocaching.data.FeedData

/**
 * This class looks at the local Feeds and updates the CacheList accordingly.
 * It is called whenever there are changes to any Feed that have new CacheEntries or HoFEntries.
 * Looks at all Feeds and all their Entries, if there is a Cache that another person has a
 * HoFEntry for, he is entered into the HallOfFame of the respective Cache.
 * If the user has a HoFEntry of their own for a cache, the cache is considered solved.
 * Caches in OwnFeed are OwnCaches.
 */
class CacheListGenerator {

    companion object {
        const val TAG = "CacheListGenerator"
    }

    private lateinit var cacheListFile: File

    fun getCacheListFileContent (context: File) {
        Log.i(TAG, "Started CacheListGenerator")
        val userNameFile = File(context, Constants.U_NAME_FILE)
        val creatorString = userNameFile.readLines().toString()
        val creator = creatorString.substring(1, creatorString.length - 1)
        cacheListFile = File(context, Constants.CACHE_LIST_FILE)
        //val filename = "personData"
        var file = File(context, Constants.PERSON_DATA)
        val content = file.readText()
        val keys = content.split(" ")
        val pubkey = keys[0].split("_")
        val salt = pubkey[1].takeLast(4)
        val feedname = creator.plus("#").plus(salt)

        val feedFile = File(context, feedname)
        val fdp = FeedDataParser()
        val list = fdp.feedToEntrylist(feedFile)

        val feedNamesFile = File(context, Constants.FEED_NAMES_FILE)
        var cacheList = CacheList(mutableListOf())

        Log.i(TAG, "Searching for Entries in OwnFeed")
        for (item in list) {
            if (item.type.equals(Constants.CACHE_ENTRY)) {
                Log.i(TAG, "Got Cache Entry")
                var cache1 = Serializer.deserializeCacheFromString(item.content)
                var cache = OwnCache(
                    cache1.title,
                    cache1.desc,
                    cache1.creator,
                    cache1.id,
                    cache1.pubKey,
                    cache1.prvKey,
                    cache1.hallOfFame,
                    cache1.plainTextHOF
                )
                Log.i(TAG, "Name of Cache Entry = "+cache.title)
                val ownCacheListFile = File(context, Constants.OWN_CACHE_LIST_FILE)
                val ownCacheContent = ownCacheListFile.readText()
                Log.i(TAG, "OwnCacheListFileContent = "+ownCacheContent)
                val listOfTuples = ownCacheContent.split("\n")
                for (tuple in listOfTuples) {
                    Log.i(TAG, "Tuple = "+tuple)
                    val tupleElem = tuple.split(":")
                    val sign = tupleElem[0]
                    val prvKey = tupleElem[1]
                    Log.i(TAG, "Signatur = "+sign)
                    Log.i(TAG, "PrvKey = "+prvKey)
                    if (sign.equals(item.signature)) {
                        Log.i(TAG, "Got correct private key")
                        cache.prvKey = prvKey.toString()
                        break
                    }
                }
                Log.i(TAG, "Checking subscribed Feeds")
                if (feedNamesFile.length() != 0L) {
                    Log.i(TAG, "I did subscribe Feeds")
                    val feedNameList = feedNamesFile.readText().split("\n")
                    for (feedName in feedNameList) {
                        Log.i(TAG, "Lookin at feed = "+feedName)
                        val feedFile = File(context, feedName)
                        val listOfEntries = fdp.feedToEntrylist(feedFile)
                        Log.i(TAG, "Feeds size of list = "+listOfEntries.size)
                        for (entry in listOfEntries) {
                            Log.i(TAG, "Entry type = "+entry.type)
                            if (entry.type.equals(Constants.HOF_ENTRY) && entry.signature.equals(
                                    item.signature
                                )
                            ) {
                                Log.i(TAG, "Added person to HoF = "+entry.content)
                                cache.addPersonToHOF(entry.content)
                            }
                        }
                    }
                }
                cacheList.add(cache)
            }
        }
        if (feedNamesFile.length() != 0L) {
            val feedNameList = feedNamesFile.readText().split("\n")
            for (feedName in feedNameList) {
                val feedFile = File(context, feedName)
                val listOfEntries = fdp.feedToEntrylist(feedFile)
                for (item in listOfEntries) {
                    if (item.type.equals(Constants.CACHE_ENTRY)) {
                        var cache1 = Serializer.deserializeCacheFromString(item.content)
                        for (feed in feedNameList) {
                            val file = File(context, feed)
                            val entries = fdp.feedToEntrylist(file)
                            for (entry in entries) {
                                if (entry.type.equals(Constants.HOF_ENTRY) && entry.signature.equals(item.signature)) {
                                    cache1.addPersonToHOF(entry.content)
                                }
                            }
                        }
                        var bool = false
                        for (entry in list) {
                            if (entry.type.equals(Constants.HOF_ENTRY) && entry.signature.equals(item.signature)) {
                                cache1.addPersonToHOF(entry.content)
                                val solvedCacheListFile = File(context, Constants.SOLVED_CACHE_LIST_FILE)
                                val solvedCacheContent = solvedCacheListFile.readText()
                                Log.i(TAG, "SolvedCacheListFileContent = "+solvedCacheContent)
                                val listOfTuples = solvedCacheContent.split("\n")
                                for (tuple in listOfTuples) {
                                    Log.i(TAG, "Tuple = "+tuple)
                                    val tupleElem = tuple.split(":")
                                    val sign = tupleElem[0]
                                    val prvKey = tupleElem[1]
                                    Log.i(TAG, "Signatur = "+sign)
                                    Log.i(TAG, "PrvKey = "+prvKey)
                                    if (sign.equals(item.signature)) {
                                        cache1.prvKey = prvKey
                                        bool = true
                                        break
                                    }
                                }
                            }
                        }
                        // Todo* programm asks to do this - is there a better way?
                        if (bool) {
                            val cache = cache1.pubKey?.let {
                                cache1.prvKey?.let { it1 ->
                                    SolvedCache(cache1.title, cache1.desc, cache1.creator, cache1.id,
                                        it, it1,
                                        cache1.hallOfFame, cache1.plainTextHOF)
                                }
                            }
                            if (cache != null) {
                                cacheList.add(cache)
                            }
                        } else {
                            val cache = cache1.pubKey?.let {
                                UnsolvedCache(cache1.title, cache1.desc, cache1.creator, cache1.id,
                                    it,
                                    cache1.hallOfFame, cache1.plainTextHOF)
                            }
                            if (cache != null) {
                                cacheList.add(cache)
                            }
                        }

                    }
                }
            }
        }
        Serializer.serializeCacheListToFile(cacheList, cacheListFile)
    }
}