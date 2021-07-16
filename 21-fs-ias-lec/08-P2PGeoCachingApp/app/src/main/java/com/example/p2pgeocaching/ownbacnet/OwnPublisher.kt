package com.example.p2pgeocaching.ownbacnet

import android.util.Log
import com.example.p2pgeocaching.RSA.RSA

/**
 * This is a subclass of [Publisher]. This one also has a [privateKey] to sign [Entry]s with.
 */
class OwnPublisher(name: String, publicKey: String, val privateKey: String) :
    Publisher(name, publicKey) {

    companion object {
        const val TAG = "OwnPublisher"
    }

    fun getSalt(): String {
        val list = publicKey.split('_')
        val n = list[1]
        val salt = n.takeLast(4)
        Log.d(TAG, "salt of Publisher:\n$salt")
        return salt
    }

    //*
    fun getSaltOfOldPublisher(key: String): String {
        val list1 = key.split(" ")
        val pub = list1[0]
        val list2 = pub.split("_")
        val n = list2[1]
        val salt = n.takeLast(4)
        Log.d(TAG, "Old salt of Publisher:\n$salt")
        return salt
    }


    /**
     * Signs the [plainText] by hashing it and encrypting it with the [privateKey].
     */
    fun sign(plainText: String): String {
        return RSA.encode(plainText.hashCode().toString(), privateKey)
    }
}