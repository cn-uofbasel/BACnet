package com.example.p2pgeocaching.activities

import android.content.Context
import android.content.Intent
import android.os.Bundle
import android.util.Log
import androidx.appcompat.app.AppCompatActivity
import com.example.p2pgeocaching.R
import com.example.p2pgeocaching.caches.Cache
import com.example.p2pgeocaching.caches.CacheList
import com.example.p2pgeocaching.caches.SolvedCache
import com.example.p2pgeocaching.constants.Constants.Companion.CACHE
import com.example.p2pgeocaching.constants.Constants.Companion.CACHE_LIST_FILE
import com.example.p2pgeocaching.constants.Constants.Companion.ID
import com.example.p2pgeocaching.constants.Constants.Companion.PUBLIC_KEY
import com.example.p2pgeocaching.data.CacheData
import com.example.p2pgeocaching.data.CacheDataParser
import com.example.p2pgeocaching.data.Serializer
import com.example.p2pgeocaching.databinding.ActivityUnsolvedCacheDetailBinding
import java.io.File

/**
 * This class is used when viewing the details of an unsolved Cache.
 */
class UnsolvedCacheDetailActivity : AppCompatActivity() {

    companion object {
        const val TAG = "UnsolvedCacheDetailActivity"
        var currentCache: Cache? = null
    }

    private lateinit var binding: ActivityUnsolvedCacheDetailBinding
    private lateinit var cache: Cache
    private lateinit var cacheList: CacheList
    private lateinit var cacheListFile: File
    private lateinit var context: Context


    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Initialize binding object
        binding = ActivityUnsolvedCacheDetailBinding.inflate(layoutInflater)
        setContentView(binding.root)

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
        title = getString(R.string.unsolved_cache_title)
        binding.cacheTitle.text = cache.title
        binding.cacheDesc.text = cache.desc
        binding.creator.text = getString(R.string.creator_text, cache.creator)
        binding.hallOfFameText.text = cache.plainTextHOF

        // If solve button is clicked, open SolveActivity
        binding.solveCacheButton.setOnClickListener {
            val intent = Intent(context, SolveActivity::class.java)
            intent.putExtra(PUBLIC_KEY, cache.pubKey)
            intent.putExtra(ID, cache.id)
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK) // Better alternative?
            context.startActivity(intent)
        }

        // Press the delete button to return to the list with the cache removed
        /*binding.deleteButtonUnsolved.setOnClickListener {
            cacheList.removeCacheByID(cache.id)
            Serializer.serializeCacheListToFile(cacheList, cacheListFile)
            finish()
        }*/
    }


    /**
     * When cache was solved, return to MainActivity.
     */
    override fun onRestart() {
        super.onRestart()
        Log.d(TAG, "onRestart() has been called")

        // Check if a CacheData object was given
        // If no CachedData object was given, return to previous activity
        val bundleData = intent?.extras?.getSerializable(CACHE)
        if (bundleData == null) {
            Log.d(OwnCacheDetailActivity.TAG, "Intent did not contain Cache")
            finish()
            return
        }
        val cacheData: CacheData = bundleData as CacheData

        // If a cache was given, parse it to
        val cache = CacheDataParser.dataToCache(cacheData)

        // Open cacheList to check if it has been solved, if yes, leave activity
        cacheListFile = File(context.filesDir, CACHE_LIST_FILE)
        val cacheList = Serializer.deserializeCacheListFromFile(cacheListFile)
        if (cacheList.findByID(cache.id) is SolvedCache) {
            finish()
        }
    }
}