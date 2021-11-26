import datetime
import hashlib
from pprint import pprint


class Account:
    def __init__(self, address='', money=0):
        self.address = address
        self.money = money

    def get_content(self):
        account_content = {
            'address': self.address,
            'money': self.money
        }
        return account_content


class Block:
    def __init__(self, index=0, time_stamp='', data='', last_hash='', miner_addr='', cur_hash=''):
        self.index = index
        self.time_stamp = time_stamp
        self.data = data
        self.last_hash = last_hash
        self.miner_addr = miner_addr
        self.cur_hash = cur_hash

    def cal_hash(self):
        string = str(self.index) + self.time_stamp + self.data + self.last_hash + self.miner_addr
        string = string.encode('utf8')
        ha = hashlib.sha256(string)
        return ha.hexdigest()

    def get_content(self):
        block_content = {
            'index': self.index,
            'time_stamp': self.time_stamp,
            'data': self.data,
            'last_hash': self.last_hash,
            'miner_addr': self.miner_addr,
            'cur_hash': self.cur_hash
        }
        return block_content


def get_genesis_block():
    block_content = {
        'index': 0,
        'time_stamp': '',
        'data': 'genesis',
        'last_hash': '0' * 64,
        'miner_addr': '0'
    }
    block = Block(**block_content)
    block.cur_hash = block.cal_hash()
    return block


def get_new_block(old_block, data, address):
    new_block = Block()
    new_block.index = old_block.index + 1
    new_block.time_stamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
    new_block.data = data
    new_block.last_hash = old_block.cur_hash
    new_block.miner_addr = address
    new_block.cur_hash = new_block.cal_hash()
    return new_block


def is_block_valid(old_block, new_block):
    if old_block.index + 1 != new_block.index:
        return False
    if old_block.cur_hash != new_block.last_hash:
        return False
    if new_block.cal_hash() != new_block.cur_hash:
        return False
    return True


if __name__ == '__main__':
    # 'time_stamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'),
    # 2021-11-20 09:43:06.672446

    # block_content = {
    #     'index': 0,
    #     'time_stamp': '2021-11-20 09:43:06.672446',
    #     'data': 'genesis',
    #     'last_hash': '0' * 64,
    #     'miner_addr': 'yzw',
    #     'cur_hash': 'zadf'
    # }
    # block = Block(**block_content)
    block = get_genesis_block()
    pprint(block.get_content())
    pass

