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

import router from '@ohos.router';
import promptAction from '@ohos.promptAction';

import prompt from '@system.prompt';
import { window } from '@kit.ArkUI';
import NetApi from '../utils/NetApi'
import { BottomOffset } from '@kit.ArkUI';
import  PreferencesUtil  from '../utils/PreferencesUtil'
import CityModel from '../models/CityModel'
import VitalModel from '../models/VitalModel'


@Entry
@Component
struct ProfilePage {
  @State currentTab: number = 2;

  // 用户信息
  @State username: string = '健康用户';
  @State email: string = '2892224158@qq.com';
  @State age: number = 65;
  @State gender: string = '女';
  @State region: string = '高原地区';
  @State isConnected: boolean = true;

  vitalList: ESObject = [];
  cityList: ESObject = [];

  cityId = '';
  userId = '';
  measureDate = '';
  deviceNo ='';


  aboutToAppear(): void {

    PreferencesUtil.createPreferences(getContext(this))

    PreferencesUtil.get("deviceNo").then(value=> {
      this.deviceNo = value.toString()
    });

    PreferencesUtil.get("cityId").then(value=> {
      this.cityId = value.toString()
    });


    PreferencesUtil.get("userId").then(value=> {
      this.userId = value.toString()
      console.log('read preferences: ', this.userId)

      // 加载数据
      this.measureDate = '2025-11-03';
      this.loadData(this.userId, this.cityId, this.measureDate);
    });


  }

  // 底部导航栏
  @Builder TabBar() {
    Row({ space: 0 }) {
      // 风险分析 - 修改这里
      Column() {
        Image($rawfile('risk_inactive.png'))
          .width(28)
          .height(28)
          .margin({ bottom: 4 })
        Text('风险分析')  // 改为风险分析
          .fontSize(12)
          .fontColor('#999999')
          .fontWeight(FontWeight.Normal)
      }
      .width('33.3%')
      .height(60)
      .justifyContent(FlexAlign.Center)
      .onClick(() => {
        router.replaceUrl({
          url: 'pages/RiskAnalysisPage'  // 改为跳转到风险分析页面
        });
      })

      // 实时监测
      Column() {
        Image($rawfile('heart_inactive.png'))
          .width(28)
          .height(28)
          .margin({ bottom: 4 })
        Text('实时监测')
          .fontSize(12)
          .fontColor('#999999')
          .fontWeight(FontWeight.Normal)
      }
      .width('33.3%')
      .height(60)
      .justifyContent(FlexAlign.Center)
      .onClick(() => {
        router.replaceUrl({
          url: 'pages/HealthMonitorPage'
        });
      })

      // 我的
      Column() {
        Image($rawfile('profile_active.png'))
          .width(32)
          .height(32)
          .margin({ bottom: 4 })
        Text('我的')
          .fontSize(13)
          .fontColor('#3368ff')
          .fontWeight(FontWeight.Medium)
      }
      .width('33.3%')
      .height(60)
      .justifyContent(FlexAlign.Center)
    }
    .width('100%')
    .height(60)
    .backgroundColor('#ffffff')
    .shadow({ radius: 8, color: '#000000', offsetX: 0, offsetY: -2 })
    .borderRadius({ topLeft: 16, topRight: 16 })
  }

