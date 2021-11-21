# coding:utf-8
# import time
# import datetime
# import hashlib
#
# dt_ms = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
# print(dt_ms)
# dt_ms = 'yzw'
# print(dt_ms)
# dt_ms = dt_ms.encode('utf8')
# print(dt_ms)
# al = hashlib.sha256(dt_ms)
# hash_str = al.hexdigest()
#
# print(hash_str)



# string = '00007dfbe965455194572505b3b02a7331db82d4dafd35f6841814b84551fe7b'
# print(len(string))
# print('0' * len(string))

# 00007dfbe965455194572505b3b02a7331db82d4dafd35f6841814b84551fe7b
# 5c47aa4ff418d8e20cb305bcf9009225f350897b39e9ebe8b8a3d16abeb80dc1
# 0123456789012345678901234567890123456789012345678901234567890123456789

# import json
#
# d = {'1': 'a', '2': (1, 2, 3)}
# print(json.dumps(d, ensure_ascii=False))



# site= {'name': '我的博客地址', 'alexa': 10000, 'url':'http://blog.csdn.net/uuihoo/'}
# pop_obj=site.pop('name') # 删除要删除的键值对，如{'name':'我的博客地址'}这个键值对
# print(pop_obj)
# print(site)

# import random
# import time
# from threading import Timer
#
# def hello():
#     print("hello, world")
# # 指定10秒后执行hello函数
# t = Timer(10.0, hello)
# t.start()
# time.sleep(2)
# print('yzw')
# print(t.is_alive())
# t.cancel()
# # print(t.is_alive())
# t.cancel()

# class Account:
#     address = ''
#     money = 0
#
#     def __init__(self, address='', money=0):
#         self.address = address
#         self.money = money
#
#     def add_money(self):
#         self.money += 100
#
#     def show(self):
#         def show_money():
#             print(self.money)
#         show_money()
#
# acc = Account()
# acc.show()

import json
import sys

news = '开过年就可以住上新房了，这可是我们期盼已久的大好事，要感谢政府的民心工程。”82岁的刘奶奶告诉记者，40多年里，一家人“蜗居”在建工局棚改片区的老房子里。自己年纪大了腿脚不好，上楼下楼很困难。房子没有通天然气，一家人做饭洗澡十分不便。而且房间阴暗逼仄，墙皮脱落，脏乱不堪。</p><p>今年10月，经过征收部门科学论证和精心规划，建工局棚改项目启动，刘奶奶一家成为了第一批签约的住户，在听涛苑、北辰明珠、江南时代等多个安置房源中，她选择了江南时代94平方米的新房，面积翻了一倍，居住环境显著提升，刘奶奶感到很满意，“新房子过桥就到，江南空气好环境好，旁边就是大医院，以后求医问药也方便”。</p><p>“征收能够赢得群众支持，是充分吸收居民意愿、实行阳光征收的结果。”伍家岗区住保中心相关负责人介绍，在房屋征收过程中，市、区两级征收部门坚持把公平公正公开贯穿征收工作全过程，建工局项目专班成立临时党支部突击队、政策宣传队、为民服务队统领征收队伍开展工作，做到入户摸底清、政策宣讲明、签约意向定，把基础工作、认定程序、协商过程前置，并制定具体有效的解决方案，帮助群众异地搬迁。</p><p>截至目前，累计完成签约493户，签约率达74%，片区内671户居民将告别棚户区，迎来新生活'

# print(len(news))
# print(sys.getsizeof(news))
# print(news)
# news = news.encode('utf8')
# print(len(news))
# print(sys.getsizeof(news))
# print(news)

# print(news[:1000])

msg = news.encode('utf8')
length = sys.getsizeof(msg)
batch_size = 1000

recev = []

if length > 1024:
    order = 0
    for i in range(0, length+1, batch_size):
        piece = (str(order) + '@').encode() + msg[i: i+batch_size]
        recev.append(piece)
        order += 1
