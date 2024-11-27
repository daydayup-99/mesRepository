import os
import time

import pyuac

def disable_log_bin(my_ini_path):
    """
    注释掉 my.ini 文件中的 log-bin 配置项
    :param my_ini_path: my.ini 文件的路径
    """
    try:
        # 确保 my.ini 文件存在
        if not os.path.exists(my_ini_path):
            print(f"找不到配置文件: {my_ini_path}")
            return

        # 读取文件内容
        with open(my_ini_path, "r", encoding="utf-8") as file:
            lines = file.readlines()

        # 修改内容：找到 log-bin 配置项并注释掉
        modified = False
        for i, line in enumerate(lines):
            if line.strip().lower().startswith("log-bin"):
                # 如果找到了 log-bin 行，则注释掉
                lines[i] = "#" + " " + line
                modified = True
                print(f"注释掉了: {line.strip()}")
                break  # 假设只需要处理一个 log-bin 配置项

        if not modified:
            print("未找到 log-bin 配置项，文件未做更改。")
            return

        # 将修改后的内容写回文件
        with open(my_ini_path, "w", encoding="utf-8") as file:
            file.writelines(lines)

        print(f"成功修改 {my_ini_path} 文件，已注释掉 log-bin 配置项。")

    except Exception as e:
        print(f"发生错误: {e}")

if __name__ == "__main__":
    # 使用 pyuac 提升权限
    if not pyuac.isUserAdmin():
        pyuac.runAsAdmin()
    else:
        # 调用函数
        my_ini_path = "C:\\ProgramData\\MySQL\\MySQL Server 8.0\\my.ini"  # 根据实际路径修改
        disable_log_bin(my_ini_path)
