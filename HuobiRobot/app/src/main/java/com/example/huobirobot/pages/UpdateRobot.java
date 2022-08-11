package com.example.huobirobot.pages;

import android.os.Message;
import android.text.Editable;
import android.text.TextWatcher;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.Spinner;
import android.widget.TextView;

import androidx.core.content.ContextCompat;

import com.example.huobirobot.MainActivity;
import com.example.huobirobot.R;

import org.json.JSONObject;

public class UpdateRobot {
    private MainActivity mainActivity = null;


    Spinner geometric_currency_type = null;
    TextView geometric_policy_max_price = null;
    TextView geometric_policy_min_price = null;
    TextView geometric_policy_grid_num = null;
    TextView geometric_policy_per_invest = null;
    Button geometric_policy_cancel = null;
    Button geometric_policy_confirm = null;

    Spinner infinite_policy_currency_type = null;
    TextView infinite_policy_min_price = null;
    TextView infinite_policy_max_price = null;
    TextView infinite_policy_sell_percent = null;
    TextView infinite_policy_buy_percent = null;
    TextView infinite_policy_per_invest = null;
    TextView infinite_policy_expect_money = null;

    Button infinite_policy_cancel = null;
    Button infinite_policy_confirm = null;


    Button display_robot_parameter = null;

    String currency_type = null;

    int select_robot = GEOMETRIC_CODE;

    double per_grid;
    double need_money;


    String robot_id;

    private static int GEOMETRIC_CODE = 0;
    private static int INFINITE_CODE = 1;

    private static int OK_PARAMETER = 0;
    private static int ERROR_PARAMETER = -1;

    public int isValidParameter = ERROR_PARAMETER;


    public UpdateRobot(MainActivity mainActivity) {
        this.mainActivity = mainActivity;
    }

