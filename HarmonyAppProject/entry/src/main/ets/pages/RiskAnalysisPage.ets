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

// RiskAnalysisPage.ets
import router from '@ohos.router';
import promptAction from '@ohos.promptAction';

import prompt from '@system.prompt';
import { window } from '@kit.ArkUI';
import NetApi from '../utils/NetApi'
import { BottomOffset } from '@kit.ArkUI';
import  PreferencesUtil  from '../utils/PreferencesUtil'
import CityModel from '../models/CityModel'
import VitalModel from '../models/VitalModel'


// 明确定义所有接口类型
interface HealthStatus {
  level: string;
  confidence: number;
  description: string;
  vitalSigns: VitalSigns;
  trends: Trends;
  keyFindings: string;
  suggestions: string;
}

interface VitalSigns {
  bloodOxygen: string;
  heartRate: string;
  bloodPressure: string;
}

interface Trends {
  bloodOxygen: string;
  heartRate: string;
  bloodPressure: string;
}

interface ChartData {
  bloodOxygen: number[];
  heartRate: number[];
  timestamps: string[];
}

interface RiskDistributionItem {
  type: string;
  value: number;
  color: ResourceColor | string;
}

interface FeatureImportanceItem {
  name: string;
  value: number;
  color: ResourceColor | string;
}

@Entry
@Component
struct RiskAnalysisPage {
  @State currentTab: number = 0; // 当前选中的底部标签：0-风险分析，1-实时监测，2-我的

  // 风险分析数据
  @State healthStatus: HealthStatus = {
    level: '中等风险',
    confidence: 0.7,
    description: '您的健康状况处于中等风险，多项指标异常，需要密切关注。',
    vitalSigns: {
      bloodOxygen: '偏低',
      heartRate: '偏高',
      bloodPressure: '正常'
    },
    trends: {
      bloodOxygen: '下降',
      heartRate: '上升',
      bloodPressure: '稳定'
    },
    keyFindings: '血氧和心率异常，需要密切关注。',
    suggestions: '减少活动量，增加休息，必要时吸氧。'
  };

  @State chartData: ChartData = {
    bloodOxygen: [95, 93, 91, 89, 87, 85, 83],
    heartRate: [72, 75, 78, 82, 85, 88, 90],
    timestamps: ['09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00']
  };

  @State riskDistribution: RiskDistributionItem[] = [
    { type: '无风险', value: 25, color: '#52C41A' },
    { type: '轻度风险', value: 35, color: '#FAAD14' },
    { type: '中等风险', value: 25, color: '#FA8C16' },
    { type: '重度风险', value: 15, color: '#F5222D' }
  ];

  @State featureImportance: FeatureImportanceItem[] = [
    { name: '血氧', value: 0.20, color: '#1890FF' },
    { name: '心率', value: 0.18, color: '#FF4D4F' },
    { name: '呼吸', value: 0.15, color: '#13C2C2' },
    { name: '收缩压', value: 0.12, color: '#722ED1' },
    { name: '舒张压', value: 0.10, color: '#EB2F96' },
    { name: '阻抗', value: 0.08, color: '#FA8C16' },
    { name: '温度', value: 0.07, color: '#52C41A' },
    { name: '睡眠', value: 0.05, color: '#FAAD14' }
  ];

  vitalList: ESObject = [];
  cityList: ESObject = [];

  cityId = '';
  userId = '';
  measureDate = '';
  deviceNo ='';

  riskLevel = 0;  // 高反风险等级
  riskReport = ''; // 高反风险说明

  // 模拟实时风险数据
  @State realTimeRiskData: number[] = [65, 72, 58, 80, 45, 90, 75, 60];
  @State realTimeRiskLabels: string[] = ['血氧', '心率', '呼吸', '血压', '体温', '睡眠', '活动', '海拔'];



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
      // 风险分析 - 使用现有的heart图标
      Column() {
        Image($rawfile(this.currentTab === 0 ? 'risk_active.png' : 'risk_inactive.png'))
          .width(this.currentTab === 0 ? 32 : 28)
          .height(this.currentTab === 0 ? 32 : 28)
          .margin({ bottom: 4 })
        Text('风险分析')
          .fontSize(this.currentTab === 0 ? 13 : 12)
          .fontColor(this.currentTab === 0 ? '#1890ff' : '#999999')
          .fontWeight(this.currentTab === 0 ? FontWeight.Medium : FontWeight.Normal)
      }
      .width('33.3%')
      .height(60)
      .justifyContent(FlexAlign.Center)
      .onClick(() => {
        this.currentTab = 0;
        router.replaceUrl({
          url: 'pages/RiskAnalysisPage',
          params: { fromPage: 'RiskAnalysisPage' }
        }).then(() => {
          console.info('跳转到风险分析页面成功');
        })
      })

