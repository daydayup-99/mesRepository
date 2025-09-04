import subprocess
import pyuac
def update_mysql_permissions():
    try:
        # 登录 MySQL 并执行命令
        commands = """
        USE mysql;
        UPDATE user SET host='%' WHERE user='root';
        FLUSH PRIVILEGES;
        """
        # 使用 subprocess 调用 MySQL
        process = subprocess.run(
            ["mysql", "-u", "root", "-pYMZ123"],  # 提示用户输入密码
            input=commands,
            text=True,
            check=True
        )
        print("权限修改成功，root 用户现在可以被远程访问。")
    except subprocess.CalledProcessError as e:
        print(f"权限修改失败，请检查 MySQL 是否正确安装或登录权限: {e}")
    except Exception as e:
        print(f"发生错误: {e}")

def restart_mysql_service():
    """
    重启 MySQL 服务以应用配置
    """
    possible_services = ["MySQL80", "MySQL"]  # 确保这里写的是正确的服务名称
    if not pyuac.isUserAdmin():
        pyuac.runAsAdmin()
        return
    for service_name in possible_services:
        try:
            # 停止服务
            subprocess.run(["net", "stop", service_name], check=True)
            # 启动服务
            subprocess.run(["net", "start", service_name], check=True)
            print(f"MySQL 服务 {service_name} 已成功重启。")
            return
        except subprocess.CalledProcessError:
            continue  # 尝试下一个服务名
    print("无法重启 MySQL 服务，请检查服务名称或权限。")

def main():
    print("开始配置 MySQL 服务器...")
    update_mysql_permissions()
    restart_mysql_service()
    print("MySQL 服务器配置完成，可远程访问")


if __name__ == "__main__":
    main()