package com.example.p2pgeocaching.ownbacnet

/**
 * Publisher is the owner of a [Feed]. They are uniquely identified through their [publicKey].
 * They will sign the [Entry]s in their feed with their own private key, verifying their identity.
 */
open class Publisher(val name: String, val publicKey: String) {

    // TODO: Can be done in future to get a better overview. At the moment, the publisher
    // is created through the personData file and Username file

}