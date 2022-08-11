package com.example.huobirobot.pages;

import android.app.AlertDialog;
import android.app.DatePickerDialog;
import android.content.Context;
import android.content.DialogInterface;
import android.os.Message;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ImageView;
import android.widget.ListView;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import com.example.huobirobot.R;
import com.example.huobirobot.MainActivity;
import org.json.JSONArray;
import org.json.JSONObject;

import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.Reader;
import java.io.UnsupportedEncodingException;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.ArrayList;
import java.util.List;
import java.util.Random;

public class RobotInfo {

    private MainActivity mainActivity = null;

    private TextView balance_usdt = null;

    private Button add_robot = null;
    private Button get_log = null;
    private Button ip_modify = null;
    private Button back_login = null;

    int cancel_order_flag = 1;
    int cancel_currency_flag = 1;

    public RobotInfo(MainActivity mainActivity) {
        this.mainActivity = mainActivity;
    }

    public void Shift() {
        mainActivity.setContentView(R.layout.activity_main);
        balance_usdt = (TextView) mainActivity.findViewById(R.id.balance_usdt);
        add_robot = mainActivity.findViewById(R.id.add_robot);
        get_log = mainActivity.findViewById(R.id.get_log);
        ip_modify = mainActivity.findViewById(R.id.ip_modify);
        back_login = mainActivity.findViewById(R.id.back_login);

        add_robot.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                if(mainActivity.setUrl.currenct_api.compareTo("空")==0){
                    mainActivity.showMessage("暂未添加API, 添加机器人功能拒绝开放");
                    return;
                }

                mainActivity.showMessage("切换到添加机器人界面，请等待跳转.....");
                mainActivity.addRobot.Shift();
            }
        });

        get_log.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                mainActivity.showMessage("切换到日志查看界面，请等待跳转......");
                mainActivity.getLog.Shift();

            }
        });

        ip_modify.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                mainActivity.setUrl.Shift();
            }
        });

        back_login.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                mainActivity.login.Shift();
            }
        });

        getRobotInfo();

    }

    public void displayDialog(String robot_id) {

        final String[] items = new String[]{"终止后撤销未成交订单", "终止后自动兑换为投入币种"};

        AlertDialog.Builder builder = new AlertDialog.Builder(mainActivity);

        builder.setTitle("删除id为 " + robot_id + " 的交易机器人")

                .setMultiChoiceItems(items, //选项条

                        new boolean[]{true, true},// //这个參数必须是boolean[]的，不能使Boolean[]的，有几个item就数组长度几个，true为勾选，false则相反

                        new DialogInterface.OnMultiChoiceClickListener() {
                            @Override
                            public void onClick(DialogInterface dialog, int which, boolean isChecked) {
                                if (isChecked) {
                                    if (which == 0){
                                        cancel_order_flag = 1;
                                    }else {
                                        cancel_currency_flag = 1;
                                    }
                                    mainActivity.showMessage("启动" + items[which]);
                                }else {
                                    if (which == 0){
                                        cancel_order_flag = 0;
                                    }else {
                                        cancel_currency_flag = 0;
                                    }
                                    mainActivity.showMessage("取消" + items[which]);
                                }

                            }
                        })
                .setPositiveButton("确认", new DialogInterface.OnClickListener() {
                    @Override
                    public void onClick(DialogInterface dialog, int which) {
                        mainActivity.showMessage("命令执行中，请等待跳转......");
                        IntnetThread intnetThread = new IntnetThread();
                        String[] attributes = {"robot_id", "cancel_order", "cancel_currency"};
                        String[] values = {robot_id, String.valueOf(cancel_order_flag), String.valueOf(cancel_currency_flag)};
                        intnetThread.setParameter(attributes, values);
                        intnetThread.setMainActivity(mainActivity, MainActivity.State.ROBOT_MODIFY);
                        intnetThread.setUrl("/api/delet_robot");
                        intnetThread.start();
                    }
                })

                .setNegativeButton("取消", null);

        builder.create().show();

    }



    public void getRobotInfo() {

        if (mainActivity.setUrl.currenct_api.compareTo("空")==0){
            return;
        }
        IntnetThread intnetThread = new IntnetThread();
        String[] attributes = {"account_id"};
        String[] values = {mainActivity.setUrl.currenct_account};
        intnetThread.setParameter(attributes, values);
        intnetThread.setMainActivity(mainActivity, MainActivity.State.ROBOTS_INFO);
        intnetThread.setUrl("/api/get_robot_info");
        intnetThread.start();
    }


    public void refreshRobotInfo(JSONObject jsonObject) throws Exception {
        balance_usdt.setText("账户目前持有USDT: " + jsonObject.getString("balance"));
        ListView dreamTable = (ListView) mainActivity.findViewById(R.id.robot_info_table);
        if (jsonObject.getInt("count") == 0) {
            return;
        }

        JSONArray infoList = jsonObject.getJSONArray("data");

        List<RobotContent> RobotContentList = new ArrayList<>();
        for (int i = 0; i < infoList.length(); i++) {
            JSONObject unitObject = infoList.getJSONObject(i);
            RobotContent dreamContent = new RobotContent(unitObject);
            RobotContentList.add(dreamContent);
        }

        RobotContentAdapter adapter = new RobotContentAdapter(mainActivity, R.layout.robot_list, RobotContentList);
        dreamTable.setAdapter(adapter);
    }


    private class RobotContent {

        private JSONObject data;

        public RobotContent(JSONObject data) {
            this.data = data;
        }

        public JSONObject getData() {
            return data;
        }

    }

    private class RobotContentAdapter extends ArrayAdapter<RobotContent> {

        private int recourceId;

        public RobotContentAdapter(Context context, int resource, List<RobotContent> objects) {
            super(context, resource, objects);
            recourceId = resource;
        }

        @NonNull
        @Override
    /*
    为什么要重写getView？因为适配器中其实自带一个返回布局的方法，
    这个方法可以是自定义适配一行的布局显示，因为我们需要更复杂的布局内容，
    所以我们直接重写它，，不需要在导入一个简单的TextView或者ImageView布局让适配器在写入布局数据。
    所以在recourceId自定义布局id直接导入到getView里面，getView方法不在convertView中获取布局了。
    最后只要返回一个view布局就可以。
     */
        public View getView(int position, @Nullable View convertView, @NonNull ViewGroup parent) {
            RobotContent robotList = getItem(position); //得到集合中指定位置的一组数据，并且实例化
            LayoutInflater inflater = LayoutInflater.from(mainActivity);
            View view = inflater.inflate(R.layout.robot_list, null, false);//用布局裁剪器(又叫布局膨胀器)，将导入的布局裁剪并且放入到当前布局中
            JSONObject data = robotList.getData();
            try {
                String policy_type = data.getString("policy_type");
                String currency_type = data.getString("currency_type");
                String max_price = data.getString("max_price");
                String min_price = data.getString("min_price");
                String robot_id = data.getString("robot_id");
                String status = data.getString("status");
                String invested_num = data.getString("invested_num");
                String runtime = data.getString("runtime");
                String trade_num = data.getString("trade_num");
                String currency_price = data.getString("currency_price");
                String grid_num = data.getString("grid_num");
                String grid_per = data.getString("grid_per");
                String robot_profit = data.getString("robot_profit");
                String float_profit = data.getString("float_profit");
                String robot_profit_rate = data.getString("robot_profit_rate");
                String total_profit = data.getString("total_profit");
                String total_year_rate = data.getString("total_year_rate");
                String grid_profit_rate = data.getString("grid_profit_rate");
                String hold_num = data.getString("hold_num");

                TextView robot_policy = (TextView) view.findViewById(R.id.robot_policy);
                TextView robot_invese_num = (TextView) view.findViewById(R.id.robot_invese_num);
                TextView robot_profit_view = (TextView) view.findViewById(R.id.robot_profit);
                TextView float_profit_view = (TextView) view.findViewById(R.id.float_profit);
                TextView total_profit_view = (TextView) view.findViewById(R.id.total_profit);
                TextView robot_year_profit = (TextView) view.findViewById(R.id.robot_year_profit);
                TextView currency_now_price = (TextView) view.findViewById(R.id.currency_now_price);
                TextView robot_max_price = (TextView) view.findViewById(R.id.robot_max_price);
                TextView robot_min_price = (TextView) view.findViewById(R.id.robot_min_price);
                TextView robot_grid_num = (TextView) view.findViewById(R.id.robot_grid_num);
                TextView amount_per_grid = (TextView) view.findViewById(R.id.amount_per_grid);
                TextView robot_trade_num = (TextView) view.findViewById(R.id.robot_trade_num);
                TextView robot_run_time = (TextView) view.findViewById(R.id.robot_run_time);
                TextView robot_id_view = (TextView) view.findViewById(R.id.robot_id);
                TextView robot_status = (TextView) view.findViewById(R.id.robot_status);
                TextView robot_hold_num = (TextView) view.findViewById(R.id.robot_hold_num);
                TextView robot_grid_profit_rate = (TextView) view.findViewById(R.id.robot_grid_profit_rate);


                TextView robot_pause = (TextView) view.findViewById(R.id.robot_pause);
                TextView robot_delete = (TextView) view.findViewById(R.id.robot_delete);
                TextView robot_order_detail = (TextView) view.findViewById(R.id.robot_order_detail);
                TextView robot_update = (TextView) view.findViewById(R.id.robot_update);

                robot_policy.setText(policy_type + "( " + currency_type + " )");
                robot_invese_num.setText("已投资额: " + invested_num);
                robot_profit_view.setText("网格套利利润: " + robot_profit + "( " + robot_profit_rate + "% )");
                float_profit_view.setText("浮动利润: " + float_profit);
                total_profit_view.setText("总利润: " + total_profit);
                robot_year_profit.setText("年化收益率: " + total_year_rate + "%");
                currency_now_price.setText("当前价格: " + currency_price);
                robot_max_price.setText("最高价格: " + max_price);
                robot_min_price.setText("最低价格: " + min_price);
                robot_grid_num.setText("网格数量: " + grid_num);
                amount_per_grid.setText("每格买卖金额: " + grid_per);
                robot_trade_num.setText("交易次数: " + trade_num);
                robot_run_time.setText("运行时间: " + runtime);
                robot_id_view.setText("机器人id: " + robot_id);
                robot_status.setText("运行状态: " + status);
                robot_hold_num.setText("机器人持币量: " + hold_num);
                robot_grid_profit_rate.setText("单位网格利润: " + grid_profit_rate + "%");


                robot_pause.setOnClickListener(new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        mainActivity.showMessage("命令执行中，请等待跳转......");
                        IntnetThread intnetThread = new IntnetThread();
                        String[] attributes = {"robot_id"};
                        String[] values = {robot_id};
                        intnetThread.setParameter(attributes, values);
                        intnetThread.setMainActivity(mainActivity, MainActivity.State.ROBOT_MODIFY);
                        intnetThread.setUrl("/api/modify_status");
                        intnetThread.start();
                    }
                });

                robot_delete.setOnClickListener(new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        displayDialog(robot_id);
                    }
                });

                robot_update.setOnClickListener(new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        mainActivity.showMessage("切换到修改机器人信息界面，请等待跳转......");
                        mainActivity.updateRobot.Shift(robot_id, policy_type);
                    }
                });


                robot_order_detail.setOnClickListener(new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        mainActivity.showMessage("切换到获取订单详情界面，请等待跳转......");
                        mainActivity.orderInfo.Shift(robot_id);
                    }
                });

            } catch (Exception e) {
            }
            return view;
        }


    }
}
