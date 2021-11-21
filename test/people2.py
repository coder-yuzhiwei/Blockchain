import socket
import sys
import json
import threading


def main():
    # port = int(sys.argv[1])  # 从命令行获取端口号
    port = 8892
    fromA = ("127.0.0.1", port)
    toB = ("127.0.0.1", 8891)
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind((fromA[0], fromA[1]))

    def send():
        while True:
            s = input('请输入：')
            msg = {
                'type': 'chat',
                'body': {
                    'data': s
                }
            }
            msg = json.dumps(msg).encode('utf8')
            udp_socket.sendto(msg, toB)

    def receive():
        while True:
            total_data = bytes()
            while True:
                data, addr = udp_socket.recvfrom(1024)
                total_data += data
                if len(data) < 1024:
                    break
            total_data = json.loads(total_data.decode())
            print()
            print(total_data)
            print(addr)

    t1 = threading.Thread(target=receive, args=())
    t2 = threading.Thread(target=send, args=())

    t1.start()
    t2.start()


if __name__ == '__main__':
    main()