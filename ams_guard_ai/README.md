#  ams_guard_ai — 高反风险 AI 分析引擎

「峰峦守护」的 **AI 风险分析层**，基于 **scikit-learn** 实现高原反应（AMS）智能分级。支持**随机森林（RF）** 与 **支持向量机（SVM）** 两种模型，输入 8 维体征特征，输出 4 级风险等级与自然语言健康建议。

---

##  文件清单

| 文件 | 功能 |
|------|------|
| [main.py](main.py) | 主入口：串联数据库 → 体征 → AI → 风险报告全流程 |
| [predictor.py](predictor.py) | `AMSPredictor` 类，模型加载 + 风险预测 + 预警入库 |
| [model_trainer.py](model_trainer.py) | `ModelTrainer` 类，随机森林训练 + 评估 + 特征重要性 |
| [mobile_ai.py](mobile_ai.py) | 移动健康分析（针对鸿蒙端数据格式适配） |
| [scenario_service.py](scenario_service.py) | 场景服务（城市海拔、环境温氧查询） |
| [health_report.py](health_report.py) | 健康报告生成（总结 / 详细两种模板，支持语音播报） |
| [alert_rescue.py](alert_rescue.py) | 救援警报触发（重度高反 / SOS） |
| [database.py](database.py) | SQLite 中间库管理器（`snow_guard_ams.db`） |
| [data_generator.py](data_generator.py) | 模拟数据生成器（高原旅行场景高反合成数据） |
| [visualizer.py](visualizer.py) | 数据可视化（matplotlib / seaborn 图表） |
| **rf_model.pkl** | ⭐ 预训练随机森林模型 |
| **svm_model.pkl** | ⭐ 预训练 SVM 模型 |
| **scaler.pkl** | ⭐ StandardScaler 特征标准化器 |

##  输入特征

8 维体征特征向量：

| # | 特征 | 含义 |
|---|------|------|
| 1 | SpO₂ | 血氧饱和度（%） |
| 2 | HR | 心率（次/分） |
| 3 | RR | 呼吸频率（次/分） |
| 4 | SBP | 收缩压（mmHg） |
| 5 | DBP | 舒张压（mmHg） |
| 6 | altitude | 当前海拔（m） |
| 7 | temperature | 环境温度（℃） |
| 8 | sleep_quality | 睡眠质量（0-10） |

##  风险等级

| 等级 | 名称 | 含义 | 建议 |
|:----:|------|------|------|
| 0 | 无风险 | 体征正常，可正常活动 | 保持当前状态 |
| 1 | 轻度 | 轻微不适，降低运动量 | 多喝水，密切观察 |
| 2 | 中度 | 明显高反症状 | 吸氧 + 休息，警惕恶化 |
| 3 | 重度 | 严重危险 | 立即下降海拔 + 就医 |

## 

### 直接预测（使用预训练模型）

```bash
pip install numpy pandas scikit-learn joblib
python main.py
```

### 重新训练模型

有标注好的高反数据集时执行：

```bash
python model_trainer.py
```

`RandomForestClassifier` 配置：
- `n_estimators=100`
- `max_depth=10`
- `min_samples_split=5`
- `min_samples_leaf=2`
- `random_state=42`

### 生成模拟数据（用于 demo）

```bash
python data_generator.py
```

##  模型文件格式

`rf_model.pkl` / `svm_model.pkl` 为字典格式：

```python
{
    'model':        训练好的分类器,
    'scaler':       StandardScaler,
    'feature_names': ['SpO2', 'HR', 'RR', 'SBP', 'DBP', 
                      'altitude', 'temperature', 'sleep_quality']
}
```

通过 `joblib.load()` 加载，`predictor.py` 中的 `AMSPredictor` 类直接调用：

```python
predictor = AMSPredictor(db_manager, model_path='rf_model.pkl')
predictor.load_model()
result = predictor.predict_risk(physiological_data)
# → {'risk_level': 2, 'risk_description': '中度风险', 
#    'probabilities': {'无风险': '0.0500', '轻度风险': '0.1500', 
#                      '中度风险': '0.6000', '重度风险': '0.2000'}}
```

##  数据流

```
ams_vital_data (MySQL)          data_generator.py (模拟)
           │                            │
           ▼                            ▼
    database.py ──► SQLite 中间库 (snow_guard_ams.db)
           │
           ▼
    predictor.py  ──►  rf_model.pkl / scaler.pkl
           │
           ▼
    risk_level (0-3) + probabilities
           │
     ┌─────┼────────┐
     ▼     ▼        ▼
 health  alert   scenario
 _report _rescue _service
     │
     ▼
 报告文本 + 建议 → ams_user_risk (MySQL)
```

##  注意事项

- `main.py` 中默认使用硬编码测试参数，实际部署时需改为从 MySQL 动态读取
- SQLite 中间库文件 `snow_guard_ams.db` 首次运行自动创建，包含 `physiological_data`、`warnings` 等表
- 模型训练需要已标注的 `AMS_risk` 目标值，由 `data_generator.py` 中的 `_calculate_risk_level()` 规则生成
