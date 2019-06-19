# -*- coding:utf-8 -*-  
import selectors  #基于select模块实现的IO多路复用，建议大家使用
import socket
import struct
import cv2                
import datetime
import getpass
import time
sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)#端口重复利用
sock.bind(('0.0.0.0',8801))
sock.listen()
sock.setblocking(False)#非阻塞
sel=selectors.DefaultSelector() #根据平台选择最佳的IO多路复用机制，优先级如下：epoll|kqueue|devpoll > poll > select.  既支持多个客户端同时通信

def getdata(conn,datalen):
    data=b''
    while datalen > 0:  #循环接收body字节流，而不是一次接收完是因为，存在发送的数据大于tcp缓冲区大小，从而导致接收数据不完整
        try:
            buff = conn.recv(datalen)
        except Exception as e: #非阻塞socket,在tcp缓冲区为空时，即接收不到数据时，会报10035,正常现象，这时只需要继续接收即可
            if e.errno==10035:
                continue;
            raise
        data += buff
        datalen -= len(buff)
    return data
    
def sendfile(conn,filename):
    with open(filename,'rb') as fd:
        data=fd.read()
        buff=struct.pack('>HLL',2,len(filename.encode('utf8')),len(data))+filename.encode('utf8')+data #data直接采用二进制编码发送
        conn.sendall(buff)
        print('客户端已成功发送文件：',filename)

def sendpicture(conn):
    user_name = getpass.getuser() # 获取当前用户名
    hostname = socket.gethostname() # 获取当前主机名
    # #with……as……语法：当进入时自动执行类的__enter__函数，退出时自动执行__exit__函数
    cap = cv2.VideoCapture(0) #0表示启用第一个摄像头
    for i in range(0,1):    
        now_time = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S') #当前utc时间
        picture_name = hostname + '_' + user_name+ '_'  + now_time + '.png'
        f, frame = cap.read()#此刻拍照
        cv2.imwrite(picture_name, frame)# 将拍摄内容保存为png图片
        sendfile(conn,picture_name)
        time.sleep(1) #休息1s防止文件重名导致覆盖
    cap.release()# 关闭调用的摄像头

def read(conn,mask):
    try:
        head = conn.recv(10) #接收前10个字节的tcp包头
        (types,data1_len,data2_len) = struct.unpack('>HLL',head) #将字节流转为整形
        data1=getdata(conn,data1_len)
        data2=getdata(conn,data2_len)

        if types==1: #客户端服务器字符串交互
            print(data1.decode('utf8')) #将utf-8解码为Unicode,从而在终端上能识别中文
            buff=input('>>>>')
            conn.sendall(buff.encode('utf8'))
        elif types==2: #服务器接收客户端发过来文件/照片，并存储
            with open(data1,'wb') as fd:
                fd.write(data2)
        elif types==3: #服务器拍照，然后发给客户端
            sendpicture(conn)
        elif types==4: #直接发文件
            sendfile(conn,'服务端测试文件.txt')
    except Exception as e:
        print('客户端已关闭连接-------',conn, e)
        sel.unregister(conn)

def accept(sock,mask):
    conn,addr=sock.accept()
    print('接收到客户端的连接-------',conn)
    sel.register(conn,selectors.EVENT_READ,read)


sel.register(sock, selectors.EVENT_READ, accept)  #注册功能
while True:
    print('wating....')
    events=sel.select()   #[(sock)，（），（）]   监听

    for key,mask in events:
        # print(key.data)       #accept   找出有活动的绑定函数
        # print(key.fileobj)    #sock     找出有活动的文件描述符
        func=key.data
        obj=key.fileobj
        func(obj,mask)  #1 accept(sock,mask) 2read(conn,mask)
