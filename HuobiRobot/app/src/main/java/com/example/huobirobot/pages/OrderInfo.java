package com.example.huobirobot.pages;

import android.content.Context;
import android.graphics.Color;
import android.os.Build;
import android.os.Handler;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.ListView;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.annotation.RequiresApi;
import androidx.core.content.ContextCompat;

import com.example.huobirobot.MainActivity;
import com.example.huobirobot.R;

import org.json.JSONArray;
import org.json.JSONObject;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.Timer;
import java.util.TimerTask;

public class OrderInfo {
    private static int SEND_CODE = 0;
    private static int GET_CODE = 1;
    public Button order_trade = null;
    public Button order_pender = null;
    private MainActivity mainActivity = null;


    Timer timer = new Timer();                    //创建一个定时器对象
    TimerTask task = null;



    public String robot_id;
    public OrderInfo(MainActivity mainActivity) {
        this.mainActivity = mainActivity;
    }

    public void Shift(String robot_id) {
        this.robot_id = robot_id;
        mainActivity.setContentView(R.layout.activity_order);
        order_trade = mainActivity.findViewById(R.id.order_trade);
        order_pender = mainActivity.findViewById(R.id.order_pender);

        order_trade.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                getTradeOrdersInfo(robot_id);
                order_trade.setBackground(ContextCompat.getDrawable(mainActivity, R.drawable.balck_stroke));
                order_pender.setBackground(ContextCompat.getDrawable(mainActivity, R.drawable.white_stroke));
                stopFlush();
            }
        });

        order_pender.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                getPenderOrdersInfo(robot_id);
                order_trade.setBackground(ContextCompat.getDrawable(mainActivity, R.drawable.white_stroke));
                order_pender.setBackground(ContextCompat.getDrawable(mainActivity, R.drawable.balck_stroke));
                startFlush();
            }
        });
        order_pender.callOnClick();

    }

    public void startFlush(){
        if(task == null){
            task = new TimerTask(){
                @Override
                public void run()
                {
                    try
                    {
                        getPenderOrdersInfo(robot_id);
                    }catch (Exception e)
                    {
                        e.printStackTrace();
                    }
                }
            };
        }else {
            return;
        }
        timer.purge();
        timer.schedule(task,0,5000);                //启动定时器

    }

    public void stopFlush(){
        if (task == null){
            return;
        }
        task.cancel();
        task = null;
    }

    public void getTradeOrdersInfo(String robot_id) {
        IntnetThread intnetThread = new IntnetThread();
        intnetThread.setMainActivity(mainActivity, MainActivity.State.ORDERS_TRADE_INFO);
        String[] attributes = {"robot_id"};
        String[] values = {robot_id};
        intnetThread.setParameter(attributes, values);
        intnetThread.setUrl("/api/get_trade_order_info");
        intnetThread.start();
    }

    public void getPenderOrdersInfo(String robot_id) {
        IntnetThread intnetThread = new IntnetThread();
        intnetThread.setMainActivity(mainActivity, MainActivity.State.ORDERS_PENDER_INFO);
        String[] attributes = {"robot_id"};
        String[] values = {robot_id};
        intnetThread.setParameter(attributes, values);
        intnetThread.setUrl("/api/get_pender_order_info");
        intnetThread.start();
    }


    public void displayTradeOrder(JSONObject jsonObject) {

        try {

            LayoutInflater inflater = LayoutInflater.from(this.mainActivity);
            LinearLayout order_content = mainActivity.findViewById(R.id.order_content);
            View order_view = (LinearLayout) inflater.inflate(R.layout.trade_order, null);
            ViewGroup.LayoutParams layoutParams = order_content.getLayoutParams();
            order_view.setLayoutParams(layoutParams);
            order_content.removeAllViews();
            order_content.addView(order_view);


            if (jsonObject.getInt("trade_count") != 0) {
                JSONArray infoList = jsonObject.getJSONArray("trade_data");
                List<Content> tradeContentList = new ArrayList<>();
                for (int i = 0; i < infoList.length(); i++) {
                    JSONObject unitObject = infoList.getJSONObject(i);
                    Content content = new Content(unitObject);
                    tradeContentList.add(content);
                }
                ListView tradeTable = (ListView) mainActivity.findViewById(R.id.order_trade_table);
                TradeContentAdapter adapter = new TradeContentAdapter(mainActivity, R.layout.trade_order_list, tradeContentList);
                tradeTable.setAdapter(adapter);
            }

        } catch (Exception e) {
            System.out.println(e.getMessage());
        }
    }

    public void displayPenderOrder(JSONObject jsonObject) {

        try {
            LayoutInflater inflater = LayoutInflater.from(this.mainActivity);
            LinearLayout order_content = mainActivity.findViewById(R.id.order_content);
            View order_view = (LinearLayout) inflater.inflate(R.layout.pender_order, null);
            ViewGroup.LayoutParams layoutParams = order_content.getLayoutParams();
            order_view.setLayoutParams(layoutParams);
            order_content.removeAllViews();
            order_content.addView(order_view);

            String per_invest = jsonObject.getString("per_invest");
            String currency_price = jsonObject.getString("currency_price");
            TextView order_price_view = mainActivity.findViewById(R.id.oreder_price);
            TextView oreder_grid = mainActivity.findViewById(R.id.oreder_grid);
            order_price_view.setText("当前价格: "+currency_price);
            oreder_grid.setText("每格买卖: " + per_invest);

            if (jsonObject.getInt("pender_count") != 0) {
                JSONArray infoList = jsonObject.getJSONArray("pender_data");
                List<Content> penderContentBuyList = new ArrayList<>();
                List<Content> penderContentSellList = new ArrayList<>();
                for (int i = 0; i < infoList.length(); i++) {
                    JSONObject unitObject = infoList.getJSONObject(i);
                    Content content = new Content(unitObject);

                    if (unitObject.getString("order_type").compareTo("买入") == 0) {
                        penderContentBuyList.add(content);
                    } else {
                        penderContentSellList.add(content);
                    }
                }
                ListView penderBuyTable = (ListView) mainActivity.findViewById(R.id.pender_order_buy);
                ListView penderSellTable = (ListView) mainActivity.findViewById(R.id.pender_order_sell);

                PenderContentAdapter buyAdapter = new PenderContentAdapter(mainActivity, R.layout.pender_order_list, penderContentBuyList);
                PenderContentAdapter sellAdapter = new PenderContentAdapter(mainActivity, R.layout.pender_order_list, penderContentSellList);

                penderBuyTable.setAdapter(buyAdapter);
                penderSellTable.setAdapter(sellAdapter);
            }

        } catch (Exception e) {
            System.out.println(e.getMessage());
        }
    }


    private class Content {

        private JSONObject data;

        public Content(JSONObject data) {
            this.data = data;
        }

        public JSONObject getData() {
            return data;
        }
    }

    private class PenderContentAdapter extends ArrayAdapter<Content> {

        private int recourceId;

        public PenderContentAdapter(Context context, int resource, List<Content> objects) {
            super(context, resource, objects);
            recourceId = resource;
        }

        @NonNull
        @Override
        public View getView(int position, @Nullable View convertView, @NonNull ViewGroup parent) {
            Content marketContent = getItem(position); //得到集合中指定位置的一组数据，并且实例化
            LayoutInflater inflater = LayoutInflater.from(mainActivity);
            View view = inflater.inflate(R.layout.pender_order_list, null, false);//用布局裁剪器(又叫布局膨胀器)，将导入的布局裁剪并且放入到当前布局中
            JSONObject unitObject = marketContent.getData();
            try {
                String order_price = unitObject.getString("order_price");
                String order_rate = unitObject.getString("order_rate");


                TextView pender_order_rate = (TextView) view.findViewById(R.id.pender_order_rate);
                TextView pender_order_price = (TextView) view.findViewById(R.id.pender_order_price);
                TextView order_rank = (TextView) view.findViewById(R.id.order_rank);




                if (unitObject.getString("order_type").compareTo("买入") == 0) {
                    pender_order_rate.setTextColor(Color.RED);
                    order_rank.setTextColor(Color.RED);
                    pender_order_price.setTextColor(Color.RED);
                } else {
                    pender_order_rate.setTextColor(Color.GREEN);
                    order_rank.setTextColor(Color.GREEN);
                    pender_order_price.setTextColor(Color.GREEN);
                }


                pender_order_rate.setText(order_rate+ "%");
                pender_order_price.setText(order_price);
                order_rank.setText(String.valueOf(position + 1));

            } catch (Exception e) {
                mainActivity.showMessage(e.getMessage());
            }

            return view;
        }


    }

    private class TradeContentAdapter extends ArrayAdapter<Content> {

        private int recourceId;

        public TradeContentAdapter(Context context, int resource, List<Content> objects) {
            super(context, resource, objects);
            recourceId = resource;
        }

        @NonNull
        @Override
        public View getView(int position, @Nullable View convertView, @NonNull ViewGroup parent) {
            Content tradeContent = getItem(position); //得到集合中指定位置的一组数据，并且实例化
            LayoutInflater inflater = LayoutInflater.from(mainActivity);
            View view = inflater.inflate(R.layout.trade_order_list, null, false);//用布局裁剪器(又叫布局膨胀器)，将导入的布局裁剪并且放入到当前布局中
            JSONObject unitObject = tradeContent.getData();
            try {
                String order_time = unitObject.getString("order_time");
                String order_status = unitObject.getString("order_status");
                String sell_time = unitObject.getString("sell_time");
                String sell_price = unitObject.getString("sell_price");
                String sell_transfee = unitObject.getString("sell_transfee");
                String sell_amount = unitObject.getString("sell_amount");
                String buy_time = unitObject.getString("buy_time");
                String buy_price = unitObject.getString("buy_price");
                String buy_transfee = unitObject.getString("buy_transfee");
                String buy_amount = unitObject.getString("buy_amount");



                TextView trade_order_time = (TextView) view.findViewById(R.id.trade_order_time);
                TextView trade_order_status = (TextView) view.findViewById(R.id.trade_order_status);
                TextView trade_sell_time = (TextView) view.findViewById(R.id.trade_sell_time);
                TextView trade_sell_price = (TextView) view.findViewById(R.id.trade_sell_price);
                TextView trade_sell_transfee = (TextView) view.findViewById(R.id.trade_sell_transfee);
                TextView trade_sell_amount = (TextView) view.findViewById(R.id.trade_sell_amount);
                TextView trade_buy_time = (TextView) view.findViewById(R.id.trade_buy_time);
                TextView trade_buy_price = (TextView) view.findViewById(R.id.trade_buy_price);
                TextView trade_buy_transfee = (TextView) view.findViewById(R.id.trade_buy_transfee);
                TextView trade_buy_amount = (TextView) view.findViewById(R.id.trade_buy_amount);

                trade_order_time.setText(order_time);
                trade_order_status.setText(order_status);
                trade_sell_time.setText(sell_time);
                trade_sell_price.setText(sell_price);
                trade_sell_transfee.setText(sell_transfee);
                trade_sell_amount.setText(sell_amount);
                trade_buy_time.setText(buy_time);
                trade_buy_price.setText(buy_price);
                trade_buy_transfee.setText(buy_transfee);
                trade_buy_amount.setText(buy_amount);


                LinearLayout trade_order_info = view.findViewById(R.id.trader_order_info);
                trade_order_info.setVisibility(View.INVISIBLE);
                Button trader_order_extend = (Button) view.findViewById(R.id.trade_order_extend);

                trader_order_extend.setOnClickListener(new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        if (trade_order_info.getVisibility() == View.VISIBLE) {
                            trade_order_info.setVisibility(View.INVISIBLE);
                        } else {
                            trade_order_info.setVisibility(View.VISIBLE);
                        }
                    }
                });

            } catch (Exception e) {
                mainActivity.showMessage(e.getMessage());
            }

            return view;
        }
    }

}

