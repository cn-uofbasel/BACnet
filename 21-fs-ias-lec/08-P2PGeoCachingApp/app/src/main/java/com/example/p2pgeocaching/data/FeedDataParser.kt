package com.example.p2pgeocaching.data

import com.example.p2pgeocaching.ownbacnet.CacheEntry
import com.example.p2pgeocaching.ownbacnet.Entry
import java.io.File
import android.util.Log
import com.example.p2pgeocaching.caches.CacheListGenerator

/**
 * This class parses a FeedData object to an actual Feed and back.
 */
class FeedDataParser {

    companion object {
        const val TAG = "FeedDataParser"
    }

    fun feedToEntrylist(feedFile : File): List<Entry> {
        if(feedFile.length() == 0L) {
            return mutableListOf()
        } else {
            val content = feedFile.readText()
            Log.i(TAG, "Content = "+content)
            val entrylist = content.split("-*-*-")
            val listOfEntries = mutableListOf<Entry>()
            for (item in entrylist) {
                val ep = item.split("***")
                val entry = Entry(
                    ep[0].toLong(),// timestamp
                    ep[1].toInt(), // id
                    ep[2],         // signedPreviousSignature
                    ep[3],         // content
                    ep[4],         // type
                    ep[5]          // signature
                )
                Log.i(TAG, "Entry Id = "+entry.id)
                Log.i(TAG, "Entry Content = "+entry.content)
                Log.i(TAG, "Entry Signature = "+entry.signature)
                Log.i(TAG, "Entry Previous = "+entry.signedPreviousSignature)
                Log.i(TAG, "Entry Time = "+entry.timestamp)
                Log.i(TAG, "Entry Type = "+entry.type)
                listOfEntries.add(entry)
            }
            return listOfEntries
        }
    }

    fun appendCacheToFeed(cacheEntry : Entry) : String {
        val str =
            cacheEntry.timestamp.toString()
                .plus("***")
                .plus("".plus(cacheEntry.id.toString()))
                .plus("***")
                .plus("".plus(cacheEntry.signedPreviousSignature))
                .plus("***")
                .plus("".plus(cacheEntry.content))
                .plus("***")
                .plus("".plus(cacheEntry.type))
                .plus("***")
                .plus("".plus(cacheEntry.signature))
        return str
    }

}