import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox
import subprocess
import threading
import queue


############################## 后端
def select_file():
    file_path = filedialog.askopenfilename(filetypes=[("视频文件","*.mkv")])
    if file_path:
        entry_file_path.delete(0,tk.END)
        entry_file_path.insert(0,file_path)

def select_output_directoty():
    directory = filedialog.askdirectory()
    if directory:
        entry_output_dir.delete(0,tk.END)
        entry_output_dir.insert(0,directory)

def run_ffmpeg(command):  #创建进程中很重要的函数
    try:
        result = subprocess.run(  
            command,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr 

# 下面的为主函数
def subtitle_video():
    """"启动提取线程"""
    # 定义函数内的变量
    input_file = entry_file_path.get()
    output_dir = entry_output_dir.get()
    target_format = combo_format.get()  # 输出格式在前端被选择 
    stream_index = int(combo_trail.get())-1 # 指定类型流的索引

    # 构建文件的输出路径(包含文件名)
    file_name = input_file.split("/")[-1].split(".")[0]
    output_file = f"{output_dir}/{file_name}_subtitle_{stream_index+1}.{target_format}"

    # 创建ffmpeg命令
    map_spec = f"0:s:{stream_index}"
    command = ['ffmpeg','-i',input_file]
    command.extend(['-map',map_spec,output_file])  #-map 0:s:0: 表示从第一个输入文件（索引为0）中选择第一个字幕流（索引为0）,
    # 如果视频文件中有多个字幕流，你可以调整索引来选择不同的字幕流。
    # 不要有多余的空格

    if not all([input_file, output_dir]):
        messagebox.showerror("错误", "请先选择输入文件和输出目录")
        return

    #创建进程（有了这个才能使用command）
    def execute():
        # 添加进度提示
        progress_window = tk.Toplevel()
        progress_window.title("处理中")
        tk.Label(progress_window, text="正在提取字幕，请稍候...").pack(padx=20, pady=10)
        progress_window.grab_set()  # 模态对话框

        success, output = run_ffmpeg(command)
        progress_window.destroy()

        if success:
            messagebox.showinfo("完成", f"字幕已提取至：\n{output_file}")
        else:
            messagebox.showerror("错误", f"提取失败：\n{output}")

    threading.Thread(target=execute).start()


########################################################## 前端
#主窗口
root = tk.Tk()
root.title("MKV字幕提取 V0.1")

# 待提取字幕的视频文件选择
ttk.Label(root,text="选择MKV文件:").grid(row=0,column=0,padx=10,pady=5)
entry_file_path = tk.Entry(root,width=40) 
entry_file_path.grid(row=0,column=1,padx=5,pady=5)  # 中间显示文件地址的窗口
ttk.Button(root,text="浏览",command=select_file).grid(row=0,column=2,padx=5,pady=5)  # 创建一个按钮，按钮上显示字体，且将按钮操作绑定到后端的某个函数上，做对应的触发（调用）操作

# 输出文件的位置
ttk.Label(root,text="选择位置").grid(row=1,column=0,padx=10,pady=5)
entry_output_dir = tk.Entry(root,width=40) 
entry_output_dir.grid(row=1,column=1,padx=5,pady=5)  # 中间显示文件地址的窗口
ttk.Button(root,text="浏览",command=select_output_directoty).grid(row=1,column=2,padx=5,pady=5)  # 创建一个按钮，按钮上显示字体，且将按钮操作绑定到后端的某个函数上，做对应的触发（调用）操作

# 格式选择组件
ttk.Label(root,text="目标格式:").grid(row=2,column=0,padx=10,pady=5)
combo_format = ttk.Combobox(root,values=["srt","txt"],width=15)  # combo_format内容 是一个抽屉  如果其他地方需要使用这里的值，那么就给他一个函数名。不需要的话不设置也可以
combo_format.grid(row=2,column=1,padx=5,pady=5)  # 抽屉 combo_format 显示的位置
combo_format.current(0) # 将下拉框的默认选项设置为第一个（索引从0开始）

# 选择字幕轨道
ttk.Label(root,text="选择字幕轨道").grid(row=3,column=0,padx=10,pady=5)
combo_trail = ttk.Combobox(root,values=[str(i) for i in range(1, 11)])  # 生成1-10
combo_trail.grid(row=3,column=1,padx=5,pady=5) 
combo_trail.current(0)  # 将下拉框的默认选项设置为第一个（索引从0开始）

# 启动提取进程
ttk.Label(root,text="开始提取:").grid(row=4,column=0,padx=10,pady=5)
ttk.Button(root,text="开始提取",command=subtitle_video).grid(row=4,column=1,padx=5,pady=5)

# 在代码末尾添加 root.mainloop() 以启动 GUI 主事件循环。Tkinter 程序需要这个调用来显示窗口并处理用户交互。
# 启动主循环
root.mainloop()