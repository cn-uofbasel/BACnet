package com.example.p2pgeocaching.bluetooth

import android.bluetooth.BluetoothDevice
import android.content.Context
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ArrayAdapter
import android.widget.TextView
import com.example.p2pgeocaching.R

class BluetoothDeviceListAdapter (context: Context, val resource: Int, val devices: ArrayList<BluetoothDevice?>):
    ArrayAdapter<BluetoothDevice>(context, resource, devices){

    private val layoutInflater: LayoutInflater = context.getSystemService(Context.LAYOUT_INFLATER_SERVICE) as LayoutInflater

    override fun getView(position: Int, convertView: View?, parent: ViewGroup): View {
        val tempConvertView = layoutInflater.inflate(resource, parent, false)
        val device: BluetoothDevice? = devices[position]

        val deviceName: TextView = tempConvertView.findViewById(R.id.deviceName)
        val deviceAddress: TextView = tempConvertView.findViewById(R.id.deviceAddress)

        deviceName.text = device?.name
        deviceAddress.text = device?.address

        return tempConvertView
    }
}
