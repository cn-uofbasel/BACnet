package com.example.p2pgeocaching.activities

import android.content.Context
import android.os.Bundle
import android.util.Log
import android.view.KeyEvent
import android.view.View
import android.view.inputmethod.InputMethodManager
import androidx.appcompat.app.AppCompatActivity
import com.chaquo.python.Python
import com.chaquo.python.android.AndroidPlatform
import com.example.p2pgeocaching.R
import com.example.p2pgeocaching.RSA.RSA
import com.example.p2pgeocaching.caches.CacheListGenerator
import com.example.p2pgeocaching.constants.Constants.Companion.PERSON_DATA
import com.example.p2pgeocaching.constants.Constants.Companion.U_NAME_FILE
import com.example.p2pgeocaching.databinding.ActivityUserNameBinding
import com.example.p2pgeocaching.inputValidator.InputValidator
import com.example.p2pgeocaching.ownbacnet.OwnFeed
import com.example.p2pgeocaching.ownbacnet.OwnPublisher
import com.example.p2pgeocaching.p2pexceptions.StringContainsIllegalCharacterException
import java.io.File


/**
 * This activity enables the user to add their name to the system or change it.
 */
class UserNameActivity : AppCompatActivity() {

    companion object {
        const val TAG = "UserNameActivity"
    }

    private lateinit var binding: ActivityUserNameBinding

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        title = getString(R.string.user_name_title)

        Log.d(TAG, "UserNameActivity was opened successfully.")

        binding = ActivityUserNameBinding.inflate(layoutInflater)
        setContentView(binding.root)

        // Get the file for the username
        val context = applicationContext
        val userNameFile = File(context.filesDir, U_NAME_FILE)
        val personData = File(context.filesDir, PERSON_DATA)

        // initialize fields
        val key = personData.readText()
        val salt = getSalt(key)
        var userName = userNameFile.readLines().toString()
        userName = userName.substring(1, userName.length - 1)
        val feedName = "$userName#$salt"
        val saltMessage = getString(R.string.salt_message, salt)
        val userNameMessage = getString(R.string.user_name_message, userName)
        val feedNameMessage = getString(R.string.feed_name_message, feedName)
        binding.currentUserNameText.text = userNameMessage
        binding.saltText.text = saltMessage
        binding.yourFeedName.text = feedNameMessage


        // validate input, show error message or return
        binding.userNameButton.setOnClickListener {
            Log.d(TAG, "Button was pressed")
            handleInput(userNameFile, context.filesDir)
        }

        // close keyboard when enter is pressed
        binding.userNameEditText.setOnKeyListener { view, keyCode, _ ->
            handleKeyEvent(
                view,
                keyCode
            )
        }
    }

    // This method returns salt
    fun getSalt(key: String): String {
        val list1 = key.split(' ')
        val pub = list1[0]
        val list2 = pub.split('_')
        val n = list2[1]
        val salt = n.takeLast(4)
        Log.d(OwnPublisher.TAG, "Old salt of Publisher:\n$salt")
        return salt
    }

    /**
     * This function looks if the entered text is legal.
     * If it is, it saves it and writes to the file.
     * If it is not, displays error message.
     */
    private fun handleInput(file: File, context: File) {
        Log.d(TAG, "handleInput() was called")
        val userNameString: String = binding.userNameEditText.text.toString()
        Log.d(TAG, "usernameString is: $userNameString")

        // Username is empty
        if (userNameString == "") {
            Log.d(TAG, "Empty username detected")
            binding.userNameErrorText.text = getString(R.string.warning_empty_user_name)

        } else { // Username is not empty
            var hasIllegalCharacters = false
            try {
                InputValidator.checkUserNameForIllegalCharacters(userNameString)
            } catch (e: StringContainsIllegalCharacterException) {
                Log.d(TAG, "String contains illegal characters")

                // Contains illegal characters
                hasIllegalCharacters = true
                binding.userNameErrorText.text =
                    getString(R.string.warning_illegal_characters_user_name)
            }

            // Everything is correct, write to file, go back
            if (!hasIllegalCharacters) {

                //val fileName = "personData"
                var personFile = File(context, PERSON_DATA)
                val fileContent = personFile.readText()

                personFile.delete()

                val userNameFile = File(context, U_NAME_FILE)
                var oldUserName = userNameFile.readLines().toString()
                oldUserName = oldUserName.substring(1, oldUserName.length - 1)

                val keyPair: String = RSA.generateKeys()
                Log.d(MainActivity.TAG, "after RSA")
                val pubKey = RSA.getPublicKey(keyPair)
                Log.d(MainActivity.TAG, "Public Key: $pubKey")
                val prvKey = RSA.getPrivateKey(keyPair)
                Log.d(MainActivity.TAG, "Private Key: $prvKey")

                val ownPublisher = OwnPublisher(userNameString, pubKey, prvKey)
                val ownFeed = OwnFeed(mutableListOf(), ownPublisher)
                ownFeed.createNewFeed(oldUserName, fileContent, context)
                personFile.createNewFile()
                val text = pubKey.plus(" ").plus(prvKey)
                personFile.writeText(text)

                Log.d(TAG, "User name was accepted")
                file.delete()
                Log.d(TAG, "Original file was deleted")
                file.writeText(userNameString)
                Log.d(TAG, "Written to file: $userNameString")
                val cacheListGenerator = CacheListGenerator()
                cacheListGenerator.getCacheListFileContent(context)

                binding.userNameErrorText.text = ""

                // Go back to original screen
                /*
                val context = applicationContext
                var intent = Intent(context, MainActivity::class.java)
                intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
                context.startActivity(intent)
                */
                finish()
            }
        }
    }

    /**
     * Closes keyboard when enter is pressed
     */
    private fun handleKeyEvent(view: View, keyCode: Int): Boolean {
        if (keyCode == KeyEvent.KEYCODE_ENTER) {
            // Hide the keyboard
            val inputMethodManager =
                getSystemService(Context.INPUT_METHOD_SERVICE) as InputMethodManager
            inputMethodManager.hideSoftInputFromWindow(view.windowToken, 0)
            return true
        }
        return false
    }

}
