package ch.bacnet.qrlink;

import androidx.appcompat.app.AppCompatActivity;

import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;

import ch.bacnet.qrlink.R;

public class MainActivity extends AppCompatActivity {

    Button scanButtonA;
    Button scanButtonB;


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        scanButtonA = (Button) findViewById(R.id.btn_scan_A);
        scanButtonB = (Button) findViewById(R.id.btn_scan_B);


        String environmentPath = android.os.Environment.getDataDirectory().getAbsolutePath();
        final String pathToChaquoPythonFiles = environmentPath + "/data/com.chaquo.python.console/files";

        //Log.d("MainActivity", "Absolute path until now: " + getApplicationContext().getFilesDir().getPath());
        //Log.d("MainActivity", "Absolute path for chaquo: " + pathToChaquoPythonFiles);


        scanButtonA.setOnClickListener(new View.OnClickListener()  {
            @Override
            public void onClick(View view) {
                Intent startScannerIntent = new Intent(getApplicationContext(), ScanCodeActivity.class);

                //startScannerIntent.putExtra("path", pathToChaquoPythonFiles);
                startScannerIntent.putExtra("device", 'A');
                startScannerIntent.putExtra("packetsize", 12);

                startActivity(startScannerIntent);
            }
        });


        scanButtonB.setOnClickListener(new View.OnClickListener()  {
            @Override
            public void onClick(View view) {

                Intent startScannerIntent = new Intent(getApplicationContext(), ScanCodeActivity.class);

                startScannerIntent.putExtra("path", getApplicationContext().getFilesDir().getPath());
                startScannerIntent.putExtra("device", 'B');
                startScannerIntent.putExtra("packetsize", 12);

                startActivity(startScannerIntent);
            }
        });

    }
}
