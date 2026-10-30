# Copyright (C) 2026 PeakGuard Team
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from datetime import datetime
import numpy as np

class AlertRescue:
    def __init__(self, voice_interaction=None, gps_service=None):
        """初始化预警与救援模块
        
        Args:
            voice_interaction: VoiceInteraction实例，用于语音交互
            gps_service: GPSService实例，用于获取位置信息
        """
        self.voice_interaction = voice_interaction
        self.gps_service = gps_service or GPSService()
        self.alert_service = AlertService()
        self.rescue_service = RescueService()
        self.map_service = MapService()
        self.emergency_contacts = []
    
    def set_emergency_contacts(self, contacts):
        """设置紧急联系人
        
        Args:
            contacts: 紧急联系人列表
        """
        self.emergency_contacts = contacts
        print(f"📞 已设置 {len(contacts)} 个紧急联系人")
    
    def check_health_risk(self, physiological_data, analysis_result):
        """检查健康风险并生成预警
        
        Args:
            physiological_data: 生理数据
            analysis_result: 健康分析结果
        
        Returns:
            dict: 风险检查结果
        """
        risk_level = analysis_result.get('risk_assessment', {}).get('risk_level', 0)
        risk_description = analysis_result.get('risk_assessment', {}).get('risk_description', '无风险')
        
        # 基于风险等级生成预警
        if risk_level >= 2:
            # 生成预警信息
            alert_message = f"⚠️  健康预警：您的高原反应风险等级为{risk_level}，{risk_description}。"
            
            # 推送预警信息
            alert_result = self.alert_service.push_alert({
                'type': 'health_risk',
                'level': risk_level,
                'message': alert_message,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            
            return {
                'risk_level': risk_level,
                'alert_generated': True,
                'alert_result': alert_result
            }
        
        return {
            'risk_level': risk_level,
            'alert_generated': False
        }
    
    def call_rescue(self, emergency_type='health_emergency', additional_info=None):
        """呼叫救援
        
        Args:
            emergency_type: 紧急情况类型
            additional_info: 额外信息
        
        Returns:
            dict: 救援呼叫结果
        """
        print("🚨 正在呼叫救援...")
        
        # 获取当前位置
        location = self.gps_service.get_current_location()
        
        # 查找最近的救援点
        nearest_rescue_points = self.map_service.find_nearest_rescue_points(location)
        
        # 生成救援请求
        rescue_request = {
            'emergency_type': emergency_type,
            'location': location,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'additional_info': additional_info,
            'nearest_rescue_points': nearest_rescue_points
        }
        
        # 发送救援请求
        rescue_result = self.rescue_service.send_rescue_request(rescue_request)
        
        # 通知紧急联系人
        if self.emergency_contacts:
            self._notify_emergency_contacts(rescue_request)
        
        # 语音播报救援状态
        if self.voice_interaction:
            rescue_message = f"紧急救援已呼叫，最近的救援点距离您{nearest_rescue_points[0]['distance']:.1f}公里。"
            self.voice_interaction.synthesize_speech(rescue_message)
        
        return {
            'rescue_request': rescue_request,
            'rescue_result': rescue_result,
            'nearest_rescue_points': nearest_rescue_points
        }
    
    def _notify_emergency_contacts(self, rescue_request):
        """通知紧急联系人
        
        Args:
            rescue_request: 救援请求信息
        """
        for contact in self.emergency_contacts:
            notification_message = f"【雪域卫士】紧急通知：您的联系人正在高海拔地区遇到紧急情况。\n"
            notification_message += f"紧急类型：{rescue_request['emergency_type']}\n"
            notification_message += f"时间：{rescue_request['timestamp']}\n"
            if rescue_request['location']:
                lat, lon = rescue_request['location']
                notification_message += f"位置：纬度 {lat:.4f}，经度 {lon:.4f}\n"
            notification_message += "请尽快与对方取得联系。"
            
            print(f"📱 正在通知紧急联系人 {contact['name']} ({contact['phone']})...")
            print(f"   通知内容：{notification_message}")
            # 实际部署时，这里会发送真实的通知
    
    def report_emergency(self, emergency_message, physiological_data=None):
        """语音上报紧急情况
        
        Args:
            emergency_message: 紧急情况描述
            physiological_data: 生理数据
        
        Returns:
            dict: 上报结果
        """
        print(f"🚨 正在上报紧急情况：{emergency_message}")
        
        # 获取当前位置
        location = self.gps_service.get_current_location()
        
        # 生成紧急情况报告
        emergency_report = {
            'message': emergency_message,
            'location': location,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'physiological_data': physiological_data,
            'status': 'reported'
        }
        
        # 发送紧急情况报告
        report_result = self.rescue_service.report_emergency(emergency_report)
        
        # 通知紧急联系人
        if self.emergency_contacts:
            self._notify_emergency_contacts({
                'emergency_type': 'reported_emergency',
                'location': location,
                'timestamp': emergency_report['timestamp'],
                'additional_info': emergency_message
            })
        
        # 语音播报确认
        if self.voice_interaction:
            confirmation_message = "紧急情况已上报，救援服务正在赶来，请保持冷静。"
            self.voice_interaction.synthesize_speech(confirmation_message)
        
        return {
            'emergency_report': emergency_report,
            'report_result': report_result
        }
    
    def get_nearest_medical_facilities(self, location=None):
        """获取最近的医疗机构
        
        Args:
            location: 位置信息，默认为当前位置
        
        Returns:
            list: 最近的医疗机构列表
        """
        if not location:
            location = self.gps_service.get_current_location()
        
        medical_facilities = self.map_service.find_nearest_medical_facilities(location)
        return medical_facilities
    
    def get_rescue_route(self, destination=None):
        """获取救援路线
        
        Args:
            destination: 目的地，默认为最近的救援点
        
        Returns:
            dict: 救援路线信息
        """
        current_location = self.gps_service.get_current_location()
        
        if not destination:
            # 查找最近的救援点
            nearest_rescue_points = self.map_service.find_nearest_rescue_points(current_location)
            if nearest_rescue_points:
                destination = nearest_rescue_points[0]['location']
            else:
                return None
        
        route = self.map_service.get_route(current_location, destination)
        return route

class AlertService:
    def __init__(self):
        """初始化预警服务"""
        self.alert_history = []
    
    def push_alert(self, alert_data):
        """推送预警信息
        
        Args:
            alert_data: 预警数据
        
        Returns:
            dict: 推送结果
        """
        # 模拟推送预警信息
        # 实际部署时，这里会调用真实的推送服务
        
        print(f"📱 正在推送预警：{alert_data['message']}")
        
        # 模拟推送至手机锁屏
        self._push_to_phone_lock_screen(alert_data)
        
        # 模拟推送至手表
        self._push_to_watch(alert_data)
        
        # 记录预警历史
        self.alert_history.append({
            'alert_id': self._generate_alert_id(),
            'data': alert_data,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        
        return {
            'status': 'success',
            'message': '预警推送成功',
            'alert_id': self.alert_history[-1]['alert_id']
        }
    
    def _push_to_phone_lock_screen(self, alert_data):
        """推送至手机锁屏"""
        print(f"🔒 推送至手机锁屏：{alert_data['message']}")
    
    def _push_to_watch(self, alert_data):
        """推送至手表"""
        print(f"⌚ 推送至手表：{alert_data['message']}")
    
    def _generate_alert_id(self):
        """生成预警ID"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        random_suffix = np.random.randint(1000, 9999)
        return f"ALERT_{timestamp}_{random_suffix}"
    
    def get_alert_history(self, limit=10):
        """获取预警历史
        
        Args:
            limit: 限制数量
        
        Returns:
            list: 预警历史
        """
        return self.alert_history[-limit:]

class RescueService:
    def __init__(self):
        """初始化救援服务"""
        self.rescue_requests = []
    
    def send_rescue_request(self, rescue_request):
        """发送救援请求
        
        Args:
            rescue_request: 救援请求数据
        
        Returns:
            dict: 发送结果
        """
        # 模拟发送救援请求
        # 实际部署时，这里会调用真实的救援服务API
        
        print("📞 正在发送救援请求...")
        
        # 生成救援请求ID
        request_id = self._generate_request_id()
        
        # 记录救援请求
        self.rescue_requests.append({
            'request_id': request_id,
            'data': rescue_request,
            'status': 'pending',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        
        # 模拟救援服务响应
        print("✅ 救援请求已发送，正在等待响应...")
        
        return {
            'status': 'success',
            'request_id': request_id,
            'message': '救援请求已发送'
        }
    
    def report_emergency(self, emergency_report):
        """上报紧急情况
        
        Args:
            emergency_report: 紧急情况报告
        
        Returns:
            dict: 上报结果
        """
        # 模拟上报紧急情况
        print("📢 正在上报紧急情况...")
        
        # 生成报告ID
        report_id = self._generate_report_id()
        
        return {
            'status': 'success',
            'report_id': report_id,
            'message': '紧急情况已上报'
        }
    
    def _generate_request_id(self):
        """生成救援请求ID"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        random_suffix = np.random.randint(1000, 9999)
        return f"RESCUE_{timestamp}_{random_suffix}"
    
    def _generate_report_id(self):
        """生成报告ID"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        random_suffix = np.random.randint(1000, 9999)
        return f"REPORT_{timestamp}_{random_suffix}"
    
    def get_rescue_request_status(self, request_id):
        """获取救援请求状态
        
        Args:
            request_id: 救援请求ID
        
        Returns:
            dict: 救援请求状态
        """
        for request in self.rescue_requests:
            if request['request_id'] == request_id:
                return request
        return None

class MapService:
    def __init__(self):
        """初始化地图服务"""
        self.medical_facilities = self._load_medical_facilities()
        self.rescue_points = self._load_rescue_points()
    
    def _load_medical_facilities(self):
        """加载医疗机构信息"""
        # 模拟加载医疗机构信息
        return [
            {'name': '拉萨市人民医院', 'type': 'hospital', 'location': (29.6500, 91.1000), 'contact': '0891-1234567'},
            {'name': '日喀则市人民医院', 'type': 'hospital', 'location': (29.2700, 88.8700), 'contact': '0892-1234567'},
            {'name': '林芝市人民医院', 'type': 'hospital', 'location': (29.6400, 94.2100), 'contact': '0894-1234567'},
            {'name': '昌都市人民医院', 'type': 'hospital', 'location': (31.1500, 97.1800), 'contact': '0895-1234567'},
            {'name': '那曲市人民医院', 'type': 'hospital', 'location': (31.4800, 92.0700), 'contact': '0896-1234567'}
        ]
    
    def _load_rescue_points(self):
        """加载救援点信息"""
        # 模拟加载救援点信息
        return [
            {'name': '拉萨救援中心', 'type': 'rescue_center', 'location': (29.6500, 91.1000), 'contact': '120'},
            {'name': '珠峰救援站', 'type': 'rescue_station', 'location': (28.0170, 86.9206), 'contact': '120'},
            {'name': '纳木错救援点', 'type': 'rescue_point', 'location': (30.7733, 90.6417), 'contact': '120'},
            {'name': '稻城亚丁救援站', 'type': 'rescue_station', 'location': (29.3047, 100.1860), 'contact': '120'},
            {'name': '九寨沟救援中心', 'type': 'rescue_center', 'location': (33.2600, 103.9200), 'contact': '120'}
        ]
    
    def find_nearest_medical_facilities(self, location, limit=3):
        """查找最近的医疗机构
        
        Args:
            location: 当前位置
            limit: 返回数量限制
        
        Returns:
            list: 最近的医疗机构
        """
        if not location:
            return []
        
        # 计算距离并排序
        facilities_with_distance = []
        for facility in self.medical_facilities:
            distance = self._calculate_distance(location, facility['location'])
            facilities_with_distance.append({
                'name': facility['name'],
                'type': facility['type'],
                'location': facility['location'],
                'contact': facility['contact'],
                'distance': distance
            })
        
        # 按距离排序
        facilities_with_distance.sort(key=lambda x: x['distance'])
        
        return facilities_with_distance[:limit]
    
    def find_nearest_rescue_points(self, location, limit=3):
        """查找最近的救援点
        
        Args:
            location: 当前位置
            limit: 返回数量限制
        
        Returns:
            list: 最近的救援点
        """
        if not location:
            return []
        
        # 计算距离并排序
        rescue_points_with_distance = []
        for point in self.rescue_points:
            distance = self._calculate_distance(location, point['location'])
            rescue_points_with_distance.append({
                'name': point['name'],
                'type': point['type'],
                'location': point['location'],
                'contact': point['contact'],
                'distance': distance
            })
        
        # 按距离排序
        rescue_points_with_distance.sort(key=lambda x: x['distance'])
        
        return rescue_points_with_distance[:limit]
    
    def get_route(self, start_location, end_location):
        """获取路线
        
        Args:
            start_location: 起点
            end_location: 终点
        
        Returns:
            dict: 路线信息
        """
        # 模拟获取路线
        distance = self._calculate_distance(start_location, end_location)
        
        # 模拟预计时间（假设平均速度为60公里/小时）
        estimated_time = distance / 60 * 60  # 转换为分钟
        
        return {
            'start_location': start_location,
            'end_location': end_location,
            'distance': distance,
            'estimated_time': estimated_time,
            'steps': [
                {'instruction': '从起点出发', 'distance': 0},
                {'instruction': '沿当前道路行驶', 'distance': distance * 0.5},
                {'instruction': '到达终点', 'distance': distance}
            ]
        }
    
    def _calculate_distance(self, coord1, coord2):
        """计算两个坐标点之间的距离
        
        Args:
            coord1: 第一个坐标 (纬度, 经度)
            coord2: 第二个坐标 (纬度, 经度)
        
        Returns:
            float: 距离 (公里)
        """
        # 使用简单的欧几里得距离计算
        # 实际部署时，应该使用更准确的地理距离计算方法
        lat1, lon1 = coord1
        lat2, lon2 = coord2
        
        # 近似计算，1度纬度约为111公里
        distance = np.sqrt(
            ((lat2 - lat1) * 111) ** 2 +
            ((lon2 - lon1) * 111 * np.cos(np.radians(lat1))) ** 2
        )
        
        return distance

class GPSService:
    def __init__(self):
        """初始化GPS服务"""
        self.is_available = True
    
    def get_current_location(self):
        """获取当前位置
        
        Returns:
            tuple: (纬度, 经度)
        """
        if not self.is_available:
            return None
        
        # 模拟获取位置
        # 实际部署时，这里会调用真实的GPS API
        
        # 返回默认位置（拉萨）
        return (29.6528, 91.1709)
    
    def get_altitude(self, location):
        """获取指定位置的海拔
        
        Args:
            location: 位置 (纬度, 经度)
        
        Returns:
            float: 海拔高度
        """
        # 模拟获取海拔
        # 实际部署时，这里会调用真实的海拔API
        
        # 基于位置的简单模拟
        if location:
            lat, lon = location
            # 模拟不同位置的海拔
            if 29 < lat < 31 and 90 < lon < 92:
                return 3500 + np.random.uniform(-500, 500)
            elif 28 < lat < 29 and 86 < lon < 88:
                return 4500 + np.random.uniform(-500, 500)
            else:
                return 2000 + np.random.uniform(-500, 500)
        return 0
