# -*- coding:utf-8 -*-  
import socket
import struct
import cv2                
import datetime
import getpass
import time
client=socket.socket()
client.connect(('0.0.0.0',8801))

def strmode():#服务器和客户端交互，互相发送
    while True:
        inp=input('请输入要发送给服务器的内容>>>>').encode('utf8') #从Unicode转为utf-8,字符串网络传输编码采用utf-8，既支持中文也节省带宽资源
        lenth=len(inp)
        buff=struct.pack('>HLL',1,lenth,0)+inp
        client.sendall(buff)
        data=client.recv(1024)
        print('已收到服务器的回复：',data.decode('utf8'))

def sendfile(client,filename):
    with open(filename,'rb') as fd:
        data=fd.read()
        buff=struct.pack('>HLL',2,len(filename.encode('utf8')),len(data))+filename.encode('utf8')+data #data直接采用二进制编码发送
        client.sendall(buff)
        print('客户端已成功发送文件：',filename)

def clienttoserver_filemode(): #客户端拍照，然后发给服务端
    user_name = getpass.getuser() # 获取当前用户名
    hostname = socket.gethostname() # 获取当前主机名
    # #with……as……语法：当进入时自动执行类的__enter__函数，退出时自动执行__exit__函数
    cap = cv2.VideoCapture(0) #0表示启用第一个摄像头
    while True:    
        now_time = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S') #当前utc时间
        picture_name = hostname + '_' + user_name+ '_'  + now_time + '.png'
        f, frame = cap.read()#此刻拍照
        cv2.imwrite(picture_name, frame)# 将拍摄内容保存为png图片    
        sendfile(client,picture_name)
        time.sleep(10)#每隔10s拍一次 
    cap.release()# 关闭调用的摄像头
    

def servertoclient_filemode(types):#服务端拍照，然后发给客户端
    def getdata(conn,datalen):
        data=b''
        while datalen > 0:  #循环接收body字节流，而不是一次接收完是因为，存在发送的数据大于tcp缓冲区大小，从而导致接收数据不完整
            buff = conn.recv(datalen)
            data += buff
            datalen -= len(buff)
        return data
    buff=struct.pack('>HLL',types,0,0)
    client.sendall(buff)
    head=client.recv(10)
    (types,data1_len,data2_len) = struct.unpack('>HLL',head) #将字节流转为整形
    data1=getdata(client,data1_len)
    data2=getdata(client,data2_len)
    with open(data1,'wb') as fd:
        fd.write(data2)
        print('客户端已成功接收文件：',data1.decode('utf8'))

# while True:
#     mode=input('请输入要使用的模式：\n字符串传输模式请输入1回车;\n客户端拍照，然后发给服务端传输模式请输入2回车;\n服务端拍照，然后发给客户端传输模式请输入3回车;\n>>>>')
#     if mode == '1':
#         strmode()
#         break
#     elif mode == '2':
#         clienttoserver_filemode()
#         break
#     elif mode == '3':
#         servertoclient_filemode(3)
#         break
#     elif mode == '4':
#         servertoclient_filemode(4)
#         break    
#     elif mode == '5': #使用的是types==3的协议
#         sendfile(client,'客户端测试文件.txt')
#         break
#     else:
#         print('输入错误')

clienttoserver_filemode()   
client.close()