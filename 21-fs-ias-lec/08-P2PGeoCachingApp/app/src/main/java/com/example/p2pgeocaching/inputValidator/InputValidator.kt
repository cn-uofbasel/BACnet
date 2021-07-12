package com.example.p2pgeocaching.inputValidator

import com.example.p2pgeocaching.p2pexceptions.KeyIsNotLegalException
import com.example.p2pgeocaching.p2pexceptions.StringContainsIllegalCharacterException

/**
 * This class is used to check if a list of strings or a single string contains characters which are not allowed.
 */
class InputValidator {

    companion object {
        private val userNameLegalCharacters: List<Char> = generateLegalCharactersForUserName()
        private val textIllegalCharacters: List<Char> = generateIllegalCharactersForText()


        /**
         * Simple function that checks if any of the Strings provided in [arguments] contains an illegal
         * character for user names.
         * If one does, throws a [StringContainsIllegalCharacterException].
         */
        fun checkUserNameForIllegalCharacters(arguments: List<String>) {
            // Checks for illegal characters in strings
            for (str in arguments) {
                for (char in str) {
                    if (char !in userNameLegalCharacters) {
                        throw StringContainsIllegalCharacterException()
                    }
                }
            }
        }


        /**
         * If only a single string is provided, casts it to array list and calls original function.
         */
        fun checkUserNameForIllegalCharacters(argument: String) {
            checkUserNameForIllegalCharacters(arrayListOf(argument))
        }


        /**
         * This function checks the Strings provided in [arguments] for any illegal characters.
         * If they do, throws [StringContainsIllegalCharacterException]
         */
        fun checkTextForIllegalCharacters(arguments: List<String>) {
            // Checks for illegal characters in strings
            for (str in arguments) {
                for (char in str) {
                    if (char in textIllegalCharacters) {
                        throw StringContainsIllegalCharacterException()
                    }
                }
            }
        }


        /**
         * This function is the same as checkTextForIllegalCharacters, except it can be called with
         * a single string instead of a list.
         */
        fun checkTextForIllegalCharacters(argument: String) {
            checkTextForIllegalCharacters(listOf(argument))
        }


        /**
         * This function takes a string and checks if it is a legal key.
         * Throws [KeyIsNotLegalException].
         * Keys have the shape of <number>_<number>.
         */
        fun checkKey(key: String) {
            var underScoreHasBeenEncountered = false
            for (char in key) {
                if (char.isDigit()) { // Skip

                } else if (char == '_') {

                    // No two underscores
                    if (underScoreHasBeenEncountered) {
                        throw KeyIsNotLegalException()
                    } else {
                        underScoreHasBeenEncountered = true
                    }

                } else { // Illegal character
                    throw KeyIsNotLegalException()
                }
            }

            // Exactly one underscore, cannot be last character
            if (key[key.lastIndex] == '_' || !underScoreHasBeenEncountered) {
                throw KeyIsNotLegalException()
            }
        }


        /**
         * This function generates a list of all the legal characters for user names and returns it.
         * The legal characters are the letters a-z, A-Z, <space>, and numbers 0-9.
         */
        private fun generateLegalCharactersForUserName(): List<Char> {
            // Create list with space character ' ' in it
            val listOfChars = mutableListOf(' ')

            // Add characters a-z
            var char = 'a'
            while (char <= 'z') {
                listOfChars.add(char)
                char++
            }

            // Add characters A-Z
            char = 'A'
            while (char <= 'Z') {
                listOfChars.add(char)
                char++
            }

            // Add numbers 0-9
            char = '0'
            while (char <= '9') {
                listOfChars.add(char)
                char++
            }

            // Return result
            return listOfChars
        }


        /**
         * This function generates a list of all the legal characters for text and returns it.
         * The legal characters are the letters a-z, A-Z, the numbers 0-9
         */
        private fun generateIllegalCharactersForText(): List<Char> {
            // Create list with some characters illegal in texts in it and return it
            return listOf('{', '}', ';')
        }
    }
}