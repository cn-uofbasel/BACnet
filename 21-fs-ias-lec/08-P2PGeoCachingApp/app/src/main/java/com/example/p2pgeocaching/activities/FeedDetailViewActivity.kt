package com.example.p2pgeocaching.activities

import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import com.example.p2pgeocaching.R
import com.example.p2pgeocaching.constants.Constants.Companion.FEED_NAME
import com.example.p2pgeocaching.constants.Constants.Companion.FEED_NAMES_FILE
import com.example.p2pgeocaching.databinding.ActivityFeedDetailViewBinding
import java.io.File

/**
 * This is the detail view of an activity, enabling the user to delete it.
 */
class FeedDetailViewActivity : AppCompatActivity() {

    companion object {
        const val TAG = "FeedDetailViewActivity"
    }

    private lateinit var binding: ActivityFeedDetailViewBinding
    private lateinit var feedName: String

    /**
     * Writes the name and binds the button to delete
     */
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Initialize the binding object
        binding = ActivityFeedDetailViewBinding.inflate(layoutInflater)
        setContentView(binding.root)
        val context = applicationContext

        // Check if there was a string given
        val bundleData: String = intent?.extras?.getString(FEED_NAME).toString()

        // was empty, exit
        if (bundleData == "") {
            finish()
            return

        } else { // was not empty
            feedName = bundleData
            title = getString(R.string.feedDetailTitle)
            binding.feedName.text = bundleData
        }

        // set up delete button
        binding.deleteFeedButton.setOnClickListener {
            // initialize the file
            val feedNameFile = File(context.filesDir, FEED_NAMES_FILE)
            val feedFile = File(context.filesDir, feedName)
            feedFile.delete()
            val text = feedNameFile.readText()
            val list = text.split('\n')
            if (feedNameFile.exists()) {
                feedNameFile.delete()
            }
            feedNameFile.createNewFile()
            if (list.size == 1) {
                finish()
            }
            for (item in list) {
                if (!item.equals(feedName)) {
                    if (feedNameFile.length() == 0L) {
                        feedNameFile.appendText(item)
                    } else {
                        feedNameFile.appendText("\n".plus(item))
                    }
                }
            }
            finish()
        }
    }
}