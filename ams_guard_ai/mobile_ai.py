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

import numpy as np
import pandas as pd
from datetime import datetime
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib
import os

class MobileAIModel:
    def __init__(self, model_type='svm_rf'):
        """初始化移动端AI模型
        
        Args:
            model_type: 模型类型，可选值: 'svm_rf', 'tensorflow_lite', 'openharmony_ai'
        """
        self.model_type = model_type
        self.model_loaded = False
        self.scaler = None
        self.svm_model = None
        self.rf_model = None
        self.feature_names = ['SpO2', 'HR', 'RR', 'SBP', 'DBP', 'altitude', 'temperature', 'sleep_quality']
        self.model_files = {
            'svm': 'svm_model.pkl',
            'rf': 'rf_model.pkl',
            'scaler': 'scaler.pkl'
        }
        
        # 加载模型
        self._load_model()
    
    def _load_model(self):
        """加载轻量化AI模型"""
        print(f"🔄 正在加载{self._get_model_name()}模型...")
        
        if self.model_type == 'svm_rf':
            # 尝试加载预训练模型
            try:
                if os.path.exists(self.model_files['svm']) and os.path.exists(self.model_files['rf']) and os.path.exists(self.model_files['scaler']):
                    self.svm_model = joblib.load(self.model_files['svm'])
                    self.rf_model = joblib.load(self.model_files['rf'])
                    self.scaler = joblib.load(self.model_files['scaler'])
                    self.model_loaded = True
                    print(f"✅ {self._get_model_name()}模型加载成功！")
                else:
                    # 如果模型文件不存在，生成模拟数据并训练模型
                    print("ℹ️  模型文件不存在，正在生成模拟数据并训练模型...")
                    self._train_model()
                    self.model_loaded = True
                    print(f"✅ {self._get_model_name()}模型训练并加载成功！")
            except Exception as e:
                print(f"❌ 模型加载失败: {e}")
                # 加载失败时，回退到基于规则的评分系统
                self.model_loaded = True
                print("ℹ️  回退到基于规则的评分系统")
        else:
            # 模拟其他模型加载过程
            # 实际部署时，这里会加载真实的TensorFlow Lite或OpenHarmony AI模型
            self.model_loaded = True
            print(f"✅ {self._get_model_name()}模型加载成功！")
    
    def _get_model_name(self):
        """获取模型名称"""
        if self.model_type == 'svm_rf':
            return "SVM+随机森林"
        elif self.model_type == 'tensorflow_lite':
            return "TensorFlow Lite"
        elif self.model_type == 'openharmony_ai':
            return "OpenHarmony AI"
        return "轻量化AI"
    
    def preprocess_data(self, physiological_data):
        """预处理输入数据"""
        # 确保输入数据包含所有必要特征
        for feature in self.feature_names:
            if feature not in physiological_data:
                physiological_data[feature] = 0.0
        
        # 提取特征值
        input_data = np.array([physiological_data[feature] for feature in self.feature_names])
        
        # 数据标准化（模拟）
        # 实际部署时，这里会使用训练时的scaler参数
        mean_values = np.array([95.0, 80.0, 18.0, 120.0, 80.0, 3500.0, 10.0, 7.0])
        std_values = np.array([3.0, 10.0, 3.0, 15.0, 10.0, 1000.0, 5.0, 2.0])
        
        normalized_data = (input_data - mean_values) / std_values
        return normalized_data
    
    def predict_health_risk(self, physiological_data):
        """预测健康风险
        
        Args:
            physiological_data: 包含生理数据的字典
                SpO2: 血氧饱和度
                HR: 心率
                RR: 呼吸频率
                SBP: 收缩压
                DBP: 舒张压
                altitude: 海拔
                temperature: 温度
                sleep_quality: 睡眠质量
        
        Returns:
            包含风险评估结果的字典
        """
        if not self.model_loaded:
            self._load_model()
        
        # 预处理数据
        input_data = self.preprocess_data(physiological_data)
        
        # 预测风险
        if self.model_type == 'svm_rf' and self.svm_model and self.rf_model:
            # 使用SVM+随机森林模型进行预测
            try:
                # 准备输入数据
                input_features = np.array([physiological_data[feature] for feature in self.feature_names]).reshape(1, -1)
                
                # 使用scaler进行数据标准化
                if self.scaler:
                    input_features_scaled = self.scaler.transform(input_features)
                else:
                    input_features_scaled = input_features
                
                # 获取两个模型的预测结果
                svm_pred = self.svm_model.predict(input_features_scaled)[0]
                rf_pred = self.rf_model.predict(input_features_scaled)[0]
                
                # 集成预测结果（投票法）
                if svm_pred == rf_pred:
                    risk_level = svm_pred
                else:
                    # 投票不一致时，使用基于规则的评分作为参考
                    rule_based_score = self._calculate_risk_score(physiological_data)
                    risk_level = min(3, max(0, int(rule_based_score)))
                
                # 计算风险评分
                risk_score = float(risk_level)
                
            except Exception as e:
                print(f"❌ 模型预测失败: {e}")
                # 预测失败时，回退到基于规则的评分系统
                risk_score = self._calculate_risk_score(physiological_data)
                risk_level = min(3, max(0, int(risk_score)))
        else:
            # 模拟模型预测或使用基于规则的评分系统
            risk_score = self._calculate_risk_score(physiological_data)
            risk_level = min(3, max(0, int(risk_score)))
        
        risk_levels = ['无风险', '轻度风险', '中度风险', '重度风险']
        
        result = {
            'risk_level': risk_level,
            'risk_description': risk_levels[risk_level],
            'risk_score': risk_score,
            'health_metrics': {
                'SpO2': f"{physiological_data['SpO2']:.1f}%",
                'HR': f"{physiological_data['HR']:.1f} 次/分",
                'RR': f"{physiological_data['RR']:.1f} 次/分",
                'altitude': f"{physiological_data['altitude']:.0f} 米",
                'temperature': f"{physiological_data['temperature']:.1f} °C"
            },
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'model_type': self.model_type
        }
        
        return result
    
    def _calculate_risk_score(self, data):
        """计算风险评分"""
        score = 0
        
        # 血氧影响
        if data['SpO2'] < 90:
            score += 2
        elif data['SpO2'] < 95:
            score += 1
        
        # 心率影响
        if data['HR'] > 100:
            score += 1
        if data['HR'] > 120:
            score += 1
        
        # 呼吸频率影响
        if data['RR'] > 24:
            score += 1
        
        # 海拔影响
        altitude_factor = (data['altitude'] - 2000) / 1000
        if altitude_factor > 0:
            score += altitude_factor * 0.5
        
        # 温度影响
        if data['temperature'] < 0:
            score += 0.5
        
        # 睡眠质量影响
        if data['sleep_quality'] < 5:
            score += 1
        
        return score
    
    def _train_model(self):
        """生成模拟数据并训练SVM和随机森林模型"""
        print("🔄 正在生成模拟数据...")
        
        # 生成模拟数据
        n_samples = 1000
        
        # 生成特征数据
        SpO2 = np.random.normal(95, 3, n_samples)
        SpO2 = np.clip(SpO2, 80, 100)
        
        HR = np.random.normal(80, 15, n_samples)
        HR = np.clip(HR, 50, 150)
        
        RR = np.random.normal(18, 4, n_samples)
        RR = np.clip(RR, 10, 30)
        
        SBP = np.random.normal(120, 20, n_samples)
        SBP = np.clip(SBP, 90, 180)
        
        DBP = np.random.normal(80, 15, n_samples)
        DBP = np.clip(DBP, 60, 120)
        
        altitude = np.random.normal(3500, 1000, n_samples)
        altitude = np.clip(altitude, 1000, 5000)
        
        temperature = np.random.normal(10, 10, n_samples)
        temperature = np.clip(temperature, -20, 30)
        
        sleep_quality = np.random.normal(7, 2, n_samples)
        sleep_quality = np.clip(sleep_quality, 1, 10)
        
        # 构建特征矩阵
        X = np.column_stack([SpO2, HR, RR, SBP, DBP, altitude, temperature, sleep_quality])
        
        # 生成标签（基于规则的风险等级）
        y = []
        for i in range(n_samples):
            data = {
                'SpO2': SpO2[i],
                'HR': HR[i],
                'RR': RR[i],
                'SBP': SBP[i],
                'DBP': DBP[i],
                'altitude': altitude[i],
                'temperature': temperature[i],
                'sleep_quality': sleep_quality[i]
            }
            score = self._calculate_risk_score(data)
            risk_level = min(3, max(0, int(score)))
            y.append(risk_level)
        
        y = np.array(y)
        
        # 划分训练集和测试集
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        print(f"📊 数据集划分完成: 训练集 {len(X_train)} 样本, 测试集 {len(X_test)} 样本")
        
        # 数据标准化
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        print("🔄 正在训练SVM模型...")
        # 训练SVM模型
        self.svm_model = SVC(kernel='rbf', C=1.0, gamma='scale', random_state=42)
        self.svm_model.fit(X_train_scaled, y_train)
        
        print("🔄 正在训练随机森林模型...")
        # 训练随机森林模型
        self.rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.rf_model.fit(X_train_scaled, y_train)
        
        # 评估模型
        print("📈 正在评估模型性能...")
        
        # 评估SVM
        svm_pred = self.svm_model.predict(X_test_scaled)
        svm_accuracy = accuracy_score(y_test, svm_pred)
        print(f"SVM模型准确率: {svm_accuracy:.4f}")
        
        # 评估随机森林
        rf_pred = self.rf_model.predict(X_test_scaled)
        rf_accuracy = accuracy_score(y_test, rf_pred)
        print(f"随机森林模型准确率: {rf_accuracy:.4f}")
        
        # 评估集成模型（投票法）
        ensemble_pred = []
        for i in range(len(X_test)):
            if svm_pred[i] == rf_pred[i]:
                ensemble_pred.append(svm_pred[i])
            else:
                # 投票不一致时，使用多数类
                ensemble_pred.append(np.bincount([svm_pred[i], rf_pred[i]]).argmax())
        
        ensemble_accuracy = accuracy_score(y_test, ensemble_pred)
        print(f"集成模型准确率: {ensemble_accuracy:.4f}")
        
        # 保存模型
        print("💾 正在保存模型...")
        joblib.dump(self.svm_model, self.model_files['svm'])
        joblib.dump(self.rf_model, self.model_files['rf'])
        joblib.dump(self.scaler, self.model_files['scaler'])
        
        print("✅ 模型训练完成并保存成功！")
    
    def analyze_health_metrics(self, physiological_data):
        """分析健康指标
        
        Args:
            physiological_data: 包含生理数据的字典
        
        Returns:
            包含健康指标分析的字典
        """
        analysis = {
            'SpO2': {
                'value': physiological_data['SpO2'],
                'status': self._analyze_spo2(physiological_data['SpO2']),
                'recommendation': self._get_spo2_recommendation(physiological_data['SpO2'])
            },
            'HR': {
                'value': physiological_data['HR'],
                'status': self._analyze_hr(physiological_data['HR']),
                'recommendation': self._get_hr_recommendation(physiological_data['HR'])
            },
            'RR': {
                'value': physiological_data['RR'],
                'status': self._analyze_rr(physiological_data['RR']),
                'recommendation': self._get_rr_recommendation(physiological_data['RR'])
            },
            'altitude': {
                'value': physiological_data['altitude'],
                'status': self._analyze_altitude(physiological_data['altitude']),
                'recommendation': self._get_altitude_recommendation(physiological_data['altitude'])
            }
        }
        
        return analysis
    
    def _analyze_spo2(self, spo2):
        """分析血氧饱和度"""
        if spo2 >= 95:
            return "正常"
        elif spo2 >= 90:
            return "轻度降低"
        elif spo2 >= 85:
            return "中度降低"
        else:
            return "重度降低"
    
    def _get_spo2_recommendation(self, spo2):
        """获取血氧饱和度建议"""
        if spo2 >= 95:
            return "血氧饱和度正常，继续保持"
        elif spo2 >= 90:
            return "血氧饱和度轻度降低，建议适当休息"
        elif spo2 >= 85:
            return "血氧饱和度中度降低，建议减少活动强度"
        else:
            return "血氧饱和度重度降低，建议立即休息并考虑吸氧"
    
    def _analyze_hr(self, hr):
        """分析心率"""
        if hr >= 60 and hr <= 100:
            return "正常"
        elif hr > 100 and hr <= 120:
            return "轻度升高"
        elif hr > 120:
            return "明显升高"
        else:
            return "过低"
    
    def _get_hr_recommendation(self, hr):
        """获取心率建议"""
        if hr >= 60 and hr <= 100:
            return "心率正常，继续保持"
        elif hr > 100 and hr <= 120:
            return "心率轻度升高，建议适当休息"
        elif hr > 120:
            return "心率明显升高，建议立即休息并监测"
        else:
            return "心率过低，建议咨询医生"
    
    def _analyze_rr(self, rr):
        """分析呼吸频率"""
        if rr >= 12 and rr <= 20:
            return "正常"
        elif rr > 20 and rr <= 25:
            return "轻度增快"
        elif rr > 25:
            return "明显增快"
        else:
            return "过慢"
    
    def _get_rr_recommendation(self, rr):
        """获取呼吸频率建议"""
        if rr >= 12 and rr <= 20:
            return "呼吸频率正常，继续保持"
        elif rr > 20 and rr <= 25:
            return "呼吸频率轻度增快，建议适当休息"
        elif rr > 25:
            return "呼吸频率明显增快，建议立即休息并监测"
        else:
            return "呼吸频率过慢，建议咨询医生"
    
    def _analyze_altitude(self, altitude):
        """分析海拔"""
        if altitude < 2500:
            return "低海拔"
        elif altitude < 3500:
            return "中海拔"
        elif altitude < 4500:
            return "高海拔"
        else:
            return "极高海拔"
    
    def _get_altitude_recommendation(self, altitude):
        """获取海拔建议"""
        if altitude < 2500:
            return "低海拔地区，一般无高原反应风险"
        elif altitude < 3500:
            return "中海拔地区，建议适当适应"
        elif altitude < 4500:
            return "高海拔地区，建议缓慢上升并注意休息"
        else:
            return "极高海拔地区，建议做好充分准备并携带氧气"
    
    def get_model_info(self):
        """获取模型信息"""
        return {
            'model_type': self.model_type,
            'model_name': self._get_model_name(),
            'feature_names': self.feature_names,
            'model_loaded': self.model_loaded,
            'capabilities': [
                '实时血氧、心率、呼吸频率分析',
                '结合环境数据进行高反风险评估',
                '轻量级部署，适合移动端运行',
                '快速响应，低延迟预测'
            ]
        }

