package com.example.huobirobot.pages;

import android.view.View;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.Spinner;
import android.widget.TextView;

import com.example.huobirobot.MainActivity;
import com.example.huobirobot.R;

import org.json.JSONObject;

public class SetUrl {
    private MainActivity mainActivity = null;

    public SetUrl(MainActivity mainActivity){this.mainActivity = mainActivity;}



    private TextView api_key = null;
    private TextView secret_key = null;
    private Button key_confirm = null;
    private Button key_cancel = null;
    private Spinner plantform_select = null;

    private TextView account_nickname = null;
    private Button account_nickname_confirm = null;
    private Button account_nickname_cancel = null;


    public TextView account_current = null;
    public TextView account_pantform_current = null;


    private TextView api_current = null;


    private Spinner account_select = null;
    private Button  account_select_confirm = null;
    private Button  account_select_cancel = null;



    public String[] currency_type = {"btcusdt"};

    public String[] account_list = {"空"};
    public String[] api_list = {"空"};
    public String[] nickname_list = {"空"};
    public String[] plantform_list = {"空"};
    public String[] account_plantform = {"空"};


    public String currenct_api = api_list[0];
    public String currenct_account = account_list[0];
    public String current_nickname = nickname_list[0];
    public String current_plantform = plantform_list[0];

    public int selected_index = 0;
    

    public String ipUrl = "http://8.210.174.164:8000";

