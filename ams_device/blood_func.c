/*
 * Copyright (C) 2026 PeakGuard Team
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#include <stdio.h>
#include <string.h>
#include <unistd.h> 
#include "ohos_init.h"
#include "cmsis_os2.h"  
#include "errcode.h"  
 
#include "iot_uart.h"
#include "pinctrl.h"
#include "uart.h"
#include <time.h> 
 
#include "iot_gpio_ex.h" 
#include "iot_server.h"     // SLE服务端接口

#include "ws2812_spi.h" 
#include "iot_time.h"
#include "mqtt_main.h"      // publish_radar_data

//                          
#define BPT_UART_ID        0     // uart_1, ws63e: 15 tx, 16 rx
#define RADAR_UART_ID      3     // uart_2, ws63e:  8 tx,  7 rx
//#define LED_BUTTON_PIN     3     // LED按键GPIO
#define SOS_BUTTON_PIN    12      // SOS按键GPIO 
#define UART_BUFF_SIZE      10240  


// 1. 字符串初始化：3+7+33+17+65+17 = 142 
//static char sts[3] = {0};        // 2+1
static int sts = 0;             // 1 report, 0 no
static char cmd[7] = {0};        // 6+1
static char value[33] = {0};     // 32+1
static char result[17] = {0};    // 16+1
static char action[65] = {0};    // 64+1
static char timestamp[17] = {0}; // 16+1 

//========================================================
// SLE 接收和发送函数
//========================================================

// 处理从 sle client 发来的数据
// kind:
// 04 01 00    >> 04 lamp, 01 (01低亮, 02中亮, 03高亮, 00关灯), 00结束符
void ProcessClient(uint8_t *data, uint16_t length)
{
    uint8_t buff[16] = {0};  

    if (data == NULL || length == 0) {
        return;
    }

    if (memcpy_s(buff, length, data, length) != EOK) {
        return;
    } 

    if(buff[0] == 0x04){
        int lampIndex = (int)buff[1]; 

        ws2812_spi_bright(lampIndex); 
    } 
}


// 发送数据给 sle client
// kind:
// 04 01 00    >> 04 lamp, 01 (01低亮, 02中亮, 03高亮, 00关灯), 00结束符
void SendToClient(uint8_t *data, uint16_t length)
{
    iot_server_send_data(data, length); 
} 
   

// 同步时钟给 sle client
void SendClock(void)
{ 
    int current_hour, current_minute;
    
    // 获取当前小时和分钟
    currHourMinInt(&current_hour, &current_minute); 
    //osal_printk("=== timer exec: %02d:%02d\r\n", current_hour, current_minute);
 
    // 03 01 08 19    >> 03 clock, 01 test,  08:hr, 19:min  => 08:19
    uint8_t data[] = { 0x03, 0x01, current_hour, current_minute, 0x00 };    
    SendToClient(data, sizeof(data));
}


//========================================================
// 血压计相关函数
// uart_1, ws63e: 15 tx, 16 rx
//========================================================


uint8_t uart_buff[UART_BUFF_SIZE] = {0}; 

static void uart1_rx_callback(const void *buffer, uint16_t orginLen, bool error)
{  
    unused(error);

    if (buffer == NULL || orginLen == 0) {
        return;
    }

    if (memcpy_s(uart_buff, orginLen, buffer, orginLen) != EOK) {
        return;
    } 

    if(orginLen>0){
        // osal_printk("<== uart_buff [%d]: \r\n", orginLen);
        // for (int j = 0; j < orginLen; j++) {
        //    osal_printk("%02X ", uart_buff[j]);
        // }
        // osal_printk("\r\n"); 
    }

    if(orginLen == 5) {
        //FD FD 06 0D 0A 
        if( uart_buff[2] == 0x06) {
            osal_printk("==> start test ... \r\n"); 

            uint8_t data[] = { 0x02, 0x01, 0x00 };   // 02: blood, 01
            SendToClient(data, sizeof(data));
        } 
        //FD FD 02 0D 0A 
        else if( uart_buff[2] == 0x02) { 
            osal_printk("<== stop test. \r\n"); 

            uint8_t data[] = { 0x02, 0x02, 0x00 };   // 02: blood, 02
            SendToClient(data, sizeof(data));
        }  
    }

    if(orginLen == 7) {
        //FD FD FB 00 0E 0D 0A
        if( uart_buff[2] == 0xFB) {
            int high = (int)uart_buff[3] * 256 + (int)uart_buff[4];
            osal_printk("++> test value: %d \r\n", high); 

            //char *data = "send from iot server!\n";
            //int ret = SendToClient((uint8_t *)data, strlen(data));
            uint8_t data[] = { 0x02, 03, uart_buff[3], uart_buff[4] };   // 02: blood, 03, high, low
            SendToClient(data, sizeof(data));

            //OLED_ShowNum(36, 60, high, 3, 16, 1);   // 0+32 = 32+4
        } 
    }

    if(orginLen == 9) {
        // FD FD FC 70 4B 40 00 0D 0A
        if( uart_buff[2] == 0xFC) {
            int high = (int)uart_buff[3];
            int low  = (int)uart_buff[4];
            int heart  = (int)uart_buff[5];
            osal_printk("==> test result: high= %d, low= %d, heart= %d \r\n", high, low, heart); 

            //publish_radar_data();

            uint8_t data[] = { 0x02, 04, uart_buff[3], uart_buff[4], uart_buff[5] };   // 02: blood, 04, high, low, heart
            SendToClient(data, sizeof(data));
            
            // OLED_ShowNum(36, 60, high, 3, 16, 1);   // 0+32 = 32+4
            // OLED_ShowNum(116, 60, low, 3, 16, 1);   // 0+32 = 32+4
            // OLED_ShowNum(196, 60, heart, 3, 16, 1);   // 0+32 = 32+4

            //=== 血压测量结果，发送至 mqtt： 33 01
            sprintf(cmd, "%02X%02X", 0x33, 0x01); 
            sprintf(value, "%02X %02X %02X", high, low, heart);        
            sprintf(result, "%d,%d,%d", high, low, heart);       
            sprintf(action, "high= %d, low= %d, heart= %d \r\n", high, low, heart);      //心率数值：%d bpm  
            currTimeStamp(timestamp);  // 当前时间戳  

            osal_printk("+++ cmd: %s, value: %s, result: %s, action: %s \r\n", cmd, value, result, action); 

            // 发布数据
            publish_radar_data(cmd, value, result, action, timestamp);  // 发布数据 
        }
    }
}


void Blood_Task(void)
{      
    // 1. 初始化SLE服务端
    iot_server_init();  // "sle_server.h" // SLE服务端接口    
    osDelay(200);

    // 2.初始化uart1：15,16
    uapi_pin_set_mode(15, IOT_IO_FUNC_GPIO_15_UART1_TXD); // uart1 tx  
    uapi_pin_set_mode(16, IOT_IO_FUNC_GPIO_16_UART1_RXD); // uart1 rx  

    // 3.先重置
    uapi_uart_deinit(BPT_UART_ID);
    IotUartAttribute uart_attr = {9600, 8, 1, 0, 100, 100, 0}; 
 
    // 4.初始化
    IoTUartInit(BPT_UART_ID, &uart_attr); 
      
    // 5.注册回调函数  
    (void)uapi_uart_register_rx_callback(BPT_UART_ID, UART_RX_CONDITION_FULL_OR_SUFFICIENT_DATA_OR_IDLE,
        1024, uart1_rx_callback); 
    
    osal_printk("\r\n== Blood-Pressure-Test start... \r\n\r\n");  
    
} 
 

//============== 自定义方法 =============== 

// 公共参数
static uint8_t lastPresence = 0;   // 人体存在  
static uint8_t lastStatus = 0;     // 运动信息 
static uint8_t lastDistance = 0;   // 距离   
// 睡眠雷达   
static uint8_t lastBreath = 0;     // 呼吸 
static uint8_t lastHeart  = 0;     // 心跳 

//static int bFalling  = 0;      // 进入跌倒状态，0表示未跌倒，1表示跌倒；跌倒报文次数，3次再另外上报自定义跌倒预警：83 0F
static int bPresence = 0;      // 进入有人状态， 0表无人，1表示有人

// 自定义：81 0F 呼吸报警
void add_breath_report(uint8_t hi, uint8_t low, uint8_t val){ 
    // 加上运动信息为判断条件，即人员相对静止(1)时，才发出异常报警
    if(lastStatus != 1)
        return; // 运动信息为0或2时，不上报异常  
    
    // 人员距离 120cm
    if(lastDistance > 120)
        return;        
    
    

    // 正常上报报文 
    if( sts==1 ){  
        sprintf(cmd, "%02X%02X", hi, low); 
        sprintf(value, "%02X", val);   
        sprintf(result, "%d", val);     

        osal_printk("+++ add.cmd: %s, value: %s, result: %s, action: %s \r\n", cmd, value, result, action);
        // 设置时间 
        currTimeStamp(timestamp);   // 当前时间 
        publish_radar_data(cmd, value, result, action, timestamp);  // 发布数据 
    }
} 

// 自定义指令： 
 
// 66 02 (wifi参数)，上端查询nv中的wifi参数
void read_wifi_param(void){
    char ssid[64] = {0} ;   //  
    char psk[64] = {0} ;   //  
    Read_Wifi(ssid, psk);  
 
    sprintf(cmd, "%02X%02X", 0x66, 0x02);
    sprintf(value, "%s",  0x00);                      // value: 
    sprintf(result, "%d", 0x00);                      // result = 00
    sprintf(action, "wifi.ssid: %s, psk: %s", ssid, psk);           // 文本

    osal_printk("+++ add.cmd: %s, value: %s, result: %s, action: %s \r\n", cmd, value, result, action);
    // 设置时间 
    currTimeStamp(timestamp);   // 当前时间 
    publish_radar_data(cmd, value, result, action, timestamp);  // 发布数据
} 

//========================================================
// 4、递推平均滤波法：
//    把连续N个采样值看成一个队列，队列长度固定为N；每次采样到一个新数据放入队尾，并扔掉队首的一次数据。
//    把队列中的N各数据进行平均运算，即获得新的滤波结果
//========================================================

// https://zhuanlan.zhihu.com/p/271154535
// 常见的滤波算法(C语言) 

#define N 15
int que_buf[N] = {0};
int que_idx = 0;    

// 滤波算法
int filter(int newValue) { 
    int sum = 0;

    if(que_idx<N){
        que_buf[que_idx] = newValue;        // que_idx<N, 直接进队
        que_idx++;
    }
    else {  // que_idx=N   
        for (int i = 0; i<N-1; i++){
            que_buf[i] = que_buf[i + 1];    // 挤掉[0]，即留出[N-1]
        }
        que_buf[N-1] = newValue;            // 再进队尾
    }
 
    for(int i = 0; i < N; i++) {
        //printf("=== i: %d \r\n",  que_buf[i]);
        sum += que_buf[i];
    }
    return (int)(sum / N);
}


// 经过滤波后发送指令控制led灯带 
int lastMove = -1;  
int MoveToLamp(int val)
{
    // 滤波之后的值，且==N  
    val = filter(val);          

    if(que_idx==N){  
        int moveLevel=0; 

        if(val<=10) {  
            moveLevel = 0;
        } 
        else if(val<=40) {  
            moveLevel = 1;
        }
        // else if(val<=40){   
        //     //moveLevel = 2;  
        //     //改成氛围灯效果 
        // }
        else {  
            moveLevel = 3;
        }

        // 执行显示
        if(moveLevel != lastMove){
            ws2812_spi_bright(moveLevel); 
            lastMove = moveLevel;
        }
    }

}

//========================================================
// 睡眠雷达相关函数
// uart_2, ws63e: 8 tx, 7 rx
//========================================================

#define printFlag 1     // 打印标志
int packetLen = 10;     // 根据协议，一包数据至少10个字节；但是 02A4（雷达固件版本返回报文的长度=9）  
uint8_t firstBuff[UART_BUFF_SIZE] = {0};   
uint16_t firstLen= 0; 
uint8_t readBuff[UART_BUFF_SIZE] = {0};   

int radar_data_parse(const uint8_t *buffer, uint16_t orginLen)   
{   
    if (buffer == NULL || orginLen == 0 || orginLen < packetLen) {
        return;
    } 

    if(printFlag){
        // osal_printk("<== buffer [%d]: ", orginLen);
        // for (int j = 0; j < orginLen; j++) {
        //    osal_printk("%02X ", buffer[j]);
        // }
        // osal_printk("\r\n"); 
    } 

    // 固件回复数据，存在分包情况
    //<== buffer [16]: 53 59 02 A4 00 11 47 36 30 53 4D 31 53 59 76 30 
    //<== buffer [10]: 31 30 31 31 34 34 00 5E 54 43 
 
    //===== 分包问题 begin：
	if (Check_CheckSum(buffer, orginLen-2) == 0)  {   
        // 第一包：以53 59开头
        if(buffer[0]==0x53 && buffer[1]==0x59) {
            int dataLen = (int) buffer[5];  // 协议中第6位是数据长度
            if(dataLen > orginLen-9) {
                memset(firstBuff, 0, orginLen+1);        // 初始化
                memcpy(firstBuff, buffer, orginLen);     // 复制数据：buff => firstBuff    
                firstBuff[orginLen] = '\0';              // 结束符
                firstLen = orginLen;

                // 仅仅保存第一包数据
                return 0;
            } 
        }
        // 第二包数据：以54 43 结尾
        else if(buffer[orginLen-2]==0x54 && buffer[orginLen-1]==0x43){
            // firstLen 作为判断分包的依据，如果是粘包情况，则buffLen=0
            if(firstLen>0){
                memcpy(firstBuff + firstLen, buffer, orginLen);     // 复制数据：buff => readBuff + buffLen   
                firstBuff[firstLen + orginLen] = '\0';              // 结束符 

                // 第一包+第二包拼接起来后，重新处理数据包
                radar_data_parse(firstBuff, firstLen + orginLen); 
                firstLen= 0;  // 归零
            }
        }
        else {
            // 暂不考虑既没有开头，也没有结尾的数据包--即使存在这种情况！
        }
 
    }

    //===== 粘包问题 begin：
	if (Check_CheckSum(buffer, orginLen-2) == 0)  {     
         
        // 先处理两个53之间的数据包，至少10个字节（协议报文长度>=10）；多余的数据继续分解
        int sindex, eindex;
        sindex=-1; eindex=-1;
        for (int j = 0; j < orginLen; j++){
            if(sindex==-1){
                if(buffer[j]== 0x53 && buffer[j+1]== 0x59){ 
                    sindex=j;
                    //osal_printk("111=> %d : %d\r\n", sindex, eindex);
                }
            }
            else {
                if(buffer[j]== 0x53 && buffer[j+1]== 0x59){
                    eindex=j;
                    //osal_printk("222=> %d : %d\r\n", sindex, eindex); 
                    break;  // 找到一组开关，停止循环。多余的53不再考虑
                } 
            } 
        } 
        
        // 根据协议，一包数据至少10个字节，可能是9
        if(eindex-sindex>=packetLen) {  
            uint8_t *temp_buff = NULL;     // 中间报文数据 
            temp_buff = malloc(UART_BUFF_SIZE);   

            int temp_len = eindex - sindex; // temp_len = eindex - sindex;

            // 第一包数据  
            memset(temp_buff, 0, temp_len+1);    
            memcpy(temp_buff, buffer + sindex, temp_len);
            temp_buff[temp_len] = '\0'; 
            
            if(printFlag) { 
                osal_printk("==> first pack - temp_buff [%d]: ", temp_len); 
                for (int j = 0; j < temp_len; j++){
                    osal_printk("%02X ", temp_buff[j]);
                }
                osal_printk("\r\n"); 
            }

            // 第一包数据处理
            radar_data_parse(temp_buff, temp_len);

            // 剩余数据处理
            temp_len = orginLen - eindex;
            memset(temp_buff, 0, temp_len+1);    
            memcpy(temp_buff, uart_buff + eindex, temp_len);
            temp_buff[temp_len] = '\0'; 
            
            if(printFlag) { 
                osal_printk("==> second pack - temp_buff [%d]: ", temp_len); 
                for (int j = 0; j < temp_len; j++){
                    osal_printk("%02X ", temp_buff[j]);
                }
                osal_printk("\r\n");
            }

            // 后续数据处理
            radar_data_parse(temp_buff, temp_len);

            free(temp_buff);  // 及时释放资源
        }  

		return 0; // 校验失败 
	}
 
    // == 校验成功的数据包，不存在粘包和分包情况

    // 复制数据：uart_buff => orginBuff    
    //uint8_t *readBuff = malloc(orginLen+1);   
    if(readBuff){
        memset(readBuff, 0, orginLen+1);    
        memcpy(readBuff, buffer, orginLen);
        readBuff[orginLen] = '\0';
 
        // if(printFlag) { 
        //     osal_printk("<== readBuff [%d]: ", orginLen);
        //     for (int j = 0; j < orginLen; j++) {
        //         osal_printk("%02X ", readBuff[j]);
        //     }
        //     osal_printk("\r\n");
        // }
    }

    sts = 0; // 每次归零

    int len = orginLen;  

    if(readBuff[0]==0x53 && readBuff[1]==0x59){

        // 主动报文长度
        if(len>=packetLen ){

            sprintf(cmd, "%02X%02X", readBuff[2], readBuff[3]);     

            // 心跳包信息
            if( strcmp(cmd,"0101")==0 ){
                // sts = 0;           // 不上报
            } 

            // 85 02 心率数值：每分钟60-100次(bpm)
            else if( strcmp(cmd,"8502")==0 || strcmp(cmd,"8582")==0){  
                sprintf(value, "%02X", readBuff[6]);        
                sprintf(result, "%d", readBuff[6]);       
                sprintf(action, "heart: %d bpm", readBuff[6]);      //心率数值：%d bpm    

                // 如果 8001 = presence，则发送
                if( lastPresence == 1){  
                    int val = (int)readBuff[6];
                    lastHeart = val;
                    //osal_printk("==> heart: %d bpm\r\n", val);  

                    // 01 01 66    >> 01 sleep,  01 heart,  66 heart 
                    // 01 02 27    >> 01 sleep,  02 breath,  27 breath   
                    uint8_t data[] = { 0x01, 0x01, val, 0x00 };    
                    SendToClient(data, sizeof(data));

                    // 每次呼吸数值异常（过高或过低）时，重新监测人员存在和距离
                    int normal= 0;
                    if(val==0x00){
                        normal= 0; 
                    }
                    else if( val>0x00 && val<0x3C) {    // 0 ~ 60
                        normal= 0; 
                    } 
                    

                    if( normal==0){
                        // 
                        Query_Distance();
                        Query_Presence();
                    } 

                    sts = 1;    // 上报mqtt 
                }
            }

            //===== 睡眠雷达：80(04、05)、81(01、02、05)、85(01、02、05)、84(00、01、02、0C)
            //===== 睡眠监测 

            // 其他的值
            else 
            if( strcmp(cmd, "8103")!=0 && strcmp(cmd, "8002")!=0 && strcmp(cmd, "0707")!=0 
             && strcmp(cmd, "8005")!=0 && strcmp(cmd, "8004")!=0 && strcmp(cmd, "8505")!=0 
             && strcmp(cmd, "8105")!=0 )
            {
                osal_printk("<== other buff [%d]: ", orginLen);
                for (int j = 0; j < orginLen; j++) {
                    osal_printk("%02X ", readBuff[j]);
                }
                osal_printk("\r\n");
            }

            //===== 发送到 mqtt server
            if( sts == 1 )
            {   
                currTimeStamp(timestamp);  // 当前时间戳

                osal_printk("+++ cmd: %s, value: %s, result: %s, action: %s \r\n", cmd, value, result, action);

                // 发布数据
                publish_radar_data(cmd, value, result, action, timestamp);  // 发布数据 

                 

                osDelay(5);   // 必须延时！
            }

            osDelay(5);   // 必须延时！

        }

    } 
 
   
}

// 写指令，必须要先初始化(uart open)
int radar_write(const uint8_t *write_buff, int write_len){   
    int ret = 0;
    //if(uart_status ==1) 
    {
        ret = IoTUartWrite(RADAR_UART_ID, write_buff, write_len);  // 返回写入的数据长度，否则返回-1
        if (ret == -1) {
            osal_printk("=!= failed to write uart! err code = %d\n", ret);
            return 0;
        }  
        osal_printk(">>> write uart success. len: %d, cmd: %02X %02X. \r\n", ret,  write_buff[2], write_buff[3]);
        osDelay(10); 
    }
    return ret;
}



static void uart2_rx_callback(const void *buffer, uint16_t orginLen, bool error)
{  
    unused(error);
    radar_data_parse((uint8_t *)buffer, orginLen);

}

void Radar_Task(void)
{         
    // 2.初始化uart2：7,8 
    uapi_pin_set_mode(7, IOT_IO_FUNC_GPIO_7_UART2_RXD);     // uart2.rx + radar.tx  
    uapi_pin_set_mode(8, IOT_IO_FUNC_GPIO_8_UART2_TXD);     // uart2.tx + radar.rx 

    // 3.先重置
    uapi_uart_deinit(RADAR_UART_ID);
    IotUartAttribute uart_attr = {115200, 8, 1, 0, 100, 100, 0}; 
 
    // 4.初始化
    IoTUartInit(RADAR_UART_ID, &uart_attr); 
      
    // 5.注册回调函数  
    (void)uapi_uart_register_rx_callback(RADAR_UART_ID, UART_RX_CONDITION_FULL_OR_SUFFICIENT_DATA_OR_IDLE,
        1024, uart2_rx_callback); 
    
    osal_printk("\r\n== Radar-Monitor start... \r\n\r\n");    
 
}


//===========================================================
// 时钟函数
//===========================================================

void clock_timer_cb(void *arg)
{
    (void)arg;
    
    // 每秒执行，判断时间是否为 这分钟的开始
    uint32_t t = get_local_client();  // 
    struct tm *tblock;
    tblock = localtime((const time_t *)&t);   //北京时间补偿8小时
    // 秒 == 0 
    if(tblock->tm_sec == 0) {
        //printf("*** timer +> %02d:%02d \r\n", tblock->tm_min, tblock->tm_sec);
        
        SendClock();        // 整分校时

        Query_Presence();   // 每分钟查询人员存在，确保状态检测正常
    }
 
}
 
void timer_periodic(void)
{
    osTimerId_t periodic_tid = osTimerNew(clock_timer_cb, osTimerPeriodic, NULL, NULL);
    if (periodic_tid == NULL) {
        osal_printk("[Timer Test] osTimerNew(periodic timer) failed.\r\n");
        return;
    } 

    // 每秒触发一次
    uint32_t timeLen = 1 * 100; // 1 * 1s
 
    osStatus_t status = osTimerStart(periodic_tid, timeLen);
    if (status != osOK) {
        osal_printk("[Timer Test] osTimerStart(periodic timer) failed.\r\n");
        return;
    }  
}

//===========================================================
// 程序入口函数
//===========================================================

static void Blood_Entry(void)
{   
    // // ws2812_pwm 初始化
    // // Ws2812_Init(); 
   
    // ws2812 spi 初始化
    ws2812_spi_init();    
    //osDelay(10);  
    ws2812_spi_bright(255);     // 高亮
    ws2812_spi_bright(0);       // 熄灭 

    //LedPower_Register();        // Led灯电源控制
    SosPress_Register();        // SOS按键控制
 
    
    osThreadAttr_t attr1; 
    attr1.name = "Radar_Task";
    attr1.attr_bits = 0U;
    attr1.cb_mem = NULL;
    attr1.cb_size = 0U;
    attr1.stack_mem = NULL;
    attr1.stack_size = 10240;
    attr1.priority = 25;
    if (osThreadNew((osThreadFunc_t)Radar_Task, NULL, &attr1) == NULL)
    {
        osal_printk("== [Blood_Entry] falied to create Radar_Task(). \r\n");
    } 
     
      
    osThreadAttr_t attr; 
    attr.name = "Blood_Task";
    attr.attr_bits = 0U;
    attr.cb_mem = NULL;
    attr.cb_size = 0U;
    attr.stack_mem = NULL;
    attr.stack_size = 10240;
    attr.priority = 25;

    if (osThreadNew((osThreadFunc_t)Blood_Task, NULL, &attr) == NULL) {
        osal_printk("== [Blood_Entry] falied to create Blood_Task() \r\n");
    }  
    
    osDelay(500);
    timer_periodic();           // 启动定时器
}

// 程序入口
APP_FEATURE_INIT(Blood_Entry);




//========================================================
// LED 电源开关控制
//========================================================

/*
// LED灯的通电状态
static int LedPower = 1;

static void led_power_callback(pin_t pin, uintptr_t param)
{ 
    UNUSED(param);
    //osal_printk("== led_power_callback() .\r\n");

    // 读取当前GPIO电平：0 = falling, 1 = risign
    int level = uapi_gpio_get_val(pin);
    if (level == 0) {
        //if(LedPower == 1)
        { 
            osal_printk("== LED Button pressed (falling edge)\r\n");
            ws2812_spi_bright(0); // 按下熄灭 LED
            LedPower = 0;
        }
    } else {
        //if(LedPower == 0)
        {
            osal_printk("== LED Button released (rising edge)\r\n");
            ws2812_spi_bright(3); // 松开高亮 LED
            LedPower = 1;
        }
    }
}

static void LedPower_Register(void)
{
    uapi_pin_set_mode(LED_BUTTON_PIN, 0); 
    uapi_gpio_set_dir(LED_BUTTON_PIN, 0);  
    uapi_pin_set_pull(LED_BUTTON_PIN, 3);    // ==3

    errcode_t ret =uapi_gpio_register_isr_func(LED_BUTTON_PIN, (1 | 2), led_power_callback);
    if (ERRCODE_SUCC != ret) {
        // Cleanup any potentially registered interrupt on failure
        uapi_gpio_unregister_isr_func(LED_BUTTON_PIN);
        osal_printk("== ERROR: Failed to register gpio isr\r\n");
        return -1;
    } 

    
    // // Enable interrupts for the configured pin
    // ret = uapi_gpio_enable_interrupt(LED_BUTTON_PIN); 
    // if (ERRCODE_SUCC != ret) {
    //     uapi_gpio_unregister_isr_func(LED_BUTTON_PIN);
    //     osal_printk("Error: Failed to enable GPIO interrupts\r\n");
    //     return -1;
    // } 

    osal_printk("== LedPower_Register().\r\n");
}

*/