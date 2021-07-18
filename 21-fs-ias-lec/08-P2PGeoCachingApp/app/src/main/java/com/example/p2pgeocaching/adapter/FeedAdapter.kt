package com.example.p2pgeocaching.adapter

import android.content.Intent
import android.os.Build
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.view.accessibility.AccessibilityNodeInfo
import android.widget.Button
import androidx.annotation.RequiresApi
import androidx.recyclerview.widget.RecyclerView
import com.example.p2pgeocaching.R
import com.example.p2pgeocaching.activities.FeedDetailViewActivity
import com.example.p2pgeocaching.constants.Constants.Companion.FEED_NAME

/**
 * This class servers as the link between the recyclerView in FeedActivity and the list of Feeds.
 */
class FeedAdapter(val feedNameList: List<String>) :
    RecyclerView.Adapter<FeedAdapter.FeedViewHolder>() {

    /**
     * Contains reference on how to display the items in the list
     */
    class FeedViewHolder(val view: View) : RecyclerView.ViewHolder(view) {
        val button: Button = view.findViewById(R.id.feed_list_item)
    }

    /**
     * Returns the number of items in the list
     */
    override fun getItemCount(): Int {
        return feedNameList.size
    }

    /**
     * Creates a new view with R.layout.item_view as its layout
     */
    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): FeedAdapter.FeedViewHolder {
        val layout = LayoutInflater
            .from(parent.context)
            .inflate(R.layout.feed_list_item, parent, false)

        // Setup custom accessibility delegate to set the text read
        layout.accessibilityDelegate = CacheAdapter
        return FeedAdapter.FeedViewHolder(layout)
    }

    /**
     * Replaces the content of an existing view with new data
     */
    override fun onBindViewHolder(holder: FeedAdapter.FeedViewHolder, position: Int) {

        // Saves the string to item in the button
        val item: String = feedNameList[position]

        // give the button a name
        holder.button.text = item

        // What to do when clicked
        holder.button.setOnClickListener {
            val context = holder.view.context

            // Set intent, put the name as extra
            val intent = Intent(context, FeedDetailViewActivity::class.java)
            intent.putExtra(FEED_NAME, item)

            // Start DetailActivity
            context.startActivity(intent)
        }
    }

    // Setup custom accessibility delegate to set the text read with
    // an accessibility service
    companion object Accessibility : View.AccessibilityDelegate() {
        @RequiresApi(Build.VERSION_CODES.LOLLIPOP)
        override fun onInitializeAccessibilityNodeInfo(
            host: View?,
            info: AccessibilityNodeInfo?
        ) {
            super.onInitializeAccessibilityNodeInfo(host, info)
            // With `null` as the second argument to [AccessibilityAction], the
            // accessibility service announces "double tap to activate".
            // If a custom string is provided,
            // it announces "double tap to <custom string>".
            val customString = host?.context?.getString(R.string.look_up_cache_detail)
            val customClick =
                AccessibilityNodeInfo.AccessibilityAction(
                    AccessibilityNodeInfo.ACTION_CLICK,
                    customString
                )
            info?.addAction(customClick)
        }
    }
}