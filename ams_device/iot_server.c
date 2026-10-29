/**
 * Copyright (c) HiSilicon (Shanghai) Technologies Co., Ltd. 2023-2023. All rights reserved.
 *
 * Description: SLE UART Server Source. \n
 *
 * History: \n
 * 2023-07-17, Create file. \n
 */

#include "cmsis_os2.h"

#include "common_def.h"
//#include "securec.h"
#include "soc_osal.h"
#include "sle_errcode.h"
#include "sle_connection_manager.h"
#include "sle_device_discovery.h"

#include "iot_server_ex.h"
#include "iot_server.h"
#include "osal_timer.h"
//#include "mqtt_main.h"  //publish_radar_data
#include "blood_func.h"

#ifdef CONFIG_SAMPLE_SUPPORT_LOW_LATENCY_TYPE
#include "sle_low_latency.h"
#endif
#define OCTET_BIT_LEN           8
#define UUID_LEN_2              2
#define UUID_INDEX              14 
#define UART_BUFF_LENGTH        0x100
#define SLE_MTU_SIZE            200 

#define UUID_16BIT_LEN 2
#define UUID_128BIT_LEN 16
#define log_print(fmt, args...)     osal_printk(fmt, ##args)
#define LOG_ID                      "[sle uart server]"
#define SLE_SERVER_INIT_DELAY_MS    1000
#define SPEED_DEFAULT_TIMEOUT_MULTIPLIER 0x1f4

// ??
static sle_uart_server_msg_queue g_sle_uart_server_msg_queue = NULL;

uint8_t g_mac[SLE_ADDR_LEN] = {0x11,0x11,0x22,0x22,0x00,0x25}; // 0x04-->0x07

static uint8_t g_sle_uuid_base[] = { 0x37, 0xBE, 0xA8, 0x80, 0xFC, 0x70, 0x11, 0xEA, \
    0xB7, 0x20, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 };

    
/* 广播ID */
#define SLE_ADV_HANDLE_DEFAULT  1
/* sle server app uuid for test */
static char g_app_uuid[UUID_LEN_2] = { 0x12, 0x34 };
/* server notify property uuid for test */
static char g_property_uuid[OCTET_BIT_LEN] = { 0x06, 0x05, 0x04, 0x03, 0x02, 0x01 };

/* sle connect acb handle */
static uint16_t g_conn_hdl = 0;
/* sle server handle */
static uint8_t g_server_handle = 0;
/* sle service handle */
static uint16_t g_service_hdl = 0;
/* sle ntf property handle */
static uint16_t g_property_hdl = 0;
/* sle pair acb handle */
uint16_t g_pair_hdl;


// ===== 
uint16_t get_connect_id(void) {
    return g_conn_hdl;
}

uint16_t iot_client_is_connected(void) {
    return g_pair_hdl;
}

void iot_server_register_msg(sle_uart_server_msg_queue sle_uart_server_msg) {
    g_sle_uart_server_msg_queue = sle_uart_server_msg;
}


void iot_server_sample_set_mcs(uint16_t conn_id)
{
#ifdef CONFIG_SAMPLE_SUPPORT_PERFORMANCE_TYPE
    if (sle_set_mcs(conn_id, 10) != 0) { // mcs10
        osal_printk("%s sle_set_mcs fail\r\n", LOG_ID);
        return;
    }
    osal_printk("%s sle_set_mcs success\r\n", LOG_ID);
#else
    unused(conn_id);
    // 非跑流sample使用原mcs参数
#endif
    return;
}

// sle_uuid_setu2 ==>

static void encode2byte_little(uint8_t *_ptr, uint16_t data) {
    *(uint8_t *)((_ptr) + 1) = (uint8_t)((data) >> 0x8);
    *(uint8_t *)(_ptr) = (uint8_t)(data);
}

