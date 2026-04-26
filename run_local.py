#!/usr/bin/env python3
"""
智剪 - 本地测试服务器
快速启动一个本地HTTP服务器来测试静态页面
"""
import http.server
import socketserver
import os
import webbrowser
import threading

PORT = 8080
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class QuietHandler(http.server.SimpleHTTPRequestHandler):
    """静默处理请求"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)
    
    def log_message(self, format, *args):
        pass  # 静默日志

def open_browser():
    """延迟打开浏览器"""
    import time
    time.sleep(1)
    webbrowser.open(f'http://localhost:{PORT}')

if __name__ == "__main__":
    print("""
╔═══════════════════════════════════════════════════════╗
║                                                       ║
║   🎬 智剪 - AI智能视频剪辑                            ║
║                                                       ║
║   正在启动本地服务器...                                ║
║                                                       ║
╚═══════════════════════════════════════════════════════╝
    """)
    
    with socketserver.TCPServer(("", PORT), QuietHandler) as httpd:
        print(f"✅ 服务已启动: http://localhost:{PORT}")
        print(f"📁 当前目录: {DIRECTORY}")
        print("\n按 Ctrl+C 停止服务器\n")
        
        # 在新线程中打开浏览器
        threading.Thread(target=open_browser, daemon=True).start()
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 服务器已停止")
