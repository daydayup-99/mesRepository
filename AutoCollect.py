import os
from datetime import datetime
from zipfile import ZipFile
import sys

curDate = datetime.now().strftime('%Y%m%d')

def create_zip(file_paths, output_file):
    """
    使用 zipfile 模块创建 ZIP 文件。
    将指定路径下的多个文件打包到当前路径下的文件夹中。
    :param file_paths: 包含要打包的文件路径的列表
    :param output_file: 输出的 ZIP 文件路径
    """
    # 确保输出目录存在
    output_dir = os.path.dirname(output_file)
    os.makedirs(output_dir, exist_ok=True)

    with open('file_list.txt', 'w') as file_list:
        for file_path in file_paths:
            file_list.write(f'"{file_path}_{curDate}"\n')

    with ZipFile(output_file, 'w') as zipf:
        for file_path in file_paths:
            zipf.write(file_path, os.path.basename(file_path))  # 只写入文件名，不包含路径

    print(f"文件已打包到: {output_file}")

def find_files_in_directory(directory, file_names):
    """
    查找目录中指定名称的文件。
    :param directory: 要查找的目录路径
    :param file_names: 要查找的文件名列表
    :return: 查找到的文件路径列表
    """
    found_files = []
    for file in os.listdir(directory):
        file_tmp_path = os.path.join(directory, file)
        if file in file_names and os.path.isfile(file_tmp_path):
            found_files.append(file_tmp_path)
    return found_files

def main():
    # 从用户输入获取文件夹路径和版本号
    folder_path = os.path.dirname(sys.executable)
    print("当前路径：" + folder_path)
    version = input("请输入版本号：")

    file_path = os.path.join(folder_path, 'Daemon.txt')
    write_file = f'AISystem-YMZ-Entire-v{version}-rc.exe'
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"文件已删除: {file_path}")
    with open(file_path, 'w') as f:
        f.write(write_file)
    print(f"文件已创建: {file_path}")

    file_names = ['Interface.dll', 'EtData.dll', 'Daemon.exe', 'DetectDll.dll', 'AIBaseTool.dll', 'AIBaseUI.dll', 'AIDataManage.exe',
                  'AIErrDataDll.dll', 'AIStatistic.exe', f'AISystem-YMZ-Entire-v{version}-rc.exe', 'AIVerify.dll', 'AllPostSettingWin.dll',
                  'Config.dll', 'DDADDetector.dll', 'BaseTool.dll', 'DCodeManagerModule.dll', 'DrawGerber-2024-latest.dll', 'ImageLib.dll',
                  'libcrypto-1_1-x64.dll', 'libmysql.dll', 'libssl-1_1-x64.dll', 'libEGL.dll', 'libEGLd.dll', 'libGLESV2.dll', 'libiomp5md.dll',
                  'libiompstubs5md.dll', 'AIMes.dll', 'opencv_world460.dll', 'Daemon.txt']
    # file_names = [f'AISystem-YMZ-Entire-v{version}-rc.exe', 'libssl-1_1-x64.dll']
    # 查找指定文件
    file_paths = find_files_in_directory(folder_path, file_names)
    if not file_paths:
        print("没有找到指定的文件。")
        return

    output_file = os.path.join(folder_path, f'AISystem-v{version}.rar')

    # 创建 RAR 文件
    create_zip(file_paths, output_file)

if __name__ == "__main__":
    main()