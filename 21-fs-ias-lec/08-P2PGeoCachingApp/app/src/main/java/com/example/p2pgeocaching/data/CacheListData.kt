package com.example.p2pgeocaching.data

import java.io.Serializable

/**
 * This class is used to store CacheLists as data.
 */
@kotlinx.serialization.Serializable
data class CacheListData(val dataList: List<CacheData>) : Serializable