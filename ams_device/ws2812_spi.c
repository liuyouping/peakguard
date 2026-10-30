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
#include "soc_osal.h"
#include "errcode.h"  

//#include "iot_gpio.h" 
#include "iot_gpio_ex.h"
#include "spi.h"  
#include "ws2812_spi.h"

//#include "los_interrupt.h"

#define spi_port    0    
 
#define on      0xFC //F0    // 11110000 - 高电平700ns，低电平600ns
#define off     0xE0 //C0    // 11000000 - 高电平350ns，低电平900ns
 
#define ledCount  10
#define bufCount (ledCount * 24) 
  
// spi初始化
int spi_init(void)
{    
    spi_attr_t config = { 0 };  
    config.is_slave = false;                                    // 主机模式  
    config.frame_size = HAL_SPI_FRAME_SIZE_8;                   // 帧大小，8位   
    config.slave_num  = 1;                                      // 片选 0  
    config.spi_frame_format = HAL_SPI_FRAME_FORMAT_STANDARD;    // 传输模式：标准   
    config.clk_polarity = 0;                                    // 极性：第一个时钟沿采集  
    config.tmod = HAL_SPI_TRANS_MODE_TX;                        // 传输模式：收发模式   
    config.sste = 0; 

    spi_extra_attr_t ext_config = { 0 }; 
    ext_config.sspi_param.wait_cycles = 0x10;                   // 等待周期  

    // deinit
    uapi_spi_deinit(spi_port);
 
    // 初始化SPI 
    int ret = uapi_spi_init(spi_port, &config, &ext_config);
    if(ret) {
        osal_printk("!! spi_init() fail: ret = %X \r\n", ret);
        return 0;
    } 
 
    osal_printk("== spi_init() succ ... \r\n");
    return 1;
} 

// 修复spi_write函数
void spi_write(uint8_t *buffer, int length) 
{  
    if (buffer == NULL || length <= 0) {
        osal_printk("!! spi_write() Invalid buffer parameters\r\n");
        return;
    }
    
 
    errcode_t ret = uapi_spi_master_write(spi_port, &xdata, 0xFF); // 增加超时
    if (ret != ERRCODE_SUCC) {
        //osal_printk("!! spi_write() write error: %X\r\n", ret);
    }   
}


// ===== 2. 颜色数值格式化   
void ws2812_format_new_0(uint8_t red, uint8_t green, uint8_t blue, uint8_t *buff) 
{ 
    if (buff == NULL) return;
    
    // GRB顺序（WS2812B要求）
    for(int i = 7; i >= 0; i--) {
        buff[7-i] = (green & (1 << i)) ? on : off;
    } 
    
    for(int i = 7; i >= 0; i--) {
        buff[16 + (7-i)] = (blue & (1 << i)) ? on : off;
    }
}

// 3byte为rgb转成24byte
void ws2812_format_new(uint8_t red, uint8_t green, uint8_t blue, uint8_t *buff) { 
    uint8_t data[24] = {0};  
    // 按位发送
    for(int i = 0; i < 8; i++)         // GREEN
    { 
        data[i] = (green & (0x01 << (7-i))) ? on : off; 
    }   
   
    for(int i = 0; i < 8; i++)         // BLUE
    { 
        data[i + 16] = (blue & (0x01 << (7-i))) ? on : off; 
    }
     
    memcpy(buff, data, 24);
}
 
// ===== 3. 灯珠控制函数  
void ws2812_close(void) 
{   
    uint8_t data[bufCount];
    memset(data, 0, sizeof(data)); 
    
    for (int i = 0; i < ledCount; i++) {
        uint8_t led_data[24];
        // 白色：全亮
        ws2812_format_new(0, 0, 0, led_data);
        memcpy(&data[i * 24], led_data, 24);
    }
    
    spi_write(data, bufCount);
    usleep(100);

    osal_printk(">> ws2812_close() ok.\r\n"); 
}

