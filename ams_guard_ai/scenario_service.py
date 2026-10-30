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

class ScenarioService:
    def __init__(self):
        """初始化场景化服务模块"""
        self.current_scenario = 'default'
        self.scenarios = {
            'tourism': TourismScenario(),
            'hotel': HotelScenario(),
            'expedition': ExpeditionScenario()
        }
        self.gps_service = GPSService()
    
    def detect_scenario(self, context):
        """检测当前场景
        
        Args:
            context: 上下文信息，包含位置、时间、活动等
        
        Returns:
            str: 场景类型
        """
        # 基于上下文信息检测场景
        # 这里使用简单的规则检测，实际部署时可以使用更复杂的算法
        
        # 检查是否在酒店区域
        if context.get('is_in_hotel', False):
            self.current_scenario = 'hotel'
        # 检查是否在旅游景点
        elif context.get('is_in_tourist_area', False) or context.get('activity', '') == 'tourism':
            self.current_scenario = 'tourism'
        # 检查是否在科考区域
        elif context.get('is_in_expedition_area', False) or context.get('activity', '') == 'expedition':
            self.current_scenario = 'expedition'
        else:
            self.current_scenario = 'default'
        
        print(f"🏞️  检测到当前场景：{self.get_scenario_name()}")
        return self.current_scenario
    
    def get_scenario_name(self):
        """获取场景名称"""
        scenario_names = {
            'tourism': '旅游场景',
            'hotel': '酒店场景',
            'expedition': '科考场景',
            'default': '默认场景'
        }
        return scenario_names.get(self.current_scenario, '未知场景')
    
    def get_scenario_service(self, scenario_type=None):
        """获取场景服务实例
        
        Args:
            scenario_type: 场景类型
        
        Returns:
            ScenarioBase实例
        """
        if scenario_type:
            return self.scenarios.get(scenario_type)
        return self.scenarios.get(self.current_scenario)
    
    def process_scenario(self, scenario_type, user_info, context, physiological_data=None):
        """处理场景相关业务
        
        Args:
            scenario_type: 场景类型
            user_info: 用户信息
            context: 上下文信息
            physiological_data: 生理数据
        
        Returns:
            dict: 处理结果
        """
        scenario_service = self.get_scenario_service(scenario_type)
        if scenario_service:
            return scenario_service.process(user_info, context, physiological_data)
        else:
            return {
                'status': 'error',
                'message': '场景服务不存在'
            }
    
    def get_scenario_recommendations(self, scenario_type, user_info, physiological_data, analysis_result):
        """获取场景相关建议
        
        Args:
            scenario_type: 场景类型
            user_info: 用户信息
            physiological_data: 生理数据
            analysis_result: 分析结果
        
        Returns:
            list: 建议列表
        """
        scenario_service = self.get_scenario_service(scenario_type)
        if scenario_service:
            return scenario_service.get_recommendations(user_info, physiological_data, analysis_result)
        return []

class ScenarioBase:
    def __init__(self):
        """初始化场景基类"""
        self.scenario_type = 'base'
    
    def process(self, user_info, context, physiological_data=None):
        """处理场景业务
        
        Args:
            user_info: 用户信息
            context: 上下文信息
            physiological_data: 生理数据
        
        Returns:
            dict: 处理结果
        """
        return {
            'status': 'success',
            'scenario': self.scenario_type,
            'message': '场景处理完成'
        }
    
    def get_recommendations(self, user_info, physiological_data, analysis_result):
        """获取场景相关建议
        
        Args:
            user_info: 用户信息
            physiological_data: 生理数据
            analysis_result: 分析结果
        
        Returns:
            list: 建议列表
        """
        return []

