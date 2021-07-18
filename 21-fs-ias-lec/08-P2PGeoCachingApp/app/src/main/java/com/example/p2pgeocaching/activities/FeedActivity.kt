package com.example.p2pgeocaching.activities

import android.content.Intent
import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.example.p2pgeocaching.R
import com.example.p2pgeocaching.adapter.FeedAdapter
import com.example.p2pgeocaching.constants.Constants.Companion.FEED_NAMES_FILE
import com.example.p2pgeocaching.constants.Constants.Companion.USE_DUMMY_FEED_NAME_LIST
import com.example.p2pgeocaching.databinding.ActivityFeedBinding
import java.io.File

/**
 * This activity enables the user to view their feeds.
 */
class FeedActivity : AppCompatActivity() {

    companion object {
        const val TAG = "FeedActivity"
    }

    private lateinit var binding: ActivityFeedBinding
    private lateinit var recyclerView: RecyclerView
    private lateinit var feedNameList: List<String>

    /**
     * Reads from files which feeds the user is subscribed to.
     * Displays them in recyclerList, when pressed on they open FeedDetailViewActivity
     * The button at the bottom is for adding new feeds, leads to AddNewFeedActivity.
     */
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Initialize the binding object
        binding = ActivityFeedBinding.inflate(layoutInflater)
        setContentView(binding.root)

        // Set title
        title = getString(R.string.feeds_title)


        // Opens the files used in the app for storage
        val context = applicationContext
        val feedsNameFile = File(context.filesDir, FEED_NAMES_FILE)

        // User has not subscribed to any feeds or is opening the app for the first time
        // show them a message
        if (!feedsNameFile.exists() && !USE_DUMMY_FEED_NAME_LIST) {
            feedNameList = mutableListOf()
            binding.emptyFeedListPromptText.text = getString(R.string.empty_feed_list_prompt)

        } else { // File exists

            // for testing purposes
            feedNameList = if (USE_DUMMY_FEED_NAME_LIST) {
                mutableListOf("Wolf#2404", "Adam#1234")

            } else { // actual implementation
                //*
                getFeedList(feedsNameFile.readText())
                //mutableListOf()
            }

            // File exists, but is empty, show message
            if (feedNameList.isEmpty()) {
                binding.emptyFeedListPromptText.text = getString(R.string.empty_feed_list_prompt)

            } else { // List of feeds exists
                // initialize the recyclerview
                recyclerView = binding.feedRecyclerView
                recyclerView.layoutManager = LinearLayoutManager(this)
                recyclerView.adapter = FeedAdapter(feedNameList)

                // remove prompt in background
                binding.emptyFeedListPromptText.text = ""
            }
        }

        // When button is clicked, open activity to add new Feed
        binding.addFeedButton.setOnClickListener {
            val intent = Intent(context, AddNewFeedActivity::class.java)
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            context.startActivity(intent)
            onRestart()
        }
    }

    //*
    fun getFeedList (text: String): List<String> {
        if (text.length == 0) {
            return mutableListOf()
        } else {
            return text.split('\n')
        }
    }

    /**
     * When new cache is added and it returns to this activity, refresh list.
     */
    override fun onRestart() {
        super.onRestart()
        val context = applicationContext
        val feedsNameFile = File(context.filesDir, FEED_NAMES_FILE)
        if (!feedsNameFile.exists() && !USE_DUMMY_FEED_NAME_LIST) {
            feedNameList = mutableListOf()
            binding.emptyFeedListPromptText.text = getString(R.string.empty_feed_list_prompt)

        } else { // File exists

            // for testing purposes
            feedNameList = if (USE_DUMMY_FEED_NAME_LIST) {
                mutableListOf("Wolf#2404", "Adam#1234")

            } else { // actual implementation
                //*
                getFeedList(feedsNameFile.readText())
                //mutableListOf()
            }

            // File exists, but is empty, show message
            if (feedNameList.isEmpty()) {
                binding.emptyFeedListPromptText.text = getString(R.string.empty_feed_list_prompt)

            } else { // List of feeds exists
                // initialize the recyclerview
                recyclerView = binding.feedRecyclerView
                recyclerView.layoutManager = LinearLayoutManager(this)
                recyclerView.adapter = FeedAdapter(feedNameList)

                // remove prompt in background
                binding.emptyFeedListPromptText.text = ""
            }
        }
    }
}