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

@Entry
@Component
struct Index {
  @State message: string = '雪域精灵'
  @State countdown: number = 3 // 倒计时状态
  @State timer: number = 0 // 定时器ID

  aboutToAppear() {
    // 启动倒计时定时器
    this.timer = setInterval(() => {
      if (this.countdown > 1) {
        this.countdown -= 1
      } else {
        // 倒计时结束，清除定时器并跳转
        clearInterval(this.timer)
        router.replaceUrl({
          url: 'pages/LoginPage'
        })
      }
    }, 1000)
  }
  

  aboutToDisappear() {
    // 页面消失时清除定时器，防止内存泄漏
    if (this.timer) {
      clearInterval(this.timer)
    }
  }

  build() {
    Column() {
      // 跳过按钮和倒计时 - 使用绝对定位放在右上角
      Row({ space: 8 }) {
        Text(`跳过(${this.countdown}s)`)
          .fontSize(16)
          .fontColor('#1296db')

        // 如果需要更明显的倒计时，可以添加一个圆形进度条
        // Circle({ width: 20, height: 20 })
        //   .fill(Color.Transparent)
        //   .stroke('#1296db')
        //   .strokeWidth(2)
        //   .overlay(
        //     Text(this.countdown.toString())
        //       .fontSize(12)
        //       .fontColor('#1296db')
        //   )
      }
      .position({ x: '80%', y: '5%' })
      .onClick(() => {
        // 清除定时器
        if (this.timer) {
          clearInterval(this.timer)
        }
        // 立即跳转
        router.replaceUrl({
          url: 'pages/LoginPage'
        })
      })

      // 上方空白区域，将内容向下推
      Blank()
        .height('20%') // 使用百分比高度，适配不同屏幕

      // 主内容区域
      Column() {
        // 图标部分
        Image($rawfile('app-icon.jpg'))
          .width(120)
          .height(120)
          .objectFit(ImageFit.Contain)
          .borderRadius(60) // 圆形图标
          .margin({ bottom: 30 })

        // 主标题
        Text(this.message)
          .fontSize(36)
          .fontWeight(FontWeight.Bold)
          .fontColor('#1a1a1a')
          .margin({ bottom: 15 })

        // 副标题
        Text('高原健康智能监测平台')
          .fontSize(24)
          .fontColor('#666666')
          .fontWeight(FontWeight.Medium)
      }
      .alignItems(HorizontalAlign.Center)

      // 使用空白空间将底部文字推到最底部
      Blank()
        .flexGrow(1) // 占据剩余空间

      // 底部标语 - 在最最最下面，底部上面一点
      Text('致力于您的健康生活保驾护航！')
        .fontSize(14)
        .fontColor('#999999')
        .margin({ bottom: 60 }) // 距离底部60像素
    }
    .width('100%')
    .height('100%')
    .justifyContent(FlexAlign.Start) // 改为Start，从上到下排列
    .alignItems(HorizontalAlign.Center)
    .backgroundColor('#f5f5f5')
  }
}