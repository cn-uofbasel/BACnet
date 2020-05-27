package ch.bacnet.qrlink;

import androidx.appcompat.app.AppCompatActivity;

import android.Manifest;
import android.app.Dialog;
import android.content.Intent;
import android.graphics.Bitmap;
import android.media.AudioManager;
import android.media.ToneGenerator;
import android.os.Bundle;
import android.os.FileUtils;
import android.util.Base64;
import android.util.Log;
import android.view.Window;
import android.widget.ImageView;
import android.widget.Toast;

import com.chaquo.python.PyObject;
import com.chaquo.python.Python;
import com.chaquo.python.android.AndroidPlatform;
import com.google.zxing.BarcodeFormat;
import com.google.zxing.MultiFormatWriter;
import com.google.zxing.Result;
import com.google.zxing.WriterException;
import com.google.zxing.common.BitMatrix;

import ch.bacnet.qrlink.R;
import io.reactivex.functions.Consumer;
import me.dm7.barcodescanner.zxing.ZXingScannerView;

import com.gun0912.tedpermission.TedPermissionResult;
import com.journeyapps.barcodescanner.BarcodeEncoder;
import com.tedpark.tedpermission.rx2.TedRx2Permission;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.util.Arrays;

//MainActivity.resultTextView.setText(result.getText()); // TODO: implement this for finished msg
public class ScanCodeActivity extends AppCompatActivity implements ZXingScannerView.ResultHandler {

    ZXingScannerView scannerView;
    ToneGenerator toneGenerator;
    Dialog qrPopupDialog;
    ImageView popupImageView;
    int qrSize;

    Python py;
    PyObject transport;
    String dirName;

    int cameraID;

    private char device;

    private String path;

    private int PACKETSIZE;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        getCameraPermission();
        cameraID = 1;
        scannerView = new ZXingScannerView(this);
        setContentView(scannerView);

        Intent intent = getIntent();
        this.device = intent.getCharExtra("device", 'Z');
        this.PACKETSIZE = intent.getIntExtra("packetsize", 12);


        Log.d("ScanCodeActivity", "Started as device " + device);

        toneGenerator = new ToneGenerator(AudioManager.STREAM_ALARM, 40);

        qrPopupDialog = new Dialog(this);
        qrPopupDialog.getWindow().requestFeature(Window.FEATURE_NO_TITLE);
        qrPopupDialog.setContentView(getLayoutInflater().inflate(R.layout.image_layout, null));
        qrPopupDialog.setCanceledOnTouchOutside(false);
        qrPopupDialog.show();

        popupImageView = qrPopupDialog.findViewById(R.id.popupImageView);

        qrSize = getResources().getDisplayMetrics().widthPixels;

        /*
        synchronized (shouldReceiveMonitor) {
            shouldReceive = false;
        }

        synchronized (shouldUpdateQRMonitor) {
            shouldUpdateQR = false;
        }

        wholeInput = new byte[0];
         */

        dirName = "/";

