#!/usr/bin/python3

import sys
import os
import grp
import signal
import threading
import socketserver
import random
import subprocess
import argparse
from sound_defs import SOCKET_FILE, PLAY_RANDOM, LOAD_FILES


SOCKET_FILE_PERMISSION = 0o750
AUDIO_FILE_ENDINGS = ["wav", "w64", "mp3", "ogg", "opus", "flac", "aif", "aifc", "aiff", "aiffc"]
PLAY_CMD = "/usr/bin/play"

def supported_audio_file_endings():
    return AUDIO_FILE_ENDINGS


class Context():
    def __init__(self):
        self.socket_file = None
        self.player = None
        self.server = None

    def load(self, music_dir, group, socket_file):
        self.socket_file = socket_file
        self.player = Player(music_dir)
        self.server = socketserver.UnixStreamServer(self.socket_file, CommandHandler)
        if group:
            try:
                gid = grp.getgrnam(group)
                os.chown(self.socket_file, -1, gid.gr_gid)
            except KeyError:
                print("ERROR: Invalid group specified, skipping group adjustment.")
            except PermissionError:
                print("ERROR: No permission to change socket group.")
        os.chmod(self.socket_file, SOCKET_FILE_PERMISSION)

    def cleanup(self):
        print(f"Shutting down ...")

        if self.server:
            self.server.shutdown()
            os.remove(self.socket_file)
        if self.player:
            self.player.shutdown()


class Player():
    def __init__(self, music_dir):
        self.proc = None
        self.music_dir = music_dir
        print(f"Loading sound files in directory {music_dir} ...")
        self.files = self.__build_file_list__()

    def load_sound_files(self):
        print(f"Reloading sound files {self.music_dir} ...")
        self.files = self.__build_file_list__()

    def __build_file_list__(self):
        list_of_files = []

        for root, dirs, files in os.walk(self.music_dir):
            for file in files:
                if self.is_music_file(file):
                    list_of_files.append(os.path.join(root, file))

        return list_of_files

    def is_music_file(self, file):
        for ending in AUDIO_FILE_ENDINGS:
            if file.lower().endswith("." + ending):
                return True
        return False

    def is_playing(self) -> bool:
        if self.proc is not None and self.proc.returncode is None:
            returncode = self.proc.poll()
            return returncode is None
        return False

    def play_random(self):
        if not self.is_playing():
            music_file = random.choice(self.files)
            print(f"Starting playback: {music_file}")
            self.proc = subprocess.Popen([PLAY_CMD, "-q", music_file])

    def shutdown(self):
        if self.is_playing():
            print("Killing player child process")
            self.proc.terminate()


class CommandHandler(socketserver.StreamRequestHandler):
    def handle(self):
        command = self.rfile.readline().decode("utf-8")
        #print(command)
        if command == PLAY_RANDOM:
            ctx.player.play_random()
        elif command == LOAD_FILES:
            ctx.player.load_sound_files()
        else:
            print(f'ERROR: Unkown command received: {command}')



ctx = Context()
def handle_terminate(signum, frame):
    ct = threading.Thread(target=lambda : ctx.cleanup())
    ct.start()


def main() -> int:
    parser = argparse.ArgumentParser(description='KloPi sound server')
    parser.add_argument("music_dir")
    parser.add_argument("--group", nargs='?')
    parser.add_argument("--socket", nargs='?', default=SOCKET_FILE)
    args = parser.parse_args()

    ctx.load(args.music_dir, args.group, args.socket)

    signal.signal(signal.SIGINT, handle_terminate)
    signal.signal(signal.SIGTERM, handle_terminate)

    # start server
    ctx.server.serve_forever()

    return 0

if __name__ == '__main__':
    sys.exit(main())  # next section explains the use of sys.exit
