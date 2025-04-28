import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox
import subprocess
import threading
import queue

def time_to_seconds(time_str):
    """将时间字符串转换为秒数"""
    h, m, s = time_str.split(':')
    return int(h)*3600 + int(m)*60 + float(s)

def run_conversion(command, progress_queue):
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
            
            # 解析总时长
            if 'Duration:' in line:
                parts = line.split('Duration:')
                if len(parts) > 1:
                    duration_str = parts[1].split(',')[0].strip()
                    try:
                        total_duration = time_to_seconds(duration_str)
                        progress_queue.put(('duration', total_duration))
                    except:
                        pass
            
            # 解析当前进度时间
            if 'time=' in line:
                time_part = line.split('time=')[1].split(' ')[0]
                try:
                    current_time = time_to_seconds(time_part)
                    if total_duration and total_duration > 0:
                        progress = (current_time / total_duration) * 100
                        progress_queue.put(('progress', progress))
                except:
                    pass

        # 检查进程返回值
        if process.returncode == 0:
            progress_queue.put(('success', '视频转换成功！'))
        else:
            progress_queue.put(('error', f'转换失败，错误码：{process.returncode}'))
            
    except Exception as e:
        progress_queue.put(('error', f'转换异常：{str(e)}'))

def update_progress(progress_queue, thread):
    """更新进度条和界面状态"""
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
        elif data_type == 'error':
            messagebox.showerror("错误", data_value)
            btn_convert.config(state=tk.NORMAL)
            label_progress.config(text="转换失败")
            progress_bar['value'] = 0
    
    # 如果线程仍在运行，继续检查队列
    if thread.is_alive():
        root.after(100, update_progress, progress_queue, thread)
    else:
        btn_convert.config(state=tk.NORMAL)

def select_file():
    """选择视频文件"""
    file_path = filedialog.askopenfilename(filetypes=[("视频文件", "*.mp4;*.avi;*.mov;*.mkv;*.webm")])
    if file_path:
        entry_file_path.delete(0, tk.END)
        entry_file_path.insert(0, file_path)

def select_output_directory():
    """选择输出目录"""
    directory = filedialog.askdirectory()
    if directory:
        entry_output_dir.delete(0, tk.END)
        entry_output_dir.insert(0, directory)

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

    # 初始化进度条
    progress_bar['value'] = 0
    label_progress.config(text="转换中...")
    btn_convert.config(state=tk.DISABLED)

    # 创建进度队列和线程
    progress_queue = queue.Queue()
    thread = threading.Thread(
        target=run_conversion,
        args=(command, progress_queue),
        daemon=True
    )
    thread.start()

    # 启动进度更新循环
    root.after(100, update_progress, progress_queue, thread)

# 创建主窗口
root = tk.Tk()
root.title("视频格式转换器 v1.2")

# 文件选择组件
tk.Label(root, text="选择视频文件:").grid(row=0, column=0, padx=10, pady=5)
entry_file_path = tk.Entry(root, width=40)
entry_file_path.grid(row=0, column=1, padx=5, pady=5)
tk.Button(root, text="浏览", command=select_file).grid(row=0, column=2, padx=5, pady=5)

# 输出目录组件
tk.Label(root, text="输出目录:").grid(row=1, column=0, padx=10, pady=5)
entry_output_dir = tk.Entry(root, width=40)
entry_output_dir.grid(row=1, column=1, padx=5, pady=5)
tk.Button(root, text="浏览", command=select_output_directory).grid(row=1, column=2, padx=5, pady=5)

# 格式选择组件
tk.Label(root, text="目标格式:").grid(row=2, column=0, padx=10, pady=5)
combo_format = ttk.Combobox(root, values=["mp4", "avi", "mov", "mkv"], width=15)
combo_format.grid(row=2, column=1, padx=5, pady=5)
combo_format.current(0)

# 编码参数组件
tk.Label(root, text="编码参数:").grid(row=3, column=0, padx=10, pady=5)
combo_parameter = ttk.Combobox(root, values=["copy", "libx264", "libx265"], width=15)
combo_parameter.grid(row=3, column=1, padx=5, pady=5)
combo_parameter.current(0)

# 进度条组件
progress_bar = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
progress_bar.grid(row=4, column=0, columnspan=3, padx=10, pady=10)
label_progress = tk.Label(root, text="等待开始转换")
label_progress.grid(row=5, column=0, columnspan=3)

# 转换按钮
btn_convert = tk.Button(root, text="开始转换", command=convert_video)
btn_convert.grid(row=6, column=1, pady=10)

# 启动主循环
root.mainloop()