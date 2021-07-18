package com.example.p2pgeocaching.activities

import android.os.Bundle
import android.util.Log
import androidx.appcompat.app.AppCompatActivity
import com.example.p2pgeocaching.constants.Constants
import com.example.p2pgeocaching.databinding.ActivityAddNewFeedBinding
import com.example.p2pgeocaching.inputValidator.InputValidator
import java.io.File

/**
 * This activity enables the user to add a new Feed to their subscriptions.
 */
class AddNewFeedActivity : AppCompatActivity() {


    companion object {
        const val TAG = "AddNewFeedActivity"
    }

    private lateinit var binding: ActivityAddNewFeedBinding

    /**
     * Opens files, sets up button
     */
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Initialize the binding object
        binding = ActivityAddNewFeedBinding.inflate(layoutInflater)
        setContentView(binding.root)

        // Opens the files used in the app for storage
        val context = applicationContext
        val feedListFile = File(context.filesDir, Constants.U_NAME_FILE)

        //*
        binding.saveFeedButton.setOnClickListener {
            val feedFile = File(context.filesDir, Constants.FEED_NAMES_FILE)
            Log.d(TAG, "Activated SaveFeedButton")
            val publisherName = binding.publisherNameEditText.text.toString()
            Log.d(TAG, "PublisherName = "+publisherName)
            val pubKeyText = binding.pubKeyEditText.text.toString()
            Log.d(TAG, "PubKey = "+pubKeyText)
            InputValidator.checkUserNameForIllegalCharacters(publisherName)
            if (pubKeyText.length == 4) {
                val text = publisherName.plus('#').plus(pubKeyText)
                if (feedFile.length() == 0L) {
                    feedFile.appendText(text)
                } else {
                    feedFile.appendText("\n".plus(text))
                }
                val fileName = text
                Log.d(TAG, "FileName = " + fileName)
                var file = File(context.filesDir, fileName)
                file.createNewFile()
                if (file.exists()) {
                    Log.d(TAG, "File exists")
                }
            }
            finish()
        }
    }
}