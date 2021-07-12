package com.example.p2pgeocaching.activities

import android.content.Context
import android.os.Bundle
import android.util.Log
import androidx.appcompat.app.AppCompatActivity
import com.example.p2pgeocaching.R
import com.example.p2pgeocaching.caches.Cache
import com.example.p2pgeocaching.caches.CacheList
import com.example.p2pgeocaching.constants.Constants.Companion.CACHE
import com.example.p2pgeocaching.constants.Constants.Companion.CACHE_LIST_FILE
import com.example.p2pgeocaching.data.CacheData
import com.example.p2pgeocaching.data.CacheDataParser
import com.example.p2pgeocaching.data.Serializer
import com.example.p2pgeocaching.databinding.ActivitySolvedCacheDetailBinding
import java.io.File

/**
 * This class is used when viewing the details of a solved Cache.
 */
class SolvedCacheDetailActivity : AppCompatActivity() {

    companion object {
        const val TAG = "SolvedCacheDetailActivity"
        var currentCache: Cache? = null
    }

    private lateinit var binding: ActivitySolvedCacheDetailBinding
    private lateinit var cache: Cache
    private lateinit var cacheList: CacheList
    private lateinit var context: Context
    private lateinit var cacheListFile: File


    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Initialize binding object
        binding = ActivitySolvedCacheDetailBinding.inflate(layoutInflater)
        setContentView(binding.root)

        // Opens the files used in the app for storage
        context = applicationContext
        cacheListFile = File(context.filesDir, CACHE_LIST_FILE)

        // Get cacheList
        cacheList = Serializer.deserializeCacheListFromFile(cacheListFile)

        // Check if a CacheData object was given
        // If no CachedData object was given and there is no currentCache,
        // return to previous activity
        val bundleData = intent?.extras?.getSerializable(CACHE)

        // no data was given
        if (bundleData == null) {
            Log.d(OwnCacheDetailActivity.TAG, "Intent did not contain Cache")

            // returning from previous entry, make cache currentCache
            if (currentCache != null) {
                cache = currentCache!!

                // no cache was given and there is no previous cache, exit
            } else {
                finish()
                return
            }

            // there is a cache given, make it currentCache
        } else {
            val cacheData: CacheData = bundleData as CacheData

            // If a cache was given, parse it to cache and to currentCache
            cache = CacheDataParser.dataToCache(cacheData)
            currentCache = cache
        }

        // Open cacheList to check if it is still in there, if not, leave activity
        context = applicationContext
        cacheListFile = File(context.filesDir, CACHE_LIST_FILE)
        cacheList = Serializer.deserializeCacheListFromFile(cacheListFile)
        if (cacheList.findByID(cache.id) == null) {
            currentCache = null
            finish()
            return
        }

        // Initialize the fields of the UI
        title = getString(R.string.solved_cache_title)
        binding.cacheTitle.text = cache.title
        binding.cacheDesc.text = cache.desc
        binding.creator.text = getString(R.string.creator_text, cache.creator)
        binding.hallOfFameText.text = cache.plainTextHOF

        // Press the delete button to return to the list with the cache removed
        /*binding.deleteButtonSolved.setOnClickListener {
            cacheList.removeCacheByID(cache.id)
            Serializer.serializeCacheListToFile(cacheList, cacheListFile)
            finish()
        }*/
    }
}