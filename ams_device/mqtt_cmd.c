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

#include "ohos_init.h" 
#include "cmsis_os2.h" 
#include "ohos_types.h"
#include "stdio.h" 
#include "stdlib.h"
#include "string.h"
#include "time.h"
#include "unistd.h"

#include "cJSON.h"    
//include/
#include "iot_flash.h"          // ssid 等 nv 操作  
#include "iot_crc16.h"          // 需要 crc16 校验
#include "uart_task.h"          // 需要 uart_write, set_report_open, read_hi3861_version
#include "iot_ota.h"            // 需要 ota
#include "mqtt_cmd.h"           //  

//#include "yb_ws2812.h"          // open_lamp(), open_breath()

//#include "hi_reset.h"
#include "json_checker.h"
  
// // 写数据 
// int radar_write(const unsigned char *write_buff, int write_len);

// // 写数据 
// int radar_write(const unsigned char *write_buff, int write_len){
//     (void)write_buff;
//     (void)write_len;
    
//     return 1;
// }


// 软重启设备 reset
void Soft_Reboot(void){
    //hi_soft_reboot(5);
    //hi_hard_reboot(5);
}


// 上位机查询人体距离
void Query_Distance(void){
    unsigned char *write_cmd = NULL;     // 需要写入串口的数据 
    write_cmd = malloc(32);  
    memset(write_cmd, 0, 32);            // 每次都置0

    // 53 59 80 84 00 01 0F C0 (192) 54 43 
    write_cmd[0] = 0x53;
    write_cmd[1] = 0x59;
    write_cmd[2] = 0x80;
    write_cmd[3] = 0x84;
    write_cmd[4] = 0x00;
    write_cmd[5] = 0x01;   
    // 6,7
    write_cmd[6] = 0x0F;
    write_cmd[7] = 0xC0;

    write_cmd[8] = 0x54;
    write_cmd[9] = 0x43;

    radar_write(write_cmd, 10);         // 写入OK，能正确收到回显报文
    //osal_printk("=@= write uart [80 84] \r\n");

    // 释放内存
    free(write_cmd);
}


// 上位机查询人体存在与否
void Query_Presence(void){
    unsigned char *write_cmd = NULL;     // 需要写入串口的数据 
    write_cmd = malloc(32);  
    memset(write_cmd, 0, 32);            // 每次都置0

    // 53 59 80 81 00 01 0F BD (189) 54 43 
    write_cmd[0] = 0x53;
    write_cmd[1] = 0x59;
    write_cmd[2] = 0x80;
    write_cmd[3] = 0x81;
    write_cmd[4] = 0x00;
    write_cmd[5] = 0x01;   
    // 6,7
    write_cmd[6] = 0x0F;
    write_cmd[7] = 0xBD;

    write_cmd[8] = 0x54;
    write_cmd[9] = 0x43;

    radar_write(write_cmd, 10);         // 写入OK，能正确收到回显报文
    //osal_printk("=@= write uart [80 81] \r\n");

    // 释放内存
    free(write_cmd);
}


// 上位机查询雷达固件版本
void Radar_Version(void){
    unsigned char *write_cmd = NULL;     // 需要写入串口的数据 
    write_cmd = malloc(32);  
    memset(write_cmd, 0, 32);            // 每次都置0
 
    // 53 59 02 A4 00 01 0F 62 (98) 54 43  
    write_cmd[0] = 0x53;
    write_cmd[1] = 0x59;
    write_cmd[2] = 0x02;
    write_cmd[3] = 0xA4;
    write_cmd[4] = 0x00;
    write_cmd[5] = 0x01;   
    // 6,7
    write_cmd[6] = 0x0F;
    write_cmd[7] = 0x62;

    write_cmd[8] = 0x54;
    write_cmd[9] = 0x43;

    radar_write(write_cmd, 10);         // 写入OK，能正确收到回显报文
    //osal_printk("=@= write uart [02 A4] \r\n");

    // 释放内存
    free(write_cmd);
}


