import tkinter as tk
from tkinter import ttk  # 导入ttk模块
from tkinter import filedialog, messagebox
import ffmpeg

def select_file():
    """选择要转换的视频文件"""
    file_path = filedialog.askopenfilename(filetypes=[("视频文件", "*.mp4;*.avi;*.mov;*.mkv")])
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
    """调用ffmpeg进行视频格式转换"""
    input_file = entry_file_path.get()
    output_dir = entry_output_dir.get()
    target_format = combo_format.get()
    modify_mode = combo_mode.get()

    if not input_file or not output_dir or not target_format:
        messagebox.showerror("错误", "请选择完整的输入文件、输出目录和目标格式！")
        return

    # 提取文件名
    file_name = input_file.split("/")[-1].split(".")[0]

    # 构建输出文件路径
    output_file = f"{output_dir}/{file_name}_converted.{target_format}"

    try:
        # 调用ffmpeg进行格式转换
        ffmpeg.input(input_file).output(output_file).run()
        messagebox.showinfo("成功", f"视频转换成功！输出文件：{output_file}")
    except ffmpeg.Error as e:
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
label_mode = tk.Label(root, text="选择修改模式:")
label_mode.grid(row=3, column=0, padx=10, pady=10)

combo_mode = ttk.Combobox(root, values=["普通转换", "高级设置"])  # 使用ttk.Combobox
combo_mode.grid(row=3, column=1, padx=10, pady=10)

# 转换按钮
btn_convert = tk.Button(root, text="开始转换", command=convert_video)
btn_convert.grid(row=4, column=1, padx=10, pady=20)

# 运行主循环
root.mainloop()
