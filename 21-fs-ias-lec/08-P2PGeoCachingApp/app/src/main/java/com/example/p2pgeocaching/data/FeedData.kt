package com.example.p2pgeocaching.data

import android.util.Log
import com.example.p2pgeocaching.caches.CacheListGenerator
import com.example.p2pgeocaching.constants.Constants
import java.io.File
import java.io.Serializable
import com.example.p2pgeocaching.ownbacnet.Entry
import com.example.p2pgeocaching.ownbacnet.LogEntry
import com.example.p2pgeocaching.ownbacnet.OwnPublisher
import com.example.p2pgeocaching.ownbacnet.OwnFeed

/**
 * This class represents a feed in data form to be serialized and back.
 */
@kotlinx.serialization.Serializable
class FeedData : Serializable {

    var stringFileContent: String = ""

    constructor(context: File) {
        stringFileContent = feedToData(context)
    }

    constructor(file: File, context: File) {
        dataToFeed(file, context)
    }

    companion object {
        const val TAG = "FeedData"
    }

    private fun feedToData(context: File): String {
        val file = File(context, "file")
        if (!file.exists()) {
            file.createNewFile()
            Log.i(TAG, "Created File")
        } else {
            file.delete()
            file.createNewFile()
            Log.i(TAG, "Deleted and Created File")
        }

        val userNameFile = File(context, Constants.U_NAME_FILE)
        var userName = userNameFile.readLines().toString()
        userName = userName.substring(1, userName.length - 1)
        val personData = File(context, Constants.PERSON_DATA)
        val content = personData.readText()
        val keys = content.split(" ")
        val pubkey = keys[0].split("_")
        val salt = pubkey[1].takeLast(4)
        val feedName = userName.plus("#").plus(salt)
        Log.i(TAG, "feedName = $feedName")
        val ownFeedFile = File(context, feedName)
        val ownFeedContent = ownFeedFile.readText()
        Log.i(TAG, "Before if")
        if (ownFeedContent.isNotEmpty()) {
            Log.i(TAG, "length is not zero")
            file.appendText(feedName)
            file.appendText("\n_:_:_")
            file.appendText("\n".plus(ownFeedContent))
            Log.i(TAG, "File Content after adding own feed = "+file.readText())
        }

        val feedNamesFile = File(context, Constants.FEED_NAMES_FILE)
        if (feedNamesFile.length() != 0L) {
            val feedNameList = feedNamesFile.readText().split("\n")

            for (feed in feedNameList) {
                val feedFile = File(context, feed)
                val feedContent = feedFile.readText()
                if (file.length() == 0L && feedContent.isNotEmpty()) {
                    file.appendText(feed)
                    file.appendText("\n_:_:_")
                    file.appendText("\n".plus(feedContent))
                    Log.i(TAG, "File Content after adding new feed = " + file.readText())
                } else if (feedContent.isNotEmpty()) {
                    file.appendText("\n#####")
                    file.appendText("\n".plus(feed))
                    file.appendText("\n_:_:_")
                    file.appendText("\n".plus(feedContent))
                    Log.i(TAG, "File Content after adding new feed = " + file.readText())
                }
            }
        }
        if (file.length() != 0L) {
            file.appendText("\n$$$$$")
        }
        Log.i(TAG, "File Content at the end = "+file.readText())
        return file.readText()
    }

