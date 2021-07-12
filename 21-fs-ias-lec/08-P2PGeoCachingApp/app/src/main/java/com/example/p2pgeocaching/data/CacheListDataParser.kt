package com.example.p2pgeocaching.data

import com.example.p2pgeocaching.caches.Cache
import com.example.p2pgeocaching.caches.CacheList

/**
 * This class is used to transform data to [CacheList] and vice versa.
 */
class CacheListDataParser {

    companion object {

        /**
         * Returns a [CacheList] when given a [CacheListData].
         */
        fun dataToList(data: CacheListData): CacheList {
            val list = mutableListOf<Cache>()
            data.dataList.forEach {
                list.add(CacheDataParser.dataToCache(it))
            }
            return CacheList(list)
        }


        /**
         * Creates a [CacheListData] when given a [CacheList].
         */
        fun listToData(cacheList: CacheList): CacheListData {
            val newList = mutableListOf<CacheData>()
            cacheList.list.forEach {
                newList.add(CacheDataParser.cacheToData(it))
            }
            return CacheListData(newList)
        }
    }
}