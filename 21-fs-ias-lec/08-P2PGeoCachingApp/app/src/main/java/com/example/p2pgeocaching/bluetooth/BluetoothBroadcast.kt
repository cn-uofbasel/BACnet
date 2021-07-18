package com.example.p2pgeocaching.bluetooth

import android.bluetooth.BluetoothAdapter
import android.bluetooth.BluetoothDevice
import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.util.Log
import com.example.p2pgeocaching.R
import com.example.p2pgeocaching.activities.BluetoothTransferActivity

/**
 * This class notices all bluetooth related changes such as the current state of the adapter(on,off, etc.)
 */
class BluetoothBroadcast(
    private val bluetoothHandler: BluetoothHandler,
    val activity: BluetoothTransferActivity
): BroadcastReceiver() {

    companion object {
        const val TAG = "BluetoothBroadcast"
    }

    override fun onReceive(context: Context, intent: Intent) {
        when(intent.action) {
            BluetoothAdapter.ACTION_STATE_CHANGED -> {

                when (intent.getIntExtra(BluetoothAdapter.EXTRA_STATE, BluetoothAdapter.ERROR)) {
                    BluetoothAdapter.STATE_OFF -> {
                        Log.i(TAG, "STATE OFF")
                    }

                    BluetoothAdapter.STATE_TURNING_OFF -> {
                        Log.i(TAG, "STATE TURNING OFF")
                    }

                    BluetoothAdapter.STATE_ON -> {
                        Log.i(TAG, "STATE ON")
                    }

                    BluetoothAdapter.STATE_TURNING_ON -> {
                        Log.i(TAG, "STATE TURNING ON")
                    }
                }
            }

            BluetoothAdapter.ACTION_SCAN_MODE_CHANGED -> {

                when(intent.getIntExtra(BluetoothAdapter.EXTRA_SCAN_MODE, BluetoothAdapter.ERROR)) {
                    BluetoothAdapter.SCAN_MODE_CONNECTABLE_DISCOVERABLE -> {
                        Log.i(TAG, "Discoverability Enabled")
                    }

                    BluetoothAdapter.SCAN_MODE_CONNECTABLE -> {
                        Log.i(TAG, "Discoverability Disabled. Able to receive connections")
                    }

                    BluetoothAdapter.SCAN_MODE_NONE -> {
                        Log.i(TAG, "Discoverability Disabled. Not able to receive connections")
                    }

                    BluetoothAdapter.STATE_CONNECTING -> {
                        Log.i(TAG, "Connecting ...")
                    }

                    BluetoothAdapter.STATE_CONNECTED -> {
                        Log.i(TAG, "Connected.")
                    }
                }
            }

            BluetoothDevice.ACTION_FOUND -> {
                Log.i(TAG, "Action found device")
                val device: BluetoothDevice? = intent.getParcelableExtra(BluetoothDevice.EXTRA_DEVICE)
                println( "Device found: ${device?.name}:${device?.address}")
                if (!bluetoothHandler.devices.contains(device)) {
                    bluetoothHandler.devices.add(device)
                    bluetoothHandler.bluetoothDeviceListAdapter = BluetoothDeviceListAdapter(
                        context,
                        R.layout.device_adapter_view,
                        bluetoothHandler.devices
                    )
                    activity.listView.adapter = bluetoothHandler.bluetoothDeviceListAdapter
                }
            }

            BluetoothDevice.ACTION_BOND_STATE_CHANGED -> {
                val device: BluetoothDevice? = intent.getParcelableExtra(BluetoothDevice.EXTRA_DEVICE)

                when(device?.bondState) {
                    BluetoothDevice.BOND_BONDED -> {
                        Log.i(TAG, "BOND_BOONDED")
                        //activity.device = device
                    }

                    BluetoothDevice.BOND_BONDING -> {
                        Log.i(TAG, "BOND_BONDING")
                    }

                    BluetoothDevice.BOND_NONE -> {
                        Log.i(TAG, "BOND_NONE")
                    }
                }
            }


        }
    }
}