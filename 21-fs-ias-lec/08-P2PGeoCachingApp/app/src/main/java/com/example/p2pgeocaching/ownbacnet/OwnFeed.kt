package com.example.p2pgeocaching.ownbacnet

import android.util.Log
import com.example.p2pgeocaching.activities.MainActivity
import java.io.File
import android.content.Context

/**
 * This is a [Feed] object, owned by the user, meaning it can be modified.
 */
class OwnFeed(entries: List<Entry>, ownPublisher: OwnPublisher) : Feed(entries, ownPublisher) {

    companion object {
        const val TAG = "OwnFeed"
    }

    fun createOwnFeed(context: File) {
        var str = ""
        val name = getOwnPublisher().name
        val salt = getOwnPublisher().getSalt()
        val feedName = name.plus("#").plus(salt)
        Log.d(TAG, "feedName = $feedName")
        val file = File(context, feedName)
        file.createNewFile()
    }

    /** This method is used to create a new own feed and to delete the
     * old feed
     */
    fun createNewFeed(oldusername: String, key:String, context: File) {
        var str = ""
        val name = getOwnPublisher().name
        val salt = getOwnPublisher().getSalt()
        val feedName = name.plus("#").plus(salt)
        Log.d(TAG, "feedName = $feedName")
        val file = File(context, feedName)

        val oldFeedName = oldusername.plus("#").plus(getOwnPublisher().getSaltOfOldPublisher(key))
        val oldFile = File(context, oldFeedName)
        oldFile.delete()
        file.createNewFile()
    }

    /**
     * Returns the [Publisher] as an [OwnPublisher] object (which it always is).
     */
    fun getOwnPublisher(): OwnPublisher {
        return publisher as OwnPublisher
    }
}