      // 实时监测
      Column() {
        Image($rawfile(this.currentTab === 1 ? 'heart_active.png' : 'heart_inactive.png'))
          .width(this.currentTab === 1 ? 32 : 28)
          .height(this.currentTab === 1 ? 32 : 28)
          .margin({ bottom: 4 })
        Text('实时监测')
          .fontSize(this.currentTab === 1 ? 13 : 12)
          .fontColor(this.currentTab === 1 ? '#1890ff' : '#999999')
          .fontWeight(this.currentTab === 1 ? FontWeight.Medium : FontWeight.Normal)
      }
      .width('33.3%')
      .height(60)
      .justifyContent(FlexAlign.Center)
      .onClick(() => {
        this.currentTab = 1;
        router.replaceUrl({
          url: 'pages/HealthMonitorPage',
          params: { fromPage: 'RiskAnalysisPage' }
        }).then(() => {
          console.info('跳转到健康监测页面成功');
        })
      })

      // 我的 - 使用ic_about图标
      Column() {
        Image($rawfile(this.currentTab === 2 ? 'profile_active.png' : 'profile_inactive.png'))
          .width(this.currentTab === 2 ? 32 : 28)
          .height(this.currentTab === 2 ? 32 : 28)
          .margin({ bottom: 4 })
        Text('我的')
          .fontSize(this.currentTab === 2 ? 13 : 12)
          .fontColor(this.currentTab === 2 ? '#1890ff' : '#999999')
          .fontWeight(this.currentTab === 2 ? FontWeight.Medium : FontWeight.Normal)
      }
      .width('33.3%')
      .height(60)
      .justifyContent(FlexAlign.Center)
      .onClick(() => {
        this.currentTab = 2;
        router.replaceUrl({
          url: 'pages/ProfilePage',
          params: { fromPage: 'RiskAnalysisPage' }
        }).then(() => {
          console.info('跳转到个人中心页面成功');
        })
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

      Text('风险分析报告')
        .fontSize(18)
        .fontWeight(FontWeight.Medium)
        .fontColor('#1a1a1a')
        .margin({ left: 16 })

      Blank()

      Text('刷新')
        .fontSize(16)
        .fontColor('#1890ff')
        .onClick(() => {
          this.refreshData();
        })
    }
    .width('100%')
    .height(60)
    .padding({ left: 20, right: 20 })
    .backgroundColor('#ffffff')
  }

  private refreshData(): void {
    try {
      // 模拟刷新数据
      this.healthStatus.confidence = Math.random() * 0.3 + 0.6;
      this.realTimeRiskData = this.realTimeRiskData.map(() => Math.floor(Math.random() * 40) + 40);
      promptAction.showToast({ message: '数据已刷新' });
    } catch (error) {
      console.error('刷新数据失败:', error);
      promptAction.showToast({ message: '刷新失败，请重试' });
    }
  }

  // 健康状态卡片
  @Builder HealthStatusCard() {
    Column({ space: 10 }) {
      Row({ space: 10 }) {
        Text(this.healthStatus.level)
          .fontSize(20)
          .fontWeight(FontWeight.Bold)
          .fontColor('#fff')
        Text(`置信度: ${(this.healthStatus.confidence * 100).toFixed(0)}%`)
          .fontSize(14)
          .fontColor('rgba(255,255,255,0.8)')
          .backgroundColor('rgba(255,255,255,0.2)')
          .padding(4)
          .borderRadius(10)
      }
      .width('100%')
      .justifyContent(FlexAlign.SpaceBetween)

      Text(this.healthStatus.description)
        .fontSize(14)
        .fontColor('#fff')
        .lineHeight(20)
    }
    .width('100%')
    .padding(20)
    .backgroundColor('#FF7A45')
    .borderRadius(12)
    .opacity(0.95)
  }

