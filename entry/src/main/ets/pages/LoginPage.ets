/*
 * Copyright (C) 2026 PeakGuard Team
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as published
 * by the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
 */

import promptAction from '@ohos.promptAction';
import router from '@ohos.router';

import NetApi from '../utils/NetApi'
import LoginModel from '../models/LoginModel'
import  PreferencesUtil  from '../utils/PreferencesUtil'

//let prefer = new PreferencesUtil();

let msg: String = 'login页面传来的数据'


@Entry
@Component
struct LoginPage {
  // 状态管理
  @State isLoginMode: boolean = true; // true=登录模式，false=注册模式

  @State confirmPassword: string = ''; // 注册时的确认密码
  @State passwordVisible: boolean = false; // 密码是否可见

  @State account: string = ''
  @State password: string = ''

  aboutToAppear(){
    PreferencesUtil.createPreferences(getContext(this))
    PreferencesUtil.get("account").then(value=> {
      this.account = value.toString()
      console.log('read preferences: ', this.account)
    });

    PreferencesUtil.get("password").then(value=> {
      this.password = value.toString()
    });
  }

  // 切换登录/注册模式
  toggleMode() {
    this.isLoginMode = !this.isLoginMode;
    // 切换时清空输入
    this.account = '';
    this.password = '';
    this.confirmPassword = '';
  }

  // 登录/注册提交
  submit() {
    if (this.isLoginMode) {

      if (this.account != '' && this.password != '') {
        // 登录
        this.login(this.account, this.password)

      } else {
        promptAction.showToast({
          message: '请输入账号和密码！',
          duration: 2000,
        });

      }

      //promptAction.showToast({ message: '登录成功' });
      // 跳转到健康监测页面
      // setTimeout(() => {
      //   router.pushUrl({
      //     url: 'pages/HealthMonitorPage'
      //   });
      // }, 1000);

    } else {
      // 注册逻辑
      if (!this.account || !this.password) {
        promptAction.showToast({ message: '用户名和密码不能为空' });
        return;
      }
      if (this.password !== this.confirmPassword) {
        promptAction.showToast({ message: '两次密码不一致' });
        return;
      }
      // 实际项目中调用注册接口
      promptAction.showToast({
        message: '注册成功，已自动跳转到登录界面',
        duration: 3000 // 显示3秒
      });

      // 注册成功后自动切换到登录模式
      this.isLoginMode = true;
      // 保留用户名，清空密码
      this.password = '';
      this.confirmPassword = '';
    }
  }

  build() {
    Column() {
      // 标题栏
      Column() {
        Image($rawfile('app-icon.jpg'))
          .width(80)
          .height(80)
          .margin({ bottom: 20 })

        Text(this.isLoginMode ? '欢迎登录' : '账号注册')
          .fontSize(30)
          .fontWeight(FontWeight.Bold)
          .fontColor('#1a1a1a')
      }
      .margin({ top: 60, bottom: 40 })

      // 表单区域
      Column({ space: 20 }) {
        // 用户名输入
        TextInput({ placeholder: '请输入用户名', text: this.account })
          .width('80%')
          .height(50)
          .padding({ left: 15 })
          .backgroundColor('#ffffff')
          .borderRadius(25)
          .onChange((value: string) => {
            this.account = value;
          })

        // 密码输入区域
        Row() {
          TextInput({
            placeholder: '请输入密码',
            text: this.password
          })
            .width('100%')
            .height(50)
            .padding({ left: 15 })
            .backgroundColor('#ffffff')
            .type(this.passwordVisible ? InputType.Normal : InputType.Password)
            .onChange((value: string) => {
              this.password = value;
            })

          // 密码显示/隐藏按钮
          Text(this.passwordVisible ? '隐藏' : '显示')
            .fontSize(14)
            .fontColor('#666666')
            .margin({ right: 15 })
            .onClick(() => {
              this.passwordVisible = !this.passwordVisible;
            })
        }
        .width('80%')
        .height(50)
        .backgroundColor('#ffffff')
        .borderRadius(25)
        .alignItems(VerticalAlign.Center)

        // 注册模式下显示确认密码
        if (!this.isLoginMode) {
          TextInput({
            placeholder: '请确认密码',
            text: this.confirmPassword
          })
            .width('80%')
            .height(50)
            .padding({ left: 15 })
            .backgroundColor('#ffffff')
            .borderRadius(25)
            .type(InputType.Password)
            .onChange((value: string) => {
              this.confirmPassword = value;
            })
        }

        // 忘记密码（仅登录模式显示）
        if (this.isLoginMode) {
          Text('忘记密码?')
            .fontSize(14)
            .fontColor('#1296db')
            .margin({ left: '10%', top: -10, bottom: 10 })
            .alignSelf(ItemAlign.Start)
            .onClick(() => {
              promptAction.showToast({ message: '跳转至找回密码' });
            })
        }

        // 提交按钮
        Button(this.isLoginMode ? '登录' : '注册')
          .width('80%')
          .height(50)
          .fontSize(18)
          .fontWeight(FontWeight.Medium)
          .backgroundColor('#1296db')
          .fontColor('#ffffff')
          .borderRadius(25)
          .onClick(() => {
            this.submit();
          })

        // 切换登录/注册模式
        Row({ space: 5 }) {
          Text(this.isLoginMode ? '还没有账号?' : '已有账号?')
            .fontSize(14)
            .fontColor('#666666')
          Text(this.isLoginMode ? '立即注册' : '去登录')
            .fontSize(14)
            .fontColor('#1296db')
            .onClick(() => {
              this.toggleMode();
            })
        }
        .margin({ top: 20 })
        .justifyContent(FlexAlign.Center)
      }

      // 底部区域
      Text('其他登录方式')
        .fontSize(14)
        .fontColor('#999999')
        .margin({ top: 60, bottom: 20 })

      Row({ space: 30 }) {
        // 第三方登录图标（示例）
        Image($rawfile('vx.png')) // 微信图标
          .width(40)
          .height(40)
        Image($rawfile('qq.png')) // QQ图标
          .width(40)
          .height(40)
      }
    }
    .width('100%')
    .height('100%')
    .backgroundColor('#f5f5f5')
    .justifyContent(FlexAlign.Start)
    .alignItems(HorizontalAlign.Center)
  }

  login(account: string, password: string) {
    let url = '/oper/auth'
    let loginM: LoginModel = { id: account, pwd: password }
    //let params = '{ "id": "admin", "pwd": "123456" }'
    let params = JSON.stringify(loginM)

    // 加载数据
    NetApi.getList(url, params)
      .then((res: ESObject) => {
        console.log('=====11111=')
        console.log(res.data[0]['userId']);

        if(res.code == "10000"){
          PreferencesUtil.put("account", this.account)
          PreferencesUtil.put("password", this.password)
          // save into local
          PreferencesUtil.put("userId", res.data[0]['userId'])
          PreferencesUtil.put("cityId", res.data[0]['cityId'])
          PreferencesUtil.put("deviceNo", res.data[0]['deviceNo'])

          router.pushUrl({
            url: 'pages/HealthMonitorPage',
            params: { src: msg, }
          })
        }
        else{
          promptAction.showToast({
            message: res.msg,
            duration: 2000,
          });
        }
      })
  }
}