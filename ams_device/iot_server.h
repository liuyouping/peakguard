/**
 * Copyright (c) HiSilicon (Shanghai) Technologies Co., Ltd. 2023-2023. All rights reserved.
 *
 * Description: SLE uart server Config. \n
 *
 * History: \n
 * 2023-07-17, Create file. \n
 */

#ifndef IOT_SERVER_H
#define IOT_SERVER_H

#include <stdint.h>
#include "sle_ssap_server.h"
#include "errcode.h"

#ifdef __cplusplus
#if __cplusplus
extern "C" {
#endif /* __cplusplus */
#endif /* __cplusplus */

/* Service UUID */
#define SLE_UUID_SERVER_SERVICE        0x2222

/* Property UUID */
#define SLE_UUID_SERVER_NTF_REPORT     0x2323

/* Property Property */
#define SLE_UUID_TEST_PROPERTIES  (SSAP_PERMISSION_READ | SSAP_PERMISSION_WRITE)

/* Operation indication */
#define SLE_UUID_TEST_OPERATION_INDICATION  (SSAP_OPERATE_INDICATION_BIT_READ | SSAP_OPERATE_INDICATION_BIT_WRITE | SSAP_OPERATE_INDICATION_BIT_NOTIFY | SSAP_OPERATE_INDICATION_BIT_INDICATE)

/* Descriptor Property */
#define SLE_UUID_TEST_DESCRIPTOR   (SSAP_PERMISSION_READ | SSAP_PERMISSION_WRITE)


typedef void (*sle_uart_server_msg_queue)(uint8_t *buffer_addr, uint16_t buffer_size);

uint16_t get_connect_id(void);

uint16_t iot_client_is_connected(void);

void iot_server_register_msg(sle_uart_server_msg_queue sle_uart_server_msg);

void iot_server_sample_set_mcs(uint16_t conn_id);

int iot_server_init(void); 

int iot_server_send_data(uint8_t *data, uint16_t length); 

#ifdef __cplusplus
#if __cplusplus
}
#endif /* __cplusplus */
#endif /* __cplusplus */

#endif