        init();
    }

    private void init() {
        // Initialize Python
        initializePython();
        Log.d("ScanCodeActivity", "Python initialized.");

        // Setup Path
        //initializePath();
        //Log.d("ScanCodeActivity", "Path initialized.");

        // initialize QR code:
        initializeQRCode();

        // Start synchronizer thread
        //SynchronizerThread synchronizer = new SynchronizerThread();
        //synchronizer.start();
    }

    /**
     * Synchronizes Database from device A to device B.
     *  Steps:
     *      1: A sending i_have_list to B
     *      2: B sending i_want_list to A
     *      3: A sending event_list to B
     */
    /*
    class SynchronizerThread extends Thread {

        @Override
        public void run() {
            output = new byte[PACKETSIZE];
            input = new byte[PACKETSIZE];
            if (device == 'A') {
                // Get i_have_list
                PyObject i_have_list_py = transport.callAttr("get_i_have_list", path);
                Log.d("ScanCodeActivity", "i_have_list: " + i_have_list_py);

                byte[] i_have_list = pyObject2ByteArray(i_have_list_py);
                Log.d("ScanCodeActivity", "i_have_list: " + Arrays.toString(i_have_list));
                Log.d("ScanCodeActivity", "i_have_list length: " + i_have_list.length);

                //// Step 1: Send i_have_list to B ////
                sendPacketAsSubPackets(i_have_list);

                //// Step 2: Receive i_want_list from B ////
                receivePacketAsSubPackets();

                // Handle i_want_list
                byte[] i_want_list;
                synchronized (shouldReceiveMonitor) {
                    i_want_list = wholeInput;
                    wholeInput = new byte[0];
                }
                PyObject i_want_list_py = byteArray2PyObject(i_want_list);
                PyObject event_list_py = transport.callAttr("get_event_list", i_want_list_py, path);
                byte[] event_list = pyObject2ByteArray(event_list_py);

                //// Step 3: Send event_list to B ////
                sendPacketAsSubPackets(event_list);

                Log.i("ScanCodeActivity", "Synchronization complete. Please wait for Device B to finish!");



            } else if (device == 'B') {

                //// Step 1: Receive i_have_list from A ////
                receivePacketAsSubPackets();
                Log.d("ScanCodeActivity", "Finished receiving i_have_list.");

                // Process i_have_list
                byte[] i_want_list;
                PyObject extension_list_py;
                synchronized (shouldReceiveMonitor) {
                    if (wholeInput==null) throw new AssertionError("lastReceived must not be null!");
                    byte[] i_have_list = wholeInput;
                    Log.d("ScanCodeActivity", "Received i_have_list is: " + Arrays.toString(i_have_list));
                    PyObject i_have_list_py = byteArray2PyObject(i_have_list);
                    PyObject i_want_list_and_extension_list = transport.callAttr("get_i_want_list", i_have_list_py, path);
                    PyObject i_want_list_py = i_want_list_and_extension_list.asList().get(0);
                    i_want_list = pyObject2ByteArray(i_want_list_py);
                    extension_list_py = i_want_list_and_extension_list.asList().get(1);
                    wholeInput = new byte[0];
                }
                Log.d("ScanCodeActivity", "Finished processing i_have_list.");
                Log.d("ScanCodeActivity", "Got i_want_list: " + Arrays.toString(i_want_list));
                Log.d("ScanCodeActivity", "Got extension_list_py: " + extension_list_py);

                //// Step 2: Send i_want_list to A ////
                sendPacketAsSubPackets(i_want_list);

                //// Step 3: Receive event_list from A ////
                receivePacketAsSubPackets();

                // Read event_list
                synchronized (shouldReceiveMonitor) {
                    byte[] event_list = wholeInput;
                    PyObject event_list_py = byteArray2PyObject(event_list);
                    transport.callAttr("sync_extensions", extension_list_py, event_list_py, path);
                }

                toneGenerator.startTone(AudioManager.STREAM_ALARM, 1500);

                Log.i("ScanCodeActivity", "Synchronization complete. You may exit both Apps now.");

                //onBackPressed();
            } else {
                throw new IllegalArgumentException("Device should be 'A' or 'B'.");
            }

        }

    }
     */


    private void initializePython() {
        // Start Python
        if (! Python.isStarted()) {
            Python.start(new AndroidPlatform(this));
        }

        // Get python instance
        py = Python.getInstance();
        Log.d("ScanCodeActivity", "py is: " + py);

        // Python equivalent to
        //  "import transport"
        transport = py.getModule("logSync.database_transport");
        Log.d("ScanCodeActivity", "transport is: " + transport);
        Log.d("ScanCodeActivity", "transport KEYSET: " + transport.keySet());
        // transport KEYSET:
        // [__builtins__, __cached__, __doc__, __file__, __loader__, __name__, __package__,
        // __spec__, cbor, get_event_list, get_i_have_list, get_i_want_list, pcap, sync]
    }


    private void initializePath() {
        // TODO: Set appropriate path:
        // data/data/com.chaquo.python.console/files

        //path = getApplicationContext().getFilesDir().getPath();
        if (!path.substring(path.lastIndexOf("/")+1).equals("files")) {
            path += "/files";
        }
        if (path.charAt(path.length()-1) != '/') { path += '/'; }
        path += dirName;

        File f = new File(path);
        Log.d("ScanCodeActivity", "Path: " + path);
        if (!f.exists())
            Log.d("ScanCodeActivity", "Created Path: " + path);
        f.mkdirs();

        /*
        File f = new File(path);
        if (!f.exists()) {
            f.mkdirs();
            Log.d("ScanCodeActivity", "Created new directory: " + path);
        }
         */

        File[] files = f.listFiles();
        for (File inFile : files) {
            Log.d("ScanCodeActivity", "File in path: " + inFile);
        }
    }

    private void initializeQRCode() {
        if (device == 'A') {
            // TODO: implement this
            // Get i_have_list
            i_have_list = get_i_have_list();
            outputPacket = i_have_list;
            Log.d("ScanCodeActivity (initializeQRCode)", "i_have_list to send: " + Arrays.toString(i_have_list));

            numSubpackets = getNumSubpackets(i_have_list);
            arrayInQR = getSubpacket(i_have_list, 0);
            i++;
            setByteArrayToPopupImageView(arrayInQR);

        }
    }


    /**
     * Synchronize Database from device A to device B.
     *  Steps:
     *      1: A sending i_have_list to B
     *      2: B sending i_want_list to A
     *      3: A sending event_list to B
     */
    byte[] inputSubpacket = new byte[0];
    byte[] inputPacket = new byte[0];
    byte[] outputSubpacket = new byte[0];
    byte[] outputPacket = new byte[0];
    byte[] arrayInQR = new byte[0];
    PyObject extension_list_py;

    // Only needed for readability, they're aliases in code below
    byte[] i_have_list;
    byte[] i_want_list;
    byte[] event_list;

    int i = 0;
    int step = 1;
    int numSubpackets;

    public void handleResult(Result result) {

        onPause();
        // Verify that QR code is new.
        if (Arrays.equals(inputSubpacket, decodeResult(result))) {
            Log.d("ScanCodeActivity (handleResult)", "Already received this packet: " + Arrays.toString(inputPacket));
            toneGenerator.startTone(AudioManager.STREAM_NOTIFICATION, 50);
            onResume();
            return;
        }

        toneGenerator.startTone(AudioManager.STREAM_ALARM, 50);
        inputSubpacket = decodeResult(result);

        Log.d("ScanCodeActivity (handleResult)", "Start handling new result: " + Arrays.toString(inputSubpacket));
        boolean last = inputSubpacket[0] != 0;


        if (device == 'A') {
            switch (step) {
                case 1:  // Send i_have_list to B
                    outputSubpacket = getSubpacket(outputPacket, i);
                    setByteArrayToPopupImageView(outputSubpacket);

                    Log.d("ScanCodeActivity (handleResult)", "Create i_have_list-packet to send (" + (i+1) + "/" + numSubpackets + "): " + Arrays.toString(outputSubpacket));

                    i++;
                    if (i >= numSubpackets) {
                        step++;
                        i = 0;
                        inputPacket = new byte[0];
                    }


                    break;
                case 2:  // Receive i_want_list from B
                    inputPacket = arraySmartConcat(inputPacket, inputSubpacket);

                    if (!last) {
                        setByteArrayToPopupImageView(inputSubpacket);
                    } else {  // last i_want_list-packet received
                        Log.d("ScanCodeActivity (handleResult)", "i_want_list received: " + Arrays.toString(inputPacket));

                        event_list = get_event_list(inputPacket);
                        Log.d("ScanCodeActivity (handleResult)", "event_list to send: " + Arrays.toString(event_list));

                        outputPacket = event_list;
                        numSubpackets = getNumSubpackets(outputPacket);
                        outputSubpacket = getSubpacket(outputPacket, 0);
                        setByteArrayToPopupImageView(outputSubpacket);
                        i = 1;
                        step++;
                    }

                    break;
                case 3:  // Send event_list to B
                    outputSubpacket = getSubpacket(event_list, i);
                    setByteArrayToPopupImageView(outputSubpacket);

                    i++;
                    if (i >= numSubpackets) {
                        step++;
                        i = 0;
                        inputPacket = new byte[0];
                    }
                    break;
            }
        } else if (device == 'B') {
            switch (step) {
                case 1:  // Receive i_have_list from A
                    inputPacket = arraySmartConcat(inputPacket, inputSubpacket);

                    if (!last) {
                        setByteArrayToPopupImageView(inputSubpacket);
                    } else {  // last i_have_list subpacket received

                        Log.d("ScanCodeActivity (handleResult)", "i_have_list received: " + Arrays.toString(inputPacket));
                        i_want_list = get_i_want_list(inputPacket);
                        outputPacket = i_want_list;
                        Log.d("ScanCodeActivity (handleResult)", "i_want_list to send: " + Arrays.toString(outputPacket));
                        numSubpackets = getNumSubpackets(outputPacket);
                        outputSubpacket = getSubpacket(outputPacket, 0);
                        setByteArrayToPopupImageView(outputSubpacket);
                        i = 1;

                        step++;
                    }
                    break;
                case 2:  // Send i_want_list to A
                    outputSubpacket = getSubpacket(i_want_list, i);
                    setByteArrayToPopupImageView(outputSubpacket);

                    i++;
                    if (i >= numSubpackets) {
                        step++;
                        i = 0;
                        inputPacket = new byte[0];
                    }
                    break;
                case 3:  // Receive event_list from A
                    inputPacket = arraySmartConcat(inputPacket, inputSubpacket);

                    if (!last) {
                        setByteArrayToPopupImageView(inputSubpacket);
                    } else {
                        // Sync extension
                        Log.d("ScanCodeActivity (handleResult): ", "event_list received: " + Arrays.toString(inputPacket));
                        event_list = inputPacket;
                        sync_extensions(event_list);
                        toneGenerator.startTone(AudioManager.STREAM_ALARM, 2000);
                        onBackPressed();
                    }
                    break;
            }
        } else {
            throw new IllegalArgumentException("Device should be 'A' or 'B'.");
        }
        Log.d("ScanCodeActivity (handleResult)", "Finished handling result.");

        if (!qrPopupDialog.isShowing()) {
            qrPopupDialog.show();
        }

        onResume();
    }

    private byte[] getSubpacket(byte[] wholeArray, int i) {
        boolean last = (i+1)*(PACKETSIZE-1) >= wholeArray.length;
        Log.d("ScanCodeActivity (getSubpacket)", "Trying to get subpacket of " + Arrays.toString(wholeArray));
        Log.d("ScanCodeActivity (getSubpacket)", "i: " + i);
        byte[] subpacket;
        if (!last) {
            System.arraycopy(wholeArray, i * (PACKETSIZE-1), subpacket=new byte[PACKETSIZE], 1, PACKETSIZE - 1);
        } else {
            System.arraycopy(wholeArray, i * (PACKETSIZE-1), subpacket=new byte[wholeArray.length % (PACKETSIZE - 1)+1], 1, wholeArray.length % (PACKETSIZE - 1));
            subpacket[0] = (byte)1;
        }
        Log.d("ScanCodeActivity (getSubpacket)", "Calculated subpacket: " + Arrays.toString(subpacket));
        return subpacket;
    }

    private byte[] decodeResult(Result result) {
        return Base64.decode(result.getText(), Base64.DEFAULT);
    }

    private byte[] arraySmartConcat(byte[] original, byte[] add) {
        Log.d("ScanCodeActivity (arraySmartConcat)", "Adding " + Arrays.toString(add));
        Log.d("ScanCodeActivity (arraySmartConcat)", "to " + Arrays.toString(original));
        if (add.length == 1) {
            return original;
        }
        original = Arrays.copyOf(original, original.length + add.length-1);
        System.arraycopy(add, 1, original, original.length - (add.length-1), add.length-1);
        Log.d("ScanCodeActivity (arraySmartConcat)", "Result: " + Arrays.toString(original));
        return original;
    }

    private byte[] get_i_have_list() {
        // TODO: remove Attr
        PyObject i_have_list_py = transport.callAttr("get_i_have_list", "WOLOLOO");
        Log.d("ScanCodeActivity", "i_have_list: " + i_have_list_py);

        byte[] i_have_list_out = pyObject2ByteArray(i_have_list_py);
        Log.d("ScanCodeActivity", "i_have_list: " + Arrays.toString(i_have_list_out));
        Log.d("ScanCodeActivity", "i_have_list length: " + i_have_list_out.length);

        return i_have_list_out;
    }

    private byte[] get_i_want_list(byte[] i_have_list) {
        PyObject i_have_list_py = byteArray2PyObject(i_have_list);
        PyObject i_want_list_and_extension_list = transport.call("get_i_want_list", i_have_list_py);
        PyObject i_want_list_py = i_want_list_and_extension_list.asList().get(0);
        i_want_list = pyObject2ByteArray(i_want_list_py);
        extension_list_py = i_want_list_and_extension_list.asList().get(1);
        return i_want_list;
    }

    private byte[] get_event_list(byte[] i_want_list) {
        PyObject i_want_list_py = byteArray2PyObject(i_want_list);
        PyObject event_list_py = transport.call("get_event_list", i_want_list_py);
        event_list = pyObject2ByteArray(event_list_py);
        return event_list;
    }

    private void sync_extensions(byte[] event_list) {
        PyObject event_list_py = byteArray2PyObject(event_list);
        transport.callAttr("sync_extensions", extension_list_py, event_list_py);
    }

    private int getNumSubpackets(byte[] arr) {
        return (arr.length / (PACKETSIZE-1)) + 1;
    }

    private void getCameraPermission() {

        TedRx2Permission.with(this)
                .setRationaleTitle("Camera permission")
                .setRationaleMessage("We need permission to use the camera in order to sync over QR.") // "we need permission for read contact and find your location"
                .setPermissions(Manifest.permission.CAMERA)
                .request()
                .subscribe(new Consumer<TedPermissionResult>() {
                    @Override
                    public void accept(TedPermissionResult tedPermissionResult) throws Exception {
                        if (tedPermissionResult.isGranted()) {
                            Toast.makeText(ScanCodeActivity.this, "Camera Permission Granted", Toast.LENGTH_SHORT).show();
                        } else {
                            Toast.makeText(ScanCodeActivity.this,
                                    "Camera Permission Denied\n" + tedPermissionResult.getDeniedPermissions().toString(), Toast.LENGTH_SHORT)
                                    .show();
                        }
                    }
                }, new Consumer<Throwable>() {
                    @Override
                    public void accept(Throwable throwable) throws Exception {
                    }
                });
    }

    /*
    @Override
    public void handleResult(Result result) {


        synchronized (shouldReceiveMonitor) {
            if (SEND) {
                // TODO: implement this

            } else { // RECV
                // TODO: implement this
            }

            // Update QR code if needed
            synchronized (shouldUpdateQRMonitor) {
                if (shouldUpdateQR) {
                    shouldUpdateQR = false;
                    setByteArrayToPopupImageView(setToQR);
                    //setToQR = null;
                }
            }

            // Handle QR code result
            synchronized (shouldReceiveMonitor) {
                Log.d("ScanCodeActivity (handleResult)", "shouldReceive: " + shouldReceive);
                if (shouldReceive) {
                    byte[] nowReceived = Base64.decode(result.getText(), Base64.DEFAULT);

                    if (nowReceived.length == 1)
                        Log.d("ScanCodeActivity (handleResult)", "Received empty message.");

                    Log.d("ScanCodeActivity (handleResult)", "nowReceived: " + Arrays.toString(nowReceived));
                    Log.d("ScanCodeActivity (handleResult)", "lastReceived" + Arrays.toString(lastReceived));

                    // Check if scanned code has already been scanned
                    if (!Arrays.equals(nowReceived, lastReceived)) {
                        Log.d("ScanCodeActivity (handleResult)", "nowReceived is different from lastReceived.");
                        shouldReceive = false;
                        lastReceived = nowReceived;

                        //setByteArrayToPopupImageView(lastReceived);
                        toneGenerator.startTone(AudioManager.STREAM_ALARM, 50);
                        //playBeep(100);
                        shouldReceiveMonitor.notifyAll();
                    } else {
                        Log.d("ScanCodeActivity (handleResult)", "Read same qr code as before.");
                        toneGenerator.startTone(AudioManager.STREAM_NOTIFICATION, 50);
                    }

                    // FIXME: Where do I have to be?
                    //if (lastReceived == output) {
                    //    Log.d("ScanCodeActivity (handleResult)", "lastReceived == output == " + Arrays.toString(output));
                    //    shouldReceiveMonitor.notifyAll();
                    //}
                }
            }


            try {
                if (!qrPopupDialog.isShowing()) {
                    qrPopupDialog.show();
                }
            } catch (Exception e) {
                Log.e("ScanCodeActivity (handleResult)", "Seems like there was an error when trying to show qr popup dialog.");
                e.printStackTrace();
            }
        }

        onPause();
        onResume();
    }
    */


    private static byte[] pyObject2ByteArray(PyObject o) {
        return o.toJava(byte[].class);
    }

    private PyObject byteArray2PyObject(byte[] array) {
        return transport.callAttr("get_bytes_from_tojava_pyobject", PyObject.fromJava(array));
    }

    private int setByteArrayToPopupImageView(byte[] binaryData) {
        MultiFormatWriter multiFormatWriter = new MultiFormatWriter();
        try {
            String base64Text = Base64.encodeToString(binaryData, Base64.DEFAULT);
            Log.d("ScanCodeActivity", "Writing following base64Text to QR code view: " + base64Text);
            Log.d("ScanCodeActivity", "Writing following bytearray to QR code view: " + Arrays.toString(binaryData));
            BitMatrix bitMatrix = multiFormatWriter.encode(base64Text, BarcodeFormat.QR_CODE, qrSize, qrSize);
            BarcodeEncoder barcodeEncoder = new BarcodeEncoder();
            Bitmap bitmap = barcodeEncoder.createBitmap(bitMatrix);
            popupImageView.setImageBitmap(bitmap);
        } catch (WriterException e) {
            e.printStackTrace();
            return -1;
        }
        return 0;
    }

    /*
    private void sendPacketAsSubPackets(byte[] arrayToSend) {
        int numSubPackets = (arrayToSend.length / (PACKETSIZE-1)) + 1;
        Log.d("ScanCodeActivity", "numSubPackets: " + numSubPackets);
        for (int i = 0; i < numSubPackets; i++) {

            boolean last = false;
            if (i == numSubPackets-1) {
                last = true;
            }

            // Create subPacket of i_have_list
            output = new byte[PACKETSIZE];

            if (!last) {
                System.arraycopy(arrayToSend, i * (PACKETSIZE-1), output=new byte[PACKETSIZE], 1, PACKETSIZE - 1);
                output[0] = (byte)0;
            } else {
                System.arraycopy(arrayToSend, i * (PACKETSIZE-1), output=new byte[arrayToSend.length % (PACKETSIZE - 1)+1], 1, arrayToSend.length % (PACKETSIZE - 1));
                output[0] = (byte)1;
            }
            Log.d("ScanCodeActivity", "Create packet to send (" + (i+1) + "/" + numSubPackets + "): " + Arrays.toString(output));

            // Set output
            //Log.d("ScanCodeActivity", "output: " + Arrays.toString(output));
            setToQR = output;
            synchronized (shouldUpdateQRMonitor) {
                shouldUpdateQR = true;
            }

            Log.d("ScanCodeActivity", "Wait for receiving Acknowledgement...");
            if (!last) {
                synchronized (shouldReceiveMonitor) {
                    shouldReceive = true;
                    try {
                        shouldReceiveMonitor.wait();
                    } catch (InterruptedException e) {
                        e.printStackTrace();
                    }
                }
            }
            Log.d("ScanCodeActivity", "Received Acknowledgement.");
        }
        Log.d("ScanCodeActivity", "Finished sending packet: " + Arrays.toString(arrayToSend));
    }
     */
    /**
     * Once finished, the received packet is saved in wholeInput.
     */
    /*
    private void receivePacketAsSubPackets() {
        Log.d("ScanCodeActivity (receivePacketAsSubPackets)", "Start receiving a packet as subpackets.");
        synchronized (shouldReceiveMonitor) {
            while (true) {
                // Start accepting QR codes
                shouldReceive = true;

                // Wait for scanner to get a packet (i_have_list).
                try {
                    shouldReceiveMonitor.wait();
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }

                // Concatenate lastReceived into wholeInput
                Log.d("ScanCodeActivity (receivePacketAsSubPackets)", "new lastReceived: " + Arrays.toString(lastReceived));
                Log.d("ScanCodeActivity (receivePacketAsSubPackets)", "wholeInput before concat: " + Arrays.toString(wholeInput));
                wholeInput = Arrays.copyOf(wholeInput, wholeInput.length + lastReceived.length-1);
                System.arraycopy(lastReceived, 1, wholeInput, wholeInput.length - (lastReceived.length-1), lastReceived.length-1);
                Log.d("ScanCodeActivity (receivePacketAsSubPackets)", "wholeInput after concat: " + Arrays.toString(wholeInput));

                // if 'last' flag is 1 break
                if (lastReceived[0] != 0) {
                    Log.d("ScanCodeActivity (receivePacketAsSubPackets)", "Whole input received:" + Arrays.toString(wholeInput));
                    break;
                } else {
                    synchronized (shouldUpdateQRMonitor) {
                        shouldUpdateQR = true;
                        setToQR = lastReceived;
                    }
                }
            }
        }
        Log.d("ScanCodeActivity (receivePacketAsSubPackets)", "Exit receiving subpackets. Packet complete.");
    }
    */

    private void playBeep(int playLengthInMilliseconds, int pauseLengthInMilliseconds) {
        playBeep(playLengthInMilliseconds);
        try {
            Thread.sleep(pauseLengthInMilliseconds);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
    }

    private void playBeep(int playLengthInMilliseconds) {
        toneGenerator.startTone(ToneGenerator.TONE_CDMA_ALERT_CALL_GUARD);
        try {
            Thread.sleep(playLengthInMilliseconds);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        toneGenerator.stopTone();
    }

    @Override
    protected void onPause() {
        super.onPause();

        scannerView.stopCamera();
    }

    @Override
    protected void onResume() {
        super.onResume();

        scannerView.setResultHandler(this);
        scannerView.startCamera(cameraID);
    }
    /*
    // CALLBACKS
    public byte[] rd_callback() { // called when logSync wants to receive
        lastReceived = null;
        shouldReceive = true;
        while (true) {
            if (lastReceived != null) {
                return lastReceived;
            }
        }
        //return "TestString".getBytes(StandardCharsets.UTF_8);
    }

    // Returns 0 if successful.
    // Returns -1 if error occured.
    public int wr_callback(byte[] binData) {  // called when logSync wants to send

        int errCode = setBase64ToPopupImageView(binData);
        return errCode;
    }*/


    //// THIS SECTION IS FOR DEV TESTING PURPOSES ONLY ////

    // Return a string of a certain bytesize.
    // 1 char (utf-16) needs 2 bytes.
    private String getStringOfByteSize(int size, int code) {
        // Must have: size >= 1


        char[] chars = new char[size-1];
        Arrays.fill(chars, 'a');
        //chars[chars.length-1] = (char) code;
        String text = new String(chars) + code;

        //Log.d("ScanCodeActivity", "whole object: " + text);
        //Log.d("ScanCodeActivity", "utf-8: " + text.getBytes(StandardCharsets.UTF_8));
        //Log.d("ScanCodeActivity", "utf-16: " + text.getBytes(StandardCharsets.UTF_16));
        //Log.d("ScanCodeActivity", "byteSize: " + text.getBytes(StandardCharsets.UTF_8).length);
        //Log.d("ScanCodeActivity", "code: " + text.charAt(size-1));
        return text;
    }

    /*

    private String handleResultByCounting(String text) {
        int num = Integer.parseInt(text);
        String outText = (num+1)+"";

        for (int i = 0; i < num; i++) {
            playBeep(100, 100);
        }

        if (num >= 10) {
            playBeep(1000, 0);
            onBackPressed();
        }
        return outText;
    }

    private String handleResultByCountingInLargePackets(String text) {
        int num = text.charAt(text.length()-1);
        String outTextLargePacket = text;
        if (num>lastNum) {
            lastNum = num;
            //String outText = (num+1)+"";
            outTextLargePacket = getStringOfByteSize(text.length(), num + 1);

            for (int i = 0; i < 2; i++) {
                playBeep(900, 100);
            }

            if (num >= 8) {
                playBeep(5000, 0);
                MainActivity.resultTextView.setText("Done!");
                onBackPressed();
            }
        } else {
            playBeep(2900,100);
        }
        return outTextLargePacket;
    }

    private String handleResultByCountingInDatabase(String text) {
        int num = text.charAt(text.length()-1);
        String outTextLargePacket = text;
        if (num>lastNum) {
            lastNum = num;
            //String outText = (num+1)+"";
            outTextLargePacket = getStringOfByteSize(text.length(), num + 1);

            for (int i = 0; i < 2; i++) {
                playBeep(900, 100);
            }

            if (num >= 8) {
                playBeep(5000, 0);
                MainActivity.resultTextView.setText("Done!");
                onBackPressed();
            }
        } else {
            playBeep(2900,100);
        }
        return outTextLargePacket;
    }


    private void setTextToPopupImageView(String text) {
        // Initially copied from:
        // https://medium.com/@aanandshekharroy/generate-barcode-in-android-app-using-zxing-64c076a5d83a
        MultiFormatWriter multiFormatWriter = new MultiFormatWriter();
        try {
            BitMatrix bitMatrix = multiFormatWriter.encode(text, BarcodeFormat.QR_CODE, qrSize, qrSize);
            //bitMatrix.rotate180();
            BarcodeEncoder barcodeEncoder = new BarcodeEncoder();
            Bitmap bitmap = barcodeEncoder.createBitmap(bitMatrix);
            //MainActivity.qrImageView.setImageBitmap(bitmap);
            popupImageView.setImageBitmap(bitmap);
        } catch (WriterException e) {
            e.printStackTrace();
        }
    }

    protected void switchCamera() {
        onPause();
        cameraID = (cameraID+1)%2;
        onResume();
    }

    protected void switchCameraToFrontcam() {
        onPause();
        cameraID = 1;
        onResume();
    }

    protected void switchCameraToBackcam() {
        onPause();
        cameraID = 0;
        onResume();
    }

     */

    ///////////////////////////////////////////////////////
}