  build() {
    Stack({ alignContent: Alignment.TopStart }) {
      // 添加背景图片
      Image($rawfile('app.media.backgroud.png'))
        .width('100%')
        .height('100%')
        .objectFit(ImageFit.Cover)
        .opacity(0.9)

      // 原有内容保持不变
      Column() {
        // 顶部导航栏
        Row() {
          Text('个人中心')
            .fontSize(18)
            .fontWeight(FontWeight.Medium)
            .fontColor('#1a1a1a')

          Blank()

          Text('编辑')
            .fontSize(16)
            .fontColor('#3368ff')
            .onClick(() => {
              promptAction.showToast({ message: '进入编辑模式' });
            })
        }
        .width('100%')
        .height(60)
        .padding({ left: 20, right: 20 })
        .backgroundColor('#ffffff')

        Scroll() {
          Column({ space: 16 }) {
            // 用户信息卡片
            Column() {
              Row() {
                Image($rawfile('user_avatar.png'))
                  .width(60)
                  .height(60)
                  .borderRadius(30)
                  .margin({ right: 15 })

                Column({ space: 6 }) {
                  Text(this.username)
                    .fontSize(20)
                    .fontWeight(FontWeight.Bold)
                    .fontColor('#1a1a1a')

                  Text(this.email)
                    .fontSize(14)
                    .fontColor('#666666')

                  Row({ space: 8 }) {
                    Text(this.age + '岁')
                      .fontSize(12)
                      .fontColor('#999999')
                      .padding({ left: 8, right: 8, top: 2, bottom: 2 })
                      .backgroundColor('#f0f0f0')
                      .borderRadius(10)

                    Text(this.gender)
                      .fontSize(12)
                      .fontColor('#999999')
                      .padding({ left: 8, right: 8, top: 2, bottom: 2 })
                      .backgroundColor('#f0f0f0')
                      .borderRadius(10)

                    Text(this.region)
                      .fontSize(12)
                      .fontColor('#999999')
                      .padding({ left: 8, right: 8, top: 2, bottom: 2 })
                      .backgroundColor('#f0f0f0')
                      .borderRadius(10)
                  }
                }
                .alignItems(HorizontalAlign.Start)
              }
              .width('100%')
              .margin({ bottom: 20 })

              Row() {
                Text('设备状态：')
                  .fontSize(14)
                  .fontColor('#666666')

                Row({ space: 6 }) {
                  Circle({ width: 8, height: 8 })
                    .fill(this.isConnected ? '#52c41a' : '#ff4d4f')

                  Text(this.isConnected ? '已连接' : '未连接')
                    .fontSize(14)
                    .fontColor(this.isConnected ? '#52c41a' : '#ff4d4f')
                }

                Blank()

                Button(this.isConnected ? '断开连接' : '连接设备')
                  .fontSize(12)
                  .width(80)
                  .height(28)
                  .backgroundColor(this.isConnected ? '#fff2f0' : '#f6ffed')
                  .fontColor(this.isConnected ? '#ff4d4f' : '#52c41a')
                  .borderRadius(14)
                  .onClick(() => {
                    this.isConnected = !this.isConnected;
                    promptAction.showToast({
                      message: this.isConnected ? '设备已连接' : '设备已断开'
                    });
                  })
              }
              .width('100%')
            }
            .width('100%')
            .padding(20)
            .backgroundColor('#ffffff')
            .borderRadius(16)
            .shadow({ radius: 8, color: '#000000', offsetX: 0, offsetY: 2 })
            .margin({ left: 20, right: 20, top: 20 })

            // 设置菜单
            Column() {
              Text('设置')
                .fontSize(16)
                .fontColor('#666666')
                .margin({ bottom: 10 })
                .alignSelf(ItemAlign.Start)

              Column() {
                this.MenuItem('消息通知', '推送设置和提醒')
                Divider().strokeWidth(0.5).color('#f0f0f0')
                this.MenuItem('隐私设置', '数据权限和管理')
                Divider().strokeWidth(0.5).color('#f0f0f0')
                this.MenuItem('帮助中心', '使用指南和常见问题')
                Divider().strokeWidth(0.5).color('#f0f0f0')
                this.MenuItem('关于我们', '版本信息和联系我们')
              }
              .width('100%')
              .backgroundColor('#ffffff')
              .borderRadius(12)
              .shadow({ radius: 4, color: '#000000', offsetX: 0, offsetY: 2 })
            }
            .width('100%')
            .margin({ left: 20, right: 20 })

            // 退出登录
            Button('退出登录')
              .width('90%')
              .height(50)
              .fontSize(16)
              .fontWeight(FontWeight.Medium)
              .backgroundColor('#ff4d4f')
              .fontColor('#ffffff')
              .borderRadius(25)
              .margin({ top: 30, bottom: 20 })
              .onClick(() => {
                promptAction.showToast({ message: '退出登录成功' });
                setTimeout(() => {
                  router.clear();
                  router.replaceUrl({
                    url: 'pages/LoginPage'
                  });
                }, 1000);
              })
          }
          .width('100%')
        }
        .flexGrow(1)

        this.TabBar()
      }
      .width('100%')
      .height('100%')
    }
    .width('100%')
    .height('100%')
    .backgroundColor('#f5f5f5')
  }

  @Builder MenuItem(title: string, subtitle: string) {
    Row() {
      Column({ space: 2 }) {
        Text(title)
          .fontSize(16)
          .fontColor('#1a1a1a')
          .alignSelf(ItemAlign.Start)

        Text(subtitle)
          .fontSize(12)
          .fontColor('#999999')
          .alignSelf(ItemAlign.Start)
      }
      .alignItems(HorizontalAlign.Start)

      Blank()

      Image($rawfile('arrow_right.png'))
        .width(16)
        .height(16)
    }
    .width('100%')
    .height(60)
    .padding({ left: 20, right: 20 })
    .backgroundColor('#ffffff')
    .onClick(() => {
      promptAction.showToast({ message: '点击了：' + title });
    })
  }


  loadData(userId: string, cityId: string, measureDate: string) {
    // 加载数据
    let url = '/user/list'
    let params = '{ "userId": "'+ userId + '" }';

    // 加载数据
    NetApi.getList(url, params)
      .then((res: ESObject) => {

        this.vitalList = res;
        console.log( res );

        this.username = res[0]['username'];;
        this.email = res[0]['email'];;
        this.age = res[0]['age'];
        this.gender = res[0]['gender'];
        this.region = res[0]['region'];
        this.isConnected = true;

      })


  }
}