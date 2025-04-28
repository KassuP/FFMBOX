import tkinter as tk
from tkinter import ttk, scrolledtext
from tkinter import filedialog, messagebox
import subprocess
import threading
import queue
import time

def time_to_seconds(time_str):
    """将时间字符串转换为秒数"""
    try:
        h, m, s = time_str.split(':')
        return int(h)*3600 + int(m)*60 + float(s)
    except:
        return 0

class ConsoleWindow:
    """控制台输出窗口"""
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("FFmpeg 输出")
        self.window.geometry("600x400")
        
        # 创建带滚动条的文本框
        self.text_area = scrolledtext.ScrolledText(self.window, wrap=tk.WORD)
        self.text_area.pack(expand=True, fill='both')
        
        # 状态标签
        self.status_label = tk.Label(self.window, text="转换进行中...")
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 自动关闭定时器
        self.auto_close = None

    def append_text(self, text):
        """添加文本到控制台"""
        self.text_area.configure(state='normal')
        self.text_area.insert(tk.END, text)
        self.text_area.see(tk.END)  # 自动滚动到底部
        self.text_area.configure(state='disabled')
    
    def set_status(self, text, success=True):
        """更新状态并安排自动关闭"""
        self.status_label.config(
            text=text,
            fg="green" if success else "red"
        )
        # 10秒后自动关闭窗口
        self.auto_close = self.window.after(10000, self.window.destroy)

def run_conversion(command, progress_queue, console_queue):
    """在新线程中执行转换任务"""
    try:
        process = subprocess.Popen(
            command,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            bufsize=1,
            universal_newlines=True,
            encoding='utf-8',
            errors='replace'
        )
        
        total_duration = None
        
        # 实时读取stderr输出
        while True:
            line = process.stderr.readline()
            if not line and process.poll() is not None:
                break
            
            # 发送到控制台窗口
            console_queue.put(line)
            
            # 解析总时长
            if 'Duration:' in line:
                parts = line.split('Duration:')
                if len(parts) > 1:
                    duration_str = parts[1].split(',')[0].strip()
                    total_duration = time_to_seconds(duration_str)
                    progress_queue.put(('duration', total_duration))
            
            # 解析当前进度时间
            if 'time=' in line:
                time_part = line.split('time=')[1].split(' ')[0]
                current_time = time_to_seconds(time_part)
                if total_duration and total_duration > 0:
                    progress = (current_time / total_duration) * 100
                    progress_queue.put(('progress', progress))

        # 检查进程返回值
        if process.returncode == 0:
            progress_queue.put(('success', '视频转换成功！'))
            console_queue.put("\n转换成功完成！\n")
        else:
            progress_queue.put(('error', f'转换失败，错误码：{process.returncode}'))
            console_queue.put(f"\n转换失败，错误码：{process.returncode}\n")
            
    except Exception as e:
        progress_queue.put(('error', f'转换异常：{str(e)}'))
        console_queue.put(f"\n发生异常：{str(e)}\n")

def update_progress(progress_queue, console_queue, thread, console_window):
    """更新界面状态"""
    # 处理控制台输出
    while not console_queue.empty():
        line = console_queue.get()
        console_window.append_text(line)
    
    # 处理进度更新
    while not progress_queue.empty():
        data_type, data_value = progress_queue.get()
        
        if data_type == 'progress':
            progress_bar['value'] = data_value
            label_progress.config(text=f'转换进度: {data_value:.2f}%')
        elif data_type == 'success':
            messagebox.showinfo("成功", data_value)
            btn_convert.config(state=tk.NORMAL)
            label_progress.config(text="转换完成！")
            progress_bar['value'] = 100
            console_window.set_status("转换成功！", success=True)
        elif data_type == 'error':
            messagebox.showerror("错误", data_value)
            btn_convert.config(state=tk.NORMAL)
            label_progress.config(text="转换失败")
            progress_bar['value'] = 0
            console_window.set_status("转换失败！", success=False)
    
    # 如果线程仍在运行，继续检查队列
    if thread.is_alive():
        root.after(100, update_progress, progress_queue, console_queue, thread, console_window)
    else:
        btn_convert.config(state=tk.NORMAL)

def convert_video():
    """启动转换线程"""
    input_file = entry_file_path.get()
    output_dir = entry_output_dir.get()
    target_format = combo_format.get()
    target_parameter = combo_parameter.get()

    if not input_file or not output_dir or not target_format:
        messagebox.showerror("错误", "请填写所有必填项！")
        return

    # 构建输出路径
    file_name = input_file.split("/")[-1].split(".")[0]
    output_file = f"{output_dir}/{file_name}_converted.{target_format}"

    # 创建ffmpeg命令
    command = [
        'ffmpeg',
        '-i', input_file,
        '-c:v', target_parameter,
        output_file
    ]

    # 初始化界面状态
    progress_bar['value'] = 0
    label_progress.config(text="转换中...")
    btn_convert.config(state=tk.DISABLED)
    
    # 创建控制台窗口
    console_window = ConsoleWindow(root)
    
    # 创建通信队列
    progress_queue = queue.Queue()
    console_queue = queue.Queue()
    
    # 启动转换线程
    thread = threading.Thread(
        target=run_conversion,
        args=(command, progress_queue, console_queue),
        daemon=True
    )
    thread.start()

    # 启动界面更新循环
    root.after(100, update_progress, progress_queue, console_queue, thread, console_window)

# 创建主窗口
root = tk.Tk()
root.title("视频格式转换器 v1.3")

# GUI组件布局（与之前版本相同）... [保持原有界面组件代码不变]

# 启动主循环
root.mainloop()