  // 生命体征卡片
  @Builder VitalSignsCard() {
    Column({ space: 15 }) {
      Text('当前生命体征')
        .fontSize(18)
        .fontWeight(FontWeight.Bold)
        .fontColor('#333')

      Row({ space: 10 }) {
        Column({ space: 5 }) {
          Text('血氧饱和度')
            .fontSize(12)
            .fontColor('#666')
          Text(this.healthStatus.vitalSigns.bloodOxygen)
            .fontSize(16)
            .fontWeight(FontWeight.Bold)
            .fontColor('#F5222D')
        }

        Column({ space: 5 }) {
          Text('心率')
            .fontSize(12)
            .fontColor('#666')
          Text(this.healthStatus.vitalSigns.heartRate)
            .fontSize(16)
            .fontWeight(FontWeight.Bold)
            .fontColor('#FAAD14')
        }

        Column({ space: 5 }) {
          Text('血压')
            .fontSize(12)
            .fontColor('#666')
          Text(this.healthStatus.vitalSigns.bloodPressure)
            .fontSize(16)
            .fontWeight(FontWeight.Bold)
            .fontColor('#52C41A')
        }
      }
      .width('100%')
      .justifyContent(FlexAlign.SpaceBetween)
    }
    .width('100%')
    .padding(20)
    .backgroundColor('#fff')
    .borderRadius(12)
    .shadow({ radius: 8, color: '#000000', offsetX: 0, offsetY: 2 })
    .opacity(0.95)
  }

  // 趋势分析卡片
  @Builder TrendAnalysisCard() {
    Column({ space: 15 }) {
      Text('趋势分析')
        .fontSize(18)
        .fontWeight(FontWeight.Bold)
        .fontColor('#333')

      // 血氧趋势
      Column({ space: 10 }) {
        Text('血氧饱和度趋势 (%)')
          .fontSize(14)
          .fontColor('#333')
        Row({ space: 5 }) {
          ForEach(this.chartData.bloodOxygen, (item: number, index: number) => {
            Column({ space: 2 }) {
              Text(item.toString())
                .fontSize(12)
                .fontColor('#1890FF')
                .fontWeight(FontWeight.Bold)
              Text(this.chartData.timestamps[index])
                .fontSize(10)
                .fontColor('#666')
            }
            .alignItems(HorizontalAlign.Center)
            .padding(8)
            .backgroundColor('#f0f8ff')
            .borderRadius(4)
          })
        }
        .width('100%')
        .justifyContent(FlexAlign.SpaceAround)
        .padding(10)
        .backgroundColor('#fafafa')
        .borderRadius(8)
      }

      // 心率趋势
      Column({ space: 10 }) {
        Text('心率趋势 (次/分钟)')
          .fontSize(14)
          .fontColor('#333')
        Row({ space: 5 }) {
          ForEach(this.chartData.heartRate, (item: number, index: number) => {
            Column({ space: 2 }) {
              Text(item.toString())
                .fontSize(12)
                .fontColor('#FF4D4F')
                .fontWeight(FontWeight.Bold)
              Text(this.chartData.timestamps[index])
                .fontSize(10)
                .fontColor('#666')
            }
            .alignItems(HorizontalAlign.Center)
            .padding(8)
            .backgroundColor('#fff2f0')
            .borderRadius(4)
          })
        }
        .width('100%')
        .justifyContent(FlexAlign.SpaceAround)
        .padding(10)
        .backgroundColor('#fafafa')
        .borderRadius(8)
      }

      Row({ space: 10 }) {
        Column({ space: 5 }) {
          Text('血氧趋势')
            .fontSize(12)
            .fontColor('#666')
          Text(this.healthStatus.trends.bloodOxygen)
            .fontSize(16)
            .fontWeight(FontWeight.Bold)
            .fontColor('#F5222D')
        }

        Column({ space: 5 }) {
          Text('心率趋势')
            .fontSize(12)
            .fontColor('#666')
          Text(this.healthStatus.trends.heartRate)
            .fontSize(16)
            .fontWeight(FontWeight.Bold)
            .fontColor('#FAAD14')
        }

        Column({ space: 5 }) {
          Text('血压趋势')
            .fontSize(12)
            .fontColor('#666')
          Text(this.healthStatus.trends.bloodPressure)
            .fontSize(16)
            .fontWeight(FontWeight.Bold)
            .fontColor('#52C41A')
        }
      }
      .width('100%')
      .justifyContent(FlexAlign.SpaceBetween)
    }
    .width('100%')
    .padding(20)
    .backgroundColor('#fff')
    .borderRadius(12)
    .shadow({ radius: 8, color: '#000000', offsetX: 0, offsetY: 2 })
    .opacity(0.95)
  }

