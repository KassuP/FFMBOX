import tkinter as tk
from tkinter import ttk  # 导入ttk模块
from tkinter import filedialog, messagebox
import ffmpeg
import subprocess

def select_file():
    """选择要转换的视频文件"""  # 只是代码阅读的时候作为提示
    file_path = filedialog.askopenfilename(filetypes=[("视频文件", "*.mp4;*.avi;*.mov;*.mkv")])
    if file_path:
        # entry_file_path,应该是一个 tkinter.Entry 控件的实例,用于显示或输入单行文本
        entry_file_path.delete(0, tk.END)    # 清空 entry_file_path 这个文本输入框中的所有内容。 这通常是为了在显示新的文件路径之前，先移除之前可能存在的内容。
        entry_file_path.insert(0, file_path) # 将用户选择的文件的完整路径插入到 entry_file_path 这个文本输入框的开头位置。

def select_output_directory():
    """选择输出目录"""
    directory = filedialog.askdirectory()
    if directory:
        entry_output_dir.delete(0, tk.END)
        entry_output_dir.insert(0, directory)
    

def convert_video():
    """调用ffmpeg进行视频格式转换，使用-copy参数快速转换，并显示进度"""
    input_file = entry_file_path.get() # 将文本行转化为字符串
    output_dir = entry_output_dir.get()
    target_format = combo_format.get()
    target_parameter = combo_parameter.get()  # 选择编码参数
    # modify_mode = combo_mode.get()

    if not input_file or not output_dir or not target_format:
        messagebox.showerror("错误", "请选择完整的输入文件、输出目录和目标格式！")
        return

    # 提取文件名
    file_name = input_file.split("/")[-1].split(".")[0]  # 从一个包含完整文件路径的字符串提取出不带扩展名的文件名

    # 构建输出文件路径以及文件名
    output_file = f"{output_dir}/{file_name}_converted.{target_format}"  # /path/to/your/video——converted.mkv 

    # 创建ffmpeg命令
    command = [
        'ffmpeg', '-i', input_file, '-c', target_parameter,  
        output_file
    ] # command是一个列表变量

    try:
        # 启动子进程，执行ffmpeg命令并显示进度条
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # 处理ffmpeg的输出
        for line in process.stderr:
            # 查找进度信息
            if b'frame=' in line:
                output_line = line.decode('utf-8')
                # 提取进度信息
                if 'time=' in output_line:
                    time_info = output_line.split('time=')[1].split(' ')[0]
                    # 计算转换进度
                    progress = f"正在转换... 当前时间: {time_info}"
                    label_progress.config(text=progress)
                    root.update_idletasks()

        process.communicate()

        messagebox.showinfo("成功", f"视频转换成功！输出文件：{output_file}")
        label_progress.config(text="转换完成！")
    except Exception as e:
        messagebox.showerror("错误", f"视频转换失败：{str(e)}")



# 创建主窗口
root = tk.Tk()
root.title("视频格式转换器")

# 文件选择部分
label_file_path = tk.Label(root, text="选择视频文件:")
label_file_path.grid(row=0, column=0, padx=10, pady=10)

entry_file_path = tk.Entry(root, width=40)
entry_file_path.grid(row=0, column=1, padx=10, pady=10)

btn_browse = tk.Button(root, text="浏览", command=select_file)
btn_browse.grid(row=0, column=2, padx=10, pady=10)

# 输出目录选择部分
label_output_dir = tk.Label(root, text="选择输出目录:")
label_output_dir.grid(row=1, column=0, padx=10, pady=10)

entry_output_dir = tk.Entry(root, width=40)
entry_output_dir.grid(row=1, column=1, padx=10, pady=10)

btn_output_browse = tk.Button(root, text="浏览", command=select_output_directory)
btn_output_browse.grid(row=1, column=2, padx=10, pady=10)

# 选择目标格式
label_format = tk.Label(root, text="选择目标格式:")
label_format.grid(row=2, column=0, padx=10, pady=10)


combo_format = ttk.Combobox(root, values=["mp4", "avi", "mov", "mkv"])  # 使用ttk.Combobox
combo_format.grid(row=2, column=1, padx=10, pady=10)

# 选择修改模式
label_mode = tk.Label(root, text="选择编码参数:")
label_mode.grid(row=3, column=0, padx=10, pady=10)
# combo_mode = ttk.Combobox(root, values=["普通转换", "高级设置"])  # 使用ttk.Combobox
# combo_mode.grid(row=3, column=1, padx=10, pady=10)
# 选择编码参数
combo_parameter = ttk.Combobox(root, values=["copy", "libx264", "libx265"])
combo_parameter.grid(row=3, column=1, padx=10, pady=10)


# 显示进度信息
label_progress = tk.Label(root, text="等待转换...")
label_progress.grid(row=5, column=0, columnspan=3, pady=10)

# 转换按钮
btn_convert = tk.Button(root, text="开始转换", command=convert_video)
btn_convert.grid(row=4, column=1, padx=10, pady=20)

# 运行主循环
root.mainloop()
