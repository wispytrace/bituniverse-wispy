package com.example.huobirobot.pages;

import android.util.Log;

import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.net.URLEncoder;

public class GetData {
    // 定义一个获取网络图片数据的方法:
    public static byte[] readStream(InputStream inStream) throws Exception{
        ByteArrayOutputStream outStream = new ByteArrayOutputStream();
        byte[] buffer = new byte[1024];
        int len = 0;
        while((len = inStream.read(buffer)) != -1)
        {
            outStream.write(buffer,0,len);
        }
        inStream.close();
        return outStream.toByteArray();
    }
    public static byte[] getImage(String path) throws Exception {
        URL url = new URL(path);
        HttpURLConnection conn = (HttpURLConnection) url.openConnection();
        // 设置连接超时为5秒
        conn.setConnectTimeout(5000);
        // 设置请求类型为Get类型
        conn.setRequestMethod("GET");
        // 判断请求Url是否成功
        if (conn.getResponseCode() != 200) {
            throw new RuntimeException("请求url失败");
        }
        InputStream inStream = conn.getInputStream();
        byte[] bt = readStream(inStream);
        inStream.close();
        return bt;
    }

    // 获取网页的html源代码
    public static String getHtml(String path) throws Exception {
        URL url = new URL(path);
        HttpURLConnection conn = (HttpURLConnection) url.openConnection();
        conn.setConnectTimeout(5000);
        conn.setRequestMethod("GET");
        if (conn.getResponseCode() == 200) {
            InputStream in = conn.getInputStream();
            byte[] data = readStream(in);
            String html = new String(data, "UTF-8");
            return html;
        }
        return null;
    }
    public static String postHtml(String path, String[] atrribute, String[] value) throws Exception{

        URL url = new URL(path);
        HttpURLConnection conn = (HttpURLConnection) url.openConnection();
        conn.setConnectTimeout(5000);
        conn.setDoInput(true);
        conn.setDoOutput(true);
        conn.setUseCaches(false);
        String postData = URLEncoder.encode(atrribute[0], "UTF-8") + "=" + URLEncoder.encode(value[0], "UTF-8");
        for (int i = 1; i < atrribute.length; i++) {
            postData += "&" + URLEncoder.encode(atrribute[i], "UTF-8") + "=" + URLEncoder.encode(value[i], "UTF-8");
        }
        Log.e("lou", url.toString() + postData);
        conn.setRequestMethod("POST");

        OutputStream out = conn.getOutputStream();
        out.write(postData.getBytes());
        out.flush();
        if (conn.getResponseCode() == 200) {
            InputStream in = conn.getInputStream();
            byte[] data = readStream(in);
            String html = new String(data, "UTF-8");
            return html;
        }
        else {
            throw new Exception("网络连接失败!");
        }
    }
}