// 安装高度查询
void Query_Height(void){
    unsigned char *write_cmd = NULL;     // 需要写入串口的数据 
    write_cmd = malloc(32);  
    memset(write_cmd, 0, 32);            // 每次都置0

    // 53 59 06 82 00 01 0F 44 54 43 
    write_cmd[0] = 0x53;
    write_cmd[1] = 0x59;
    write_cmd[2] = 0x06;
    write_cmd[3] = 0x82;
    write_cmd[4] = 0x00;
    write_cmd[5] = 0x01;   
    // 6,7
    write_cmd[6] = 0x0F;
    write_cmd[7] = 0x44;

    write_cmd[8] = 0x54;
    write_cmd[9] = 0x43;

    radar_write(write_cmd, 10);   
    osal_printk("=@= write uart [06 82]. \r\n" );

    // 释放内存
    free(write_cmd);
}


// 设置安装高度
void Set_Height(char* valuestring){
    unsigned char *write_cmd = NULL;     // 需要写入串口的数据 
    write_cmd = malloc(32);  
    memset(write_cmd, 0, 32);            // 每次都置0

    write_cmd[0] = 0x53;
    write_cmd[1] = 0x59;
    write_cmd[2] = 0x06;
    write_cmd[3] = 0x02;
    write_cmd[4] = 0x00;
    write_cmd[5] = 0x02;   

    // 180cm：53 59 06 02 00 02 (00 B4 6A) 54 43
    // 200cm：53 59 06 02 00 02 (00 C8 7E) 54 43
    // 220cm：53 59 06 02 00 02 (00 DC 92) 54 43
    // 240cm：53 59 06 02 00 02 (00 F0 A6) 54 43
    // 260cm：53 59 06 02 00 02 (01 04 BB) 54 43
    if(strcmp(valuestring, "240")==0){ 
        write_cmd[6] = 0x00;
        write_cmd[7] = 0xF0;
        write_cmd[8] = 0xA6; 
    }
    else if(strcmp(valuestring, "260")==0){ 
        write_cmd[6] = 0x01;
        write_cmd[7] = 0x04;
        write_cmd[8] = 0xBB; 
    }
    else if(strcmp(valuestring, "220")==0){ 
        write_cmd[6] = 0x00;
        write_cmd[7] = 0xDC;
        write_cmd[8] = 0x92; 
    }
     else if(strcmp(valuestring, "200")==0){ 
        write_cmd[6] = 0x00;
        write_cmd[7] = 0xC8;
        write_cmd[8] = 0x7E; 
    }
    else if(strcmp(valuestring, "180")==0){ 
        write_cmd[6] = 0x01;
        write_cmd[7] = 0xB4;
        write_cmd[8] = 0x6A; 
    } 

    // 6,7,8
    write_cmd[9] = 0x54;
    write_cmd[10] = 0x43;

    radar_write(write_cmd, 11);  // 写入OK，能正确收到回显报文
    //osal_printk("=@= write urat [06 02]: %s. \r\n", valuestring);

    // 释放内存
    free(write_cmd);
}

// 查询跌倒时长
void Query_FallTime(void){
    unsigned char *write_cmd = NULL;     // 需要写入串口的数据 
    write_cmd = malloc(32);  
    memset(write_cmd, 0, 32);            // 每次都置0
 
    // 53 59 83 8C 00 01 0F CB 54 43 
    write_cmd[0] = 0x53;
    write_cmd[1] = 0x59;
    write_cmd[2] = 0x83;
    write_cmd[3] = 0x8C;
    write_cmd[4] = 0x00;
    write_cmd[5] = 0x01;   
    // 6,7
    write_cmd[6] = 0x0F;
    write_cmd[7] = 0xCB;

    write_cmd[8] = 0x54;
    write_cmd[9] = 0x43;

    radar_write(write_cmd, 10);   
    osal_printk("=@= write uart [83 8C]. \r\n" );

    // 释放内存
    free(write_cmd);
}


