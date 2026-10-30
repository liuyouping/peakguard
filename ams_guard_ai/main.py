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

from database import DatabaseManager
from mobile_ai import MobileHealthAnalyzer
import datetime


def main():
    """主程序"""
    print("=" * 60)
    print("🏔️  雪域精灵 - 高原反应智能检测系统")
    print("=" * 60)
    
    # 定义四个变量
    userId = 'LS202511001'  # 用户ID
    measureDate = '2025-11-03 00:00:00'  # 测量日期
    cityId = '0891'  # 城市ID
    devicenumber = 'DEV001'  # 设备编号
    
    print(f"📋 系统参数设置:")
    print(f"   用户ID: {userId}")
    print(f"   测量日期: {measureDate}")
    print(f"   城市ID: {cityId}")
    print(f"   设备编号: {devicenumber}")
    
    # 初始化数据库管理器
    db_manager = DatabaseManager('snow_guard_ams.db')
    
    try:
        # 连接数据库
        db_manager.connect()
        
        # 确保ams_user_risk表存在（先删除再创建）
        cursor = db_manager.conn.cursor()
        
        
        # 从ams_vital_data表获取体征数据（根据userId和measureDate）
        print(f"🔍 尝试从ams_vital_data表获取用户 {userId} 在 {measureDate} 的数据...")
        try:
            cursor.execute('''
                SELECT * FROM ams_vital_data
                WHERE userId = %s AND date(measureDate) = %s
                LIMIT 1
            ''', (userId, measureDate))
            vital_data = cursor.fetchone()
            
            if vital_data:
                print(f"✅ 已获取ams_vital_data表数据，字段: {list(vital_data.keys())}")
                
                # 尝试从ams_city表获取城市信息
                print("🔍 尝试从ams_city表获取城市信息...")
                try:
                    cursor.execute('''
                        SELECT * FROM ams_city
                        WHERE cityId = %s
                        LIMIT 1
                    ''', (cityId,))
                    city_data = cursor.fetchone()
                    
                    if city_data:
                        print(f"✅ 已获取ams_city表数据，字段: {list(city_data.keys())}")
                        print(f"📋 城市信息: {city_data}")
                    else:
                        print(f"ℹ️ ams_city表无对应数据 (cityId: {cityId})")
                        
                except Exception as e:
                    print(f"ℹ️ ams_city表查询失败: {e}")
                    
            else:
                print(f"❌ ams_vital_data表无对应数据 (userId: {userId}, date: {measureDate})")
                return
                
        except Exception as e:
            print(f"❌ ams_vital_data表查询失败: {e}")
            return
        
        # 从ams_city_temp表获取环境数据（根据cityId和measureDate）
        try:
            cursor.execute('''
                SELECT * 
                FROM ams_city_temp 
                WHERE cityId = %s AND date(measureDate) = %s
                LIMIT 1
            ''', (cityId, measureDate))
            env_data = cursor.fetchone()
            
            # 设置环境数据
            altitude = 0.0
            max_temp = 25.0
            min_temp = 15.0
            temperature = 20.0
            oxygen = 21.0
            city_name = None
            
            if env_data:
                print(f"✅ 已获取ams_city_temp表数据，字段: {list(env_data.keys())}")
                
                # 获取城市信息
                city_name = env_data.get('cityName')
                print(f"📋 城市信息: {city_name} (ID: {cityId})")
                
                # 获取温度数据
                max_temp = float(env_data.get('maxTemp', 25.0))
                min_temp = float(env_data.get('minTemp', 15.0))
                temperature = (max_temp + min_temp) / 2  # 使用平均温度
                print(f"📋 环境信息: 最高温度={max_temp}°C, 最低温度={min_temp}°C, 平均温度={temperature}°C")
                
                # 获取氧气浓度
                oxygen = float(env_data.get('oxygen', 21.0))
                print(f"📋 氧气浓度: {oxygen}%")
            else:
                print(f"ℹ️ ams_city_temp表无对应数据 (cityId: {cityId}, date: {measureDate})")
            
            # 从ams_city表获取海拔数据
            try:
                cursor.execute('''
                    SELECT altitude FROM ams_city 
                    WHERE cityId = %s
                    LIMIT 1
                ''', (cityId,))
                city_altitude_data = cursor.fetchone()
                if city_altitude_data:
                    altitude = float(city_altitude_data.get('altitude', 0.0))
                    print(f"📋 海拔 (从ams_city表获取): {altitude}米")
                else:
                    print(f"ℹ️ ams_city表无对应海拔数据 (cityId: {cityId})")
            except Exception as e:
                print(f"ℹ️ 城市海拔查询失败: {e}")
                
        except Exception as e:
            print(f"ℹ️ ams_city_temp表查询失败: {e}，使用默认环境数据")
            altitude = 0.0
            max_temp = 25.0
            min_temp = 15.0
            temperature = 20.0
            oxygen = 21.0
        
        # 处理用户数据
        processed_count = 0
        
        print(f"\n🔍 处理用户ID {userId} 的数据...")
        
        try:
            # 构建完整的生理数据字典
            physiological_data = {
                'SpO2': float(vital_data.get('SpO2', 98.0)),
                'HR': float(vital_data.get('HR', vital_data.get('heart', 75.0))),
                'RR': float(vital_data.get('RR', vital_data.get('breath', 16.0))),
                'SBP': float(vital_data.get('SBP', 120.0)),
                'DBP': float(vital_data.get('DBP', 80.0)),
                'altitude': altitude,
                'temperature': temperature,
                'oxygen': oxygen,
                'sleep_quality': float(vital_data.get('sleep_quality', 8.0))
            }
            
            print(f"📊 用户ID {userId} 的体征数据:")
            print(f"   血氧饱和度 (SpO2): {physiological_data['SpO2']:.1f}%")
            print(f"   心率 (HR): {physiological_data['HR']:.1f} 次/分")
            print(f"   呼吸频率 (RR): {physiological_data['RR']:.1f} 次/分")
            print(f"   收缩压 (SBP): {physiological_data['SBP']:.1f} mmHg")
            print(f"   舒张压 (DBP): {physiological_data['DBP']:.1f} mmHg")
            print(f"   海拔 (altitude): {physiological_data['altitude']:.1f} 米")
            print(f"   温度: 最高 {max_temp:.1f}°C, 最低 {min_temp:.1f}°C, 平均 {physiological_data['temperature']:.1f}°C")
            print(f"   氧气浓度 (oxygen): {physiological_data['oxygen']:.1f}%")
            print(f"   睡眠质量 (sleep_quality): {physiological_data['sleep_quality']:.1f}")
            
            # 使用移动端轻量化AI进行健康评估
            print("\n🧠 使用移动端轻量化AI进行健康评估...")
            mobile_health_analyzer = MobileHealthAnalyzer()
            
            # 分析健康状态
            analysis_result = mobile_health_analyzer.analyze_health(physiological_data)
            
            print("📈 健康评估结果:")
            risk_level = analysis_result['risk_assessment']['risk_level']
            risk_description = analysis_result['risk_assessment']['risk_description']
            risk_score = analysis_result['risk_assessment']['risk_score']
            
            print(f"   风险等级: {risk_level}")
            print(f"   风险描述: {risk_description}")
            print(f"   风险评分: {risk_score:.2f}")
            
            # 将预测结果写入ams_user_risk表（按照数据库设计图）
            print("\n💾 将预测结果写入ams_user_risk表...")
            
            # 准备数据
            report_date = datetime.datetime.now()
            risk_report = f"风险等级: {risk_level}, 风险描述: {risk_description}, 风险评分: {risk_score:.2f}, 设备编号: {devicenumber}"
            
            # 直接写入数据，不重新定义表结构
            cursor.execute('''
                INSERT INTO ams_user_risk (userId, reportDate, riskLevel, riskReport)
                VALUES (%s, %s, %s, %s)
            ''', (userId, report_date, risk_level, risk_report))
            
            db_manager.conn.commit()
            print("✅ 预测结果已成功写入ams_user_risk表")
            
            # 显示写入结果
            cursor.execute('''
                SELECT * FROM ams_user_risk WHERE userId = %s ORDER BY create_time DESC LIMIT 1
            ''', (userId,))
            written_result = cursor.fetchone()
            
            print("📋 写入的预测结果:")
            print(f"   ID: {written_result['id']}")
            print(f"   用户ID: {written_result['userId']}")
            print(f"   报告日期: {written_result['reportDate']}")
            print(f"   风险等级: {written_result['riskLevel']}")
            print(f"   风险报告: {written_result['riskReport']}")
            print(f"   创建时间: {written_result['create_time']}")
            
            processed_count += 1
            print("\n" + "=" * 60)
            
        except Exception as e:
            print(f"❌ 处理用户ID {userId} 时出错: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n" + "=" * 60)
        print("✅ 系统运行完成！")
        print(f"📊 已为 {processed_count} 个用户生成风险预测并写入ams_user_risk表")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 关闭数据库连接
        db_manager.close()

if __name__ == "__main__":
    main()