  // 统计分析卡片
  @Builder StatisticalAnalysisCard() {
    Column({ space: 15 }) {
      Text('统计分析')
        .fontSize(18)
        .fontWeight(FontWeight.Bold)
        .fontColor('#333')

      // 风险等级分布环形图
      Column({ space: 10 }) {
        Text('风险等级分布')
          .fontSize(16)
          .fontColor('#333')
          .fontWeight(FontWeight.Medium)

        Row({ space: 0 }) {
          Column({ space: 5 }) {
            Stack({ alignContent: Alignment.Center }) {
              Column()
                .width(120)
                .height(120)
                .backgroundColor('#f0f0f0')
                .borderRadius(60)

              Column()
                .width(100)
                .height(100)
                .backgroundColor('#fff')
                .borderRadius(50)

              Column()
                .width(60)
                .height(60)
                .backgroundColor('#fafafa')
                .borderRadius(30)

              Column({ space: 2 }) {
                Text('总体')
                  .fontSize(12)
                  .fontColor('#666')
                Text('风险')
                  .fontSize(12)
                  .fontColor('#666')
                Text('68%')
                  .fontSize(16)
                  .fontColor('#F5222D')
                  .fontWeight(FontWeight.Bold)
              }
            }
            .width(120)
            .height(120)

            Text('当前综合风险指数')
              .fontSize(10)
              .fontColor('#666')
          }

          Column({ space: 8 }) {
            ForEach(this.riskDistribution, (item: RiskDistributionItem) => {
              Row({ space: 8 }) {
                Column()
                  .width(12)
                  .height(12)
                  .backgroundColor(item.color as ResourceColor)
                  .borderRadius(6)
                Text(item.type)
                  .fontSize(12)
                  .fontColor('#333')
                  .layoutWeight(1)
                Text(`${item.value}%`)
                  .fontSize(12)
                  .fontColor('#666')
                  .fontWeight(FontWeight.Bold)
              }
              .width('100%')
              .justifyContent(FlexAlign.Start)
            })
          }
          .layoutWeight(1)
          .padding({ left: 15 })
        }
        .width('100%')
        .padding(15)
        .backgroundColor('#fafafa')
        .borderRadius(8)
      }

      // 实时风险评估
      Column({ space: 10 }) {
        Text('实时风险评估')
          .fontSize(16)
          .fontColor('#333')
          .fontWeight(FontWeight.Medium)

        Column({ space: 8 }) {
          ForEach(this.realTimeRiskData, (value: number, index: number) => {
            Row({ space: 10 }) {
              Text(this.realTimeRiskLabels[index])
                .fontSize(12)
                .fontColor('#333')
                .width(40)

              Column() {
                Column()
                  .width(`${value}%`)
                  .height(12)
                  .backgroundColor(this.getRiskColor(value))
                  .borderRadius(6)
              }
              .width('60%')
              .height(12)
              .backgroundColor('#f0f0f0')
              .borderRadius(6)

              Text(`${value}%`)
                .fontSize(10)
                .fontColor(this.getRiskColor(value))
                .fontWeight(FontWeight.Bold)
            }
            .width('100%')
            .justifyContent(FlexAlign.Start)
          })
        }
        .padding(15)
        .backgroundColor('#fafafa')
        .borderRadius(8)
      }

      // 特征重要性图表
      Column({ space: 10 }) {
        Text('特征重要性分析')
          .fontSize(16)
          .fontColor('#333')
          .fontWeight(FontWeight.Medium)

        Column({ space: 8 }) {
          ForEach(this.featureImportance, (item: FeatureImportanceItem) => {
            Row({ space: 10 }) {
              Text(item.name)
                .fontSize(12)
                .fontColor('#333')
                .width(50)

              Column() {
                Column()
                  .width(`${item.value * 100}%`)
                  .height(16)
                  .backgroundColor(item.color as ResourceColor)
                  .borderRadius(8)
              }
              .width('60%')
              .height(16)
              .backgroundColor('#f0f0f0')
              .borderRadius(8)

              Text((item.value * 100).toFixed(1) + '%')
                .fontSize(10)
                .fontColor('#666')
                .fontWeight(FontWeight.Bold)
            }
            .width('100%')
            .justifyContent(FlexAlign.Start)
          })
        }
        .padding(15)
        .backgroundColor('#fafafa')
        .borderRadius(8)
      }

      // 风险趋势预测
      Column({ space: 10 }) {
        Text('风险趋势预测')
          .fontSize(16)
          .fontColor('#333')
          .fontWeight(FontWeight.Medium)

        Row({ space: 5 }) {
          ForEach([30, 45, 60, 75, 68, 55, 40], (value: number, index: number) => {
            Column({ space: 2 }) {
              Text(value.toString() + '%')
                .fontSize(10)
                .fontColor(this.getRiskColor(value))
              Column()
                .width(20)
                .height(value * 0.8)
                .backgroundColor(this.getRiskColor(value))
                .borderRadius(4)
              Text(['过去', '2h', '4h', '6h', '当前', '2h', '4h'][index])
                .fontSize(8)
                .fontColor('#666')
            }
            .alignItems(HorizontalAlign.Center)
            .padding(5)
            .backgroundColor('#f8f8f8')
            .borderRadius(4)
          })
        }
        .width('100%')
        .justifyContent(FlexAlign.SpaceAround)
        .padding(15)
        .backgroundColor('#fafafa')
        .borderRadius(8)
      }
    }
    .width('100%')
    .padding(20)
    .backgroundColor('#fff')
    .borderRadius(12)
    .shadow({ radius: 8, color: '#000000', offsetX: 0, offsetY: 2 })
    .opacity(0.95)
  }