// 设置跌倒时长
void Set_FallTime(char* valuestring){
    unsigned char *write_cmd = NULL;     // 需要写入串口的数据 
    write_cmd = malloc(32);  
    memset(write_cmd, 0, 32);            // 每次都置0
 
    // 53 59 83 0C 00 04 (00 00 00 XX) ? 54 43   
    write_cmd[0] = 0x53;
    write_cmd[1] = 0x59;
    write_cmd[2] = 0x83;
    write_cmd[3] = 0x0C;
    write_cmd[4] = 0x00;
    write_cmd[5] = 0x04;
    //
    write_cmd[6] = 0x00;
    write_cmd[7] = 0x00;
    write_cmd[8] = 0x00;
    int sec = atoi(valuestring);
    write_cmd[9] = sec;

    // sum
    unsigned char sum = Cal_CheckSum(write_cmd, 10); 
	write_cmd[9+1] = sum; 
    write_cmd[9+2] = 0x54;
    write_cmd[9+3] = 0x43;

    radar_write(write_cmd, 13);  // 写入OK，能正确收到回显报文
    osal_printk("=@= write urat [83 0C]: %s. \r\n", valuestring);

    // 释放内存
    free(write_cmd);
}

// 上位机查询跌倒状态
void Query_Falling(void){
    unsigned char *write_cmd = NULL;     // 需要写入串口的数据 
    write_cmd = malloc(32);  
    memset(write_cmd, 0, 32);            // 每次都置0

    // 53 59 83 81 00 01 0F C0 (192) 54 43 
    write_cmd[0] = 0x53;
    write_cmd[1] = 0x59;
    write_cmd[2] = 0x83;
    write_cmd[3] = 0x81;
    write_cmd[4] = 0x00;
    write_cmd[5] = 0x01;   
    // 6,7
    write_cmd[6] = 0x0F;
    write_cmd[7] = 0xC0;

    write_cmd[8] = 0x54;
    write_cmd[9] = 0x43;

    radar_write(write_cmd, 10);         // 写入OK，能正确收到回显报文
    osal_printk("=@= write uart [83 81] \r\n");

    // 释放内存
    free(write_cmd);
}




// 查询安装睡眠检测开关
void Query_Sleep(void){
    unsigned char *write_cmd = NULL;     // 需要写入串口的数据 
    write_cmd = malloc(32);  
    memset(write_cmd, 0, 32);            // 每次都置0
 
    // 53 59 84 80 00 01 0F C0() 54 43 
    write_cmd[0] = 0x53;
    write_cmd[1] = 0x59;
    write_cmd[2] = 0x84;
    write_cmd[3] = 0x80;
    write_cmd[4] = 0x00;
    write_cmd[5] = 0x01;   
    // 6,7
    write_cmd[6] = 0x0F;
    write_cmd[7] = 0xC0;

    write_cmd[8] = 0x54;
    write_cmd[9] = 0x43;

    radar_write(write_cmd, 10);   
    osal_printk("=@= write uart [84 80]. \r\n" );

    // 释放内存
    free(write_cmd);
}


// 设置睡眠检测开关
void Set_Sleep(char* valuestring){
    unsigned char *write_cmd = NULL;     // 需要写入串口的数据 
    write_cmd = malloc(32);  
    memset(write_cmd, 0, 32);            // 每次都置0 
    
    // 关：53 59 84 00 00 01 00() 31() 54 43 
    // 开：53 59 84 00 00 01 01() 32() 54 43 
    if(strcmp(valuestring, "00")==0){ 
        write_cmd[6] = 0x00;
        write_cmd[7] = 0x31; 
    }
    else if(strcmp(valuestring, "01")==0){ 
        write_cmd[6] = 0x01;
        write_cmd[7] = 0x32; 
    }

    write_cmd[0] = 0x53;
    write_cmd[1] = 0x59;
    write_cmd[2] = 0x84;
    write_cmd[3] = 0x80;
    write_cmd[4] = 0x00;
    write_cmd[5] = 0x02;   
    // 6,7
    write_cmd[8] = 0x54;
    write_cmd[9] = 0x43;

    radar_write(write_cmd, 11);  // 写入OK，能正确收到回显报文
    osal_printk("=@= write urat [84 80]: %s. \r\n", valuestring);

    // 释放内存
    free(write_cmd);
}


