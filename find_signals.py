#!/usr/bin/python3

from datetime import datetime
import sys
import gpiod
import numpy as np
from gpioread import DataCollector, connect_line


def print_sequence(values):
    pre = [0 for i in range(15)]
    pre.append(1)
    pre = np.array(pre, dtype=bytes).tobytes()
    post = [0 for i in range(15)]
    post.insert(0, 1)
    post = np.array(post, dtype=bytes).tobytes()

    values = np.array(values, dtype=bytes).tobytes()
    #print(values)                                                                                                                                                           

    begin = values.find(pre)
    #print(begin)                                                                                                                                                            
    if begin != -1:
        values = values[(begin+len(pre)-1):]
        #print(values)                                                                                                                                                       

        end = values.find(post)
        #print(end)                                                                                                                                                          
        if end != -1:
            result = values[:(end+1)]
            rest = values[(end+1):]
            print(f"{result} {len(result)} bit")
            print_sequence(rest)



if __name__ == '__main__':
    (chip, line) = connect_line()

    beginning_time = datetime.now()
    dc = DataCollector(with_deltas=True)
    #0.36ms sample size
    while (True):
        line.event_wait()
        for evt in line.event_read_multiple():
            #print_event(evt)
            dc.record_samples(evt)
            if (datetime.now() - beginning_time).seconds > 1:
                # print("Captured Data")
                # print("=============")
                # print(np.array(dc.VALUES, dtype=bytes).tobytes())
                #print(dc.deltas)
                print()
                print("Detected Signals")
                print("================")
 
                print_sequence(dc.VALUES)
                sys.exit(0)

    #chip.close()