  // 关键发现卡片
  @Builder KeyFindingsCard() {
    Column({ space: 10 }) {
      Text('关键发现')
        .fontSize(18)
        .fontWeight(FontWeight.Bold)
        .fontColor('#333')
      Text(this.healthStatus.keyFindings)
        .fontSize(14)
        .fontColor('#F5222D')
        .lineHeight(20)
    }
    .width('100%')
    .padding(20)
    .backgroundColor('#fff')
    .borderRadius(12)
    .shadow({ radius: 8, color: '#000000', offsetX: 0, offsetY: 2 })
    .opacity(0.95)
  }

  // 建议卡片
  @Builder SuggestionsCard() {
    Column({ space: 10 }) {
      Text('健康建议')
        .fontSize(18)
        .fontWeight(FontWeight.Bold)
        .fontColor('#333')
      Text(`• ${this.healthStatus.suggestions}`)
        .fontSize(14)
        .fontColor('#333')
        .lineHeight(20)
      Text('• 监测血氧和心率变化')
        .fontSize(14)
        .fontColor('#333')
        .lineHeight(20)
      Text('• 避免剧烈运动')
        .fontSize(14)
        .fontColor('#333')
        .lineHeight(20)
      Text('• 及时补充水分')
        .fontSize(14)
        .fontColor('#333')
        .lineHeight(20)
    }
    .width('100%')
    .padding(20)
    .backgroundColor('#fff')
    .borderRadius(12)
    .shadow({ radius: 8, color: '#000000', offsetX: 0, offsetY: 2 })
    .opacity(0.95)
  }

  // 操作按钮
  @Builder ActionButtons() {
    Row({ space: 10 }) {
      Button('返回')
        .width('45%')
        .height(44)
        .backgroundColor('#fff')
        .fontColor('#333')
        .borderRadius(8)
        .onClick(() => this.goBack())

      Button('查看详细报告')
        .width('45%')
        .height(44)
        .backgroundColor('#1890FF')
        .fontColor('#fff')
        .borderRadius(8)
        .onClick(() => this.viewDetailReport())
    }
    .width('100%')
    .justifyContent(FlexAlign.SpaceBetween)
    .margin({ bottom: 20 })
  }

