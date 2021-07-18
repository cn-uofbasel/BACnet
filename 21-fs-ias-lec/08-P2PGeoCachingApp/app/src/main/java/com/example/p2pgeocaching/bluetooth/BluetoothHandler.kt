package com.example.p2pgeocaching.bluetooth

import android.bluetooth.*
import android.content.Context
import android.util.Log
import android.widget.Toast
import com.example.p2pgeocaching.activities.BluetoothTransferActivity
import com.example.p2pgeocaching.constants.Constants.Companion.BUFFERSIZE
import com.example.p2pgeocaching.data.FeedData
import java.io.*
import java.math.BigInteger
import java.util.*

/**
 * This Class has all functions to connect to devices via Bluetooth
 */

class BluetoothHandler(
    val activity: BluetoothTransferActivity,
    manager: BluetoothManager,
    var applicationContext: Context
) {

    companion object {
        const val TAG = "BluetoothHandler"
    }

    var context: File = File("file")
    val bluetoothAdapter: BluetoothAdapter = manager.adapter

    private val appName: String = "P2P_Geocaching"
    private val uuid: UUID = UUID.fromString("708305f5-933b-40ad-b687-5b8ebfd8b5c6")

    private var serverSenderThread: SenderThread? = null  // Server
    private var clientReceiverThread: ReceiverThread? = null    // Client

    val state: BluetoothBroadcast = BluetoothBroadcast(this, activity)

    var devices: ArrayList<BluetoothDevice?> = ArrayList() // If you want to display the devices found
    lateinit var bluetoothDeviceListAdapter: BluetoothDeviceListAdapter


    /**
     * This method starts the serverThread and listens for incoming connections
     */
    fun startSender(c:  File) {
        Log.i(TAG, "Starting server thread and waiting for incoming connections ...")
        context = c
        serverSenderThread = SenderThread()
        serverSenderThread?.start()
    }

    /**
     * This method starts a clientThread and tries to connect with a server device
     */
    fun startReceiver(device: BluetoothDevice?, c: File) {
        Log.i(TAG, "Connecting Bluetooth ...")
        context = c
        clientReceiverThread = ReceiverThread(device)
        clientReceiverThread?.start()
    }

    /**
     * This method stops the connection by closing their sockets
     */
    fun stop() {
        clientReceiverThread?.cancel()
        serverSenderThread?.cancel()

        Log.i(TAG, "Bluetooth Handler closed all sockets")
    }

    /**
     * This inner class represents the server thread who accepts incoming connections
     */
    inner class SenderThread: Thread() {

        private val serverSocket: BluetoothServerSocket? =
            bluetoothAdapter.listenUsingInsecureRfcommWithServiceRecord(appName, uuid)
        private var socket: BluetoothSocket? = null

        override fun run() {

            while(true) {
                try {
                    Log.i(TAG, "Server is waiting in try block before accept before runOnUiThread")
                    if (serverSocket == null) {
                        Log.i(TAG, "Serversocket is null")
                    }
                    makeToast("waiting for incoming connection")
                    Log.i(TAG, "Server is waiting in try block before accept after runOnUiThread")

                    socket = serverSocket?.accept()

                    Log.i(TAG, "socket accepted")
                    makeToast("accepted an incoming connection")
                    val outputStream = socket?.outputStream
                    while(true) {
                        val fd = FeedData(context)
                        if (fd.stringFileContent.isNotEmpty()) {
                            Log.i(TAG, "feedToSend = " + fd.stringFileContent)
                            Log.i(TAG, "File to bytes, bytearraysize: " + fd.stringFileContent.length)
                            val charset = Charsets.UTF_8
                            val msgSplit =  fd.stringFileContent.chunked(BUFFERSIZE)
                            val splitSeq = msgSplit.size
                            Log.i(TAG, "chunks to send = $splitSeq ")
                            val sentSeq = BigInteger.valueOf(splitSeq.toLong()).toByteArray()
                            outputStream?.write(sentSeq) // Erste Nachricht an receiver ist Anzahl substring die er erhält
                            var counter = 0
                            while(counter < splitSeq) {
                                val bytes = msgSplit[counter].toByteArray(charset)
                                write(bytes, outputStream)
                                Log.i(TAG, "write bytes chunk = "+bytes.contentToString())
                                Log.i(TAG, "written bytes as String = " + bytes.toString(charset))
                                Log.i(TAG, "counter = $counter")
                                counter++
                            }

                            makeToast("feeds sent")
                            Log.i(TAG, "write bytes = "+fd.stringFileContent.toByteArray().contentToString())
                        }
                        serverSocket?.close()
                        makeToast("closed your socket")
                        Log.i(TAG, "close server")
                        break
                    }

                } catch (e: IOException) {
                    makeToast("can't accept connections")
                    makeToast("try again later")
                    Log.e(TAG, "Socket's accept() method failed")
                    break
                }
                break
            }
        }

        private fun write(bytes: ByteArray, outputStream: OutputStream?) {
            Log.i(TAG, "in write")
            try {
                outputStream?.write(bytes)
                Log.i(TAG, "write-socket write")
            } catch (e: IOException) {
                Log.e(TAG, "outputstream error", e)

            }
        }

        private fun makeToast(msg: String) {
            activity.runOnUiThread {
                Toast.makeText(applicationContext, msg, Toast.LENGTH_SHORT).show()
            }
            Log.e(TAG, "TOAST: $msg")
        }

        fun cancel() {
            try {
                serverSocket?.close()
                makeToast("closed your socket by cancel()")
            } catch (e: IOException) {
                Log.e(TAG, "Could not close the connect socket", e)
            }
        }
    }

    /**
     * This inner class represents the client thread who tries to connect to the server
     */
    inner class ReceiverThread(val device: BluetoothDevice?): Thread() {

        private val clientSocket: BluetoothSocket? = device?.createRfcommSocketToServiceRecord(uuid)
        private val buffer: ByteArray = ByteArray(BUFFERSIZE)

        override fun run() {
            Log.i(TAG, "ConnectThread: in run()")

            makeToast("waiting for connection")

            clientSocket?.connect()

            makeToast("connection accepted")
            Log.i(TAG, "run: ConnectThread connected.")
            val receivedFeedFile = File(context, "rcvFile")

            try {
                Log.i(TAG, "In try")

                makeToast("wait... you are receiving data")

                read(buffer, receivedFeedFile)

                makeToast("feed received")
                Log.i(TAG, "read File")
            } catch (e: IOException) {
                Log.e(TAG, "ConnectThread: inputstream error")
            }
            clientSocket?.close()
            makeToast("closed your socket")
        }

        private fun read(bytes: ByteArray, file: File) {
            Log.i(TAG, "Started read")
            var finalMsg = ""
            val inputStream = clientSocket?.inputStream
            val charset = Charsets.UTF_8

            val splitSeq = inputStream?.read() // Is this chunksize?
            Log.i(TAG, "splitSeq = $splitSeq")
            var counter = 0
            while(true) {
                while(counter < splitSeq!!) {
                    inputStream.read(bytes)
                    finalMsg += bytes.toString(charset)
                    Log.i(TAG, "Received bytes = ${bytes.toString(charset)}")
                    Log.i(TAG, "finalMsg = $finalMsg")
                    Log.i(TAG, "counter = $counter")
                    counter++
                }
                if(counter == splitSeq) {
                    break
                }
            }

            Log.i(TAG, "Inputstream $finalMsg")

            if (!file.exists()) {
                Log.i(TAG, "File doesn't exist")
                file.createNewFile()
                Log.i(TAG, "CreatedFile")
            } else {
                file.delete()
                file.createNewFile()
            }
            Log.i(TAG, "Going to write in File")
            file.writeText(finalMsg)
            Log.i(TAG, "Wrote to File = "+file.readText())
            FeedData(file, context)
            Log.i(TAG, "dataToFeed over")
        }

        private fun makeToast(msg: String) {
            activity.runOnUiThread {
                Toast.makeText(applicationContext, msg, Toast.LENGTH_SHORT).show()
            }
            Log.e(TAG, msg)
        }

        fun cancel() {
            try {
                clientSocket?.close()
                activity.runOnUiThread {
                    Log.i(TAG, "in runOnUiThread before Toast")
                    Toast.makeText(applicationContext, "closed your socket", Toast.LENGTH_SHORT).show()
                    Log.i(TAG, "in runOnUiThread after Toast")
                }
            } catch (e: IOException) {
                Log.e(TAG, "Could not close the client socket", e)
            }
        }
    }
}