class MobileHealthAnalyzer:
    def __init__(self):
        """初始化移动端健康分析器"""
        self.svm_rf_model = MobileAIModel('svm_rf')
        self.tf_lite_model = MobileAIModel('tensorflow_lite')
        self.openharmony_model = MobileAIModel('openharmony_ai')
        self.current_model = self.svm_rf_model
    
    def switch_model(self, model_type):
        """切换模型类型"""
        if model_type == 'svm_rf':
            self.current_model = self.svm_rf_model
        elif model_type == 'tensorflow_lite':
            self.current_model = self.tf_lite_model
        elif model_type == 'openharmony_ai':
            self.current_model = self.openharmony_model
        print(f"✅ 已切换到{self.current_model._get_model_name()}模型")
    
    def analyze_health(self, physiological_data):
        """分析健康状态
        
        Args:
            physiological_data: 包含生理数据的字典
        
        Returns:
            包含健康分析结果的字典
        """
        # 获取风险评估
        risk_assessment = self.current_model.predict_health_risk(physiological_data)
        
        # 获取健康指标分析
        health_metrics_analysis = self.current_model.analyze_health_metrics(physiological_data)
        
        # 生成综合分析报告
        analysis_report = {
            'risk_assessment': risk_assessment,
            'health_metrics': health_metrics_analysis,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'model_used': self.current_model._get_model_name()
        }
        
        return analysis_report
    
    def get_recommendations(self, analysis_result):
        """根据分析结果生成建议"""
        risk_level = analysis_result['risk_assessment']['risk_level']
        recommendations = []
        
        # 基于风险等级的建议
        if risk_level == 0:
            recommendations.append("您的健康状态良好，继续保持当前的活动强度和作息规律。")
        elif risk_level == 1:
            recommendations.append("您有轻度高原反应风险，建议适当休息，避免剧烈运动。")
        elif risk_level == 2:
            recommendations.append("您有中度高原反应风险，建议减少活动，增加休息时间，考虑吸氧。")
        else:
            recommendations.append("您有重度高原反应风险，建议立即休息，吸氧，并考虑下撤到低海拔地区。")
        
        # 基于健康指标的建议
        for metric, info in analysis_result['health_metrics'].items():
            if info['status'] != "正常":
                recommendations.append(info['recommendation'])
        
        return recommendations
