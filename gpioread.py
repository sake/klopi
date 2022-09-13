import gpiod

COLLECTION_WIDTH_MS = 500
MAX_DIFF_TIME_MS = 50
#SAMPLE_WIDTH_MS = 0.36
SAMPLE_WIDTH_MS = 0.3

def num_samples():
    return int(COLLECTION_WIDTH_MS / SAMPLE_WIDTH_MS)

class DataCollector:
    def __init__(self, backwards=False, with_deltas=False) -> None:
        self.backwards = backwards
        self.with_deltas = with_deltas
        self.last_event_time = 0
        self.VALUES = self.init_values()
        self.deltas = self.init_values()

    def init_values(self):
        return [0 for n in range(num_samples())]

    def clear_values(self):
        self.VALUES = self.init_values()

    def record_samples(self, event):
        event_time = event.sec + (event.nsec / 1000000000)
        sig_duration = (event_time - self.last_event_time) * 1000

        # update last event time
        if self.last_event_time == 0:
            self.last_event_time = event_time
            # discard first event
            return
        else:
            self.last_event_time = event_time

        if self.with_deltas:
            self.deltas.append(sig_duration)
            self.deltas.pop(0)
        #print(sig_duration)
        #print(f'{sig_duration:.3f}')
        #print('{0:.6g}'.format(sig_duration))

        old_sigval = None
        if event.type == gpiod.LineEvent.RISING_EDGE:
            old_sigval = 0
        elif event.type == gpiod.LineEvent.FALLING_EDGE:
            old_sigval = 1
        else:
            raise TypeError('Invalid event type')

        num_recorded_samples = int(sig_duration / SAMPLE_WIDTH_MS)
        if num_recorded_samples > num_samples():
            num_recorded_samples = num_samples()
        #print(num_recorded_samples)
        #print(len(self.VALUES))
        
        # append new values
        if self.backwards:
            for n in range(num_recorded_samples):
                self.VALUES.insert(0, old_sigval)
            # pop equal number of values
            for i in range(num_recorded_samples):
                self.VALUES.pop(-1)
        else:
            self.VALUES.extend([old_sigval for n in range(num_recorded_samples)])
            # pop equal number of values
            for i in range(num_recorded_samples):
                self.VALUES.pop(0)


def print_event(event):
    if event.type == gpiod.LineEvent.RISING_EDGE:
        evstr = ' RISING EDGE'
    elif event.type == gpiod.LineEvent.FALLING_EDGE:
        evstr = 'FALLING EDGE'
    else:
        raise TypeError('Invalid event type')

    print('event: {} offset: {} timestamp: [{}.{}]'.format(evstr,
                                                            event.source.offset(),
                                                            event.sec, event.nsec))

def connect_line():
    chip = gpiod.Chip('gpiochip0', gpiod.Chip.OPEN_BY_NAME)
    line = chip.find_line('CON2-P08')

    # config = gpiod.line_request()
    # config.consumer = "gpiotest"
    # config.request_type = gpiod.line_request.DIRECTION_INPUT

    # line.set_direction_input()
    # line.set_flags(gpiod.BIAS_PULL_UP)
    flags = gpiod.LINE_REQ_FLAG_BIAS_PULL_UP
    line.request("gpiotest", type=gpiod.LINE_REQ_EV_BOTH_EDGES, flags=flags)

    return (chip, line)