    public void Shift(String robot_id, String policy_type) {
        mainActivity.setContentView(R.layout.activity_update_robot);
        this.robot_id = robot_id;
        display_robot_parameter = mainActivity.findViewById(R.id.update_robot_parameter_info);

        display_robot_parameter.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                getInvestParameter();
            }
        });

        if (policy_type.compareTo("等比网格机器人")==0){
            select_robot = GEOMETRIC_CODE;
            displayGeometric(robot_id);
        }else {
            select_robot = INFINITE_CODE;
            displayInfinite(robot_id);
        }

        getRobotParameter(robot_id);
        displayInfo();
        isValidParameter = ERROR_PARAMETER;

    }

    public void getRobotParameter(String robot_id){
        IntnetThread intnetThread = new IntnetThread();
        intnetThread.setMainActivity(mainActivity, MainActivity.State.GET_UPDATE_ROBOT_PARAMETER);
        intnetThread.setUrl("/api/get_robot_parameter");
        String[] attributes = {"robot_id"};
        String[] values = {robot_id};
        intnetThread.setParameter(attributes, values);
        intnetThread.start();
    }

    public void setRobotParameter(JSONObject jsonObject) throws Exception{
        jsonObject = jsonObject.getJSONObject("data");
        if(select_robot == GEOMETRIC_CODE){
            geometric_policy_max_price.setText(jsonObject.getString("max_price"));
            geometric_policy_min_price.setText(jsonObject.getString("min_price"));
            geometric_policy_grid_num.setText(jsonObject.getString("grid_num"));
            geometric_policy_per_invest.setText(jsonObject.getString("per_invest"));

            currency_type = jsonObject.getString("currency_type");
            int index = -1;
            for(int i = 0; i < mainActivity.setUrl.currency_type.length; i++) {
                if (mainActivity.setUrl.currency_type[i].compareTo(currency_type) == 0) {
                    index = i;
                }
                geometric_currency_type.setSelection(index);
            }

            }else{

            infinite_policy_max_price.setText(jsonObject.getString("max_price"));
            infinite_policy_min_price.setText(jsonObject.getString("min_price"));
            infinite_policy_buy_percent.setText(jsonObject.getString("buy_percent"));
            infinite_policy_sell_percent.setText(jsonObject.getString("sell_percent"));
            infinite_policy_per_invest.setText(jsonObject.getString("per_invest"));
            infinite_policy_expect_money.setText(jsonObject.getString("expect_money"));

            currency_type = jsonObject.getString("currency_type");
            int index = -1;
            for(int i = 0; i < mainActivity.setUrl.currency_type.length; i++) {
                if (mainActivity.setUrl.currency_type[i].compareTo(currency_type) == 0) {
                    index = i;
                }
                infinite_policy_currency_type.setSelection(index);
            }
            }


        }



    public void getInvestParameter() {
        IntnetThread intnetThread = new IntnetThread();
        intnetThread.setMainActivity(mainActivity, MainActivity.State.GET_INVEST_PARAMETER_UPDATE);
        intnetThread.setUrl("/api/get_invest_parameter");
        String[] attributes = {};
        String[] values = {};
        if (select_robot == GEOMETRIC_CODE) {
            attributes = new String[]{"robot_type", "currency_type", "max_price", "min_price", "grid_num", "per_invest", "account_id"};
            values = new String[]{Integer.toString(select_robot),geometric_currency_type.getSelectedItem().toString(), geometric_policy_max_price.getText().toString(),
                    geometric_policy_min_price.getText().toString(), geometric_policy_grid_num.getText().toString(),
                    geometric_policy_per_invest.getText().toString(), mainActivity.setUrl.currenct_account};
        } else if (select_robot == INFINITE_CODE) {
            attributes = new String[]{"robot_type", "currency_type", "sell_percent", "expect_money", "account_id"};
            values = new String[]{Integer.toString(select_robot),infinite_policy_currency_type.getSelectedItem().toString(), infinite_policy_sell_percent.getText().toString(),
                    infinite_policy_expect_money.getText().toString(), mainActivity.setUrl.currenct_account};
        }
        intnetThread.setParameter(attributes, values);
        intnetThread.start();
    }

    public void setInvestParameter(JSONObject jsonObject) throws Exception {
        isValidParameter = jsonObject.getInt("valid");
        if (isValidParameter != OK_PARAMETER){
            mainActivity.showMessage("参数设置错误");
            return;
        }
        jsonObject = jsonObject.getJSONObject("invest_data");
        double currency_price = jsonObject.getDouble("currency_price");
        double usdt_num = jsonObject.getDouble("usdt_num");
        double btc_num = jsonObject.getDouble("btc_num");
        double usdt_need = jsonObject.getDouble("usdt_need");
        double btc_need = jsonObject.getDouble("btc_need");

        per_grid = jsonObject.getDouble("per_grid");
        need_money = usdt_need + btc_need * currency_price;


        TextView parameter_price = mainActivity.findViewById(R.id.parameter_price);
        TextView parameter_avaible = mainActivity.findViewById(R.id.parameter_avaible);
        TextView parameter_per_grid = mainActivity.findViewById(R.id.parameter_per_grid);
        TextView parameter_need = mainActivity.findViewById(R.id.parameter_need);

        parameter_price.setText("当前价格:" + String.valueOf(currency_price));
        parameter_avaible.setText("可用usdt: "+String.valueOf(usdt_num)+ "\n可用btc: "+String.valueOf(btc_num));
        parameter_per_grid.setText("每格利润/%: "+String.valueOf(per_grid));
        parameter_need.setText("需要usdt: "+usdt_need+"\n需要btc: "+btc_need+"\n usdt总价值:"+need_money);
//        if (need_money > (usdt_num + btc_num*currency_price) || ((btc_need < btc_num) && (usdt_num < usdt_need))){
//            isValidParameter = ERROR_PARAMETER;
//            mainActivity.showMessage("参数设置错误, 需要的资金大于持有资金");
//            return;
//        }

    }


    public void displayGeometric(String robot_id) {
        LayoutInflater inflater = LayoutInflater.from(this.mainActivity);
        LinearLayout add_robot_content = mainActivity.findViewById(R.id.update_robot_content);
        View robot_view = (LinearLayout) inflater.inflate(R.layout.geometric_robot, null);
        ViewGroup.LayoutParams layoutParams = add_robot_content.getLayoutParams();
        robot_view.setLayoutParams(layoutParams);
        add_robot_content.removeAllViews();
        add_robot_content.addView(robot_view);


        Spinner spgeometric = mainActivity.findViewById(R.id.geometric_policy_currency_type);
        initSpinner(spgeometric);

        geometric_currency_type = mainActivity.findViewById(R.id.geometric_policy_currency_type);
        geometric_policy_max_price = mainActivity.findViewById(R.id.geometric_policy_max_price);
        geometric_policy_min_price = mainActivity.findViewById(R.id.geometric_policy_min_price);
        geometric_policy_grid_num = mainActivity.findViewById(R.id.geometric_policy_grid_num);
        geometric_policy_per_invest = mainActivity.findViewById(R.id.geometric_policy_per_invest);
        geometric_policy_confirm = mainActivity.findViewById(R.id.geometric_policy_confirm);
        geometric_policy_cancel = mainActivity.findViewById(R.id.geometric_policy_cancel);


        geometric_policy_confirm.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                if (isValidParameter != OK_PARAMETER){
                    mainActivity.showMessage("所设置参数有问题，或未点击计算参数按钮");
                    return;
                }
                mainActivity.showMessage("修改，请等待跳转......");
                geometric_policy_confirm.setEnabled(false);
                IntnetThread intnetThread = new IntnetThread();
                intnetThread.setMainActivity(mainActivity, MainActivity.State.UPDATE_STATE);
                String[] attributes = {"robot_id","currency_type","max_price", "min_price", "grid_num", "per_invest", "expect_money", "per_grid"};
                String[] values = {robot_id, geometric_currency_type.getSelectedItem().toString(), geometric_policy_max_price.getText().toString(),
                        geometric_policy_min_price.getText().toString(), geometric_policy_grid_num.getText().toString(), geometric_policy_per_invest.getText().toString(),
                        String.valueOf(need_money), String.valueOf(per_grid)};
                intnetThread.setParameter(attributes, values);
                intnetThread.setUrl("/api/update_geometric_robot");
                intnetThread.start();
            }
        });

        geometric_policy_cancel.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                mainActivity.robotInfo.Shift();
            }
        });

    }

    public void displayInfinite(String robot_id) {
        LayoutInflater inflater = LayoutInflater.from(this.mainActivity);
        LinearLayout add_robot_content = mainActivity.findViewById(R.id.update_robot_content);
        View robot_view = (LinearLayout) inflater.inflate(R.layout.infinite_robot, null);
        ViewGroup.LayoutParams layoutParams = add_robot_content.getLayoutParams();
        robot_view.setLayoutParams(layoutParams);
        add_robot_content.removeAllViews();
        add_robot_content.addView(robot_view);

        Spinner spInfinite = mainActivity.findViewById(R.id.infinite_policy_currency_type);
        initSpinner(spInfinite);


        infinite_policy_currency_type = mainActivity.findViewById(R.id.infinite_policy_currency_type);
        infinite_policy_min_price = mainActivity.findViewById(R.id.infinite_policy_min_price);
        infinite_policy_max_price = mainActivity.findViewById(R.id.infinite_policy_max_price);
        infinite_policy_buy_percent = mainActivity.findViewById(R.id.infinite_policy_buy_percent);
        infinite_policy_sell_percent = mainActivity.findViewById(R.id.infinite_policy_sell_percent);
        infinite_policy_per_invest = mainActivity.findViewById(R.id.infinite_policy_per_invest);
        infinite_policy_expect_money = mainActivity.findViewById(R.id.infinite_policy_expect_money);

        infinite_policy_confirm = mainActivity.findViewById(R.id.infinite_policy_confirm);
        infinite_policy_cancel = mainActivity.findViewById(R.id.infinite_cancel);



        infinite_policy_confirm.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                if (isValidParameter != OK_PARAMETER){
                    mainActivity.showMessage("所设置参数有问题，或未点击计算参数按钮");
                    return;
                }
                infinite_policy_confirm.setEnabled(false);
                mainActivity.showMessage("修改中，请等待跳转......");
                IntnetThread intnetThread = new IntnetThread();
                intnetThread.setMainActivity(mainActivity, MainActivity.State.UPDATE_STATE);
                String[] attributes = {"robot_id", "currency_type","max_price", "min_price", "per_invest", "sell_percent", "buy_percent", "expect_money"};
                String[] values = {robot_id, infinite_policy_currency_type.getSelectedItem().toString(), infinite_policy_max_price.getText().toString(),
                        infinite_policy_min_price.getText().toString(), infinite_policy_per_invest.getText().toString(), infinite_policy_sell_percent.getText().toString(),
                        infinite_policy_buy_percent.getText().toString(), infinite_policy_expect_money.getText().toString()};
                intnetThread.setParameter(attributes, values);
                intnetThread.setUrl("/api/update_infinite_robot");
                intnetThread.start();
            }
        });



        infinite_policy_cancel.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                mainActivity.robotInfo.Shift();
            }
        });

    }

    public void displayInfo() {
        LayoutInflater inflater = LayoutInflater.from(this.mainActivity);
        LinearLayout robot_parameter = mainActivity.findViewById(R.id.update_robot_parameter);
        View robot_view = (LinearLayout) inflater.inflate(R.layout.robot_parameter, null);
        ViewGroup.LayoutParams layoutParams = robot_parameter.getLayoutParams();
        robot_view.setLayoutParams(layoutParams);
        robot_parameter.removeAllViews();
        robot_parameter.addView(robot_view);
    }


    private void initSpinner(Spinner spinner) {


        //声明一个下拉列表的数组适配器
        ArrayAdapter<String> starAdapter = new ArrayAdapter<String>(mainActivity, R.layout.item_select, mainActivity.setUrl.currency_type);
        //设置数组适配器的布局样式
        starAdapter.setDropDownViewResource(R.layout.item_dropdown);
        //从布局文件中获取名叫sp_dialog的下拉框
        //设置下拉框的标题，不设置就没有难看的标题了
        spinner.setPrompt("请选择货币类型");
        //设置下拉框的数组适配器
        spinner.setAdapter(starAdapter);
        //设置下拉框默认的显示第一项
        spinner.setSelection(0);
        //给下拉框设置选择监听器，一旦用户选中某一项，就触发监听器的onItemSelected方法
    }
}
