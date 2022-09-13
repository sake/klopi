#!/usr/bin/python3

import argparse
import sys
import pyinotify
from sound_defs import SOCKET_FILE
from soundclient import SoundClient


class EventHandler(pyinotify.ProcessEvent):
    def my_init(self, sc: SoundClient):
        self.sc = sc

    def process_default(self, event):
        #print(str(event))

        # the simple implementation just calls the reload functionality on every change
        # in the future the events shall be grouped according to a suitable time frame such as 5 seconds
        self.sc.reload_music()


def run_watcher(music_dir, handler):
    wm = pyinotify.WatchManager()
    notify = pyinotify.Notifier(wm, read_freq=2)
    mask = pyinotify.IN_DELETE | pyinotify.IN_CREATE | pyinotify.IN_MOVED_TO | pyinotify.IN_MOVED_FROM
    wm.add_watch(path=music_dir, mask=mask, auto_add=True, rec=True, proc_fun=handler)
    notify.loop()

def main() -> int:
    parser = argparse.ArgumentParser(description='KloPi music watcher')
    parser.add_argument("music_dir")
    #parser.add_argument("--group", nargs='?')
    parser.add_argument("--socket", nargs='?', default=SOCKET_FILE)
    args = parser.parse_args()

    sc = SoundClient(args.socket)
    handler = EventHandler(sc=sc)

    run_watcher(args.music_dir, handler)

    return 0

if __name__ == '__main__':
    sys.exit(main())  # next section explains the use of sys.exit
