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
    def __init__(self, index=0, time_stamp='', data='', last_hash='', miner_addr='', diff_num=0, nonce=0, cur_hash=''):
        self.index = index
        self.time_stamp = time_stamp
        self.data = data
        self.last_hash = last_hash
        self.miner_addr = miner_addr
        self.diff_num = diff_num
        self.nonce = nonce
        self.cur_hash = cur_hash

    def cal_hash(self):
        string = str(self.index) + self.time_stamp + self.data + self.last_hash + self.miner_addr + str(self.diff_num)\
                 + str(self.nonce)
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
            'diff_num': self.diff_num,
            'nonce': self.nonce,
            'cur_hash': self.cur_hash
        }
        return block_content


def get_genesis_block():
    block_content = {
        'index': 0,
        'time_stamp': '',
        'data': 'genesis',
        'last_hash': '0' * 64,
        'miner_addr': '0',
        'diff_num': 0,
        'nonce': 0
    }
    block = Block(**block_content)
    # 使创世区块也满足hash < bigNum
    big_num = 1 << (256 - block.diff_num)
    while True:
        cur_hash = block.cal_hash()
        hash_num = int(cur_hash, 16)
        if hash_num < big_num:
            block.cur_hash = cur_hash
            break
        else:
            block.nonce += 1
    return block


def is_block_valid(old_block, new_block):
    if old_block.index + 1 != new_block.index:
        return False
    if old_block.cur_hash != new_block.last_hash:
        return False
    if new_block.cal_hash() != new_block.cur_hash:
        return False
    # 验证pow
    big_num = 1 << (256 - new_block.diff_num)
    hash_num = int(new_block.cur_hash, 16)
    if hash_num >= big_num:
        return False
    return True


if __name__ == '__main__':
    block = get_genesis_block()
    pprint(block.get_content())

