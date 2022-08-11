package com.example.huobirobot.pages;

import android.os.Handler;
import android.os.Message;
import android.util.Log;

import com.example.huobirobot.MainActivity;

import org.json.JSONObject;

public class IntnetThread extends Thread{

    private String[] attributes = {""};

    private String[] values = {""};

    private String url = "";

    private MainActivity mainActivity;

    private MainActivity.State state;

    public void setParameter(String[] attributes, String[] values){
        this.values = new String[values.length];
        this.attributes = new String[attributes.length];
        for (int i = 0; i < attributes.length; i++){
            this.attributes[i] = attributes[i];
            this.values[i] = values[i];
        }
    }

    public void setUrl(String url){
        this.url = mainActivity.setUrl.ipUrl + url;
    }

    public void setMainActivity(MainActivity mainActivity, MainActivity.State state){
        this.mainActivity = mainActivity;
        this.state = state;
    }

    public void run() {
        try {
            String jsonStr = GetData.postHtml(url, attributes, values);
            Message message = new Message();
            JSONObject jsonMessage = new JSONObject(jsonStr);
            jsonMessage.put("state", state);
            message.obj = jsonMessage;
            mainActivity.myHander.sendMessage(message);

        } catch (Exception e) {
            Log.e("lou", e.getMessage());
            Message message = new Message();
            JSONObject jsonMessage = new JSONObject();
            try {
                jsonMessage.put("state", MainActivity.State.ERROR_STATE);
                jsonMessage.put("status", mainActivity.ERRO_CODE);
                jsonMessage.put("message", e.getMessage());
            }catch (Exception ej)
            {
                return;
            }
            message.obj = jsonMessage;
            mainActivity.myHander.sendMessage(message);
        }
    }
}
