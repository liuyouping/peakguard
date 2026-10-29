# Copyright (C) 2026 PeakGuard Team
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from sklearn.metrics import confusion_matrix

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

class ResultVisualizer:
    def __init__(self, db_manager):
        self.db_manager = db_manager
    
    def visualize_training_results(self, X_test, y_test, y_pred, feature_importance):
        """可视化训练结果"""
        print("🔄 正在生成可视化图表...")
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('雪域卫士 - 高原反应检测分析', fontsize=16, fontweight='bold')
        
        # 1. 混淆矩阵
        cm = confusion_matrix(y_test, y_pred)
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=axes[0, 0],
                   xticklabels=['无风险', '轻度', '中度', '重度'],
                   yticklabels=['无风险', '轻度', '中度', '重度'])
        axes[0, 0].set_title('混淆矩阵')
        axes[0, 0].set_xlabel('预测标签')
        axes[0, 0].set_ylabel('真实标签')
        
        # 2. 特征重要性
        feature_importance_display = feature_importance.copy()
        feature_importance_display['feature'] = ['血氧', '心率', '呼吸', '收缩压', '舒张压', '海拔', '温度', '睡眠']
        feature_importance_display = feature_importance_display.sort_values('importance', ascending=True)
        
        axes[0, 1].barh(feature_importance_display['feature'], feature_importance_display['importance'])
        axes[0, 1].set_title('特征重要性分析')
        axes[0, 1].set_xlabel('重要性得分')
        
        # 3. 风险等级分布
        risk_counts = pd.Series(y_test).value_counts().sort_index()
        risk_labels = ['无风险', '轻度', '中度', '重度']
        colors = ['#2ecc71', '#f39c12', '#e67e22', '#e74c3c']
        axes[1, 0].pie(risk_counts.values, labels=risk_labels, autopct='%1.1f%%', colors=colors)
        axes[1, 0].set_title('风险等级分布')
        
        # 4. 血氧饱和度与风险等级的关系
        query = "SELECT SpO2, AMS_risk FROM physiological_data"
        data = pd.read_sql_query(query, self.db_manager.conn)
        sns.boxplot(data=data, x='AMS_risk', y='SpO2', ax=axes[1, 1], palette=colors)
        axes[1, 1].set_title('血氧饱和度与风险等级关系')
        axes[1, 1].set_xlabel('风险等级')
        axes[1, 1].set_ylabel('血氧饱和度(%)')
        
        plt.tight_layout()
        plt.savefig('snow_guard_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()
        print("📊 可视化图表已保存至: snow_guard_analysis.png")
    
    def show_database_sample(self):
        """显示数据库样本数据"""
        print("\n📋 数据库样本数据:")
        
        tables = ['users', 'physiological_data', 'warnings', 'model_info']
        for table in tables:
            print(f"\n--- {table} 表样本 ---")
            try:
                df_sample = self.db_manager.get_sample_data(table, limit=3)
                print(df_sample)
            except Exception as e:
                print(f"  无法读取 {table} 表: {e}")