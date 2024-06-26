# 实验名称
搭建对象存储
# 实验环境
| 属性| 值|
|:--------:|:-------:|
|设备名称   |LAPTOP-U93DQ6K3|
|处理器	    |AMD Ryzen 5 4600H with Radeon Graphics 3.00 GHz|
|机带 RAM	|16.0 GB (15.4 GB 可用)|
|系统类型	|64 位操作系统, 基于 x64 的处理器
|Windows规格|Windows 11 家庭中文版|
|Linux版本| Ubuntu 22.04.2 LTS(WSL 2) |
# 实验记录
## 实验2-1： 安装OpenStack-Swift作为服务端
1. 使用docker hub，找到一个可用的openswift的镜像：
https://hub.docker.com/r/fnndsc/docker-swift-onlyone
2. 确保在wsl已经成功安装docker,可使用如下命令
```shell
    docker ps
```
3. 创建存储卷
```shell
    docker volume create swift_storage
```
4. 依据该镜像，创建并运行对应的容器
```shell
    docker run -d --name swift-onlyone -p 12345:8080 -v swift_storage:/srv -t fnndsc/docker-swift-onlyone
```
5. 使用docker ps检验对应容器是否运行成功,如下图所示，即为安装成功：

![ServerInstall](./figure/ServerInstall.png)

## 实验2-2：安装python-swiftclient作为客户端
1. 在Ubuntu中创建对应的conda虚拟环境bigdata,并安装相应的python库：
```shell
    conda create -n bigdata python=3.x
    conda activate bigdata
    pip install python-swiftclient
```
## 实验2-3：验证是否能够正常连接
因为服务端和客户端都在同一个系统中，所以服务器ip为127.0.0.1，且该镜像自带一个chris用户，直接使用即可。
1. 通过下面命令，将当前目录的anypdf.pdf传入存储系统的user_uploads容器中，并命名为mypdf.pdf:
```shell
swift -A http://127.0.0.1:12345/auth/v1.0 -U chris:chris1234 -K testing upload --object-name mypdf.pdf user_uploads ./anypdf.pdf
```
2. 通过如下命令，可查看存储系统中的容器
```shell
swift -A http://127.0.0.1:12345/auth/v1.0 -U chris:chris1234 -K testing list
```
# 实验小结
1. 通过改实验，初步了解了存储系统服务端和客户端的交互方式。
2. 更重要的是，通过该实验，我深刻地体会到了镜像的重要性，它可以帮助我们大大节省配环境的时间，让我们能够更快地专注到实际的系统研究上。虽然在学习docker的使用的过程中，遇到了不少的麻烦，但磨刀不误砍柴工，学习新事物、拥抱新事物的最终回报总是让人兴奋的。