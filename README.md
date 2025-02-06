# HTTP 代理服务器（基于 SOCKS5 转发）

这是一个简单的 HTTP 代理服务器示例，使用 Python 实现，并通过 SOCKS5 代理进行转发。代码中内嵌了 SOCKS5 配置，无需额外的配置文件。

## 功能特点

- 支持 GET 和 POST 请求的转发
- 使用 SOCKS5 代理转发 HTTP 请求
- 实时统计上传和下载速率及总流量
- 基于多线程处理并发请求

## 使用说明

1. **环境要求**

   - Python 3.x
   - 安装依赖包：`PySocks`

   可以使用以下命令安装依赖：
   ```bash
   pip install PySocks
   ```

2. **配置**

   在代码中直接修改以下 SOCKS5 配置参数为你实际的代理信息：
   ```python
   # 直接在代码中配置 SOCKS5 代理参数
   SOCKS5_PROXY_HOST = '127.0.0.1'
   SOCKS5_PROXY_PORT = 1080
   SOCKS5_USERNAME = 'your_username'
   SOCKS5_PASSWORD = 'your_password'
   ```

3. **运行**

   直接运行 Python 文件即可启动本地 HTTP 代理服务器，默认监听端口为 `18888`：
   ```bash
   python your_proxy_file.py
   ```

4. **日志与统计**

   程序启动后会在终端实时显示当前上传、下载速率以及总的上传、下载流量信息，例如：
   ```
   当前上传: 10.50 KB/s | 当前下载: 20.30 KB/s | 总上传: 1.23 MB | 总下载: 4.56 MB
   ```

## 代码结构

- **ProxyHTTPRequestHandler**  
  继承自 `http.server.BaseHTTPRequestHandler`，用于处理 HTTP 请求并通过 SOCKS5 代理进行转发。

- **print_status 函数**  
  通过一个后台线程实时统计并打印数据传输量。

- **start_proxy_server 函数**  
  启动代理服务器，监听指定端口并处理客户端请求。

## 注意事项

- 目前代码仅支持 HTTP 协议，对于 HTTPS 请求需要额外处理（如隧道转发）。
- 代码中对异常做了基本处理，建议根据实际需求完善错误处理逻辑。
- 如果需要进一步扩展功能，可参考 Python 官方文档和相关网络编程资料。

## 许可证

本项目采用 MIT 许可证，详情请参见 [LICENSE](LICENSE) 文件。

---

欢迎提出 Issue 和 PR，共同改进此项目！
