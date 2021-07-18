package com.example.p2pgeocaching.data

import android.util.Log
import com.example.p2pgeocaching.caches.Cache
import com.example.p2pgeocaching.caches.CacheList
import com.google.gson.Gson
import java.io.File

/**
 * This class takes objects and saves them to file.
 * It can also create objects by reading from files.
 * It can also create objects from JSON and create JSON from objects.
 */
class Serializer {

    companion object {

        private const val TAG = "Serializer"


        /**
         * Given the file [cacheListFile] containing the serialized version of the cache list, returns
         * the object encoded in it. If the file is empty, return empty list.
         */
        fun deserializeCacheListFromFile(cacheListFile: File): CacheList {

            return if (cacheListFile.exists()) {
                // Read file, deserialize it, assign it to cacheList

                val cacheListDataString = cacheListFile.readText().toString()
                Log.d(TAG, "Read the following from file:\n$cacheListDataString")

                // Does not work unfortunately:
                //val cacheListData = Json.decodeFromString<CacheListData>(cacheListDataString)

                // Alternatively, use GSON:
                val gson = Gson()
                val cacheListData = gson.fromJson(cacheListDataString, CacheListData::class.java)

                // Transform from data to the actual object
                CacheListDataParser.dataToList(cacheListData)
            } else { // CacheListFile has not been created yet, return empty list
                CacheList(mutableListOf())
            }
        }


        /**
         * This function serializes the [cacheList] and writes it to [cacheListFile].
         */
        fun serializeCacheListToFile(cacheList: CacheList, cacheListFile: File) {
            val cacheListData = CacheListDataParser.listToData(cacheList)

            // Does not work unfortunately:
            //val serializedCacheList = Json.encodeToString(cacheListData)

            // Use Gson instead:
            val gson = Gson()
            val serializedCacheList = gson.toJson(cacheListData)
            Log.i(TAG, "Wrote the following to file:\n$serializedCacheList")

            // Overwrite file with new JSON cacheList
            cacheListFile.delete()
            cacheListFile.writeText(serializedCacheList)

        }

        /**
         * This function serializes a single [Cache] and returns the String.
         */
        fun serializeCacheToString(cache: Cache): String {
            val cacheData = CacheDataParser.cacheToData(cache)

            val gson = Gson()
            return gson.toJson(cacheData)
        }

        /**
         * This function deserializes a single [Cache] from a String.
         */
        fun deserializeCacheFromString(cacheString: String): Cache {
            val gson = Gson()
            val cacheData = gson.fromJson(cacheString, CacheData::class.java)
            return CacheDataParser.dataToCache(cacheData)
        }
    }
}