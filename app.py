from flask import Flask, render_template
from flask_socketio import SocketIO
import os
import time
import random
from threading import Lock

# Flask & SocketIO 初始化
app = Flask(__name__)
socketio = SocketIO(app)

# 配置类
class Config:
    TEMPLATE_PATH = 'templates/index.html'
    DATA_UPDATE_INTERVAL = 5  # 动态数据发送间隔
    FILE_CHECK_INTERVAL = 1  # 文件变更检测间隔

# 文件监视状态
file_watch_lock = Lock()
last_modified_time = os.path.getmtime(Config.TEMPLATE_PATH)

# 路由
@app.route('/')
def serve_index():
    return render_template('index.html')

@app.route('/history-archive')
def serve_history_archive():
    return render_template('history-archive.html')

@app.route('/traffic-rental')
def serve_traffic_rental():
    return render_template('traffic-rental.html')

# 文件变更监视功能
def watch_file_changes():
    global last_modified_time
    while True:
        time.sleep(Config.FILE_CHECK_INTERVAL)
        with file_watch_lock:
            current_modified_time = os.path.getmtime(Config.TEMPLATE_PATH)
            if current_modified_time != last_modified_time:
                last_modified_time = current_modified_time
                socketio.emit('reload')  # 通知客户端文件变更

# 动态数据发送功能
def send_dynamic_data():
    while True:
        socketio.sleep(Config.DATA_UPDATE_INTERVAL)
        data = {'message': f'动态数据: {random.randint(1, 100)}'}
        socketio.emit('update', data)

# 处理客户端连接
@socketio.on('connect')
def handle_connect(auth):  # 接受 auth 参数
    # 确保任务只启动一次
    socketio.start_background_task(watch_file_changes)
    socketio.start_background_task(send_dynamic_data)

# 运行服务
if __name__ == '__main__':
    # 启动文件监控与数据发送任务
    socketio.start_background_task(watch_file_changes)
    socketio.start_background_task(send_dynamic_data)
    socketio.run(app, host='0.0.0.0', port=8009)
