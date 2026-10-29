#  ams_device_bin — 设备固件预编译包

存放「峰峦守护」可穿戴设备的**星闪（SLE）固件预编译产物**，方便直接烧录测试，无需本地编译环境。

---

##  文件清单

| 文件 | 类型 | 说明 |
|------|------|------|
| `sle_server.fwpkg` | SLE 服务端固件 | 烧录到 **可穿戴设备**（运行 `ams_device/` 源码编译产物） |
| `sle_client.fwpkg` | SLE 客户端固件 | 烧录到 **星闪客户端**（手机侧配套） |

##  烧录工具

使用 HiSilicon 官方 **HiBurn** 工具烧录：

1. 打开 HiBurn，选择对应串口
2. 加载 `.fwpkg` 固件包
3. 按住设备 BOOT 键后点击 Download

##  固件使用须知

- 固件中的 WiFi SSID / 密码、SLE MAC 地址、MQTT Broker 等参数均为**默认值**，需按「[ams_device](../ams_device/README.md#⚙️-自定义配置)」文档修改后**重新编译**
- 预编译固件基于 WS63 SDKv102，与源码目录 `ams_device/` 版本对应
- 若修改了 `iot_server.c` / `wifi_func.c` 等关键文件，**必须重新编译**生成新固件
