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

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.preprocessing import StandardScaler
import joblib

class ModelTrainer:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = ['SpO2', 'HR', 'RR', 'SBP', 'DBP', 'altitude', 'temperature', 'sleep_quality']
    
    def load_training_data(self):
        """加载训练数据"""
        print("🔄 正在加载训练数据...")
        query = """
        SELECT SpO2, HR, RR, SBP, DBP, altitude, temperature, sleep_quality, AMS_risk 
        FROM physiological_data
        """
        df = pd.read_sql_query(query, self.db_manager.conn)
        
        X = df[self.feature_names]
        y = df['AMS_risk']
        
        print(f"📊 数据分布 - 风险等级: {dict(y.value_counts().sort_index())}")
        return X, y
    
    def train_model(self):
        """训练随机森林模型"""
        X, y = self.load_training_data()
        
        # 数据标准化
        X_scaled = self.scaler.fit_transform(X)
        
        # 划分训练集和测试集
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # 创建并训练随机森林模型
        print("🔄 正在训练随机森林模型...")
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42
        )
        
        self.model.fit(X_train, y_train)
        
        # 预测和评估
        y_pred = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"✅ 随机森林模型训练完成！")
        print(f"🎯 测试集准确率: {accuracy:.4f}")
        print("\n📋 分类报告:")
        print(classification_report(y_test, y_pred))
        
        # 特征重要性
        feature_importance = pd.DataFrame({
            'feature': self.feature_names,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print("\n📊 特征重要性:")
        print(feature_importance)
        
        # 保存模型
        self.save_model()
        
        # 保存模型信息到数据库
        self.save_model_info(accuracy, feature_importance)
        
        return X_test, y_test, y_pred, feature_importance
    
    def save_model(self):
        """保存训练好的模型"""
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_names': self.feature_names
        }
        joblib.dump(model_data, 'snow_guard_model.pkl')
        print("💾 模型已保存至: snow_guard_model.pkl")
    
    def save_model_info(self, accuracy, feature_importance):
        """保存模型信息到数据库"""
        feature_importance_str = feature_importance.to_string(index=False)
        
        cursor = self.db_manager.conn.cursor()
        cursor.execute('''
            INSERT INTO model_info (model_name, accuracy, feature_importance)
            VALUES (?, ?, ?)
        ''', ('RandomForest', accuracy, feature_importance_str))
        
        self.db_manager.conn.commit()
        print("💾 模型信息已保存到数据库")