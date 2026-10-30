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

// HealthMonitorPage.ets
import router from '@ohos.router';
import promptAction from '@ohos.promptAction';
import { JSON } from '@kit.ArkTS';

import prompt from '@system.prompt';
import { window } from '@kit.ArkUI';
import NetApi from '../utils/NetApi'
import { BottomOffset } from '@kit.ArkUI';
import  PreferencesUtil  from '../utils/PreferencesUtil'
import CityModel from '../models/CityModel'
import VitalModel from '../models/VitalModel'


@Entry
@Component
struct HealthMonitorPage {
  vitalList: ESObject = [];
  cityList: ESObject = [];

  cityId = '';
  userId = '';
  measureDate = '';
  deviceNo ='';

  @State currentTab: number = 1;

  // 健康数据，在LoadData读取数据库真实数据更新
  @State bloodOxygen: number = 0; // 血氧
  @State breathingRate: number = 0; // 呼吸率
  @State heartRate: number = 0; // 心率
  @State systolicPressure: number = 0; // 收缩压
  @State diastolicPressure: number = 0; // 舒张压
  @State bodyTemperature: number = 0; // 体温
  @State isMonitoring: boolean = false; // 监测状态
  @State batteryLevel: number = 0; // 设备电量

  // 环境数据
  @State currentCity: string = '';
  @State altitude: number = 0; // 海拔(米)
  @State environmentTemperature: number = 0; // 环境温度
  @State oxygenConcentration: number = 0; // 氧气浓度(%)

  // 日期时间
  @State currentDate: string = '';
  @State currentTime: string = '';

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