class TourismScenario(ScenarioBase):
    def __init__(self):
        """初始化旅游场景"""
        super().__init__()
        self.scenario_type = 'tourism'
        self.gps_service = GPSService()
        self.tourist_attractions = self._load_tourist_attractions()
    
    def _load_tourist_attractions(self):
        """加载旅游景点信息"""
        # 这里模拟加载旅游景点信息
        # 实际部署时，这里会从数据库或API加载真实的景点信息
        return [
            {'name': '布达拉宫', 'altitude': 3700, 'location': (29.6528, 91.1709)},
            {'name': '纳木错', 'altitude': 4718, 'location': (30.7733, 90.6417)},
            {'name': '珠峰大本营', 'altitude': 5200, 'location': (28.0170, 86.9206)},
            {'name': '稻城亚丁', 'altitude': 4100, 'location': (29.3047, 100.1860)},
            {'name': '九寨沟', 'altitude': 2000, 'location': (33.2600, 103.9200)}
        ]
    
    def process(self, user_info, context, physiological_data=None):
        """处理旅游场景业务"""
        result = super().process(user_info, context, physiological_data)
        
        # 获取当前位置
        location = context.get('location', self.gps_service.get_current_location())
        
        # 查找附近的旅游景点
        nearby_attractions = self._find_nearby_attractions(location)
        
        # 检查当前海拔是否适合活动
        altitude_warning = self._check_altitude_suitability(
            physiological_data.get('altitude', 0) if physiological_data else 0,
            context.get('planned_activity', '')
        )
        
        result['nearby_attractions'] = nearby_attractions
        result['altitude_warning'] = altitude_warning
        
        return result
    
    def _find_nearby_attractions(self, location, radius=50):
        """查找附近的旅游景点
        
        Args:
            location: 当前位置 (纬度, 经度)
            radius: 搜索半径 (公里)
        
        Returns:
            list: 附近的旅游景点
        """
        nearby = []
        if not location:
            return nearby
        
        # 简单的距离计算
        for attraction in self.tourist_attractions:
            distance = self._calculate_distance(location, attraction['location'])
            if distance <= radius:
                nearby.append({
                    'name': attraction['name'],
                    'altitude': attraction['altitude'],
                    'distance': distance,
                    'location': attraction['location']
                })
        
        # 按距离排序
        nearby.sort(key=lambda x: x['distance'])
        return nearby
    
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
    
    def _check_altitude_suitability(self, altitude, planned_activity):
        """检查当前海拔是否适合活动
        
        Args:
            altitude: 当前海拔
            planned_activity: 计划活动
        
        Returns:
            dict: 海拔适合性评估
        """
        activity_intensity = {
            'rest': 0,
            'light_walking': 1,
            'hiking': 2,
            'climbing': 3,
            'running': 3
        }
        
        intensity = activity_intensity.get(planned_activity, 1)
        
        # 基于海拔和活动强度的适合性评估
        if altitude < 3000:
            suitability = '适合'
            warning = ''
        elif altitude < 4000:
            if intensity <= 1:
                suitability = '适合'
                warning = ''
            else:
                suitability = '较适合'
                warning = '高海拔地区，建议适当减少活动强度'
        elif altitude < 4500:
            if intensity == 0:
                suitability = '适合'
                warning = ''
            elif intensity == 1:
                suitability = '较适合'
                warning = '高海拔地区，建议缓慢活动'
            else:
                suitability = '不适合'
                warning = '高海拔地区，不建议进行高强度活动'
        else:
            if intensity == 0:
                suitability = '较适合'
                warning = '极高海拔地区，建议减少停留时间'
            else:
                suitability = '不适合'
                warning = '极高海拔地区，不建议进行任何活动'
        
        return {
            'altitude': altitude,
            'planned_activity': planned_activity,
            'suitability': suitability,
            'warning': warning
        }
    
    def get_recommendations(self, user_info, physiological_data, analysis_result):
        """获取旅游场景建议"""
        recommendations = []
        
        # 基于风险等级的建议
        risk_level = analysis_result.get('risk_assessment', {}).get('risk_level', 0)
        if risk_level >= 2:
            recommendations.append('您的高原反应风险较高，建议减少活动，增加休息时间。')
        
        # 基于海拔的建议
        altitude = physiological_data.get('altitude', 0)
        if altitude > 4000:
            recommendations.append('当前海拔较高，建议随身携带氧气，避免剧烈运动。')
        
        # 旅游特有的建议
        recommendations.append('在旅游过程中，建议多喝水，保持充足的水分摄入。')
        recommendations.append('避免在高海拔地区饮酒和吸烟，这些会加重高原反应。')
        recommendations.append('建议逐渐适应海拔变化，避免快速上升。')
        
        return recommendations