// 高亮  
void ws2812_high(void) 
{    
    uint8_t data[bufCount];
    memset(data, 0, sizeof(data)); 
    
    for (int i = 0; i < ledCount; i++) {
        uint8_t led_data[24];
        // 白色：全亮
        ws2812_format_new(255, 255, 255, led_data);
        memcpy(&data[i * 24], led_data, 24);
    }
    
    spi_write(data, bufCount);
    usleep(100);

    osal_printk(">> ws2812_high() ok.\r\n"); 
}

// 中亮
void ws2812_middle(void) 
{      
    uint8_t data[bufCount];
    memset(data, 0, sizeof(data));
    
    for (int i = 0; i < ledCount; i++) {
        uint8_t led_data[24];
         
        ws2812_format_new(191, 187, 187, led_data);
        memcpy(&data[i * 24], led_data, 24);
    }
    
    spi_write(data, bufCount);
    usleep(100);

    osal_printk(">> ws2812_middle() ok.\r\n"); 
}
 
// 低亮
void ws2812_low(void) 
{   
    uint8_t data[bufCount];
    memset(data, 0, sizeof(data));
    
    for (int i = 0; i < ledCount; i++) {
        uint8_t led_data[24];
         
        ws2812_format_new(64, 64, 64, led_data);
        memcpy(&data[i * 24], led_data, 24);
    }
    
    spi_write(data, bufCount);
    usleep(100);

    osal_printk(">> ws2812_low() ok.\r\n"); 
}
 

// 红色灯光
void ws2812_sos(void) 
{   
    uint8_t data[bufCount];
    memset(data, 0, sizeof(data));
    
    for (int i = 0; i < ledCount; i++) {
        uint8_t led_data[24];
         
        ws2812_format_new(220, 20, 20, led_data);
        memcpy(&data[i * 24], led_data, 24);
    }
    
    spi_write(data, bufCount);
    usleep(100);

    osal_printk(">> ws2812_low() ok.\r\n"); 
}

// ===== 4. 呼吸灯效果     

// 修复set_color函数
void set_color(uint8_t r, uint8_t g, uint8_t b) 
{    
    uint8_t data[bufCount];
    memset(data, 0, sizeof(data));
    
    // 为每个LED生成数据
    for (int i = 0; i < ledCount; i++) {
        uint8_t led_data[24];
        ws2812_format_new(r, g, b, led_data);
        memcpy(&data[i * 24], led_data, 24);
    }
    
    spi_write(data, bufCount);
    
    // 添加复位延时
    usleep(100); // 100us复位时间
}

// 呼吸灯循环函数 
osThreadId_t g_breath = NULL;   // 线程ID   

// 启动呼吸灯进程
void start_breath(void) { 
    
    if(g_breath == NULL){
        osThreadAttr_t attr; 
        attr.name = "breath_loop";
        attr.attr_bits = 0U;
        attr.cb_mem = NULL;
        attr.cb_size = 0U;
        attr.stack_mem = NULL;
        attr.stack_size = 1024;
        attr.priority = osPriorityAboveNormal6; 

        g_breath = osThreadNew((osThreadFunc_t)breath_loop_optimized(), NULL, &attr);
        printf("*** start_breath() ... ok. g_breath = %d. \r\n", g_breath);
    }
}
 
// ===== 5. 外部控制入口    
 
void ws2812_spi_init(void) 
{ 
    spi_init();     // spi 初始化 
    
    // 接线方式：灯带的LED线(din)接 hi3861 的引脚A9  
    // g9: sda, 初始化MOSI引脚
    uapi_pin_set_mode(9, IOT_IO_FUNC_GPIO_9_SPI0_OUT);
    uapi_gpio_set_dir(9, 1);  

    osal_printk(">> ws2812_init ok.\r\n"); 
}

void ws2812_spi_bright(int level)
{ 
    stop_breath();

    if(level==0){
        ws2812_close();
    } else if(level==1) {
        ws2812_low();
    } else if(level==9) {
        ws2812_sos();
    }
} 
 