else:
    recev.append(msg)

dic = {}
for piece in recev:
    piece = piece.decode()
    if piece[0].isdigit():
        pos = 0
        while pos < len(piece):
            if piece[pos] == '@':
                break
            pos += 1
        dic[int(piece[:pos])] = piece[pos+1:]

recev_msg = ''
for i in sorted(dic):
    recev_msg += dic[i]

if recev_msg == news:
    print('ok')


"""
hjs>{"type": "block-sync-answer", "body": {"len": 6, "data": [{"index": 0, "time_stamp": "", "data": "genesis", "last_hash": "0000000000000000000000000000000000000000000000000000000000000000", "miner_addr": "0", "cur_hash": "efa477530a840cda40fb1df5a8112eed236e7be20c46884795efe3fcac12ad5f"}, {"index": 1, "time_stamp": "2021-11-20 20:49:50.882926", "data": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb", "last_hash": "efa477530a840cda40fb1df5a8112eed236e7be20c46884795efe3fcac12ad5f", "miner_addr": "yjf", "cur_hash": "e6ecb9601a0e120deaee790a0ae8a8964f71eefc5298afd4ae080f1443987c45"}, {"index": 2, "time_stamp": "2021-11-20 20:50:13.545846", "data": "yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy", "last_hash": "e6ecb9601a0e120deaee790a0ae8a8964f71eefc5298afd4ae080f1443987c45", "miner_addr": "yjf", "cur_hash": "329cddf9a151a024c308adca8230feaf9f935c254cd5a8899423e312d1d5dd42"}, {"index": 3, "time_stamp": "2021-11-20 20:51:02.900989", "data": "iamsr", "last_hash": "329cddf9a151a024c308adca8230feaf9f935c254cd5a8899423e312d1d5dd42", "miner_addr": "yzw", "cur_hash": "408dc5c36937b7a4f48377dd6ae208eb0790f4f5a4c0c40bd9b0634719e900ca"}, {"index": 4, "time_stamp": "2021-11-20 20:51:45.249479", "data": "nnnnnnnnnnnnnnnnnnnnnnnnbbbbbbbbbbbbbbbbbbb", "last_hash": "408dc5c36937b7a4f48377dd6ae208eb0790f4f5a4c0c40bd9b0634719e900ca", "miner_addr": "sr", "cur_hash": "ac12b062c919868d0193cb91b33033f1b29f3849372250dc6f33b4ff192e2256"}, {"index": 5, "time_stamp": "2021-11-20 20:52:20.973570", "data": "iamxzq", "last_hash": "ac12b062c919868d0193cb91b33033f1b29f3849372250dc6f33b4ff192e2256", "miner_addr": "yzw", "cur_hash": "7a63dad894adb096d5af6f4d03c4855289fde596a8b7f2bb272b551ce6f9da87"}]}}

8899423e312d1d5dd42", "miner_addr": "yzw", "cur_hash": "408dc5c36937b7a4f48377dd6ae208eb0790f4f5a4c0c40bd9b0634719e900ca"}, {"index": 4, "time_stamp": "2021-11-20 20:51:45.249479", "data": "nnnnnnnnnnnnnnnnnnnnnnnnbbbbbbbbbbbbbbbbbbb", "last_hash": "408dc5c36937b7a4f48377dd6ae208eb0790f4f5a4c0c40bd9b0634719e900ca", "miner_addr": "sr", "cur_hash": "ac12b062c919868d0193cb91b33033f1b29f3849372250dc6f33b4ff192e2256"}, {"index": 5, "time_stamp": "2021-11-20 20:52:20.973570", "data": "iamxzq", "last_hash": "ac12b062c919868d0193cb91b33033f1b29f3849372250dc6f33b4ff192e2256", "miner_addr": "yzw", "cur_hash": "7a63dad894adb096d5af6f4d03c4855289fde596a8b7f2bb272b551ce6f9da87"}]}}


"""




