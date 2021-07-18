package com.example.p2pgeocaching.ownbacnet

import com.example.p2pgeocaching.constants.Constants
import com.example.p2pgeocaching.constants.Constants.Companion.LOG_ENTRY
import com.example.p2pgeocaching.data.FeedDataParser
import com.example.p2pgeocaching.data.Serializer
import java.io.File
import android.util.Log

/**
 * This class is created whenever the app receives new data from another user.
 * Thanks to this, one could create a logical time line, making faking timestamps incredibly hard.
 * The [content] contains tuples of all the received non-log [Entry] [id]s and [signature]s,
 * with their respective [Publisher].
 * e. g. : "15, sdfh7Hjs89, Tom#2571; 17, asd7873HHGk, Caroline#3142; ..."
 */
class LogEntry(
    timestamp: Long,
    id: Int,
    signedPreviousSignature: String,
    content: String,
    signature: String
) : Entry(timestamp, id, signedPreviousSignature, content, LOG_ENTRY, signature) {

    companion object {

        const val TAG = "LogEntry"

        /**
         * This method lets us create a [LogEntry] with a list of [newEntries].
         * It also needs a [ownFeed] to determine the current position in the feed.
         */
        fun newLogEntry(newEntries: List<Entry>, ownFeed: OwnFeed, context: File): LogEntry {
            Log.i(TAG, "New Log Entry")
            Log.i(TAG, "newEntries size = "+newEntries.size)
            val timestamp = System.currentTimeMillis()
            Log.i(TAG, "timeStamp = "+timestamp)
            val id = ownFeed.getNextID()
            Log.i(TAG, "id = "+id)
            val previousSignature = ownFeed.getLastSignature()
            Log.i(TAG, "previous signature = "+previousSignature)
            val signedPreviousSignature = ownFeed.getOwnPublisher().sign(previousSignature)
            Log.i(TAG, "signedPreviousSignature = "+previousSignature)
            val type = LOG_ENTRY
            var content = ""

            val fdp = FeedDataParser()
            val feedNamesFile = File(context, Constants.FEED_NAMES_FILE)
            val feedNameContent = feedNamesFile.readText()
            val feedNameList = feedNameContent.split("\n")
            var bool = false
            for (entry in newEntries) {
                bool = false
                for (feedName in feedNameList) {
                    val feedFile = File(context, feedName)
                    val listOfEntries = fdp.feedToEntrylist(feedFile)
                    for (feedEntry in listOfEntries) {
                        if (entry.id.equals(feedEntry.id) &&
                                entry.type.equals(feedEntry.type) &&
                                entry.signature.equals(feedEntry.signature) &&
                                entry.content.equals(feedEntry.content)) {
                            Log.i(TAG, "Got matching entry")
                            content = content.plus(entry.id).plus(",").plus(entry.signature).plus(",").plus(feedName).plus(";")
                            bool = true
                            break
                        }
                    }
                    if (bool) {
                        break
                    }
                }
            }
            Log.i(TAG, "content = "+content)
            val concatenatedString: String =
                timestamp.toString() + id.toString() + signedPreviousSignature + type + content
            val hashString = concatenatedString.hashCode().toString()
            val signature = ownFeed.getOwnPublisher().sign(hashString)
            val logEntry = LogEntry(timestamp, id, signedPreviousSignature, content, signature)
            Log.i(TAG, "LogEntry content = "+logEntry.content)
            return logEntry
        }
    }
}