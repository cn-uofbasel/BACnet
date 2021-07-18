package com.example.p2pgeocaching.caches

/** Contains the list of caches of the device
 * Is updated upon file transfer via bluetooth
 */
class CacheList(var list: MutableList<Cache>) {


    /**
     * This function checks if the provided caches are already in the list.
     * If yes, it checks if the hallOfFame has any differences.
     * If not, adds it to the list.
     */
    fun add(caches: List<Cache>) {
        for (newCache in caches) {

            // Set to true if the object of the new caches is already in the list (meaning it does
            // not have to be added again)
            var isInList = false

            // Now we look at all caches in the list
            list.forEach {

                // The cache is already on the device. We will potentially add people to the
                // hallOfFame
                if (it.id == newCache.id) {
                    isInList = true
                    newCache.addPeopleToHOF(it.hallOfFame)
                }
            }

            // if the cache is not already in the list, add it
            if (!isInList) {
                list.add(newCache)
            }
        }
    }


    /**
     * Simple function to use add with a single cache.
     */
    fun add(cache: Cache) {
        this.add(listOf(cache))
    }


    /**
     * This function finds the [Cache] with the [idToFind] in the [CacheList] and returns it.
     */
    fun findByID(idToFind: Int): Cache? {
        for (cache in this.list) {
            if (cache.id == idToFind) {
                return cache
            }
        }
        return null
    }

    /**
     * This function removes the [Cache] in the [CacheList] that matches the [idToRemove],
     * if it exists.
     */
    fun removeCacheByID(idToRemove: Int) {
        var i = -1
        for ((index, cache) in this.list.withIndex()) {
            if (cache.id == idToRemove) {
                i = index
            }
        }

        // Removal is outside of loop to avoid ConcurrentModificationException
        if (i != -1) {
            this.list.removeAt(i)
        }
    }

}