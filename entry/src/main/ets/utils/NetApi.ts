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

import http from '@ohos.net.http';

class NetAPI {
    //BaseURL = 'http://127.0.0.1:8025'
    BaseURL = 'http://IP:5060'   // 请用真实IP替代

    // 获取列表
    getList(url, params){
        return new Promise((resolve, reject) => {
            // 创建一个http的请求对象，不可复用
            let httpRequest = http.createHttp()
            // 发送网络请求
            httpRequest.request(
                // 请求的URL路径 
                `${ this.BaseURL }${ url }`,
                {
                    // 可选，默认为http.RequestMethod.GET
                    method: http.RequestMethod.POST,
                    // 开发者根据自身业务需要添加header字段
                    header: {
                      'Content-Type': 'application/json'
                    },
                    // 当使用POST请求时此字段用于传递内容
                    extraData:  params,
                    // 可选，指定返回数据的类型
                    expectDataType: http.HttpDataType.STRING
                }
            )
            // 处理响应结果
            .then((resp: http.HttpResponse) => {
                if(resp.responseCode === 200){
                    // 请求成功
                    console.log(resp.result.toString())
                    resolve(JSON.parse(resp.result.toString()))
                }
                else{
                    console.log('查询信息失败：', JSON.stringify(resp))
                    reject('查询信息失败！')
                }
            })
            .catch((err: Error) => {
                // 请求失败
                console.log('失败：', err)
                reject('查询信息失败！')
            })
        })
    }

}

const NetApi = new NetAPI()
export default NetApi