static void sle_uuid_set_base(sle_uuid_t *out) {
    errcode_t ret;
    ret = memcpy_s(out->uuid, SLE_UUID_LEN, g_sle_uuid_base, SLE_UUID_LEN);
    if (ret != EOK) {
        log_print("%s sle_uuid_set_base memcpy fail\n", LOG_ID);
        out->len = 0;
        return ;
    }
    out->len = UUID_LEN_2;
}

static void sle_uuid_setu2(uint16_t u2, sle_uuid_t *out) {
    sle_uuid_set_base(out);
    out->len = UUID_LEN_2;
    encode2byte_little(&out->uuid[UUID_INDEX], u2);
}
// end ===


/*
 
static void sle_uart_uuid_print(sle_uuid_t *uuid) {
    if (uuid == NULL) {
        log_print("%s uuid_print,uuid is null\r\n", LOG_ID);
        return;
    }
    if (uuid->len == UUID_16BIT_LEN) {
        log_print("%s uuid: %02x %02x.\n", LOG_ID,
            uuid->uuid[14], uuid->uuid[15]);    // 14 15: uuid index 
    } else if (uuid->len == UUID_128BIT_LEN) {
        log_print("%s uuid: \n", LOG_ID);       // 14 15: uuid index 
        log_print("%s 0x%02x 0x%02x 0x%02x \n", LOG_ID, uuid->uuid[0], uuid->uuid[1],
            uuid->uuid[2], uuid->uuid[3]);
        log_print("%s 0x%02x 0x%02x 0x%02x \n", LOG_ID, uuid->uuid[4], uuid->uuid[5],
            uuid->uuid[6], uuid->uuid[7]);
        log_print("%s 0x%02x 0x%02x 0x%02x \n", LOG_ID, uuid->uuid[8], uuid->uuid[9],
            uuid->uuid[10], uuid->uuid[11]);
        log_print("%s 0x%02x 0x%02x 0x%02x \n", LOG_ID, uuid->uuid[12], uuid->uuid[13],
            uuid->uuid[14], uuid->uuid[15]);
    }
}

static void ssaps_add_service_cbk(uint8_t server_id, sle_uuid_t *uuid, uint16_t handle, errcode_t status)
{
    log_print("%s ssaps_add_service_cbk() server_id:%x, handle:%x, status:%x\r\n", LOG_ID,
        server_id, handle, status);
    sle_uart_uuid_print(uuid);
}

static void ssaps_add_property_cbk(uint8_t server_id, sle_uuid_t *uuid, uint16_t service_handle,
    uint16_t handle, errcode_t status)
{
    log_print("%s add property cbk callback server_id:%x, service_handle:%x,handle:%x, status:%x\r\n",
        LOG_ID, server_id, service_handle, handle, status);
    sle_uart_uuid_print(uuid);
}

static void ssaps_add_descriptor_cbk(uint8_t server_id, sle_uuid_t *uuid, uint16_t service_handle,
    uint16_t property_handle, errcode_t status)
{
    log_print("%s add descriptor cbk callback server_id:%x, service_handle:%x, property_handle:%x, \
        status:%x\r\n", LOG_ID, server_id, service_handle, property_handle, status);
    sle_uart_uuid_print(uuid);
}


static void ssaps_delete_all_service_cbk(uint8_t server_id, errcode_t status)
{
    log_print("%s delete all service callback server_id:%x, status:%x\r\n", LOG_ID,
        server_id, status);
}

*/

// ssaps callback ==>

 

// ssaps read, write callback ==>
 
static void ssaps_read_request_cbk(uint8_t server_id, uint16_t conn_id, ssaps_req_read_cb_t *read_cb_para,
                            errcode_t status)
{
    (void)server_id;
    (void)conn_id;
    (void)read_cb_para;
    (void)status;
}
 