// 查询入床、离床
void Query_Bed(void){
    unsigned char *write_cmd = NULL;     // 需要写入串口的数据 
    write_cmd = malloc(32);  
    memset(write_cmd, 0, 32);            // 每次都置0
 
    // 53 59 84 81 00 01 0F C1() 54 43 
    write_cmd[0] = 0x53;
    write_cmd[1] = 0x59;
    write_cmd[2] = 0x84;
    write_cmd[3] = 0x81;
    write_cmd[4] = 0x00;
    write_cmd[5] = 0x01;   
    // 6,7
    write_cmd[6] = 0x0F;
    write_cmd[7] = 0xC1;

    write_cmd[8] = 0x54;
    write_cmd[9] = 0x43;

    radar_write(write_cmd, 10);   
    osal_printk("=@= write uart [84 81]. \r\n" );

    // 释放内存
    free(write_cmd);
}



// 上位机查询睡眠统计分析
void Query_SleepStat(void){
    unsigned char *write_cmd = NULL;     // 需要写入串口的数据 
    write_cmd = malloc(32);  
    memset(write_cmd, 0, 32);            // 每次都置0
 
    // 53 59 84 8F 00 01 0F CF (207) 54 43  
    write_cmd[0] = 0x53;
    write_cmd[1] = 0x59;
    write_cmd[2] = 0x84;
    write_cmd[3] = 0x8F;
    write_cmd[4] = 0x00;
    write_cmd[5] = 0x01;   
    // 6,7
    write_cmd[6] = 0x0F;
    write_cmd[7] = 0xCF;

    write_cmd[8] = 0x54;
    write_cmd[9] = 0x43;

    radar_write(write_cmd, 10);         // 写入OK，能正确收到回显报文
    osal_printk("=@= write uart [84 8F] \r\n");

    // 释放内存
    free(write_cmd);
}


/*=====================================
//  指令解析方法   
//===================================*/