    public void Shift(){

        mainActivity.setContentView(R.layout.activity_set);


        api_key = mainActivity.findViewById(R.id.api_key);
        secret_key = mainActivity.findViewById(R.id.secret_key);
        plantform_select = mainActivity.findViewById(R.id.plantform_select);
        key_confirm = mainActivity.findViewById(R.id.key_confirm);
        key_cancel = mainActivity.findViewById(R.id.key_cancel);

        account_current = mainActivity.findViewById(R.id.account_current);
        account_pantform_current =mainActivity.findViewById(R.id.account_plantform_current);
        api_current = mainActivity.findViewById(R.id.api_current);

        account_select = mainActivity.findViewById(R.id.account_select);
        account_select_confirm = mainActivity.findViewById(R.id.account_select_confirm);
        account_select_cancel = mainActivity.findViewById(R.id.account_select_cancel);

        account_nickname = mainActivity.findViewById(R.id.account_nickname);
        account_nickname_confirm = mainActivity.findViewById(R.id.account_nickname_confirm);
        account_nickname_cancel = mainActivity.findViewById(R.id.account_nickname_cancel);



        key_confirm.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                if (currenct_api.compareTo("空") != 0){
                    mainActivity.showMessage("已绑定API，不支持切换重复绑定其他API");
                    return;
                }
                int index = account_select.getSelectedItemPosition();
                current_plantform = plantform_list[index];
                mainActivity.showMessage("命令执行中，请等待跳转......");
                IntnetThread intnetThread = new IntnetThread();
                intnetThread.setMainActivity(mainActivity, MainActivity.State.SET_ADD_API);
                String[] attributes = {"api_key","secret_key", "plantform","account_id"};
                String[] values = {api_key.getText().toString(), secret_key.getText().toString(), plantform_select.getSelectedItem().toString(), currenct_account};
                intnetThread.setParameter(attributes, values);
                intnetThread.setUrl("/api/add_api");
                intnetThread.start();
            }
        });

        key_cancel.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                mainActivity.showMessage("命令执行中，请等待跳转......");
                mainActivity.robotInfo.Shift();
            }
        });


        account_nickname_confirm.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                IntnetThread intnetThread = new IntnetThread();
                intnetThread.setMainActivity(mainActivity, MainActivity.State.MODIFY_ACCOUNT_NICKNAME);
                String[] attributes = {"account_id", "account_nickname"};
                String[] values = {currenct_account, account_nickname.getText().toString()};
                intnetThread.setParameter(attributes, values);
                intnetThread.setUrl("/api/modify_nickname");
                intnetThread.start();
            }
        });

        account_nickname_cancel.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                mainActivity.showMessage("命令执行中，请等待跳转......");
                mainActivity.robotInfo.Shift();
            }
        });

        account_nickname.setText(mainActivity.setUrl.current_nickname);




        account_current.setText(currenct_account);
        api_current.setText(currenct_api);
        account_pantform_current.setText(current_plantform);

        initSpinner(account_select, nickname_list);
        initSpinner(plantform_select, plantform_list);

        account_select_confirm.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                int index = account_select.getSelectedItemPosition();
                mainActivity.setUrl.currenct_account = mainActivity.setUrl.account_list[index];
                mainActivity.setUrl.currenct_api = mainActivity.setUrl.api_list[index];
                mainActivity.setUrl.current_nickname = mainActivity.setUrl.nickname_list[index];
                mainActivity.setUrl.current_plantform = mainActivity.setUrl.account_plantform[index];
                mainActivity.setUrl.selected_index = index;
                if (mainActivity.setUrl.currenct_account.compareTo("空") == 0){
                    mainActivity.showMessage("当前无账户，请先创建账户");
                }
                else {
                    mainActivity.showMessage("账户登录成功");
                    mainActivity.robotInfo.Shift();
                }
            }
        });

        account_select_cancel.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                mainActivity.showMessage("命令执行中，请等待跳转......");
                mainActivity.robotInfo.Shift();
            }
        });

    }


    private void initSpinner(Spinner spinner, String[] list) {
        ArrayAdapter<String> starAdapter = new ArrayAdapter<String>(mainActivity, R.layout.item_select, list);
        starAdapter.setDropDownViewResource(R.layout.item_dropdown);
        spinner.setPrompt("选择密钥ID");
        spinner.setAdapter(starAdapter);
        spinner.setSelection(0);
    }

    public void setApi(JSONObject jsonObject) throws Exception{
        int isValid = jsonObject.getInt("valid");
        if (isValid != 0){
            mainActivity.showMessage("密钥输入错误");
            return;
        }else {
            mainActivity.showMessage("密钥输入成功");
        }
        String api_key = jsonObject.getString("api_key");
        currenct_api = api_key;
        current_plantform = plantform_select.getSelectedItem().toString();
        api_list[selected_index] = api_key;
        account_plantform[selected_index] = current_plantform;
        mainActivity.robotInfo.Shift();
    }

    public void setNickname(JSONObject jsonObject) throws Exception{
        String nickname = jsonObject.getString("account_nickname");
        current_nickname = nickname;
        nickname_list[selected_index] = nickname;
        mainActivity.robotInfo.Shift();
    }


    public void getSet(){
        IntnetThread intnetThread = new IntnetThread();
        intnetThread.setMainActivity(mainActivity, MainActivity.State.GET_SET);
        intnetThread.setUrl("/api/get_set");
        intnetThread.start();
    }

    public void setSet(JSONObject jsonObject) throws Exception{
        int currency_count = jsonObject.getInt("currency_count");

        if (currency_count !=0) {
            JSONObject currencys = jsonObject.getJSONObject("currencys");
            currency_type = new String[currency_count];
            for (int i = 0; i < currency_count; i++) {
                currency_type[i] = currencys.getString(Integer.toString(i));
            }
        }

        int plantform_count = jsonObject.getInt("plantform_count");

        if (plantform_count !=0) {
            JSONObject plantforms = jsonObject.getJSONObject("plantforms");
            plantform_list = new String[plantform_count];
            for (int i = 0; i < plantform_count; i++) {
                plantform_list[i] = plantforms.getString(Integer.toString(i));
            }
        }


        int count = jsonObject.getInt("count");
        if (count != 0) {
            JSONObject apis = jsonObject.getJSONObject("apis");
            JSONObject accounts = jsonObject.getJSONObject("accounts");
            JSONObject nicknames = jsonObject.getJSONObject("nicknames");
            JSONObject account_plantforms = jsonObject.getJSONObject("account_plantforms");

            api_list = new String[count];
            account_list = new String[count];
            nickname_list = new String[count];
            account_plantform = new String[count];

            for (int i = 0; i < count; i++) {
                api_list[i] = apis.getString(Integer.toString(i));
                account_list[i] = accounts.getString(Integer.toString(i));
                nickname_list[i] = nicknames.getString(Integer.toString(i));
                account_plantform[i] = account_plantforms.getString(Integer.toString(i));
            }

        }else {
            account_list = new String[] {"空"};
            api_list = new String[] {"空"};
            nickname_list = new String[] {"空"};
            account_plantform = new String[] {"空"};

        }

        currenct_api = api_list[0];
        currenct_account = account_list[0];
        current_nickname = nickname_list[0];
        current_plantform = account_plantform[0];
    }

}