static void ssaps_write_request_cbk(uint8_t server_id, uint16_t conn_id, ssaps_req_write_cb_t *write_cb_para,
                             errcode_t status)
{
    (void)server_id;
    (void)conn_id;
    (void)status;
    //write_cb_para->value[write_cb_para->length - 1] = '\0';
    //osal_printk("[ssaps_write_request_cbk] client_send_data: %s\r\n", write_cb_para->value); 

 

    if (write_cb_para->length >= 3) { 

        int cmd0 = write_cb_para->value[0];
        int cmd1 = write_cb_para->value[1];
        // 请求当前服务器时间：0x03, 0x01, 0x00
        if(cmd0==03 && cmd1==1){
            SendClock();
        }
 
    }


    
    //uint8_t data[] = "send from iot server!";
    //int ret = iot_server_send_data(data, sizeof(data));

    //publish_radar_data(cmd, value, result, action, timestamp);  // 发布数据

    //uint8_t *d2 = (uint8_t *) write_cb_para->value;
    //publish_sle_data(d2);
 
    // kind:
    // 04 01 00    >> 04 lamp, 01 (01低亮, 02中亮, 03高亮, 00关灯), 00结束符
    ProcessClient(write_cb_para->value, write_cb_para->length); 
    
}


// ssaps 总的注册入口
static errcode_t sle_ssaps_register_cbks(void)
{
    errcode_t ret;
    ssaps_callbacks_t ssaps_cbk = {0};
    // ssaps_cbk.add_service_cb = ssaps_add_service_cbk;
    // ssaps_cbk.add_property_cb = ssaps_add_property_cbk;
    // ssaps_cbk.add_descriptor_cb = ssaps_add_descriptor_cbk;
    // ssaps_cbk.delete_all_service_cb = ssaps_delete_all_service_cbk;

    ssaps_cbk.start_service_cb = ssaps_start_service_cbk; 
    ssaps_cbk.mtu_changed_cb = ssaps_mtu_changed_cbk;
 
    ret = ssaps_register_callbacks(&ssaps_cbk);
    if (ret != ERRCODE_SLE_SUCCESS) {
        log_print("%s sle_ssaps_register_cbks(). fail :%x\r\n", LOG_ID,
            ret);
        return ret;
    }
    return ERRCODE_SLE_SUCCESS;
}
// end ===

// sle uuid 相关 ==>

static errcode_t sle_uuid_server_service_add(void)
{
    errcode_t ret;
    sle_uuid_t service_uuid = {0};
    sle_uuid_setu2(SLE_UUID_SERVER_SERVICE, &service_uuid);

    ret = ssaps_add_service_sync(g_server_handle, &service_uuid, 1, &g_service_hdl);
    if (ret != ERRCODE_SLE_SUCCESS) {
        log_print("%s sle_uuid_server_service_add(). fail, ret:%x\r\n", LOG_ID, ret);
        return ERRCODE_SLE_FAIL;
    }
    return ERRCODE_SLE_SUCCESS;
}

