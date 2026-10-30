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

import json
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

class HealthReportGenerator:
    def __init__(self, voice_interaction=None):
        """初始化健康报告生成器
        
        Args:
            voice_interaction: VoiceInteraction实例，用于语音播报
        """
        self.voice_interaction = voice_interaction
        self.report_templates = {
            'summary': "{user_name}，您的健康报告已生成。您的高原反应风险等级为{risk_level}，{risk_description}。{health_status}。",
            'detailed': "{user_name}，您的详细健康报告如下：血氧饱和度{spo2}%，心率{hr}次/分，呼吸频率{rr}次/分，当前海拔{altitude}米，温度{temperature}度。{risk_description}。{recommendations}"
        }
    
    def generate_health_report(self, user_info, analysis_result, include_visuals=True):
        """生成健康报告
        
        Args:
            user_info: 用户信息
            analysis_result: 健康分析结果
            include_visuals: 是否包含可视化内容
        
        Returns:
            dict: 健康报告
        """
        print("📋 正在生成健康报告...")
        
        # 提取用户信息
        user_name = user_info.get('name', '用户')
        user_id = user_info.get('user_id', '未知')
        
        # 提取分析结果
        risk_assessment = analysis_result.get('risk_assessment', {})
        health_metrics = analysis_result.get('health_metrics', {})
        recommendations = analysis_result.get('recommendations', [])
        
        # 生成报告内容
        report = {
            'report_id': self._generate_report_id(),
            'user_info': user_info,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'risk_assessment': risk_assessment,
            'health_metrics': health_metrics,
            'recommendations': recommendations,
            'summary': self._generate_summary(user_name, risk_assessment, health_metrics),
            'detailed': self._generate_detailed(user_name, health_metrics, risk_assessment, recommendations),
            'visuals': {}
        }
        
        # 生成可视化内容
        if include_visuals:
            report['visuals'] = self._generate_visuals(health_metrics, risk_assessment)
        
        print("✅ 健康报告生成完成！")
        return report
    
    def _generate_report_id(self):
        """生成报告ID"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        random_suffix = np.random.randint(1000, 9999)
        return f"REPORT_{timestamp}_{random_suffix}"
    
    def _generate_summary(self, user_name, risk_assessment, health_metrics):
        """生成报告摘要"""
        risk_level = risk_assessment.get('risk_level', 0)
        risk_description = risk_assessment.get('risk_description', '无风险')
        
        # 分析健康状态
        health_status_parts = []
        for metric_name, metric_data in health_metrics.items():
            if metric_data.get('status') != '正常':
                status = metric_data.get('status', '')
                health_status_parts.append(f"{self._get_metric_name(metric_name)}{status}")
        
        health_status = "、".join(health_status_parts) if health_status_parts else "各项健康指标正常"
        
        return self.report_templates['summary'].format(
            user_name=user_name,
            risk_level=risk_level,
            risk_description=risk_description,
            health_status=health_status
        )
    
    def _generate_detailed(self, user_name, health_metrics, risk_assessment, recommendations):
        """生成详细报告"""
        # 提取健康指标值
        spo2 = health_metrics.get('SpO2', {}).get('value', '未知')
        hr = health_metrics.get('HR', {}).get('value', '未知')
        rr = health_metrics.get('RR', {}).get('value', '未知')
        altitude = health_metrics.get('altitude', {}).get('value', '未知')
        temperature = health_metrics.get('temperature', {}).get('value', '未知')
        
        # 提取风险评估
        risk_description = risk_assessment.get('risk_description', '无风险')
        
        # 生成建议文本
        recommendations_text = "建议：" + "。".join(recommendations) if recommendations else "建议：保持当前健康状态。"
        
        return self.report_templates['detailed'].format(
            user_name=user_name,
            spo2=spo2,
            hr=hr,
            rr=rr,
            altitude=altitude,
            temperature=temperature,
            risk_description=risk_description,
            recommendations=recommendations_text
        )
    
    def _get_metric_name(self, metric_code):
        """获取指标名称"""
        metric_names = {
            'SpO2': '血氧饱和度',
            'HR': '心率',
            'RR': '呼吸频率',
            'altitude': '海拔',
            'temperature': '温度'
        }
        return metric_names.get(metric_code, metric_code)
    
    def _generate_visuals(self, health_metrics, risk_assessment):
        """生成可视化内容
        
        Returns:
            dict: 包含可视化内容的字典
        """
        visuals = {
            'health_metrics_chart': self._generate_health_metrics_chart(health_metrics),
            'risk_assessment_chart': self._generate_risk_assessment_chart(risk_assessment),
            'health_card': self._generate_health_card(health_metrics, risk_assessment)
        }
        return visuals
    
    def _generate_health_metrics_chart(self, health_metrics):
        """生成健康指标图表"""
        # 这里模拟生成图表
        # 实际部署时，这里会生成真实的图表并保存
        chart_data = {
            'type': 'bar_chart',
            'title': '健康指标',
            'data': []
        }
        
        for metric_name, metric_data in health_metrics.items():
            if 'value' in metric_data:
                chart_data['data'].append({
                    'metric': self._get_metric_name(metric_name),
                    'value': metric_data['value'],
                    'status': metric_data.get('status', '正常')
                })
        
        return chart_data
    
    def _generate_risk_assessment_chart(self, risk_assessment):
        """生成风险评估图表"""
        # 这里模拟生成图表
        risk_level = risk_assessment.get('risk_level', 0)
        risk_description = risk_assessment.get('risk_description', '无风险')
        
        chart_data = {
            'type': 'gauge_chart',
            'title': '高原反应风险评估',
            'risk_level': risk_level,
            'risk_description': risk_description,
            'severity': self._get_risk_severity(risk_level)
        }
        
        return chart_data
    
    def _generate_health_card(self, health_metrics, risk_assessment):
        """生成健康卡片"""
        # 提取关键指标
        spo2 = health_metrics.get('SpO2', {}).get('value', 'N/A')
        hr = health_metrics.get('HR', {}).get('value', 'N/A')
        rr = health_metrics.get('RR', {}).get('value', 'N/A')
        altitude = health_metrics.get('altitude', {}).get('value', 'N/A')
        
        risk_level = risk_assessment.get('risk_level', 0)
        risk_description = risk_assessment.get('risk_description', '无风险')
        
        health_card = {
            'type': 'health_card',
            'title': '健康状态卡片',
            'metrics': {
                '血氧': f"{spo2}%",
                '心率': f"{hr}次/分",
                '呼吸': f"{rr}次/分",
                '海拔': f"{altitude}米"
            },
            'risk_assessment': {
                'level': risk_level,
                'description': risk_description
            },
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'shareable': True
        }
        
        return health_card
    
    def _get_risk_severity(self, risk_level):
        """获取风险严重程度"""
        severity_levels = ['低', '低', '中', '高']
        return severity_levels[min(risk_level, 3)]
    
    def voice_broadcast_report(self, report, report_type='summary'):
        """语音播报健康报告
        
        Args:
            report: 健康报告
            report_type: 报告类型，'summary'或'detailed'
        """
        if not self.voice_interaction:
            print("❌ 语音播报功能未初始化")
            return False
        
        if report_type == 'summary':
            content = report.get('summary', '')
        else:
            content = report.get('detailed', '')
        
        if content:
            print("🗣️  正在语音播报健康报告...")
            self.voice_interaction.synthesize_speech(content)
            return True
        
        return False
    
    def save_report(self, report, format='json'):
        """保存健康报告
        
        Args:
            report: 健康报告
            format: 保存格式，'json'或'csv'
        
        Returns:
            str: 保存路径
        """
        report_id = report.get('report_id', 'unknown')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if format == 'json':
            file_path = f"health_report_{report_id}_{timestamp}.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
        elif format == 'csv':
            # 提取数据生成CSV
            file_path = f"health_report_{report_id}_{timestamp}.csv"
            self._save_report_as_csv(report, file_path)
        else:
            print("❌ 不支持的格式")
            return None
        
        print(f"💾 健康报告已保存至: {file_path}")
        return file_path
    
    def _save_report_as_csv(self, report, file_path):
        """将报告保存为CSV格式"""
        # 提取数据
        health_metrics = report.get('health_metrics', {})
        risk_assessment = report.get('risk_assessment', {})
        
        # 准备CSV数据
        csv_data = {
            'timestamp': [report.get('timestamp', '')],
            'user_id': [report.get('user_info', {}).get('user_id', '')],
            'user_name': [report.get('user_info', {}).get('name', '')],
            'risk_level': [risk_assessment.get('risk_level', '')],
            'risk_description': [risk_assessment.get('risk_description', '')]
        }
        
        # 添加健康指标
        for metric_name, metric_data in health_metrics.items():
            if 'value' in metric_data:
                csv_data[self._get_metric_name(metric_name)] = [metric_data['value']]
            if 'status' in metric_data:
                csv_data[f"{self._get_metric_name(metric_name)}状态"] = [metric_data['status']]
        
        # 生成CSV文件
        df = pd.DataFrame(csv_data)
        df.to_csv(file_path, index=False, encoding='utf-8-sig')
    
    def generate_shareable_card(self, report):
        """生成可分享的健康卡片
        
        Args:
            report: 健康报告
        
        Returns:
            dict: 可分享的健康卡片
        """
        health_card = report.get('visuals', {}).get('health_card', {})
        
        # 生成分享文本
        share_text = f"【雪域卫士】我的高原健康状态\n"
        share_text += f"风险等级：{health_card.get('risk_assessment', {}).get('description', '无风险')}\n"
        share_text += "健康指标：\n"
        
        for metric, value in health_card.get('metrics', {}).items():
            share_text += f"- {metric}：{value}\n"
        
        share_text += f"检测时间：{health_card.get('timestamp', '')}\n"
        share_text += "#高原健康 #雪域卫士"
        
        shareable_card = {
            'share_text': share_text,
            'health_card': health_card,
            'share_url': self._generate_share_url(report.get('report_id', ''))
        }
        
        return shareable_card
    
    def _generate_share_url(self, report_id):
        """生成分享URL"""
        # 这里模拟生成分享URL
        # 实际部署时，这里会生成真实的分享链接
        return f"https://snowguard.example.com/share/{report_id}"
    
    def get_report_summary(self, report):
        """获取报告摘要
        
        Args:
            report: 健康报告
        
        Returns:
            str: 报告摘要
        """
        return report.get('summary', '无摘要信息')
    
    def get_report_details(self, report):
        """获取报告详情
        
        Args:
            report: 健康报告
        
        Returns:
            str: 报告详情
        """
        return report.get('detailed', '无详细信息')

class HealthReportManager:
    def __init__(self, health_report_generator, database_manager=None):
        """初始化健康报告管理器
        
        Args:
            health_report_generator: HealthReportGenerator实例
            database_manager: DatabaseManager实例
        """
        self.health_report_generator = health_report_generator
        self.database_manager = database_manager
        self.reports = []
    
    def create_report(self, user_info, analysis_result):
        """创建健康报告
        
        Args:
            user_info: 用户信息
            analysis_result: 健康分析结果
        
        Returns:
            dict: 健康报告
        """
        report = self.health_report_generator.generate_health_report(user_info, analysis_result)
        self.reports.append(report)
        
        # 保存到数据库
        if self.database_manager:
            self._save_report_to_database(report)
        
        return report
    
    def _save_report_to_database(self, report):
        """保存报告到数据库"""
        # 这里模拟保存到数据库
        # 实际部署时，这里会将报告保存到真实的数据库
        print(f"💾 报告已保存到数据库: {report.get('report_id')}")
    
    def get_user_reports(self, user_id):
        """获取用户的报告列表
        
        Args:
            user_id: 用户ID
        
        Returns:
            list: 报告列表
        """
        user_reports = [report for report in self.reports 
                       if report.get('user_info', {}).get('user_id') == user_id]
        return user_reports
    
    def get_latest_report(self, user_id):
        """获取用户的最新报告
        
        Args:
            user_id: 用户ID
        
        Returns:
            dict: 最新报告
        """
        user_reports = self.get_user_reports(user_id)
        if user_reports:
            # 按时间戳排序，返回最新的
            user_reports.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            return user_reports[0]
        return None
    
    def generate_report_for_all_users(self, users_info, analysis_results):
        """为所有用户生成报告
        
        Args:
            users_info: 用户信息列表
            analysis_results: 分析结果列表
        
        Returns:
            list: 报告列表
        """
        reports = []
        for user_info, analysis_result in zip(users_info, analysis_results):
            report = self.create_report(user_info, analysis_result)
            reports.append(report)
        return reports
