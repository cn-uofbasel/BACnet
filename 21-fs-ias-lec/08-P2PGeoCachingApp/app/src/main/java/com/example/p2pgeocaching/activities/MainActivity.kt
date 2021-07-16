package com.example.p2pgeocaching.activities

import android.content.Intent
import android.os.Bundle
import android.util.Log
import androidx.appcompat.app.AppCompatActivity
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.example.p2pgeocaching.R
import com.example.p2pgeocaching.RSA.RSA
import com.example.p2pgeocaching.adapter.CacheAdapter
import com.example.p2pgeocaching.caches.CacheList
import com.example.p2pgeocaching.constants.Constants
import com.example.p2pgeocaching.constants.Constants.Companion.CACHE_LIST_FILE
import com.example.p2pgeocaching.constants.Constants.Companion.DUMMY_LIST_FILE
import com.example.p2pgeocaching.constants.Constants.Companion.USE_DUMMY_LIST
import com.example.p2pgeocaching.constants.Constants.Companion.U_NAME_FILE
import com.example.p2pgeocaching.data.Serializer.Companion.deserializeCacheListFromFile
import com.example.p2pgeocaching.databinding.ActivityMainBinding
import com.example.p2pgeocaching.ownbacnet.OwnFeed
import com.example.p2pgeocaching.ownbacnet.OwnPublisher
import java.io.File
import java.util.*

/**
 * This activity serves as the center of the app.
 * From here, we can change our name, create a new cache, look at our caches and transfer caches
 * with others.
 */
class MainActivity : AppCompatActivity() {


    companion object {
        const val TAG = "MainActivity"
    }

    lateinit var cacheList: CacheList
    private lateinit var binding: ActivityMainBinding
    private lateinit var recyclerView: RecyclerView


    /**
     * This method reads the files.
     * Also, prompts the user for a name if there is none saved.
     * Offers some buttons for different options.
     */
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        Log.d(TAG, "onCreate is called")