static errcode_t sle_uuid_server_property_add(void)
{
    errcode_t ret;
    ssaps_property_info_t property = {0};
    ssaps_desc_info_t descriptor = {0};

    // 指定的 ntf 
    uint8_t ntf_value[] = { 0x01, 0x00 };  

    property.permissions = SLE_UUID_TEST_PROPERTIES;                    // read | write
    property.operate_indication = SLE_UUID_TEST_OPERATION_INDICATION;   // +++ SSAP_OPERATE_INDICATION_BIT_NOTIFY

    sle_uuid_setu2(SLE_UUID_SERVER_NTF_REPORT, &property.uuid);

    property.value = (uint8_t *)osal_vmalloc(sizeof(g_property_uuid));
    if (property.value == NULL) {
        return ERRCODE_SLE_FAIL; 
    }

    // 修复：确保使用正确的CCC描述符类型
    descriptor.permissions = SLE_UUID_TEST_DESCRIPTOR;
    descriptor.type =  SSAP_DESCRIPTOR_CLIENT_CONFIGURATION;  // SSAP_DESCRIPTOR_USER_DESCRIPTION; //
    descriptor.operate_indication = SLE_UUID_TEST_OPERATION_INDICATION;
    descriptor.value_len = sizeof(ntf_value);

    descriptor.value = (uint8_t *)osal_vmalloc(sizeof(ntf_value));
    if (descriptor.value == NULL) {
        osal_vfree(property.value);
        return ERRCODE_SLE_FAIL;
    } 
    
    // 写入 描述符
    if (memcpy_s(descriptor.value, sizeof(ntf_value), ntf_value, sizeof(ntf_value)) != EOK) {
        osal_vfree(property.value);
        osal_vfree(descriptor.value);
        return ERRCODE_SLE_FAIL;
    }

    ret = ssaps_add_descriptor_sync(g_server_handle, g_service_hdl, g_property_hdl, &descriptor);
    if (ret != ERRCODE_SLE_SUCCESS) {
        log_print("%s sle uart add descriptor fail, ret:%x\r\n", LOG_ID, ret);
        osal_vfree(property.value);
        osal_vfree(descriptor.value);
        return ERRCODE_SLE_FAIL;
    } 

    osal_vfree(property.value);
    osal_vfree(descriptor.value);
    return ERRCODE_SLE_SUCCESS;
}

static errcode_t sle_uuid_server_add(void)
{
    errcode_t ret;
    sle_uuid_t app_uuid = {0};

    log_print("%s sle_uuid_server_add() begin ...\r\n", LOG_ID);

    app_uuid.len = sizeof(g_app_uuid);  // 12 34
    if (memcpy_s(app_uuid.uuid, app_uuid.len, g_app_uuid, sizeof(g_app_uuid)) != EOK) {
        return ERRCODE_SLE_FAIL;
    }

    // 按 uuid 注册服务
    ssaps_register_server(&app_uuid, &g_server_handle);

    if (sle_uuid_server_service_add() != ERRCODE_SLE_SUCCESS) {
        ssaps_unregister_server(g_server_handle);
        return ERRCODE_SLE_FAIL;
    } 

    log_print("%s sle_uuid_server_add() end. \r\n", LOG_ID);
    return ERRCODE_SLE_SUCCESS;
}
// end uuid ===

// sle_connect ==>

static void sle_connect_state_changed_cbk(uint16_t conn_id, const sle_addr_t *addr,
    sle_acb_state_t conn_state, sle_pair_state_t pair_state, sle_disc_reason_t disc_reason)
{
    uint8_t sle_connect_state[] = "sle_dis_connect";

    log_print("%s connect state changed callback conn_id:0x%02x, conn_state:0x%x, pair_state:0x%x, \
        disc_reason:0x%x\r\n", LOG_ID,conn_id, conn_state, pair_state, disc_reason);
    log_print("%s connect state changed callback addr:%02x:**:**:**:%02x:%02x\r\n", LOG_ID,
        addr->addr[0], addr->addr[4]);

    if (conn_state == SLE_ACB_STATE_CONNECTED)              // ==1
    {
        g_conn_hdl = conn_id;  // 连接ID

        sle_set_data_len(conn_id, SLE_MTU_SIZE-12); // 设置有效载荷, 否则客户端接受会有问题: 512-12=500 

        sle_connection_param_update_t parame = {0};
        parame.conn_id = conn_id;
        parame.interval_min = 0x20;
        parame.interval_max = 0x20;
        parame.max_latency = 0;
        parame.supervision_timeout = SPEED_DEFAULT_TIMEOUT_MULTIPLIER;
    
        sle_update_connect_param(&parame);
        
    } 
    else if (conn_state == SLE_ACB_STATE_DISCONNECTED)      // ==2
    {
        g_conn_hdl = 0;
        g_pair_hdl = 0;

        // ??
        if (g_sle_uart_server_msg_queue != NULL) {
            g_sle_uart_server_msg_queue(sle_connect_state, sizeof(sle_connect_state));
        }

        // 启动重连定时器: add by liuyp@20250912 
        iot_server_ex_stop();
        
        // 重新启动广播
        iot_server_ex_init(); 
         
    }
}

