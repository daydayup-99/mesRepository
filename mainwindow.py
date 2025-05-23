import os
import sys
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageDraw, ImageTk
from pystray import Icon, MenuItem, Menu
import configparser

config = configparser.ConfigParser()
# config_dir = os.path.dirname(os.path.realpath(__file__))
config_dir = os.path.dirname(sys.executable)
config_path = os.path.join(config_dir, 'config.ini')
config.read(config_path)

# 将表头配置保存到配置文件
def save_headers_config(selected_headers):
    if 'export' not in config:
        config.add_section('export')
    config['export']['selected_headers'] = ','.join(selected_headers)
    with open(config_path, 'w') as f:
        config.write(f)
    return True

# 从配置文件读取表头配置
def load_headers_config():
    if 'export' in config and 'selected_headers' in config['export']:
        headers_str = config['export']['selected_headers']
        if headers_str:
            return headers_str.split(',')
    return ['日期', '料号', '批量号', '假点过滤率', '总点过滤率', 'AI漏失总数', '漏失率',
           '总板数', 'AI跑板数', 'AVI缺陷总数', 'AVI缺陷总数T', 'AVI缺陷总数B', 'AVI真点总数', 'AVI真点总数T', 'AVI真点总数B',
           'AI真点总数', 'AI真点总数T', 'AI真点总数B', 'AI假点总数', 'AI假点总数T', 'AI假点总数B', '平均报点', '平均报点T', '平均报点B', '平均AI报点', '平均AI报点T',
           '平均AI报点B', 'OK板总数', 'AI_OK板总数', 'OK板比例', 'AI_OK板比例', '膜面', '机台号']

back_path = os.path.join(config_dir, 'background.jpg')

PRIMARY_COLOR = "#2196F3"  # 蓝色
BG_COLOR = "#F5F5F5"  # 浅灰色背景

window = tk.Tk()
window.title("Mes App")
window.geometry('500x400')
background_image = Image.open(back_path)
background_image = background_image.resize((500, 400), Image.Resampling.LANCZOS)
background_photo = ImageTk.PhotoImage(background_image)
canvas = tk.Canvas(window, width=500, height=400)
canvas.pack(fill="both", expand=True)
canvas.create_image(0, 0, image=background_photo, anchor="nw")

canvas.create_rectangle(50, 50, 450, 350, fill="white", outline="", stipple="gray50")

status_label = tk.Label(window, text="MES 软件正在运行中",
                        font=("Montserrat", 24, "bold"),
                        fg=PRIMARY_COLOR,
                        bg="white",
                        padx=20, pady=20,
                        relief="ridge",
                        bd=1)
canvas.create_window(250, 150, window=status_label)

