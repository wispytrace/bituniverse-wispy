package com.example.huobirobot.pages;

import android.os.Message;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;

import com.example.huobirobot.MainActivity;
import com.example.huobirobot.R;

import org.json.JSONObject;

public class GetLog {
    private MainActivity mainActivity = null;

    TextView log = null;
    public GetLog(MainActivity mainActivity){this.mainActivity = mainActivity;}

    public void Shift(){

        mainActivity.setContentView(R.layout.activity_log);
        log = mainActivity.findViewById(R.id.log);
        getLog();

    }


    public void getLog(){
        IntnetThread intnetThread = new IntnetThread();
        intnetThread.setMainActivity(mainActivity, MainActivity.State.LOG_INFO);
        intnetThread.setUrl("/api/get_log");
        intnetThread.start();
    }


    public void freshLog(JSONObject jsonObject) throws Exception{
        log.setText(jsonObject.getString("data"));
    }


}