static void sle_pair_complete_cbk(uint16_t conn_id, const sle_addr_t *addr, errcode_t status)
{
    log_print("%s pair complete conn_id: %02x, status:%x\r\n", LOG_ID,
        conn_id, status);
    log_print("%s pair complete addr: %02x:**:**:**:%02x:%02x\r\n", LOG_ID,
        addr->addr[0], addr->addr[4], addr->addr[5]); 

    g_pair_hdl = conn_id + 1;    
}



static errcode_t sle_conn_register_cbks(void)
{
    errcode_t ret;
    
    sle_connection_callbacks_t conn_cbks = {0};
    conn_cbks.connect_state_changed_cb = sle_connect_state_changed_cbk;
    conn_cbks.pair_complete_cb = sle_pair_complete_cbk;

    ret = sle_connection_register_callbacks(&conn_cbks);
    if (ret != ERRCODE_SLE_SUCCESS) {
        log_print("%s sle_conn_register_cbks()... fail: %x\r\n", LOG_ID, ret);
        return ret;
    }
    return ERRCODE_SLE_SUCCESS;
}
// end ===

 
int iot_server_init(void)
{
    errcode_t ret;

    random_mac_addr(g_mac);    // 随机地址

    // 打印mac地址
    log_print("===================mac addr: %02x:%02x:%02x:%02x:%02x:%02x==================== \r\n\r\n",
        g_mac[0], g_mac[1], g_mac[2], g_mac[3], g_mac[4], g_mac[5]);

    uapi_watchdog_disable();
 
    if (enable_sle() != ERRCODE_SUCC) {
        log_print("%s iot_server_ex_init(), enable_sle() fail !\r\n", LOG_ID );
        return -1;
    }  

    ret = iot_announce_register_cbks();
    if (ret != ERRCODE_SLE_SUCCESS) {
        log_print("%s iot_server_ex_init(), iot_announce_register_cbks() fail: %x \r\n", LOG_ID,ret);
        return ret;
    }
    ret = sle_conn_register_cbks();
    if (ret != ERRCODE_SLE_SUCCESS) {
        log_print("%s iot_server_ex_init(), sle_conn_register_cbks() fail: %x\r\n", LOG_ID, ret);
        return ret;
    }  

    ret = sle_ssaps_register_cbks();
    if (ret != ERRCODE_SLE_SUCCESS)
    {
        log_print("%s iot_server_ex_init(), sle_ssaps_register_cbks() fail: %x\r\n", LOG_ID, ret);
        return ret;
    }

    // 注册Server, 添加Service和property, 启动Service 
    ret = sle_uuid_server_add();
    if (ret != ERRCODE_SLE_SUCCESS) {
        log_print("%s iot_server_ex_init(), sle_uuid_server_add () fail: %x\r\n", LOG_ID, ret);
        return ret;
    }  

    // 设置设备公开，并公开设备 
    ret = iot_server_ex_init();
    if (ret != ERRCODE_SLE_SUCCESS) {
        log_print("%s iot_server_ex_init(), iot_server_ex_init() fail: %x\r\n", LOG_ID, ret);
        return ret;
    }

    // 正常交换数据，从 server => client 
    ssap_exchange_info_t parameter = { 0 };
    parameter.mtu_size = 36; // SLE_MTU_SIZE;
    parameter.version = 9;
    ssaps_set_info(g_server_handle, &parameter);

    //
    sle_addr_t addr = {0};
    addr.type = 0;
    memcpy_s(addr.addr, SLE_ADDR_LEN, g_mac, SLE_ADDR_LEN);
    sle_set_local_addr(&addr);

    log_print("%s init ok \r\n\r\n", LOG_ID);
    
    return ERRCODE_SLE_SUCCESS;
} 
// end ===


