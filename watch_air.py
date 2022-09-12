import argparse
from copy import deepcopy
import sys
import io
import re
import threading
from time import sleep
import gpiod
from gpioread import DataCollector, connect_line


def load_signal_strings(signals_file):
    result = []
    for line in io.open(signals_file).readlines():
        m = re.search("(0|1)+", line)
        if m:
            bitList = [int(c) for c in m.group(0)]
            result.append(bitList)
    return result

def find_signal(signals, values):
    for signal in signals:
        for i in range(len(values) - len(signal) + 1):
            # true until proven otherwise
            match_found = True
            for j in range(len(signal)):
                if values[i+j] != signal[j]:
                    match_found = False
                    break;
            if match_found:
                return True
    # we scanned everything and found nothing
    return False

def record_fun(line, dc, mutex):
    while (True):
        line.event_wait()
        evt = line.event_read()
        #print_event(evt)
        mutex.acquire()
        dc.record_samples(evt)
        mutex.release()


def search_fun(signals, dc, mutex):
    while True:
        # wait one complete timeframe
        sleep(150/1000)

        # copy data in a safe way
        mutex.acquire()
        values = deepcopy(dc.VALUES)
        mutex.release()

        if find_signal(signals, values):
            print("Signal found")

def main() -> int:
    parser = argparse.ArgumentParser(description='KloPi Air Watcher')
    parser.add_argument("signals_file")
    args = parser.parse_args()

    signals = load_signal_strings(args.signals_file)
    if len(signals) == 0:
        print("No valid signal definitions found in signals file.")
        return 1

    (chip, line) = connect_line()
    dc = DataCollector(backwards=True)

    mutex = threading.Semaphore()
    record_thread = threading.Thread(target=record_fun, args=(line, dc, mutex))
    record_thread.start()
    search_thread = threading.Thread(target=search_fun, args=(signals, dc, mutex))
    search_thread.start()

    while record_thread.is_alive() and search_thread.is_alive():
        sleep(1)

    return 0

if __name__ == '__main__':
    sys.exit(main())  # next section explains the use of sys.exit
