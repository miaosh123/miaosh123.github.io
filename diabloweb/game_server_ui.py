import os
import sys
import webbrowser
import threading
import subprocess
import socket
from http.server import HTTPServer, SimpleHTTPRequestHandler
import tkinter as tk
from tkinter import ttk, messagebox

# 自动获取当前脚本所在目录作为游戏目录
GAME_DIR = os.path.dirname(os.path.abspath(__file__))
PORT = 8000
URL = f"http://localhost:{PORT}"

class GameServer:
    def __init__(self):
        self.server = None
        self.server_thread = None
        self.running = False
    
    def start(self):
        if self.running:
            return
            
        # 检查端口是否被占用
        if self.is_port_in_use():
            messagebox.showwarning("端口占用", f"端口 {PORT} 已被占用，请先解除占用！")
            return
            
        try:
            os.chdir(GAME_DIR)
            self.server = HTTPServer(('', PORT), SimpleHTTPRequestHandler)
            self.running = True
            
            # 在新线程中运行服务器
            self.server_thread = threading.Thread(target=self.server.serve_forever)
            self.server_thread.daemon = True
            self.server_thread.start()
            
            webbrowser.open(URL)
            return True
        except Exception as e:
            messagebox.showerror("启动错误", f"启动服务器失败: {str(e)}")
            return False
    
    def stop(self):
        if self.running and self.server:
            self.server.shutdown()
            self.server.server_close()
            self.running = False
            return True
        return False
    
    def is_port_in_use(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', PORT)) == 0
    
    def kill_port_process(self):
        try:
            # Windows命令查找占用端口的PID并终止
            find_pid = f"netstat -ano | findstr :{PORT}"
            result = subprocess.run(find_pid, shell=True, capture_output=True, text=True)
            
            if result.stdout:
                lines = result.stdout.strip().split('\n')
                pids = set()
                
                for line in lines:
                    parts = line.split()
                    if len(parts) > 4:
                        pids.add(parts[-1])
                
                for pid in pids:
                    subprocess.run(f"taskkill /F /PID {pid}", shell=True)
                
                return len(pids) > 0
            return False
        except Exception as e:
            messagebox.showerror("错误", f"解除端口占用失败: {str(e)}")
            return False

class ServerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("HTML5游戏服务器控制-作者：喵少")
        self.root.geometry("450x350")
        self.root.resizable(False, False)
        
        self.server = GameServer()
        
        # 创建UI元素
        self.create_widgets()
        self.update_status()
        
        # 设置关闭窗口事件处理
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def create_widgets(self):
        # 标题
        title = ttk.Label(self.root, text="简易服务器控制", font=("Arial", 14))
        title.pack(pady=10)
        
        # 路径显示
        path_frame = ttk.Frame(self.root)
        path_frame.pack(pady=5, padx=20, fill="x")
        
        ttk.Label(path_frame, text="游戏路径:").pack(side="left")
        self.path_label = ttk.Label(path_frame, text=GAME_DIR, foreground="blue")
        self.path_label.pack(side="left", padx=5)
        
        # 状态区域
        status_frame = ttk.LabelFrame(self.root, text="服务器状态")
        status_frame.pack(pady=10, padx=20, fill="x")
        
        self.status_label = ttk.Label(status_frame, text="服务器已停止", foreground="red")
        self.status_label.pack(pady=10)
        
        # 按钮区域
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(pady=10)
        
        self.start_btn = ttk.Button(btn_frame, text="启动服务器", command=self.toggle_server)
        self.start_btn.pack(side="left", padx=10)
        
        ttk.Button(btn_frame, text="解除端口占用", command=self.kill_port).pack(side="left", padx=10)
        
        # 信息区域
        info_frame = ttk.LabelFrame(self.root, text="操作说明")
        info_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        info_text = tk.Text(info_frame, height=7, wrap="word")
        info_text.pack(padx=5, pady=5, fill="both")
        
        instructions = [
            "1. 点击[启动服务器]按钮启动游戏服务器",
            "2. 游戏将在浏览器中自动打开",
            "3. 点击[停止服务器]按钮停止服务",
            "4. 如果端口被占用，点击[解除端口占用]",
            f"当前端口: {PORT}",
            f"访问地址: {URL}",
            "注意: 请确保游戏入口文件为index.html"
        ]
        
        for line in instructions:
            info_text.insert("end", line + "\n")
        
        info_text.configure(state="disabled")
    
    def toggle_server(self):
        if self.server.running:
            if self.server.stop():
                messagebox.showinfo("成功", "服务器已停止")
        else:
            if self.server.start():
                messagebox.showinfo("成功", f"服务器已启动\n访问地址: {URL}")
        
        self.update_status()
    
    def kill_port(self):
        if self.server.kill_port_process():
            messagebox.showinfo("成功", f"已解除端口 {PORT} 的占用")
        else:
            messagebox.showinfo("信息", f"端口 {PORT} 未被占用")
        
        self.update_status()
    
    def update_status(self):
        if self.server.running:
            self.status_label.config(text="服务器运行中", foreground="green")
            self.start_btn.config(text="停止服务器")
        else:
            self.status_label.config(text="服务器已停止", foreground="red")
            self.start_btn.config(text="启动服务器")
    
    def on_close(self):
        if self.server.running:
            if messagebox.askyesno("确认", "服务器仍在运行，确定要退出吗？"):
                self.server.stop()
                self.root.destroy()
        else:
            self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ServerGUI(root)
    root.mainloop()