# 创建表头配置窗口
def show_headers_config(icon=None, item=None):
    window.deiconify()
    
    config_window = tk.Toplevel(window)
    config_window.title("表头配置")
    config_window.geometry("450x600")
    config_window.configure(bg=BG_COLOR)
    config_window.transient(window)  # 设置为主窗口的子窗口
    all_headers = ['日期', '料号', '批量号', '假点过滤率', '总点过滤率', 'AI漏失总数', '漏失率',
                  '总板数', 'AI跑板数', 'AVI缺陷总数', 'AVI缺陷总数T', 'AVI缺陷总数B', 'AVI真点总数', 'AVI真点总数T', 'AVI真点总数B',
                  'AI真点总数', 'AI真点总数T', 'AI真点总数B', 'AI假点总数', 'AI假点总数T', 'AI假点总数B', '平均报点', '平均报点T', '平均报点B', '平均AI报点', '平均AI报点T',
                  '平均AI报点B', 'OK板总数', 'AI_OK板总数', 'OK板比例', 'AI_OK板比例', '膜面', '机台号']
    current_headers = load_headers_config()
    title_frame = tk.Frame(config_window, bg=BG_COLOR, pady=10)
    title_frame.pack(fill="x")
    title_label = tk.Label(title_frame,
                          text="配置导出表头", 
                          font=("Arial", 16, "bold"),
                          bg=BG_COLOR,
                          fg=PRIMARY_COLOR)
    title_label.pack()
    desc_label = tk.Label(title_frame,
                         text="选择要在Web页面导出时包含的表头", 
                         font=("Arial", 10),
                         bg=BG_COLOR)
    desc_label.pack(pady=(5, 0))
    
    # 创建搜索过滤框
    search_frame = tk.Frame(config_window, bg=BG_COLOR, pady=10)
    search_frame.pack(fill="x", padx=20)
    
    search_label = tk.Label(search_frame, text="搜索:", bg=BG_COLOR)
    search_label.pack(side="left", padx=(0, 5))
    
    search_var = tk.StringVar()
    search_entry = tk.Entry(search_frame, textvariable=search_var, width=30)
    search_entry.pack(side="left", fill="x", expand=True)
    
    # 创建主内容框架
    content_frame = tk.Frame(config_window, bg=BG_COLOR)
    content_frame.pack(fill="both", expand=True, padx=20, pady=10)
    
    # 创建滚动区域
    scroll_frame = tk.Frame(content_frame, bg="white", bd=1, relief="solid")
    scroll_frame.pack(fill="both", expand=True)
    
    canvas = tk.Canvas(scroll_frame, bg="white", highlightthickness=0)
    scrollbar = tk.Scrollbar(scroll_frame, orient="vertical", command=canvas.yview)
    
    # 添加鼠标滚轮支持功能
    def on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    
    # 创建一个框架来放置复选框
    checkbox_frame = tk.Frame(canvas, bg="white")
    checkbox_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    
    canvas.create_window((0, 0), window=checkbox_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    canvas.bind("<MouseWheel>", on_mousewheel)
    
    var_dict = {}
    checkbox_widgets = []
    
    for i, header in enumerate(all_headers):
        var = tk.BooleanVar(value=header in current_headers)
        var_dict[header] = var
        
        row_frame = tk.Frame(checkbox_frame, bg="white", pady=3)
        row_frame.pack(fill="x", padx=10)
        
        cb = tk.Checkbutton(row_frame, 
                           text=header, 
                           variable=var, 
                           bg="white", 
                           font=("Arial", 10),
                           padx=5,
                           anchor="w")
        cb.pack(side="left", fill="x", expand=True)
        checkbox_widgets.append((cb, header))
    
    def filter_checkboxes(*args):
        search_text = search_var.get().lower()
        for cb, header in checkbox_widgets:
            if search_text and search_text not in header.lower():
                cb.pack_forget()
            else:
                cb.pack(side="left", fill="x", expand=True)
                cb.master.pack(fill="x", padx=10)
    
    search_var.trace("w", filter_checkboxes)
    
    button_frame = tk.Frame(config_window, bg=BG_COLOR, pady=10)
    button_frame.pack(fill="x", padx=20)
    
    def select_all():
        for var in var_dict.values():
            var.set(True)
    
    def deselect_all():
        for var in var_dict.values():
            var.set(False)
    
    select_all_btn = tk.Button(button_frame, 
                              text="全选", 
                              command=select_all,
                              bg=PRIMARY_COLOR,
                              fg="white",
                              font=("Arial", 10, "bold"),
                              padx=10,
                              relief="flat")
    select_all_btn.pack(side="left", padx=(0, 5))
    
    deselect_all_btn = tk.Button(button_frame, 
                                text="全不选", 
                                command=deselect_all,
                                bg=PRIMARY_COLOR,
                                fg="white",
                                font=("Arial", 10, "bold"),
                                padx=10,
                                relief="flat")
    deselect_all_btn.pack(side="left")
    
    bottom_frame = tk.Frame(config_window, bg=BG_COLOR, pady=15)
    bottom_frame.pack(fill="x", padx=20)
    
    def save_config():
        selected = [header for header, var in var_dict.items() if var.get()]
        if not selected:
            messagebox.showwarning("警告", "至少需要选择一个表头")
            return
        
        if save_headers_config(selected):
            messagebox.showinfo("成功", "表头配置已保存")
            status_label.config(text="表头配置已保存")
            window.after(3000, lambda: status_label.config(text="MES 软件正在运行中"))
            config_window.destroy()
            if icon is not None:
                hide_window()
    
    cancel_btn = tk.Button(bottom_frame, 
                          text="取消", 
                          command=config_window.destroy,
                          bg="#e0e0e0",
                          font=("Arial", 10),
                          padx=15,
                          relief="flat")
    cancel_btn.pack(side="right", padx=(5, 0))
    
    save_btn = tk.Button(bottom_frame, 
                        text="保存", 
                        command=save_config,
                        bg=PRIMARY_COLOR,
                        fg="white",
                        font=("Arial", 10, "bold"),
                        padx=15,
                        relief="flat")
    save_btn.pack(side="right")

export_btn = tk.Button(window,
                      text="配置导出表头", 
                      command=show_headers_config,
                      bg=PRIMARY_COLOR,
                      fg="white",
                      font=("Arial", 12, "bold"),
                      padx=15,
                      pady=5,
                      relief="flat")
canvas.create_window(250, 220, window=export_btn)

def create_image():
    icon_path = os.path.join(config_dir, 'icon.png')
    if os.path.exists(icon_path):
        image = Image.open(icon_path)
    else:
        width, height = 64, 64
        image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        draw.rectangle([16, 16, 48, 48], fill=PRIMARY_COLOR)
    return image

def on_show_window(icon, item):
    window.deiconify()  # 显示窗口
    status_label.config(text="MES 软件正在运行中")

def hide_window():
    window.withdraw()  # 最小化窗口

icon_instance = None
def close_application(icon, item):
    global icon_instance
    if icon_instance:
        icon_instance.stop()
    window.quit()

def minimize_to_tray():
    global icon_instance
    menu_items = [
        MenuItem("显示窗口", on_show_window),
        MenuItem("配置导出表头", show_headers_config),
        MenuItem("退出", on_closing)
    ]
    icon_instance = Icon("test", create_image(), menu=Menu(*menu_items))
    icon_instance.run()

def on_closing():
    result = messagebox.askquestion("退出确认", "是否退出？", icon='warning')
    if result == 'yes':
        close_application(None, None)
    else:
        hide_window()