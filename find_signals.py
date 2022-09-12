from datetime import datetime
import sys
import gpiod
import numpy as np
from gpioread import DataCollector


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
            print(result)
            print_sequence(rest)



if __name__ == '__main__':
    chip = gpiod.Chip('gpiochip0', gpiod.Chip.OPEN_BY_NAME)
    line = chip.find_line('CON2-P08')

    # config = gpiod.line_request()
    # config.consumer = "gpiotest"
    # config.request_type = gpiod.line_request.DIRECTION_INPUT

    # line.set_direction_input()
    # line.set_flags(gpiod.BIAS_PULL_UP)
    #flags = gpiod.LINE_REQ_FLAG_BIAS_PULL_UP
    line.request("gpiotest", type=gpiod.LINE_REQ_EV_BOTH_EDGES)#, flags=flags)

    beginning_time = datetime.now()
    dc = DataCollector()
    #0.36ms sample size
    while (True):
        line.event_wait()
        evt = line.event_read()
        #print_event(evt)
        dc.record_samples(evt)
        if (datetime.now() - beginning_time).seconds > 1:
            #print(np.array(dc.VALUES, dtype=bytes).tobytes())
            #print(dc.deltas)
            print_sequence(dc.VALUES)
            sys.exit(0)

    #chip.close()
