import socketserver
import http.server
import socket
import socks
import threading
import time
from urllib.parse import urlparse, urlunparse

# 直接在代码中配置 SOCKS5 代理参数
SOCKS5_PROXY_HOST = '127.0.0.1'
SOCKS5_PROXY_PORT = 1080
SOCKS5_USERNAME = 'your_username'
SOCKS5_PASSWORD = 'your_password'

# 全局变量跟踪数据传输量
total_upload = 0
total_download = 0
current_upload = 0
current_download = 0
lock = threading.Lock()

# 配置 SOCKS5 代理
socks.set_default_proxy(
    socks.SOCKS5,
    SOCKS5_PROXY_HOST,
    SOCKS5_PROXY_PORT,
    username=SOCKS5_USERNAME,
    password=SOCKS5_PASSWORD
)
socket.socket = socks.socksocket  # 全局替换 socket

class ProxyHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        return  # 关闭默认日志

    def do_GET(self):
        self.handle_http_request()

    def do_POST(self):
        self.handle_http_request()

    def handle_http_request(self):
        global total_upload, total_download, current_upload, current_download

        conn = None
        try:
            # 解析 URL
            parsed_url = urlparse(self.path)
            # 如果请求行中没有 scheme 和 netloc，可能需要从 Host 头获取
            if not parsed_url.scheme:
                # 默认 HTTP 协议
                target_host = self.headers.get('Host')
                if not target_host:
                    self.send_error(400, "Host header missing")
                    return
                # 解析 Host（可能包含端口）
                if ':' in target_host:
                    hostname, port_str = target_host.split(':', 1)
                    port = int(port_str)
                else:
                    hostname = target_host
                    port = 80
                # 重构 URL
                parsed_url = parsed_url._replace(scheme='http', netloc=target_host)
            else:
                hostname = parsed_url.hostname
                port = parsed_url.port or (443 if parsed_url.scheme == 'https' else 80)

            # 建立到目标服务器的连接
            conn = socket.socket()
            conn.connect((hostname, port))

            # 构造请求行及头部
            # 对于 GET 请求，若存在 query 则拼接
            path = parsed_url.path or '/'
            if parsed_url.query:
                path = f"{path}?{parsed_url.query}"

            request_line = f"{self.command} {path} HTTP/1.1\r\n"
            # 建议保留 Host 头，同时可以剔除代理相关的头部
            headers = ''
            for key, value in self.headers.items():
                if key.lower() in ['proxy-connection', 'connection']:
                    continue
                headers += f"{key}: {value}\r\n"
            # 确保 Host 头存在
            if 'host' not in self.headers:
                headers += f"Host: {hostname}\r\n"
            full_request = (request_line + headers + "\r\n").encode('utf-8')

            # 对 POST 请求，读取并附带请求体
            if self.command.upper() == 'POST':
                content_length = int(self.headers.get('Content-Length', 0))
                post_data = self.rfile.read(content_length)
                full_request += post_data
                with lock:
                    total_upload += content_length
                    current_upload += content_length

            # 发送请求到目标服务器
            conn.sendall(full_request)

            # 在成功建立连接并发送请求后，再发送200响应给客户端
            self.send_response(200)
            self.end_headers()

            # 接收目标服务器返回的数据，并实时转发给客户端
            while True:
                data = conn.recv(8192)
                if not data:
                    break
                self.wfile.write(data)
                with lock:
                    total_download += len(data)
                    current_download += len(data)

        except Exception as e:
            self.send_error(500, f"Error: {str(e)}")
        finally:
            if conn:
                conn.close()

def print_status():
    global current_upload, current_download, total_upload, total_download
    while True:
        time.sleep(1)
        with lock:
            # 计算当前上传/下载速率（KB/s）
            cur_up_kb = current_upload / 1024
            cur_down_kb = current_download / 1024
            # 转换总上传/下载量为 MB 或 GB
            total_up_mb = total_upload / (1024 * 1024)
            total_down_mb = total_download / (1024 * 1024)

            total_up_str = f"{total_up_mb / 1024:.2f} GB" if total_up_mb >= 1024 else f"{total_up_mb:.2f} MB"
            total_down_str = f"{total_down_mb / 1024:.2f} GB" if total_down_mb >= 1024 else f"{total_down_mb:.2f} MB"

            print(f"\r当前上传: {cur_up_kb:.2f} KB/s | 当前下载: {cur_down_kb:.2f} KB/s | 总上传: {total_up_str} | 总下载: {total_down_str}", end='')

            # 重置当前速率统计
            current_upload = 0
            current_download = 0

def start_proxy_server():
    PORT = 18888
    server = socketserver.ThreadingTCPServer(('', PORT), ProxyHTTPRequestHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    print(f"本地HTTP代理服务器运行在端口 {PORT}")

if __name__ == '__main__':
    # 启动状态显示线程
    threading.Thread(target=print_status, daemon=True).start()

    # 启动代理服务器
    start_proxy_server()

    # 保持主线程运行
    while True:
        time.sleep(1)
