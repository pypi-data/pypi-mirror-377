from ubox_py_sdk import DriverType, RunMode, OSType, DeviceButton, UBox, operation_timer

if __name__ == '__main__':
    print("\n示例：")
    try:
        with UBox(
                secret_id="your_secret_id_here",
                secret_key="your_secret_key_here",
        ) as ubox:
            # 初始化设备
            device = ubox.init_device(
                udid="your_device_udid_here",
                os_type=OSType.ANDROID,
                # auth_code="your_auth_code_here",
            )
            print(f"设备初始化成功: {device.udid}")
            # 执行操作
            with operation_timer("获取设备信息"):
                device_info = device.device_info()
                if device_info:
                    print(f"设备型号: {device_info.get('model', 'Unknown')}")
            with operation_timer("截图操作"):
                screenshot_result = device.screenshot("demo","./screenshots")
                print(f"截图成功: {screenshot_result.get('imageUrl', 'N/A')}")
            print("注意：使用with语句，无需手动调用ubox.close()")

    except Exception as e:
        print(f"❌ 示例执行失败: {e}")