    private fun dataToFeed (file: File, context:File) {
        Log.i(TAG, "started dataToFeed")
        try {
            val fileContentList = file.readText().replace("\n","").split("$$$$$")
            var fileContent = fileContentList[0]
            Log.i(TAG, "Received File Content = $fileContent")
            val feedList = fileContent.split("#####")

            val feedNamesFile = File(context, Constants.FEED_NAMES_FILE)
            if (feedNamesFile.length() != 0L) {
                val feedNameList = feedNamesFile.readText().split("\n")

                val fdp = FeedDataParser()

                val newEntryList = mutableListOf<Entry>()

                for (feed in feedList) {
                    Log.i(TAG, "Feed = $feed")
                    val feedElem = feed.split("_:_:_")
                    val feedName = feedElem[0]
                    Log.i(TAG, "FeedName = $feedName")
                    val feedContent = feedElem[1]
                    Log.i(TAG, "FeedContent = $feedContent")
                    for (person in feedNameList) {
                        Log.i (TAG, "Is this the Person = "+person)
                        if (person.equals(feedName)) {
                            Log.i(TAG, "Yes it's this Person: Feed is subscribed")
                            val personFile = File(context, person)
                            if (personFile.length() == 0L) {
                                Log.i (TAG, "Person's file length is zero")
                                personFile.appendText(feedContent)
                                Log.i (TAG, "Person's file content = "+personFile.readText())
                                val feedEntryList = fdp.feedToEntrylist(personFile)
                                Log.i(TAG, "feedEntryList size = "+feedEntryList.size)
                                for (element in feedEntryList) {
                                    newEntryList.add(element)
                                }
                            } else {
                                Log.i (TAG, "Person's file length is NOT zero")
                                val entryList = fdp.feedToEntrylist(personFile)
                                Log.i(TAG, "Old feedEntryList size = "+entryList.size)
                                var len = entryList.size
                                val lastEntry = entryList[len - 1]

                                val supportFile = File(context, "support")
                                if (!supportFile.exists()) {
                                    supportFile.createNewFile()
                                } else {
                                    supportFile.delete()
                                    supportFile.createNewFile()
                                }
                                supportFile.appendText(feedContent)
                                val feedEntryList = fdp.feedToEntrylist(supportFile)
                                len = feedEntryList.size
                                val lastEntryInFeed = feedEntryList[len - 1]
                                Log.i(TAG, "New feedEntryList size = "+len)

                                if (lastEntry.id < lastEntryInFeed.id) {
                                    Log.i(TAG, "We need Update")
                                    for (i in (lastEntry.id + 1)..lastEntryInFeed.id) {
                                        newEntryList.add(feedEntryList[i])
                                    }
                                    Log.i(TAG, "Old Feed Content = "+personFile.readText())
                                    personFile.delete()
                                    personFile.createNewFile()
                                    personFile.appendText(supportFile.readText())
                                    Log.i(TAG, "New Feed Content = " + personFile.readText())
                                    break
                                }
                            }
                        }
                    }
                }
                if (newEntryList.size > 0) {
                    Log.i(TAG, "New Entries")
                    val userNameFile = File(context, Constants.U_NAME_FILE)
                    var userName = userNameFile.readLines().toString()
                    userName = userName.substring(1, userName.length - 1)
                    val personData = File(context, Constants.PERSON_DATA)
                    val content = personData.readText()
                    val keys = content.split(" ")
                    val pubkey = keys[0].split("_")
                    val salt = pubkey[1].takeLast(4)
                    val feedName = userName.plus("#").plus(salt)

                    val ownPublisher = OwnPublisher(userName, keys[0], keys[1])

                    val ownFeedFile = File(context, feedName)
                    val ownFeedList = fdp.feedToEntrylist(ownFeedFile)

                    val ownFeed = OwnFeed(ownFeedList, ownPublisher)

                    val logEntry = LogEntry.Companion.newLogEntry(newEntryList, ownFeed, context)

                    val appendtext = fdp.appendCacheToFeed(logEntry)
                    Log.i(TAG, "Append Text = " + appendtext)
                    if (ownFeedFile.length() == 0L) {
                        ownFeedFile.appendText(appendtext)
                    } else {
                        ownFeedFile.appendText("-*-*-")
                        ownFeedFile.appendText("".plus(appendtext))
                    }
                    Log.i(TAG, "Own Feed Content = " + ownFeedFile.readText())
                    val generator = CacheListGenerator()
                    generator.getCacheListFileContent(context)
                }
            }
        } catch(exception: Exception) {

        }

    }

}