        // Initialize the binding object
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)


        // Opens the files used in the app for storage
        val context = applicationContext
        val userNameFile = File(context.filesDir, U_NAME_FILE)
        val cacheListFile = File(context.filesDir, CACHE_LIST_FILE)

        // For presentation and testing purposes
        if (USE_DUMMY_LIST) {

            // Open resources
            val dummyListFile = assets.open(DUMMY_LIST_FILE)
            val scanner = Scanner(dummyListFile)
            var dummyListText = ""

            // Read entire file into dummyListText
            while (scanner.hasNextLine()) {
                dummyListText += scanner.nextLine() + "\n"
            }
            Log.d(TAG, "Read DummyList:\n$dummyListText")

            // Delete old file and replace with new one
            cacheListFile.delete()
            cacheListFile.writeText(dummyListText)
        }

        // Username not selected -> put NewUser in U_NAME_FILE
        var userName = ""
        if (!userNameFile.exists()) {
            userName = "NewUser"
            userNameFile.writeText(userName)
            Log.d(TAG, "Written User Name: $userName")
            title = getString(R.string.welcome_message, userName)

        } else { // Username has been selected, show it in title
            userName = userNameFile.readLines().toString()
            userName = userName.substring(1, userName.length - 1)
            Log.d(TAG, "User name: $userName")
            title = getString(R.string.welcome_message, userName)
        }


        Log.d(TAG, "before filestuff")
        //val fileName = "personData"
        Log.d(TAG, "after filename")
        var file = File(context.filesDir, Constants.PERSON_DATA)
        Log.d(TAG, "after file")
        var fileExists = file.exists()
        Log.d(TAG, "after fileexists")
        if(!fileExists){
            Log.d(TAG, "file doesn't exist/before rsa")
            val keyPair: String = RSA.generateKeys()
            Log.d(TAG, "after RSA")
            val pubKey = RSA.getPublicKey(keyPair)
            Log.d(TAG, "Public Key: $pubKey")
            val prvKey = RSA.getPrivateKey(keyPair)
            Log.d(TAG, "Private Key: $prvKey")
            val ownPublisher = OwnPublisher(userName, pubKey, prvKey)
            val ownFeed = OwnFeed(mutableListOf(), ownPublisher)
            //*
            ownFeed.createOwnFeed(context.filesDir)
            file.createNewFile()
            val text = pubKey.plus(" ").plus(prvKey)
            file.writeText(text)
        } else {
            Log.d(TAG, "File content: " + file.readText())
        }
        // This function sets the recyclerView to the current cacheList written in the file.
        // Also removes the background text.
        // If it is empty, shows background text, and the recycler view is hidden.
        updateCacheList(cacheListFile)

        // Opens rename activity when pressed
        binding.changeUserNameButton.setOnClickListener {
            val intent = Intent(context, UserNameActivity::class.java)
            intent.putExtra(U_NAME_FILE, userNameFile)
            Log.d(TAG, "Made it past putExtra")
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK) // Better alternative?
            context.startActivity(intent)
        }

        // Opens activity to manage feeds
        binding.modifyFeedsButton.setOnClickListener {
            val intent = Intent(context, FeedActivity::class.java)
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            context.startActivity(intent)
        }

        // Opens activity to connect to others
        binding.connectButton.setOnClickListener {
            val intent = Intent(context, BluetoothTransferActivity::class.java)
            intent.putExtra(U_NAME_FILE, userNameFile)
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK) // Better alternative?
            context.startActivity(intent)
        }

        // Opens activity to create caches
        binding.createCacheButton.setOnClickListener {
            val intent = Intent(context, NewCacheActivity::class.java)
            intent.putExtra(U_NAME_FILE, userNameFile)
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK) // Better alternative?
            context.startActivity(intent)
        }

    }


    /**
     * When coming back from another activity, update the title and the list of caches.
     */
    override fun onRestart() {
        super.onRestart()

        // Gets context and file
        val context = applicationContext
        val userNameFile = File(context.filesDir, U_NAME_FILE)
        val cacheListFile = File(context.filesDir, CACHE_LIST_FILE)

        // Updates title
        if (userNameFile.exists()) {
            var userName = userNameFile.readLines().toString()

            // Remove the first and last characters (which are not needed)
            userName = userName.substring(1, userName.length - 1)
            Log.d(TAG, userName)
            title = getString(R.string.welcome_message, userName)
        }

        // Update the list of caches
        updateCacheList(cacheListFile)
    }


    /**
     * This function updates the [cacheList] and the text shown in background.
     * If [cacheList] is empty, show prompt to get caches.
     * If it contains something, show it in the [recyclerView].
     * [cacheListFile] is the file containing the serialized [CacheList] object.
     */
    private fun updateCacheList(cacheListFile: File) {

        // Initialize the CacheList field with the file contents
        if (cacheListFile.exists()) {

            // Deserialize the file and get the object
            cacheList = deserializeCacheListFromFile(cacheListFile)

            if (cacheList.list.isEmpty()) {

                // Update recyclerView to show list (if it is not empty)
                recyclerView = binding.recyclerView
                recyclerView.layoutManager = LinearLayoutManager(this)
                recyclerView.adapter = CacheAdapter(cacheList)

                // Set text prompt to "get or create caches"
                binding.emptyCacheListPromptText.text = getString(R.string.empty_list_prompt)
            } else {

                // Update recyclerView to show list (if it is not empty)
                recyclerView = binding.recyclerView
                recyclerView.layoutManager = LinearLayoutManager(this)
                recyclerView.adapter = CacheAdapter(cacheList)

                // Remove the text prompt to "get or create caches"
                binding.emptyCacheListPromptText.text = ""
            }

        } else { // File is empty

            // Initialize empty list
            cacheList = CacheList(mutableListOf())

            // Set text prompt to "get or create caches"
            binding.emptyCacheListPromptText.text = getString(R.string.empty_list_prompt)
        }
    }
}