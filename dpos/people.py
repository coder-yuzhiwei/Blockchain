import random
import threading
import socket
import sys
import json
import time

from block import *
from pprint import pprint
import config

MAX_QUEUE_SIZE = 2
MAX_VOTE_TIME = 0.5

class Node:
    account = None
    block_chain = []

    tokens = 0
    timer = None
    congress = dict()
    delegate_queue = []
    event = threading.Event()
    supporters = dict()

    def __init__(self, ip, port, name):
        # p2p网络
        self.ip = ip
        self.port = port
        self.name = name
        # 路由表包括自己
        self.friends = dict()
        self.friends[self.name] = (self.ip, self.port)
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_socket.bind((ip, port))
        self.udp_socket = udp_socket

    def send_to_one(self, msg, ip_port):
        msg = json.dumps(msg).encode('utf8')
        length = sys.getsizeof(msg)
        max_size = 1024
        batch_size = 1000
        if length > max_size:
            order = 0
            for i in range(0, length + 1, batch_size):
                piece = (str(order) + '@').encode() + msg[i: i + batch_size]
                self.udp_socket.sendto(piece, tuple(ip_port))
                order += 1
            end = 'end'.encode()
            self.udp_socket.sendto(end, tuple(ip_port))
        else:
            self.udp_socket.sendto(msg, tuple(ip_port))

    # 同样发送给自身
    def send_to_all(self, msg):
        for ip_port in self.friends.values():
            self.send_to_one(msg, ip_port)

    def explore_friends(self, known_ip_port):
        msg = {
            'type': 'explore-query',
            'body': {
                'ip': self.ip,
                'port': self.port,
                'name': self.name
            }
        }
        self.send_to_one(msg, known_ip_port)


    def receive_data(self):
        total_data = ''
        data, addr = self.udp_socket.recvfrom(1024)
        data = data.decode()
        if data[0].isdigit():
            # 分段传输
            dic = dict()
            pos = 0
            while pos < len(data):
                if data[pos] == '@':
                    break
                pos += 1
            dic[int(data[:pos])] = data[pos+1:]
            while True:
                data, addr = self.udp_socket.recvfrom(1024)
                data = data.decode()
                if not data[0].isdigit():
                    break
                pos = 0
                while pos < len(data):
                    if data[pos] == '@':
                        break
                    pos += 1
                dic[int(data[:pos])] = data[pos + 1:]
            for key in sorted(dic):
                total_data += dic[key]
        else:
            total_data += data
        total_data = json.loads(total_data)
        return total_data, addr

    def receive(self):
        while True:
            msg, addr = self.receive_data()
            if msg['type'] == 'explore-query':
                new_msg = {
                    'type': 'explore-answer',
                    'body': self.friends
                }
                self.send_to_one(new_msg, addr)
                body = msg['body']
                self.friends[body['name']] = (body['ip'], body['port'])

            elif msg['type'] == 'explore-answer':
                new_friends = msg['body']
                # 扩充路由表，并向新朋友自我介绍
                for name, ip_port in new_friends.items():
                    if name not in self.friends:
                        self.friends[name] = tuple(ip_port)
                        new_msg = {
                            'type': 'introduce',
                            'body': {
                                'ip': self.ip,
                                'port': self.port,
                                'name': self.name
                            }
                        }
                        self.send_to_one(new_msg, ip_port)

            elif msg['type'] == 'introduce':
                new_friend = msg['body']
                self.friends[new_friend['name']] = (new_friend['ip'], new_friend['port'])

            elif msg['type'] == 'chat':
                body = msg['body']
                print(f"{body['name']}: {body['data']}")

            elif msg['type'] == 'broadcast':
                if not addr == (self.ip, self.port):
                    body = msg['body']
                    print(f"{body['name']} broadcast: {body['data']}")

            elif msg['type'] == 'quit':
                name = msg['body']['name']
                if not addr == (self.ip, self.port):
                    ip_port = self.friends.pop(name)
                    print(f"{name} {ip_port} is gone")
                else:
                    break

            elif msg['type'] == 'block-trade':
                # 启动 dpos算法
                data = msg['body']['data']
                new_block = get_new_block(self.block_chain[-1], data, self.account.address)
                block_msg = {
                    'type': 'block-new-block',
                    'body': new_block.get_content()
                }
                self.send_to_all(block_msg)
            elif msg['type'] == 'block-new-block':
                new_block = Block(**msg['body'])
                if is_block_valid(self.block_chain[-1], new_block):
                    self.block_chain.append(new_block)
                    # 成功打包区块，获得奖励
                    if new_block.miner_addr == self.account.address:
                        total_bonus = 200
                        if not self.supporters:
                            self.account.money += total_bonus
                        else:
                            # 分红
                            total_tokens = sum(self.supporters.values())
                            for ip_port, tokens in self.supporters.items():
                                bonus = int(tokens / total_tokens * total_bonus)
                                new_msg = {
                                    'type': 'block-bonus',
                                    'body': {
                                        'bonus': bonus
                                    }
                                }
                                self.send_to_one(new_msg, ip_port)
                if self.delegate_queue and self.delegate_queue[0] == addr:
                    self.delegate_queue.pop(0)
                if not self.delegate_queue:
                    self.supporters = dict()
                    self.congress = dict()
                    self.tokens = 0
            elif msg['type'] == 'block-bonus':
                bonus = msg['body']['bonus']
                self.account.money += bonus
            elif msg['type'] == 'block-vote-start':
                # 从friends中随机选取一人投票
                ip_port = random.sample(list(self.friends.values()), 1)[0]
                new_msg = {
                    'type': 'block-vote',
                    'body': {
                        'tokens': self.account.money
                    }
                }
                self.send_to_one(new_msg, ip_port)
            elif msg['type'] == 'block-vote':
                tokens = msg['body']['tokens']
                self.supporters[addr] = tokens
                self.tokens += tokens
            elif msg['type'] == 'block-vote-end':
                # 发送自己的选票
                new_msg = {
                    'type': 'block-vote-tokens',
                    'body': {
                        'tokens': self.tokens
                    }
                }
                self.send_to_all(new_msg)
            elif msg['type'] == 'block-vote-tokens':
                # (ip_addr): tokens
                self.congress[addr] = msg['body']['tokens']
                # 所有节点投票完毕
                if len(self.congress) == len(self.friends):
                    queue_size = min(MAX_QUEUE_SIZE, len(self.friends))
                    # 选票前queue_size的成为代表
                    delegate_queue = sorted(self.congress.items(), key=lambda x: x[1], reverse=True)
                    self.delegate_queue = [i[0] for i in delegate_queue[:queue_size]]
                    self.event.set()
            elif msg['type'] == 'block-sync-query':
                length = msg['body']['len']
                if len(self.block_chain) > length:
                    # 发送自己的全部数据
                    block_chain_content = []
                    for b in self.block_chain:
                        block_chain_content.append(b.get_content())
                    new_msg = {
                        'type': 'block-sync-answer',
                        'body': {
                            'len': len(self.block_chain),
                            'data': block_chain_content
                        }
                    }
                    self.send_to_one(new_msg, addr)
                elif len(self.block_chain) < length:
                    # 反问更多的数据
                    new_msg = {
                        'type': 'block-sync-query',
                        'body': {
                            'len': len(self.block_chain)
                        }
                    }
                    self.send_to_one(new_msg, addr)
            elif msg['type'] == 'block-sync-answer':
                length = msg['body']['len']
                if length > len(self.block_chain):
                    # 将自己的区块链替换为新链
                    new_block_chain_content = msg['body']['data']
                    new_block_chain = []
                    for content in new_block_chain_content:
                        new_block = Block(**content)
                        new_block_chain.append(new_block)
                    self.block_chain = new_block_chain

    def console(self):
        while True:
            # 先不使用try catch 方便debug
            # try:
            cmd = input(f'{self.name}>')
            if not cmd:
                continue
            # help
            # c name msg
            params = cmd.split()
            if params[0] == 'c':
                msg = {
                    'type': 'chat',
                    'body': {
                        'name': self.name,
                        'data': params[2]
                    }
                }
                if params[1] not in self.friends:
                    print("unknown friends. use 'lf' show all friends")
                    continue
                self.send_to_one(msg, self.friends[params[1]])
            # ca msg
            elif params[0] == 'ca':
                msg = {
                    'type': 'broadcast',
                    'body': {
                        'name': self.name,
                        'data': params[1]
                    }
                }
                self.send_to_all(msg)
            # q
            elif params[0] == 'q':
                msg = {
                    'type': 'quit',
                    'body': {
                        'name': self.name
                    }
                }
                self.send_to_all(msg)
                break
            # lf
            elif params[0] == 'lf':
                for name, ip_port in self.friends.items():
                    print(name, ip_port)
            # ln
            elif params[0] == 'ln':
                print(self.name)
                print(self.ip, self.port)
            # 区块链
            # b
            elif params[0] == 'b':
                if not self.delegate_queue:
                    # 发动选举
                    msg = {
                        'type': 'block-vote-start'
                    }
                    self.send_to_all(msg)
                    # 发送选举结束
                    self.timer = threading.Timer(MAX_VOTE_TIME, self.vote_ending, args=())
                    self.timer.start()
                    self.event.clear()
                    # 等待直到选举完毕
                    self.event.wait()

                # 发送信息
                msg = {
                    'type': 'block-trade',
                    'body': {
                        'data': params[1]
                    }
                }
                ip_port = self.delegate_queue.pop(0)
                self.send_to_one(msg, ip_port)
            # lb
            elif params[0] == 'lb':
                for block in self.block_chain:
                    pprint(block.get_content())
            # la
            elif params[0] == 'la':
                pprint(self.account.get_content())
            elif params[0] == 'h':
                tips = {
                    'b': 'launch mining.    usage: b <data>    eg: b GoodMoring!',
                    'c': 'chat to one.  usage: c <fname> <data> eg: c yzw GoodMoring!',
                    'ca': 'chat to all. usage: c <data> eg: c GoodMoring!',
                    'h': 'show helps.',
                    'la': 'list account.',
                    'lb': 'list block chain.',
                    'lf': 'list friends.',
                    'ln': 'list node.',
                    'sync': 'sync block chain. usage: sync <fname>  eg: sync yzw',
                    'sl': 'sync longest block chain',
                    'q': 'quit.',
                    'lc': 'list congress',
                    'ld': 'list delegate_queue'
                }
                for cm, tip in tips.items():
                    print("{:5} {}".format(cm, tip))
            # sync 同步区块链
            elif params[0] == 'sync':
                msg = {
                    'type': 'block-sync-query',
                    'body': {
                        'len': len(self.block_chain)
                    }
                }
                if params[1] not in self.friends:
                    print("unknown friends. use 'lf' show all friends")
                    continue
                self.send_to_one(msg, self.friends[params[1]])
            # list congress
            elif params[0] == 'lc':
                pprint(self.congress)
            elif params[0] == 'ld':
                pprint(self.delegate_queue)
            elif params[0] == 'ls':
                pprint(self.supporters)

            # except BaseException:
            #     print('Errors in parameters. Try `h` for more information.')

    def vote_ending(self):
        msg = {
            'type': 'block-vote-end'
        }
        self.send_to_all(msg)

def main():
    # cmd> python people.py ip port name
    ip = sys.argv[1]
    port = int(sys.argv[2])
    name = sys.argv[3]

    node = Node(ip, port, name)
    node.account = Account(name, random.randint(1, 10) * 100)
    node.block_chain.append(get_genesis_block())

    known_ip_port = config.known_ip_port
    node.explore_friends(known_ip_port)
    # 自动同步区块和国会信息
    t1 = threading.Thread(target=node.receive, args=())
    t2 = threading.Thread(target=node.console, args=())

    t1.start()
    t2.start()


if __name__ == '__main__':
    main()