class HotelScenario(ScenarioBase):
    def __init__(self):
        """初始化酒店场景"""
        super().__init__()
        self.scenario_type = 'hotel'
        self.millimeter_wave_radar = MillimeterWaveRadar()
    
    def process(self, user_info, context, physiological_data=None):
        """处理酒店场景业务"""
        result = super().process(user_info, context, physiological_data)
        
        # 检查是否入住
        if context.get('check_in', False):
            # 启动夜间无感监测模式
            night_monitoring_result = self._start_night_monitoring(user_info)
            result['night_monitoring'] = night_monitoring_result
        
        return result
    
    def _start_night_monitoring(self, user_info):
        """启动夜间无感监测模式
        
        Args:
            user_info: 用户信息
        
        Returns:
            dict: 启动结果
        """
        # 连接房间毫米波雷达
        radar_connected = self.millimeter_wave_radar.connect()
        
        if radar_connected:
            # 启动监测
            self.millimeter_wave_radar.start_monitoring()
            
            return {
                'status': 'success',
                'message': '夜间无感监测模式已启动',
                'radar_connected': True,
                'monitoring_params': {
                    'sleep_quality': True,
                    'breathing_pattern': True,
                    'heart_rate': True,
                    'movement': True
                }
            }
        else:
            return {
                'status': 'error',
                'message': '无法连接毫米波雷达',
                'radar_connected': False
            }
    
    def get_recommendations(self, user_info, physiological_data, analysis_result):
        """获取酒店场景建议"""
        recommendations = []
        
        # 基于睡眠质量的建议
        sleep_quality = physiological_data.get('sleep_quality', 7)
        if sleep_quality < 5:
            recommendations.append('您的睡眠质量较差，建议调整房间温度和湿度，保持舒适的睡眠环境。')
        
        # 酒店特有的建议
        recommendations.append('在酒店休息时，建议保持房间通风，避免缺氧。')
        recommendations.append('睡前避免饮用咖啡、茶等刺激性饮料，有助于提高睡眠质量。')
        recommendations.append('如果感到不适，可以使用房间内的氧气设备（如有）。')
        
        return recommendations

class ExpeditionScenario(ScenarioBase):
    def __init__(self):
        """初始化科考场景"""
        super().__init__()
        self.scenario_type = 'expedition'
        self.team_manager = TeamManager()
    
    def process(self, user_info, context, physiological_data=None):
        """处理科考场景业务"""
        result = super().process(user_info, context, physiological_data)
        
        # 处理团队相关业务
        team_id = context.get('team_id')
        if team_id:
            # 获取团队信息
            team_info = self.team_manager.get_team(team_id)
            result['team_info'] = team_info
            
            # 检查用户是否为队长
            if user_info.get('user_id') == team_info.get('captain_id'):
                # 获取全员健康状态
                team_health_status = self.team_manager.get_team_health_status(team_id)
                result['team_health_status'] = team_health_status
        
        return result
    
    def get_recommendations(self, user_info, physiological_data, analysis_result):
        """获取科考场景建议"""
        recommendations = []
        
        # 基于风险等级的建议
        risk_level = analysis_result.get('risk_assessment', {}).get('risk_level', 0)
        if risk_level >= 2:
            recommendations.append('您的高原反应风险较高，建议立即通知团队其他成员，并考虑下撤到低海拔地区。')
        
        # 科考特有的建议
        recommendations.append('在科考过程中，建议定期记录健康状态，并与团队保持沟通。')
        recommendations.append('携带足够的急救药品和氧气，以应对紧急情况。')
        recommendations.append('遵循团队制定的安全规程，不要单独行动。')
        
        return recommendations

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
        # 例如：使用手机GPS或网络定位
        
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