// 解析接收到的数据 static
int parseReceivedJson(const uint8_t *src) {
    osal_printk("<<< rece json: %s \r\n", src); 

    //{"service_id":"FallingRadar","command_name":"Set_Wifi","paras":
    //{"value":"0","ssid":"iot","psk":"12345678"}}0p 
    // !!! 可能会在 字符串 尾部 多出无效字符，如[0p ]，需要抛弃 
    uint8_t data[1024];
    memset(data, 0, 1024);
    char *p = strrchr((char *)src, '}');
    size_t n = strlen((char *)src) - strlen(p+1); 
    memcpy(data, src, n); 
	//osal_printk("+++ right json: %s \r\n", data);  

    if(json_check((char *)data)==-1){
        osal_printk("=!= json structure error. \r\n");  
        return -1;
    }
    
	cJSON* cjson = NULL; 
    cJSON* service_id = NULL;
    cJSON* command_name = NULL;
    cJSON* paras = NULL; 
    cJSON* value = NULL;

    // 解析整段JSO数据，  // 引发设备重启
    cjson = cJSON_Parse((char *)data);           
    if(cjson == NULL){
        osal_printk("=!= parse json failed. \r\n");  
        return -1;
    }

    // 依次根据名称提取JSON数据（键值对） 
    service_id = cJSON_GetObjectItem(cjson, "service_id");
    command_name = cJSON_GetObjectItem(cjson, "command_name");
    paras = cJSON_GetObjectItem(cjson, "paras");
    value = cJSON_GetObjectItem(paras, "value");   // 从 paras 节点中解析 value
    if(value == NULL){
        return -1;
    }
    osal_printk("### command_name: %s \n", command_name->valuestring);

    unsigned char *write_cmd = NULL;     // 需要写入串口的数据 
    write_cmd = malloc(32);  
    memset(write_cmd, 0, 32);  // 每次都置0

    // 执行指令
    if( strcmp(service_id->valuestring, MQTT_SERVICE_ID)==0 ) {

        //===== 公有指令 ======

        // 控制 LED d灯
        if(strcmp(command_name->valuestring, "LED_ON")==0){
            // {"service_id":"HumanRadar","command_name":"LED_ON","paras":{"value":"OFF"}}
            if(strlen(value->valuestring)!=0){          // 如果节点不存在，不会报错
                //LED_ON(value->valuestring);         // 控制OFF, ON
            }
        }

        // 设置 wifi
        else if(strcmp(command_name->valuestring, "Set_Wifi")==0){ 
            // {"service_id":"FallingRadar","command_name":"Set_Wifi","paras":{"value":"0","ssid":"wifi","psk":"123456"}}
            cJSON* ssid = cJSON_GetObjectItem(paras, "ssid");   // 如果节点不存在，不会报错
            cJSON* psk  = cJSON_GetObjectItem(paras, "psk");    // 如果节点不存在，不会报错  

            if(strlen(ssid->valuestring)!=0 && strlen(psk->valuestring)!=0){
                //Save_Wifi(ssid->valuestring, psk->valuestring);  // 重新写入wifi参数   
            } 

            cJSON_Delete(ssid);
            cJSON_Delete(psk);
        }

        // 查询 wifi 参数
        else if(strcmp(command_name->valuestring, "Query_Wifi")==0) { 
            // {"service_id":"FallingRadar","command_name":"Query_Wifi","paras":{"value":"00"}}  
            //read_wifi_param();      // 在 uart_task.h 中定义
        } 
 

        // 查询 lamp 感应参数
        else if(strcmp(command_name->valuestring, "Query_Person")==0) { 
            // {"service_id":"FallingRadar","command_name":"Query_Person","paras":{"value":"00"}}  
            //read_person_param();      // 在 uart_task.h 中定义
        } 

        // 开、关 ws2812 灯珠
        else if(strcmp(command_name->valuestring, "Open_Lamp")==0){ 
            // {"service_id":"FallingRadar","command_name":"Open_Lamp","paras":{"value":"0","light":"1"}}
            cJSON* light = cJSON_GetObjectItem(paras, "light");   // 如果节点不存在，不会报错 

            if(strlen(light->valuestring)!=0 ){
                // open_lamp(light->valuestring);     
                // 从 微信端控制 led 灯
                char t1[2] = {0};
                strncpy(t1, light->valuestring, 1);  
                ws2812_spi_bright( atoi(t1) );
            } 

            cJSON_Delete(light); 
        }

        // 开、关 ws2812 呼吸灯效果
        else if(strcmp(command_name->valuestring, "Open_Breath")==0){ 
            // {"service_id":"FallingRadar","command_name":"Open_Breath","paras":{"value":"0","light":"1","delay":"250" }}
            cJSON* light = cJSON_GetObjectItem(paras, "light");   // 如果节点不存在，不会报错 
            cJSON* delay  = cJSON_GetObjectItem(paras, "delay");    // 如果节点不存在，不会报错  

            if(strlen(light->valuestring)!=0 && strlen(delay->valuestring)!=0 ){
                //open_breath(light->valuestring, delay->valuestring);   
            } 

            cJSON_Delete(light); 
            cJSON_Delete(delay); 
        }


        //===== end ======

    }
	else {
		osal_printk("=!= parse json error. \r\n");
	}
    //(void)service_id; 

    // 释放内存
    free(write_cmd);

    cJSON_Delete(value);
    cJSON_Delete(paras);
    cJSON_Delete(command_name);
    cJSON_Delete(service_id);
    cJSON_Delete(cjson);

    return 1;
}