  // 根据风险值获取颜色
  private getRiskColor(value: number): ResourceColor | string {
    if (value >= 80) return '#F5222D'; // 高风险 - 红色
    if (value >= 60) return '#FA8C16'; // 中高风险 - 橙色
    if (value >= 40) return '#FAAD14'; // 中等风险 - 黄色
    if (value >= 20) return '#52C41A'; // 低风险 - 绿色
    return '#13C2C2'; // 极低风险 - 青色
  }

  // 返回上一页
  private goBack(): void {
    try {
      router.back();
    } catch (error) {
      console.error('返回时出错:' + JSON.stringify(error));
    }
  }

  // 查看详细报告
  private viewDetailReport(): void {
    try {
      router.pushUrl({
        url: 'pages/DetailReportPage'
      });
    } catch (error) {
      console.error('跳转到详细报告时出错:' + JSON.stringify(error));
    }
  }

  private loadRiskData(): void {
    try {
      console.log('加载风险分析数据');
    } catch (error) {
      console.error('加载风险分析数据失败:', error);
      promptAction.showToast({ message: '数据加载失败' });
    }
  }

  build() {
    Stack({ alignContent: Alignment.TopStart }) {
      // 背景图片 - 放在Stack的最底层
      Image($rawfile('app.media.backgroud.png')) // 使用rawfile中的背景图片
        .width('100%')
        .height('100%')
        .objectFit(ImageFit.Cover) // 覆盖整个屏幕
        .opacity(0.9) // 设置透明度，避免影响内容阅读

      // 主要内容区域 - 放在背景图片之上
      Column({ space: 0 }) {
        // 顶部导航栏
        this.TopBar()

        // 可滚动的内容区域
        Scroll() {
          Column({ space: 16 }) {
            Column() {
              this.HealthStatusCard()
            }
            .margin({ left: 20, right: 20, top: 20 })

            Column() {
              this.VitalSignsCard()
            }
            .margin({ left: 20, right: 20 })

            Column() {
              this.TrendAnalysisCard()
            }
            .margin({ left: 20, right: 20 })

            Column() {
              this.StatisticalAnalysisCard()
            }
            .margin({ left: 20, right: 20 })

            Column() {
              this.KeyFindingsCard()
            }
            .margin({ left: 20, right: 20 })

            Column() {
              this.SuggestionsCard()
            }
            .margin({ left: 20, right: 20 })

            Column() {
              this.ActionButtons()
            }
            .margin({ left: 20, right: 20, bottom: 20 })
          }
          .width('100%')
        }
        .flexGrow(1)
        .width('100%')
        .scrollBar(BarState.Auto)
        .scrollable(ScrollDirection.Vertical)

        // 底部导航栏 - 固定在底部
        this.TabBar()
      }
      .width('100%')
      .height('100%')
    }
    .width('100%')
    .height('84%')
    .backgroundColor('#f5f5f5') // 设置Stack的背景色，以防图片加载失败
  }

  loadData(userId: string, cityId: string, measureDate: string) {
    // 加载数据
    let url = '/user/risk'
    let params = '{ "userId": "'+ userId + '", "reportDate": "' + measureDate + '" }';
    console.log('-----------')
    console.log(params);

    // 加载数据
    NetApi.getList(url, params)
      .then((res: ESObject) => {

        this.vitalList = res;
        console.log( res );

        this.riskLevel = res[0]['riskLevel'];   // 风险等级
        this.riskReport = res[0]['riskReport']; // 风险说明
        // this.heartRate = res[0]['heart']; // 心率
        // this.systolicPressure = res[0]['SBP']; // 收缩压
        // this.diastolicPressure = res[0]['DBP'];// 舒张压
        // this.bodyTemperature = res[0]['sleep_quality']; // sleep
        //this.isMonitoring = res[0]['id']; // 监测状态
        //this.batteryLevel= res[0]['breath']; // 设备电量

      })

  }
}