// send data ==>

// device通过handle向host发送数据：report 
errcode_t iot_server_send_report_by_handle(const uint8_t *data, uint16_t len)
{
    ssaps_ntf_ind_t param = {0}; 

    param.handle = g_property_hdl;
    param.type = SSAP_PROPERTY_TYPE_VALUE;  
    param.value_len = len;

    param.value = osal_vmalloc(len);    // malloc 
    // 复制数据data => param.vlaue
    if (memcpy_s(param.value, param.value_len, data, len) != EOK) {
        osal_vfree(param.value);
        return ERRCODE_SLE_FAIL;
    }  

    // // 显示需要发送的数据
    // if (len > 0)  { 
    //     osal_printk("[SLE Server]... send [%d]: ", param.value_len);
    //     for (uint16_t i = 0; i < len; i++) {
    //         osal_printk("%02X ", param.value[i]);
    //     }
    //     osal_printk("\r\n");
    // }    

    // 发送数据  
    if (ssaps_notify_indicate(g_server_handle, g_conn_hdl, &param) != ERRCODE_SUCC) {
        //log_print("[SLE Server]... ssaps_notify_indicate() fail\r\n");
        osal_vfree(param.value);
        return ERRCODE_FAIL;
    }

    osal_vfree(param.value);            // free 
    return ERRCODE_SUCC;
}

// // device通过uuid向host发送数据：report 
// errcode_t sle_server_send_report_by_uuid(const uint8_t *data, uint8_t len)
// {
//     ssaps_ntf_ind_by_uuid_t param = {0};
//     param.type = SSAP_PROPERTY_TYPE_VALUE;
//     param.start_handle = g_service_hdl;
//     param.end_handle = g_property_hdl;

//     param.value = osal_vmalloc(len);    // malloc
//     param.value_len = len;

//     if (memcpy_s(param.value, param.value_len, data, len) != EOK) {
//         osal_vfree(param.value);
//         return ERRCODE_SLE_FAIL;
//     }  

//     // uuid: 23 23
//     sle_uuid_setu2(SLE_UUID_SERVER_NTF_REPORT, &param.uuid);

//     // 发送
//     //ssaps_notify_indicate_by_uuid(g_server_handle, g_conn_hdl, &param);
//     if (ssaps_notify_indicate(g_server_handle, g_conn_hdl, &param) != ERRCODE_SUCC) {
//         log_print("[SLE Server] ssaps_notify_indicate_by_uuid() fail\r\n");
//         osal_vfree(param.value);
//         return ERRCODE_FAIL;
//     }

//     osal_vfree(param.value);            // free 
//     return ERRCODE_SUCC;
// }

// server向client发送数据 
int iot_server_send_data(uint8_t *data, uint16_t length)
{
    int ret; 

    // 检查是否有活跃的连接
    //if (g_conn_hdl != 0 && g_pair_hdl != 0) 
    { 
        // 发送数据
        ret = iot_server_send_report_by_handle(data, length);
        osDelay(1);

        if (ret != ERRCODE_SLE_SUCCESS) {
            osal_printk("[SLE Server]... iot_server_send_data() fail: 0x%X \r\n", ret);
            return ret;
        }
        //log_print("-- iot_server_send_data succ!!! \r\n");
        
        // 显示需要发送的数据
        if (length > 0)  { 
            osal_printk("[SLE Server]... send [%d]: ", length);
            for (uint16_t i = 0; i < length; i++) {
                osal_printk("%02X ", data[i]);
            }
            osal_printk("\r\n");
        }    
    } 
    // else {
    //     osal_printk("[SLE Server]... no active connection, skip send. \r\n");
    //     return ERRCODE_FAIL;
    // }

    return ret;
}

// end send data <===