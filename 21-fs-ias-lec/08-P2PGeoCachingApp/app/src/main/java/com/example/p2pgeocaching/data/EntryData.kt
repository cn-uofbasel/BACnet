package com.example.p2pgeocaching.data

import java.io.Serializable

/**
 * This class is used to store the data of an entry to be serialized and vice-versa.
 */
@kotlinx.serialization.Serializable
data class EntryData(
    val timestamp: Long,
    val id: Int,
    val signedPreviousSignature: String,
    val content: String,
    val type: String,
    val signature: String,
) : Serializable {

    // TODO: In future, the tasks of FeedData and FeedDataParser can be split up into
    // multiple classes

}