    this.updateDateTime();
    // 模拟定时更新
    setInterval(() => {
      this.updateDateTime();
    }, 60000);
  }

  updateDateTime(): void {
    const now = new Date();
    this.currentDate = `${now.getFullYear()}年${now.getMonth() + 1}月${now.getDate()}日`;
    this.currentTime = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`;
  }

  // 底部导航栏
  @Builder TabBar() {
    Row({ space: 0 }) {
      // 风险分析
      Column() {
        Image($rawfile('risk_inactive.png'))
          .width(28)
          .height(28)
          .margin({ bottom: 4 })
        Text('风险分析')
          .fontSize(12)
          .fontColor('#999999')
          .fontWeight(FontWeight.Normal)
      }
      .width('33.3%')
      .height(60)
      .justifyContent(FlexAlign.Center)
      .onClick(() => {
        router.replaceUrl({
          url: 'pages/RiskAnalysisPage'
        }).then(() => {
          console.info('跳转到风险分析页面成功');
        }).catch((error: Error) => {
          console.error('跳转失败:', error);
        });
      })

      // 实时监测 - 当前页面
      Column() {
        Image($rawfile('heart_active.png'))
          .width(32)
          .height(32)
          .margin({ bottom: 4 })
        Text('实时监测')
          .fontSize(13)
          .fontColor('#3368ff')
          .fontWeight(FontWeight.Medium)
      }
      .width('33.3%')
      .height(60)
      .justifyContent(FlexAlign.Center)
      // 移除点击事件，因为已经在当前页面

      // 我的
      Column() {
        Image($rawfile('profile_inactive.png'))
          .width(28)
          .height(28)
          .margin({ bottom: 4 })
        Text('我的')
          .fontSize(12)
          .fontColor('#999999')
          .fontWeight(FontWeight.Normal)
      }
      .width('33.3%')
      .height(60)
      .justifyContent(FlexAlign.Center)
      .onClick(() => {
        router.replaceUrl({
          url: 'pages/ProfilePage'
        }).then(() => {
          console.info('跳转到个人中心页面成功');
        }).catch((error: Error) => {
          console.error('跳转失败:', error);
        });
      })
    }
    .width('100%')
    .height(60)
    .backgroundColor('#ffffff')
    .shadow({ radius: 8, color: '#000000', offsetX: 0, offsetY: -2 })
    .borderRadius({ topLeft: 16, topRight: 16 })
  }

  // 顶部导航栏
  @Builder TopBar() {
    Row() {
      Image($rawfile('back.png'))
        .width(24)
        .height(24)
        .onClick(() => {
          router.back();
        })

      Text('健康监测')
        .fontSize(18)
        .fontWeight(FontWeight.Medium)
        .fontColor('#1a1a1a')
        .margin({ left: 16 })

      Blank()

      Row({ space: 4 }) {
        Image($rawfile('battery_icon.png'))
          .width(16)
          .height(16)
        Text(this.batteryLevel + '%')
          .fontSize(12)
          .fontColor('#666666')
      }
      .margin({ right: 16 })

      Image($rawfile('more.png'))
        .width(24)
        .height(24)
        .onClick(() => {
          promptAction.showToast({ message: '更多选项' });
        })
    }
    .width('100%')
    .height(60)
    .padding({ left: 20, right: 20 })
    .backgroundColor('#ffffff')
  }

  // 日期和位置信息卡片
  @Builder DateTimeLocationCard() {
    Column({ space: 8 }) {
      Row() {
        Text(this.currentDate)
          .fontSize(16)
          .fontColor('#ffffff')
          .fontWeight(FontWeight.Medium)
        Blank()
        Text(this.currentTime)
          .fontSize(16)
          .fontColor('#ffffff')
          .fontWeight(FontWeight.Medium)
      }
      .width('100%')

      Row({ space: 12 }) {
        Row({ space: 6 }) {
          Image($rawfile('location_icon.png'))
            .width(16)
            .height(16)
          Text(this.currentCity)
            .fontSize(14)
            .fontColor('#ffffff')
        }

        Row({ space: 6 }) {
          Image($rawfile('altitude_icon.png'))
            .width(16)
            .height(16)
          Text(this.altitude + '米')
            .fontSize(14)
            .fontColor('#ffffff')
        }
      }
      .width('100%')
      .justifyContent(FlexAlign.Start)
    }
    .width('100%')
    .padding(20)
    .backgroundColor('#4a6af9')
    .borderRadius(16)
    .shadow({ radius: 12, color: '#4a6af9', offsetX: 0, offsetY: 4 })
    .opacity(0.95)
  }

  // 环境数据卡片
  @Builder EnvironmentDataCard() {
    Column({ space: 12 }) {
      Text('环境数据')
        .fontSize(16)
        .fontWeight(FontWeight.Medium)
        .fontColor('#1a1a1a')
        .alignSelf(ItemAlign.Start)

      Row({ space: 8 }) {
        Column({ space: 8 }) {
          Row({ space: 6 }) {
            Image($rawfile('temp_env_icon.png'))
              .width(16)
              .height(16)
            Text('环境温度')
              .fontSize(12)
              .fontColor('#666666')
          }
          Text(this.environmentTemperature + '°C')
            .fontSize(18)
            .fontWeight(FontWeight.Bold)
            .fontColor('#ff6b35')
        }
        .padding(12)
        .backgroundColor('#fff5f0')
        .borderRadius(8)
        .flexGrow(1)

        Column({ space: 8 }) {
          Row({ space: 6 }) {
            Image($rawfile('oxygen_env_icon.png'))
              .width(16)
              .height(16)
            Text('氧气浓度')
              .fontSize(12)
              .fontColor('#666666')
          }
          Text(this.oxygenConcentration + '%')
            .fontSize(18)
            .fontWeight(FontWeight.Bold)
            .fontColor('#52c41a')
        }
        .padding(12)
        .backgroundColor('#f0f9ff')
        .borderRadius(8)
        .flexGrow(1)
      }
      .width('100%')
    }
    .width('100%')
    .padding(16)
    .backgroundColor('#ffffff')
    .borderRadius(12)
    .shadow({ radius: 6, color: '#000000', offsetX: 0, offsetY: 2 })
    .opacity(0.95)
  }

  // 监测控制面板
  @Builder MonitorControlPanel() {
    Column({ space: 16 }) {
      Text('设备控制')
        .fontSize(16)
        .fontWeight(FontWeight.Medium)
        .fontColor('#1a1a1a')
        .alignSelf(ItemAlign.Start)

      Row({ space: 12 }) {
        Button(this.isMonitoring ? '停止监测' : '开始监测')
          .flexGrow(1)
          .height(44)
          .fontSize(16)
          .backgroundColor(this.isMonitoring ? '#ff6b35' : '#4a6af9')
          .fontColor('#ffffff')
          .borderRadius(22)
          .onClick(() => {
            this.isMonitoring = !this.isMonitoring;
            promptAction.showToast({
              message: this.isMonitoring ? '开始健康监测' : '停止健康监测'
            });
          })

        Button('同步数据')
          .flexGrow(1)
          .height(44)
          .fontSize(16)
          .backgroundColor('#f0f0f0')
          .fontColor('#1a1a1a')
          .borderRadius(22)
          .onClick(() => {
            promptAction.showToast({ message: '数据同步中...' });
          })
      }
      .width('100%')

      Row({ space: 8 }) {
        Circle({ width: 8, height: 8 })
          .fill(this.isMonitoring ? '#52c41a' : '#ff4d4f')
        Text(this.isMonitoring ? '监测中...' : '监测已停止')
          .fontSize(14)
          .fontColor(this.isMonitoring ? '#52c41a' : '#ff4d4f')
      }
    }
    .width('100%')
    .padding(16)
    .backgroundColor('#ffffff')
    .borderRadius(12)
    .shadow({ radius: 6, color: '#000000', offsetX: 0, offsetY: 2 })
    .opacity(0.95)
  }

  // 实时数据图表区域
  @Builder RealTimeChart() {
    Column({ space: 12 }) {
      Row() {
        Text('实时数据趋势')
          .fontSize(16)
          .fontWeight(FontWeight.Medium)
          .fontColor('#1a1a1a')
        Blank()
        Text('最近1小时')
          .fontSize(12)
          .fontColor('#999999')
      }
      .width('100%')

      Column({ space: 8 }) {
        Row() {
          Text('心率变化')
            .fontSize(14)
            .fontColor('#666666')
          Blank()
          Text(this.heartRate + ' 次/分')
            .fontSize(14)
            .fontColor('#4a6af9')
            .fontWeight(FontWeight.Medium)
        }
        .width('100%')

        Row({ space: 2 }) {
          Row().width(6).height(20).backgroundColor('#4a6af9').borderRadius(2)
          Row().width(6).height(25).backgroundColor('#4a6af9').borderRadius(2)
          Row().width(6).height(30).backgroundColor('#4a6af9').borderRadius(2)
          Row().width(6).height(35).backgroundColor('#4a6af9').borderRadius(2)
          Row().width(6).height(40).backgroundColor('#4a6af9').borderRadius(2)
          Row().width(6).height(35).backgroundColor('#4a6af9').borderRadius(2)
          Row().width(6).height(30).backgroundColor('#4a6af9').borderRadius(2)
          Row().width(6).height(25).backgroundColor('#4a6af9').borderRadius(2)
          Row().width(6).height(20).backgroundColor('#4a6af9').borderRadius(2)
          Row().width(6).height(25).backgroundColor('#4a6af9').borderRadius(2)
        }
        .width('100%')
        .height(50)
        .justifyContent(FlexAlign.Center)
        .alignItems(VerticalAlign.Bottom)
      }
      .width('100%')
      .padding(12)
      .backgroundColor('#f8f9ff')
      .borderRadius(8)
    }
    .width('100%')
    .padding(16)
    .backgroundColor('#ffffff')
    .borderRadius(12)
    .shadow({ radius: 6, color: '#000000', offsetX: 0, offsetY: 2 })
    .opacity(0.95)
  }

  // 健康建议
  @Builder HealthAdvice() {
    Column({ space: 12 }) {
      Text('健康建议')
        .fontSize(16)
        .fontWeight(FontWeight.Medium)
        .fontColor('#1a1a1a')
        .alignSelf(ItemAlign.Start)

      Column({ space: 10 }) {
        Row({ space: 12 }) {
          Image($rawfile('tip_icon.png'))
            .width(18)
            .height(18)
          Text('保持规律作息，建议每晚睡眠7-8小时')
            .fontSize(13)
            .fontColor('#666666')
            .flexGrow(1)
        }

        Row({ space: 12 }) {
          Image($rawfile('tip_icon.png'))
            .width(18)
            .height(18)
          Text('适量运动，每周至少150分钟中等强度运动')
            .fontSize(13)
            .fontColor('#666666')
            .flexGrow(1)
        }

        Row({ space: 12 }) {
          Image($rawfile('tip_icon.png'))
            .width(18)
            .height(18)
          Text('均衡饮食，减少盐分和油脂摄入')
            .fontSize(13)
            .fontColor('#666666')
            .flexGrow(1)
        }
      }
    }
    .width('100%')
    .padding(16)
    .backgroundColor('#ffffff')
    .borderRadius(12)
    .shadow({ radius: 6, color: '#000000', offsetX: 0, offsetY: 2 })
    .opacity(0.95)
  }

  build() {
    Stack({ alignContent: Alignment.TopStart }) {
      // 背景图片 - 放在Stack的最底层
      Image($rawfile('app.media.backgroud.png'))
        .width('100%')
        .height('100%')
        .objectFit(ImageFit.Cover)
        .opacity(0.9)

      // 主要内容区域
      Column({ space: 0 }) {
        // 顶部导航栏
        this.TopBar()

        // 可滚动内容区域
        Scroll() {
          Column({ space: 16 }) {
            // 日期和位置卡片
            Column() {
              this.DateTimeLocationCard()
            }
            .margin({ top: 16, left: 20, right: 20 })

            // 监测控制面板
            Column() {
              this.MonitorControlPanel()
            }
            .margin({ left: 20, right: 20 })

            // 生命体征数据网格
            Column({ space: 20 }) {
              Text('生命体征')
                .fontSize(18)
                .fontWeight(FontWeight.Bold)
                .fontColor('#1a1a1a')
                .alignSelf(ItemAlign.Start)
                .margin({ bottom: 12 })

              // 使用 Row 布局，增加列间距
              Row({ space: 24 }) { // 增加列间距到24px
                // 第一列
                Column({ space: 16 }) { // 增加行间距到16px
                  // 血氧
                  Column({ space: 10 }) {
                    Row({ space: 8 }) {
                      Image($rawfile('oxygen_icon.png'))
                        .width(22)
                        .height(22)
                      Text('血氧')
                        .fontSize(15)
                        .fontColor('#666666')
                        .fontWeight(FontWeight.Medium)
                    }
                    .justifyContent(FlexAlign.Start)
                    .width('100%')

                    Text(this.bloodOxygen.toString())
                      .fontSize(24)
                      .fontWeight(FontWeight.Bold)
                      .fontColor('#4a6af9')
                      .margin({ top: 8 })

                    Text('%')
                      .fontSize(14)
                      .fontColor('#999999')
                      .margin({ top: 4 })
                  }
                  .width('100%')
                  .padding(18)
                  .backgroundColor('#ffffff')
                  .border({ width: 1, color: 'rgba(74, 106, 249, 0.2)' })
                  .borderRadius(14)
                  .shadow({ radius: 6, color: 'rgba(74, 106, 249, 0.1)', offsetX: 0, offsetY: 3 })
                  .opacity(0.95)

                  // 体温
                  Column({ space: 10 }) {
                    Row({ space: 8 }) {
                      Image($rawfile('temp_env_icon.png'))
                        .width(22)
                        .height(22)
                      Text('睡眠')
                        .fontSize(15)
                        .fontColor('#666666')
                        .fontWeight(FontWeight.Medium)
                    }
                    .justifyContent(FlexAlign.Start)
                    .width('100%')

                    Text(this.bodyTemperature.toString())
                      .fontSize(24)
                      .fontWeight(FontWeight.Bold)
                      .fontColor('#ff6b35')
                      .margin({ top: 8 })

                    Text('°C')
                      .fontSize(14)
                      .fontColor('#999999')
                      .margin({ top: 4 })
                  }
                  .width('100%')
                  .padding(18)
                  .backgroundColor('#ffffff')
                  .border({ width: 1, color: 'rgba(255, 107, 53, 0.2)' })
                  .borderRadius(14)
                  .shadow({ radius: 6, color: 'rgba(255, 107, 53, 0.1)', offsetX: 0, offsetY: 3 })
                  .opacity(0.95)

                  // 血压
                  Column({ space: 10 }) {
                    Row({ space: 8 }) {
                      Image($rawfile('pressure_icon.png'))
                        .width(22)
                        .height(22)
                      Text('血压')
                        .fontSize(15)
                        .fontColor('#666666')
                        .fontWeight(FontWeight.Medium)
                    }
                    .justifyContent(FlexAlign.Start)
                    .width('100%')

                    Text(`${this.systolicPressure}/${this.diastolicPressure}`)
                      .fontSize(24)
                      .fontWeight(FontWeight.Bold)
                      .fontColor('#fa8c16')
                      .margin({ top: 8 })

                    Text('mmHg')
                      .fontSize(14)
                      .fontColor('#999999')
                      .margin({ top: 4 })
                  }
                  .width('100%')
                  .padding(18)
                  .backgroundColor('#ffffff')
                  .border({ width: 1, color: 'rgba(250, 140, 22, 0.2)' })
                  .borderRadius(14)
                  .shadow({ radius: 6, color: 'rgba(250, 140, 22, 0.1)', offsetX: 0, offsetY: 3 })
                  .opacity(0.95)
                }
                .width('48%')

                // 第二列
                Column({ space: 16 }) { // 增加行间距到16px
                  // 心率
                  Column({ space: 10 }) {
                    Row({ space: 8 }) {
                      Image($rawfile('heart_icon.png'))
                        .width(22)
                        .height(22)
                      Text('心率')
                        .fontSize(15)
                        .fontColor('#666666')
                        .fontWeight(FontWeight.Medium)
                    }
                    .justifyContent(FlexAlign.Start)
                    .width('100%')

                    Text(this.heartRate.toString())
                      .fontSize(24)
                      .fontWeight(FontWeight.Bold)
                      .fontColor('#ff4d4f')
                      .margin({ top: 8 })

                    Text('次/分')
                      .fontSize(14)
                      .fontColor('#999999')
                      .margin({ top: 4 })
                  }
                  .width('100%')
                  .padding(18)
                  .backgroundColor('#ffffff')
                  .border({ width: 1, color: 'rgba(255, 77, 79, 0.2)' })
                  .borderRadius(14)
                  .shadow({ radius: 6, color: 'rgba(255, 77, 79, 0.1)', offsetX: 0, offsetY: 3 })
                  .opacity(0.95)

                  // 呼吸
                  Column({ space: 10 }) {
                    Row({ space: 8 }) {
                      Image($rawfile('breathing_icon.png'))
                        .width(22)
                        .height(22)
                      Text('呼吸')
                        .fontSize(15)
                        .fontColor('#666666')
                        .fontWeight(FontWeight.Medium)
                    }
                    .justifyContent(FlexAlign.Start)
                    .width('100%')

                    Text(this.breathingRate.toString())
                      .fontSize(24)
                      .fontWeight(FontWeight.Bold)
                      .fontColor('#52c41a')
                      .margin({ top: 8 })

                    Text('次/分')
                      .fontSize(14)
                      .fontColor('#999999')
                      .margin({ top: 4 })
                  }
                  .width('100%')
                  .padding(18)
                  .backgroundColor('#ffffff')
                  .border({ width: 1, color: 'rgba(82, 196, 26, 0.2)' })
                  .borderRadius(14)
                  .shadow({ radius: 6, color: 'rgba(82, 196, 26, 0.1)', offsetX: 0, offsetY: 3 })
                  .opacity(0.95)
                }
                .width('48%')
              }
              .width('100%')
              .justifyContent(FlexAlign.SpaceBetween)
            }
            .width('100%')
            .padding(20)
            .backgroundColor('#f8f9ff')
            .borderRadius(16)
            .shadow({ radius: 8, color: 'rgba(0, 0, 0, 0.1)', offsetX: 0, offsetY: 4 })
            .margin({ left: 20, right: 20 })

            // 环境数据
            Column() {
              this.EnvironmentDataCard()
            }
            .margin({ left: 20, right: 20 })

            // 实时数据图表
            Column() {
              this.RealTimeChart()
            }
            .margin({ left: 20, right: 20 })

            // 健康建议
            Column() {
              this.HealthAdvice()
            }
            .margin({ left: 20, right: 20, bottom: 20 })
          }
          .width('100%')
        }
        .flexGrow(1)
        .width('100%')
        .scrollBar(BarState.Auto)
        .scrollable(ScrollDirection.Vertical)

        // 底部导航栏
        this.TabBar()
      }
      .width('100%')
      .height('100%')
    }
    .width('100%')
    .height('84%')
    .backgroundColor('#f5f5f5')
  }


  loadData(userId: string, cityId: string, measureDate: string) {
    // 加载数据
    let url = '/user/vital'
    //let params = '{ "userId": "LS202511001", "measureDate":"2025-11-03" }'
    let params = '{ "userId": "'+ userId + '", "measureDate": "' + measureDate + '" }';
    console.log('-----------')
    console.log(params);

    // 加载数据
    NetApi.getList(url, params)
      .then((res: ESObject) => {

        this.vitalList = res;
        console.log( res );

        this.bloodOxygen = res[0]['SpO2'];  // 血氧
        this.breathingRate = res[0]['breath']; // 呼吸
        this.heartRate = res[0]['heart']; // 心率
        this.systolicPressure = res[0]['SBP']; // 收缩压
        this.diastolicPressure = res[0]['DBP'];// 舒张压
        this.bodyTemperature = res[0]['sleep_quality']; // sleep
        //this.isMonitoring = res[0]['id']; // 监测状态
        //this.batteryLevel= res[0]['breath']; // 设备电量

      })

    // 加载数据
    url = '/city/temp'
    //params = '{ "cityId": "010", "measureDate":"2025-11-03" }'
    params = '{ "cityId": "'+ cityId + '", "measureDate": "' + measureDate + '" }';
    console.log(params);
    // 加载数据
    NetApi.getList(url, params)
      .then((res: ESObject) => {
        //console.log(res.msg)
        this.cityList = res;

        //
        // 环境数据
        this.currentCity = res[0]['cityName'];
        this.altitude= res[0]['altitude'];  // 海拔(米)
        this.environmentTemperature= res[0]['maxTemp'];  // 环境温度
        this.oxygenConcentration= res[0]['oxygen'];  // 氧气浓度(%)

      })
  }
}