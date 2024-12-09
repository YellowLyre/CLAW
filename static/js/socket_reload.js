const socket = io();
socket.on('reload', () => {
  location.reload(); // 刷新页面
});
