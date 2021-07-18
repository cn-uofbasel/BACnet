package com.example.p2pgeocaching.activities

import android.os.Bundle
import android.util.Log
import androidx.appcompat.app.AppCompatActivity
import com.example.p2pgeocaching.R
import com.example.p2pgeocaching.RSA.RSA
import com.example.p2pgeocaching.caches.Cache
import com.example.p2pgeocaching.caches.CacheListGenerator
import com.example.p2pgeocaching.caches.UnsolvedCache
import com.example.p2pgeocaching.constants.Constants
import com.example.p2pgeocaching.constants.Constants.Companion.CACHE_LIST_FILE
import com.example.p2pgeocaching.constants.Constants.Companion.ID
import com.example.p2pgeocaching.constants.Constants.Companion.PUBLIC_KEY
import com.example.p2pgeocaching.constants.Constants.Companion.U_NAME_FILE
import com.example.p2pgeocaching.data.FeedDataParser
import com.example.p2pgeocaching.data.Serializer
import com.example.p2pgeocaching.databinding.ActivitySolveBinding
import com.example.p2pgeocaching.inputValidator.InputValidator
import com.example.p2pgeocaching.ownbacnet.HoFEntry
import com.example.p2pgeocaching.ownbacnet.OwnFeed
import com.example.p2pgeocaching.ownbacnet.OwnPublisher
import com.example.p2pgeocaching.p2pexceptions.KeyIsNotLegalException
import java.io.File

/**
 * This activity enables the user to solve one of their unsolved caches.
 */
class SolveActivity : AppCompatActivity() {

    companion object {
        const val TAG = "SolveActivity"
    }

    private lateinit var binding: ActivitySolveBinding
    private lateinit var publicKey: String
    private var userName = ""
    private var cache: Cache? = null


    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Initialize binding object
        binding = ActivitySolveBinding.inflate(layoutInflater)
        setContentView(binding.root)

        // Opens the files used in the app for storage
        val context = applicationContext
        val userNameFile = File(context.filesDir, U_NAME_FILE)
        val cacheListFile = File(context.filesDir, CACHE_LIST_FILE)

        // Get username
        if (userNameFile.exists()) {
            userName = userNameFile.readLines().toString()

            // Remove the first and last characters (which are not needed)
            userName = userName.substring(1, userName.length - 1)
        }

        // Get cache
        val cacheList = Serializer.deserializeCacheListFromFile(cacheListFile)
        val cacheID = intent?.extras?.getInt(ID)
        if (cacheID == null) {
            finish()
            return
        }
        cache = cacheList.findByID(cacheID!!) as UnsolvedCache
        if (cache == null) {
            finish()
            return
        }

        // Change title
        title = getString(R.string.solve_title)

        // Get the public key
        publicKey =
            intent?.extras?.getSerializable(PUBLIC_KEY).toString()
        if (publicKey == "") {
            finish()
            return
        }

        binding.submitPrivateKeyButton.setOnClickListener {
            val privateKey = binding.privateKeyEditText.text.toString()

            // Check if it is valid input
            var isValidKey = false
            try {
                InputValidator.checkKey(privateKey)
                isValidKey = true
            } catch (e: KeyIsNotLegalException) {
            }
            if (!isValidKey) {
                binding.solveErrorText.text = getString(R.string.illegal_key_error)
            } else {

                // Check that keys match
                if (privateKey != "" && isValidKeypair(privateKey, publicKey)) {
                    if (cache is UnsolvedCache) {

                        // Solves cache, removes unsolved, adds solved, saves
                        val unsolvedCache = cache as UnsolvedCache
                        val solvedCache = unsolvedCache.solveCache(userName, privateKey)

                        val creatorString = userNameFile.readLines().toString()
                        val creator = creatorString.substring(1, creatorString.length - 1)
                        var file = File(context.filesDir, Constants.PERSON_DATA)
                        val content = file.readText()
                        val keys = content.split(" ")
                        val pubkey = keys[0].split("_")
                        val salt = pubkey[1].takeLast(4)
                        val feedname = creator.plus("#").plus(salt)

                        val feedFile = File(context.filesDir, feedname)
                        val feedParser = FeedDataParser()
                        val entryList = feedParser.feedToEntrylist(feedFile)
                        val op = OwnPublisher(creator, keys[0], keys[1])
                        val ownFeed = OwnFeed(entryList, op)
                        val hofEntry = HoFEntry.Companion.newHoFEntry(privateKey, solvedCache, ownFeed, context.filesDir)

                        val appendtext = feedParser.appendCacheToFeed(hofEntry)
                        Log.i(NewCacheActivity.TAG, "AppendText = "+appendtext)
                        if (feedFile.length() == 0L) {
                            feedFile.appendText(appendtext)
                        } else {
                            feedFile.appendText("-*-*-")
                            feedFile.appendText("".plus(appendtext))
                        }
                        val solvedCacheListFile = File(context.filesDir, Constants.SOLVED_CACHE_LIST_FILE)
                        if (solvedCacheListFile.length() == 0L) {
                            Log.i(TAG, "ownCacheListFile appendedText = "+hofEntry.signature.plus(":").plus(privateKey))
                            solvedCacheListFile.appendText(hofEntry.signature.plus(":").plus(privateKey))
                        } else {
                            Log.i(NewCacheActivity.TAG, "ownCacheListFile appendedText = "+hofEntry.signature.plus(":").plus(privateKey))
                            solvedCacheListFile.appendText("\n".plus(hofEntry.signature).plus(":").plus(privateKey))
                        }
                        Log.i(TAG, "solvedCacheListFile Text = "+solvedCacheListFile.readText())
                        Log.i(TAG, "Feed Content = "+feedFile.readText())
                        val generator = CacheListGenerator()
                        generator.getCacheListFileContent(context.filesDir)
                        //cacheList.removeCacheByID(unsolvedCache.id)
                        //cacheList.add(solvedCache)
                        //Serializer.serializeCacheListToFile(cacheList, cacheListFile)
                    }
                    finish()
                } else {
                    binding.solveErrorText.text = getString(R.string.solve_cache_error)
                }
            }
        }
    }

    /**
     * This function checks if the two keys [prv] and [pub] belong to one another.
     * If they do, returns true, else false.
     * It does this by checking if encrypting, then decrypting, does not change the sample string.
     */
    private fun isValidKeypair(prv: String, pub: String): Boolean {
        val str = "some String"

        // Encrypt the String
        val cipherString = RSA.encode(str, prv)

        // Decrypt the String
        val plainString = RSA.decode(cipherString, pub)

        // Check if equal
        return str == plainString
    }
}