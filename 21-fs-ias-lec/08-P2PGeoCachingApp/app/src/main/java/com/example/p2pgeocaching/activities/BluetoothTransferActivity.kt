package com.example.p2pgeocaching.activities

import android.Manifest
import android.app.AlertDialog
import android.bluetooth.BluetoothAdapter
import android.bluetooth.BluetoothDevice
import android.bluetooth.BluetoothManager
import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import android.content.pm.PackageManager
import android.os.Bundle
import android.util.Log
import android.view.View
import android.widget.AdapterView
import android.widget.ListView
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import com.example.p2pgeocaching.R
import com.example.p2pgeocaching.bluetooth.BluetoothDeviceListAdapter
import com.example.p2pgeocaching.bluetooth.BluetoothHandler
import com.example.p2pgeocaching.databinding.ActivityBluetoothTransferBinding


/**
 * This activity handles all bluetooth related things
 */
class BluetoothTransferActivity : AppCompatActivity() {

    companion object {
        const val TAG = "BluetoothTransferActivity"
    }

    lateinit var listView: ListView
    private lateinit var intentFilter: IntentFilter
    private lateinit var bluetoothHandler: BluetoothHandler
    var bluetoothActive = false

    private lateinit var binding: ActivityBluetoothTransferBinding

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        Log.i(TAG, "Transfer")

        title = "Transfer"

        binding = ActivityBluetoothTransferBinding.inflate(layoutInflater)
        setContentView(binding.root)

        listView = findViewById(R.id.device_list_view)

        val context = applicationContext

        if(!hasRequiredPermissions()){
            Log.i(TAG, "didn't have all required permissions!")
            ActivityCompat.requestPermissions(this, arrayOf(Manifest.permission.BLUETOOTH), PackageManager.PERMISSION_GRANTED)
            ActivityCompat.requestPermissions(this, arrayOf(Manifest.permission.BLUETOOTH_ADMIN), PackageManager.PERMISSION_GRANTED)
            ActivityCompat.requestPermissions(this, arrayOf(Manifest.permission.ACCESS_COARSE_LOCATION), PackageManager.PERMISSION_GRANTED)
            ActivityCompat.requestPermissions(this, arrayOf(Manifest.permission.ACCESS_FINE_LOCATION), PackageManager.PERMISSION_GRANTED)
        }

        val bluetoothManager: BluetoothManager = getSystemService(Context.BLUETOOTH_SERVICE) as BluetoothManager
        val bluetoothAdapter = bluetoothManager.adapter
        bluetoothHandler = BluetoothHandler(this, bluetoothManager, context)

        val deviceList = bluetoothAdapter.bondedDevices
        val devices = ArrayList<BluetoothDevice?>()
        devices.addAll(deviceList)
        bluetoothHandler.devices = devices
        Log.i(TAG,"deviceList implemented size = ${devices.size}")

        listView.adapter = BluetoothDeviceListAdapter(
            context,
            R.layout.device_adapter_view,
            devices
        )

        intentFilter = IntentFilter()
        intentFilter.apply {
            addAction(BluetoothAdapter.ACTION_STATE_CHANGED)
            addAction(BluetoothAdapter.ACTION_SCAN_MODE_CHANGED)
            addAction(BluetoothDevice.ACTION_FOUND)
            addAction(BluetoothDevice.ACTION_BOND_STATE_CHANGED)
        }


        if (bluetoothAdapter != null && !bluetoothAdapter.isEnabled) {
            val enableIntent = Intent(BluetoothAdapter.ACTION_REQUEST_ENABLE)
            startActivityForResult(enableIntent, 3)
        }


        // list with bonded devices including the one with the started sender (sender device has to be bonded)
        listView.setOnItemClickListener { _: AdapterView<*>, _: View, i: Int, _: Long ->
            Log.i(TAG, "You clicked on a device")
            val deviceName: String? = bluetoothHandler.devices[i]?.name
            val deviceAddress: String? = bluetoothHandler.devices[i]?.address
            Log.i(TAG, "You clicked on device: $deviceName, $deviceAddress")
            val device = bluetoothHandler.devices[i] // device?.address!!
            bluetoothHandler.startReceiver(device, context.filesDir)
        }

        // start server and listen for connections
        binding.sendBtn.setOnClickListener {
            bluetoothHandler.startSender(context.filesDir)
        }

        // close sockets
        binding.closeBtn.setOnClickListener {
            bluetoothHandler.stop()
        }
    }

    override fun onResume() {
        super.onResume()
        Log.i(TAG, "on Resume")
        registerReceiver(bluetoothHandler.state, intentFilter)
    }

    override fun onDestroy() {
        super.onDestroy()
        unregisterReceiver(bluetoothHandler.state)
        bluetoothHandler.stop()
    }

    private fun hasPermission(permission: String): Boolean {
        return ActivityCompat.checkSelfPermission(
            this,
            permission
        ) == PackageManager.PERMISSION_GRANTED
    }

    private fun hasRequiredPermissions(): Boolean {
        val hasBluetoothPermission: Boolean = hasPermission(Manifest.permission.BLUETOOTH)
        Log.i(TAG, "hasBluetoothPermission = $hasBluetoothPermission")
        val hasBluetoothAdminPermission: Boolean =
            hasPermission(Manifest.permission.BLUETOOTH_ADMIN)
        Log.i(TAG, "hasBluetoothAdminPermission = $hasBluetoothAdminPermission")
        val hasLocationPermission: Boolean =
            hasPermission(Manifest.permission.ACCESS_COARSE_LOCATION)
        Log.i(TAG, "hasLocationPermission = $hasLocationPermission")

        checkLocationPermission()   // inApp location permission request

        val hasFineLocationPermission: Boolean =
            hasPermission(Manifest.permission.ACCESS_FINE_LOCATION)
        Log.i(TAG, "hasFineLocationPermission = $hasFineLocationPermission")
        return hasBluetoothPermission && hasBluetoothAdminPermission && hasLocationPermission && hasFineLocationPermission
    }

    private fun checkLocationPermission() {
        if (ActivityCompat.checkSelfPermission(
                this,
                Manifest.permission.ACCESS_FINE_LOCATION
            ) != PackageManager.PERMISSION_GRANTED
        ) {
            // Should we show an explanation?
            if (ActivityCompat.shouldShowRequestPermissionRationale(
                    this,
                    Manifest.permission.ACCESS_FINE_LOCATION
                )
            ) {
                // Show an explanation to the user *asynchronously* -- don't block
                // this thread waiting for the user's response! After the user
                // sees the explanation, try again to request the permission.
                AlertDialog.Builder(this)
                    .setTitle("Location Permission Needed")
                    .setMessage("This app needs the Location permission, please accept to use location functionality")
                    .setPositiveButton(
                        "OK"
                    ) { _, _ ->
                        //Prompt the user once explanation has been shown
                        ActivityCompat.requestPermissions(
                            this,
                            arrayOf(
                                Manifest.permission.ACCESS_FINE_LOCATION,
                                Manifest.permission.ACCESS_BACKGROUND_LOCATION
                            ),
                            PackageManager.PERMISSION_GRANTED
                        )
                    }
                    .create()
                    .show()
            } else {
                // No explanation needed, we can request the permission.
                ActivityCompat.requestPermissions(this, arrayOf(Manifest.permission.ACCESS_FINE_LOCATION), PackageManager.PERMISSION_GRANTED)
            }
        }
    }
}