class MillimeterWaveRadar:
    def __init__(self):
        """初始化毫米波雷达"""
        self.is_connected = False
        self.is_monitoring = False
    
    def connect(self):
        """连接毫米波雷达
        
        Returns:
            bool: 是否连接成功
        """
        # 模拟连接过程
        # 实际部署时，这里会连接真实的毫米波雷达设备
        
        print("📡 正在连接毫米波雷达...")
        # 模拟连接成功
        self.is_connected = True
        print("✅ 毫米波雷达连接成功！")
        
        return self.is_connected
    
    def start_monitoring(self):
        """开始监测"""
        if not self.is_connected:
            print("❌ 雷达未连接，无法开始监测")
            return False
        
        print("🔄 正在启动夜间无感监测...")
        self.is_monitoring = True
        print("✅ 夜间无感监测已启动")
        
        return True
    
    def stop_monitoring(self):
        """停止监测"""
        if not self.is_monitoring:
            return False
        
        print("🔄 正在停止夜间无感监测...")
        self.is_monitoring = False
        print("✅ 夜间无感监测已停止")
        
        return True
    
    def get_monitoring_data(self):
        """获取监测数据
        
        Returns:
            dict: 监测数据
        """
        if not self.is_monitoring:
            return None
        
        # 模拟监测数据
        # 实际部署时，这里会从雷达设备获取真实数据
        
        return {
            'sleep_quality': np.random.uniform(6, 9),
            'breathing_pattern': 'normal',
            'heart_rate': np.random.uniform(60, 80),
            'movement': 'minimal',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

class TeamManager:
    def __init__(self):
        """初始化团队管理器"""
        self.teams = {}
        self._initialize_sample_teams()
    
    def _initialize_sample_teams(self):
        """初始化示例团队"""
        # 创建示例团队
        self.teams['team_001'] = {
            'team_id': 'team_001',
            'team_name': '珠峰科考队',
            'captain_id': 'user_001',
            'members': [
                {'user_id': 'user_001', 'name': '张队长', 'role': 'captain'},
                {'user_id': 'user_002', 'name': '李队员', 'role': 'member'},
                {'user_id': 'user_003', 'name': '王队员', 'role': 'member'}
            ],
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def create_team(self, team_name, captain_id, members):
        """创建团队
        
        Args:
            team_name: 团队名称
            captain_id: 队长ID
            members: 成员列表
        
        Returns:
            dict: 团队信息
        """
        team_id = f"team_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        team = {
            'team_id': team_id,
            'team_name': team_name,
            'captain_id': captain_id,
            'members': members,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        self.teams[team_id] = team
        print(f"👥 团队创建成功：{team_name} (ID: {team_id})")
        
        return team
    
    def get_team(self, team_id):
        """获取团队信息
        
        Args:
            team_id: 团队ID
        
        Returns:
            dict: 团队信息
        """
        return self.teams.get(team_id)
    
    def get_team_health_status(self, team_id):
        """获取团队健康状态
        
        Args:
            team_id: 团队ID
        
        Returns:
            dict: 团队健康状态
        """
        team = self.get_team(team_id)
        if not team:
            return None
        
        # 模拟团队成员健康状态
        # 实际部署时，这里会从数据库或其他服务获取真实的健康状态
        
        team_health_status = {
            'team_id': team_id,
            'team_name': team['team_name'],
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'members_health': []
        }
        
        for member in team['members']:
            # 模拟健康状态
            health_status = {
                'user_id': member['user_id'],
                'name': member['name'],
                'role': member['role'],
                'risk_level': np.random.randint(0, 4),
                'last_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'location': (29.6528 + np.random.uniform(-0.1, 0.1), 
                             91.1709 + np.random.uniform(-0.1, 0.1))
            }
            team_health_status['members_health'].append(health_status)
        
        return team_health_status
    
    def add_member(self, team_id, member):
        """添加团队成员
        
        Args:
            team_id: 团队ID
            member: 成员信息
        
        Returns:
            bool: 是否添加成功
        """
        team = self.get_team(team_id)
        if not team:
            return False
        
        team['members'].append(member)
        print(f"👤 成员 {member['name']} 已添加到团队 {team['team_name']}")
        
        return True
    
    def remove_member(self, team_id, user_id):
        """移除团队成员
        
        Args:
            team_id: 团队ID
            user_id: 用户ID
        
        Returns:
            bool: 是否移除成功
        """
        team = self.get_team(team_id)
        if not team:
            return False
        
        original_length = len(team['members'])
        team['members'] = [member for member in team['members'] 
                         if member['user_id'] != user_id]
        
        if len(team['members']) < original_length:
            print(f"👤 成员 {user_id} 已从团队 {team['team_name']} 移除")
            return True
        
        return False
