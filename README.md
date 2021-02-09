# arptool

## 简介
使用python的原始套接字实现的arp协议, 及其相关操作  
当前实现arp主机探测相关功能(包括网段的扫描与但主机的探测)

## 开始使用
本身也没有几行代码, git拖下来直接用就成。讲究点就编译下安装到Python环境

## 安装到python环境
### 1. 下载源码
```bash
git clone https://github.com/oscarwith2960/arptool.git
```
### 2. 安装编译环境
```bash
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```
### 2. 编译安装包
```bash
make clean && make
```
### 3. 安装wheel包
```bash
cd _build
pip install arptool-*.*.*-py3-none-any.whl
```
