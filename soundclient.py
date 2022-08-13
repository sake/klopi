#!/usr/bin/python3

import sys
import socket
import argparse
from sound_defs import SOCKET_FILE, PLAY_RANDOM, LOAD_FILES

class SoundClient():
    def __init__(self, socket_file = SOCKET_FILE):
        self.socket_file = socket_file
        self.sock = None

    def connect(self):
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.connect(self.socket_file)

    def disconnect(self):
        self.sock.close()
        self.sock = None

    def send_cmd(self, cmd):
        self.connect()
        self.sock.sendall(bytes(cmd, "utf-8"))
        self.disconnect()

    def play_random(self):
        self.send_cmd(PLAY_RANDOM)

    def reload_music(self):
        self.send_cmd(LOAD_FILES)


def main() -> int:
    parser = argparse.ArgumentParser(description='KloPi sound client')
    parser.add_argument("--socket", nargs='?', default=SOCKET_FILE)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--play-random', action='store_true')
    group.add_argument('--reload-music', action='store_true')
    args = parser.parse_args()

    sc = SoundClient(args.socket)

    if args.play_random:
        sc.play_random()
    elif args.reload_music:
        sc.reload_music()

    return 0

if __name__ == '__main__':
    sys.exit(main())  # next section explains the use of sys.exit
