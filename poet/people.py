import random
import threading
import socket
import sys
import json
from block import *
from pprint import pprint
import config


class Node:
    # POET part
    account = None
    block_chain = []
    poet_base = 1
    poet_scale = 2
    timer = None

    def __init__(self, ip, port, name):
        # P2P network part
        self.ip = ip
        self.port = port
        self.name = name
        # friends include self
        self.friends = dict()
        self.friends[self.name] = (self.ip, self.port)
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_socket.bind((ip, port))
        self.udp_socket = udp_socket

    # UDP just can send 1024 bytes once, modify to send big string.
    # But when broadcast big strings, this method often raise error. Take care.
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

    # also send to node self
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

    # modify to receive big string.
    def receive_data(self):
        total_data = ''
        data, addr = self.udp_socket.recvfrom(1024)
        data = data.decode()
        if data[0].isdigit():
            # receive big string
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
                # explore self.friends, and introduce self
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
                # run poet
                data = msg['body']['data']
                rand = self.poet_base + random.random() * self.poet_scale
                # sleep rand second, then execute self.get_miner_priority
                self.timer = threading.Timer(rand, self.get_miner_priority, args=(data,))
                self.timer.start()
            elif msg['type'] == 'block-miner-priority':
                if self.timer:
                    self.timer.cancel()
            elif msg['type'] == 'block-new-block':
                new_block = Block(**msg['body'])
                if is_block_valid(self.block_chain[-1], new_block):
                    self.block_chain.append(new_block)
                    # Reward 100 for successfully packing blocks
                    if new_block.miner_addr == self.account.address:
                        self.account.money += 100
            elif msg['type'] == 'block-sync-query':
                length = msg['body']['len']
                if len(self.block_chain) > length:
                    # send all blockchain data
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
                    # query back
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
                    # replace self.blockchain with longer blockchain
                    new_block_chain_content = msg['body']['data']
                    new_block_chain = []
                    for content in new_block_chain_content:
                        new_block = Block(**content)
                        new_block_chain.append(new_block)
                    self.block_chain = new_block_chain

    def console(self):
        while True:
            cmd = input(f'{self.name}>')
            try:
                if not cmd:
                    continue
                params = cmd.split()
                # chat to one
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
                # chat to all
                elif params[0] == 'ca':
                    msg = {
                        'type': 'broadcast',
                        'body': {
                            'name': self.name,
                            'data': params[1]
                        }
                    }
                    self.send_to_all(msg)
                # quit
                elif params[0] == 'q':
                    msg = {
                        'type': 'quit',
                        'body': {
                            'name': self.name
                        }
                    }
                    self.send_to_all(msg)
                    break
                # list friends
                elif params[0] == 'lf':
                    for name, ip_port in self.friends.items():
                        print(name, ip_port)
                # list node message
                elif params[0] == 'ln':
                    print('name: ', self.name)
                    print('ip port', self.ip, self.port)
                # block data
                elif params[0] == 'b':
                    msg = {
                        'type': 'block-trade',
                        'body': {
                            'data': params[1]
                        }
                    }
                    self.send_to_all(msg)
                # list blockchain
                elif params[0] == 'lb':
                    for block in self.block_chain:
                        pprint(block.get_content())
                # list accounts message
                elif params[0] == 'la':
                    pprint(self.account.get_content())
                # help
                elif params[0] == 'h':
                    tips = {
                        'b':    'launch mining.     usage: b <data>             eg: b GoodMoring!',
                        'c':    'chat to one.       usage: c <friend> <data>    eg: c yzw GoodMoring!',
                        'ca':   'chat to all.       usage: c <data>             eg: c GoodMoring!',
                        'h':    'show helps.',
                        'la':   'list account.',
                        'lb':   'list block chain.',
                        'lf':   'list friends.',
                        'ln':   'list node.',
                        'sync': 'sync block chain.  usage: sync <friend>        eg: sync yzw',
                        'q':    'quit.'
                    }
                    for cmd, tip in tips.items():
                        print("{:5} {}".format(cmd, tip))
                # sync blockchain
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
            except BaseException:
                print('Errors in parameters. Try `h` for more information.')

    def get_miner_priority(self, data):
        # inform other nodes immediately
        remind_msg = {
            'type': 'block-miner-priority',
            'body': {
                'name': self.name
            }
        }
        self.send_to_all(remind_msg)
        # generate new block
        new_block = get_new_block(self.block_chain[-1], data, self.account.address)
        block_msg = {
            'type': 'block-new-block',
            'body': new_block.get_content()
        }
        self.send_to_all(block_msg)


def main():
    # cmd> python people.py ip port name
    ip = sys.argv[1]
    port = int(sys.argv[2])
    name = sys.argv[3]

    node = Node(ip, port, name)
    node.account = Account(name, 100)
    node.block_chain.append(get_genesis_block())

    known_ip_port = config.known_ip_port
    node.explore_friends(known_ip_port)
    t1 = threading.Thread(target=node.receive, args=())
    t2 = threading.Thread(target=node.console, args=())

    t1.start()
    t2.start()


if __name__ == '__main__':
    main()
