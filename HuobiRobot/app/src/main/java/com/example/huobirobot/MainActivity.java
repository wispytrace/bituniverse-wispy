package com.example.huobirobot;

import androidx.appcompat.app.AppCompatActivity;

import android.os.Bundle;
import android.os.Handler;
import android.os.Message;
import android.util.Log;
import android.view.KeyEvent;
import android.view.View;
import android.widget.Toast;

import com.example.huobirobot.pages.AddRobot;
import com.example.huobirobot.pages.GetData;
import com.example.huobirobot.pages.GetLog;
import com.example.huobirobot.pages.IntnetThread;
import com.example.huobirobot.pages.Login;
import com.example.huobirobot.pages.OrderInfo;
import com.example.huobirobot.pages.RobotInfo;
import com.example.huobirobot.pages.SetUrl;
import com.example.huobirobot.pages.UpdateRobot;

import org.json.JSONObject;

public class MainActivity extends AppCompatActivity {

    public static final int ERRO_CODE = -1;
    public static final int SUCC_CODE = 0;


    public Toast mToast = null;
    public SetUrl setUrl = new SetUrl(this);

    public RobotInfo robotInfo = new RobotInfo(this);
    public AddRobot addRobot = new AddRobot(this);
    public OrderInfo orderInfo = new OrderInfo(this);
    public UpdateRobot updateRobot = new UpdateRobot(this);
    public GetLog getLog = new GetLog(this);
    public Login login = new Login(this);



    public enum State {
        GET_SET,
        ROBOTS_INFO,
        ORDERS_TRADE_INFO,
        ORDERS_PENDER_INFO,
        LOG_INFO,
        ADD_STATE,
        UPDATE_STATE,
        GET_INVEST_PARAMETER_ADD,
        GET_INVEST_PARAMETER_UPDATE,
        GET_UPDATE_ROBOT_PARAMETER,
        ERROR_STATE,
        SET_ADD_API,
        LOGIN_FRESH,
        ROBOT_MODIFY,
        DELETE_ACCOUNT,
        MODIFY_ACCOUNT_NICKNAME
    }

    public Handler myHander = new Handler() {
        public void handleMessage(Message message) {
            try {
                JSONObject jsonObject = (JSONObject) message.obj;
                int status = jsonObject.getInt("status");
                State state = (State) jsonObject.get("state");
                if (status == ERRO_CODE) {
                    showMessage(message.obj.toString());
                    Log.e("lou", message.obj.toString());
                } else if (status == SUCC_CODE) {
                    showMessage("数据更新成功");
                    switch (state) {
                        case GET_SET:
                            setUrl.setSet(jsonObject);
                            setUrl.Shift();
                            break;
                        case LOGIN_FRESH:
                            setUrl.setSet(jsonObject);
                            login.Shift();
                            break;
                        case SET_ADD_API:
                            setUrl.setApi(jsonObject);
                            break;
                        case ROBOTS_INFO:
                            robotInfo.refreshRobotInfo(jsonObject);
                            break;
                        case ADD_STATE:
                            robotInfo.Shift();
                            break;
                        case UPDATE_STATE:
                            robotInfo.Shift();
                        case ORDERS_TRADE_INFO:
                            orderInfo.displayTradeOrder(jsonObject);
                            break;
                        case ORDERS_PENDER_INFO:
                            orderInfo.displayPenderOrder(jsonObject);
                            break;
                        case LOG_INFO:
                            getLog.freshLog(jsonObject);
                            break;
                        case GET_INVEST_PARAMETER_ADD:
                            addRobot.setInvestParameter(jsonObject);
                            break;
                        case GET_INVEST_PARAMETER_UPDATE:
                            updateRobot.setInvestParameter(jsonObject);
                            break;
                        case GET_UPDATE_ROBOT_PARAMETER:
                            updateRobot.setRobotParameter(jsonObject);
                            break;
                        case ROBOT_MODIFY:
                            robotInfo.Shift();
                            break;
                        case DELETE_ACCOUNT:
                            login.deleteRobotCallback(jsonObject);
                            break;
                        case MODIFY_ACCOUNT_NICKNAME:
                            setUrl.setNickname(jsonObject);
                            break;

                        default:
                            showMessage("发生了未知错误2");
                    }
                }
                super.handleMessage(message);
            } catch (Exception e) {
                System.out.println(e.getMessage());
                showMessage(e.getMessage());
            }
        }
    };

    public boolean onKeyDown(int keyCode, KeyEvent event) {
        if ((keyCode == KeyEvent.KEYCODE_BACK)) {
            if (login.is_login_state){
                loadLogin();
                return false;
            }
            orderInfo.stopFlush();
            robotInfo.Shift();

            return false;
        } else {
            return super.onKeyDown(keyCode, event);
        }
    }

    public void showMessage(String message) {
        if (mToast == null) {
            mToast = Toast.makeText(this, message, Toast.LENGTH_SHORT);
        } else {
            View view = mToast.getView();
            mToast.cancel();
            mToast = new Toast(this);
            mToast.setView(view);
            mToast.setDuration(Toast.LENGTH_SHORT);
            mToast.setText(message);
        }
        mToast.show();
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        this.setContentView(R.layout.activity_loading);
        loadLogin();
    }

    private void loadLogin(){
        IntnetThread intnetThread = new IntnetThread();
        intnetThread.setMainActivity(this, State.LOGIN_FRESH);
        intnetThread.setUrl("/api/get_set");
        intnetThread.start();
    }

}