package com.example.huobirobot.pages;

import android.app.AlertDialog;
import android.content.DialogInterface;
import android.view.View;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.Spinner;
import android.widget.TextView;

import com.example.huobirobot.MainActivity;
import com.example.huobirobot.R;

import org.json.JSONObject;

public class Login {
    private MainActivity mainActivity = null;

    public Login(MainActivity mainActivity){this.mainActivity = mainActivity;}


    public boolean is_login_state = false;

    private Spinner account_select = null;
    private Button  account_select_confirm = null;

    private Button add_account = null;
    private Button delete_account = null;



    public void Shift(){

        mainActivity.setContentView(R.layout.activity_login);

        account_select = mainActivity.findViewById(R.id.account_select);
        account_select_confirm = mainActivity.findViewById(R.id.account_select_confirm);
        add_account = mainActivity.findViewById(R.id.add_account);
        delete_account = mainActivity.findViewById(R.id.delete_account);

        initSpinner(account_select, mainActivity.setUrl.nickname_list);

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
                    is_login_state = false;
                    mainActivity.robotInfo.Shift();
                }
            }
        });

        add_account.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                displayAddDialog();
            }
        });

        delete_account.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                int index = account_select.getSelectedItemPosition();
                mainActivity.setUrl.currenct_account = mainActivity.setUrl.account_list[index];
                mainActivity.setUrl.currenct_api = mainActivity.setUrl.api_list[index];
                mainActivity.setUrl.current_nickname = mainActivity.setUrl.nickname_list[index];
                if (mainActivity.setUrl.currenct_account.compareTo("空") == 0){
                    mainActivity.showMessage("当前无账户，请先创建账户");
                }
                else {
                    displayDeleteDialog(mainActivity.setUrl.account_list[index], mainActivity.setUrl.nickname_list[index]);
                }
            }
        });

        is_login_state = true;

    }

    public void deleteRobotCallback(JSONObject jsonObject) throws Exception{
        int valid = jsonObject.getInt("valid");
        if (valid != 0) {
            mainActivity.showMessage("删除失败, 请先删除账户内机器人");
            return;
        }
        IntnetThread intnetThread = new IntnetThread();
        intnetThread.setMainActivity(mainActivity, MainActivity.State.LOGIN_FRESH);
        intnetThread.setUrl("/api/get_set");
        intnetThread.start();
    }

    private void initSpinner(Spinner spinner, String[] list) {
        ArrayAdapter<String> starAdapter = new ArrayAdapter<String>(mainActivity, R.layout.item_select, list);
        starAdapter.setDropDownViewResource(R.layout.item_dropdown);
        spinner.setPrompt("选择密钥ID");
        spinner.setAdapter(starAdapter);
        spinner.setSelection(0);
    }

    public void displayAddDialog() {

        AlertDialog.Builder builder = new AlertDialog.Builder(mainActivity);

        builder.setTitle("是否添加一个账户")

                .setPositiveButton("确认", new DialogInterface.OnClickListener() {
                    @Override
                    public void onClick(DialogInterface dialog, int which) {
                        mainActivity.showMessage("命令执行中，请等待跳转......");
                        IntnetThread intnetThread = new IntnetThread();
                        intnetThread.setMainActivity(mainActivity, MainActivity.State.LOGIN_FRESH);
                        intnetThread.setUrl("/api/add_account");
                        intnetThread.start();
                    }
                })
                .setNegativeButton("取消", null);
        builder.create().show();
    }

    public void displayDeleteDialog(String account_id, String account_name) {

        AlertDialog.Builder builder = new AlertDialog.Builder(mainActivity);

        builder.setTitle("是否删除名称为 " + account_name + " 的账户")

                .setPositiveButton("确认", new DialogInterface.OnClickListener() {
                    @Override
                    public void onClick(DialogInterface dialog, int which) {
                        mainActivity.showMessage("命令执行中，请等待跳转......");
                        IntnetThread intnetThread = new IntnetThread();
                        String[] attributes = {"account_id"};
                        String[] values = {account_id};
                        intnetThread.setParameter(attributes, values);
                        intnetThread.setMainActivity(mainActivity, MainActivity.State.DELETE_ACCOUNT);
                        intnetThread.setUrl("/api/delete_account");
                        intnetThread.start();
                    }
                })
                .setNegativeButton("取消", null);
        builder.create().show();
    }



}

