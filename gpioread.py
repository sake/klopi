import gpiod

COLLECTION_WIDTH_MS = 200
MAX_DIFF_TIME_MS = 50
#SAMPLE_WIDTH_MS = 0.36
SAMPLE_WIDTH_MS = 0.3


class DataCollector:
    def __init__(self) -> None:
        self.last_event_time = 0
        self.VALUES = self.init_values()
        self.deltas = self.init_values()

    def init_values(self):
        return [0 for n in range(int(COLLECTION_WIDTH_MS / SAMPLE_WIDTH_MS))]

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

        self.deltas.append(sig_duration)
        self.deltas.pop(0)
        #print(sig_duration)
        #print(f'{sig_duration:.3f}')
        #print('{0:.6g}'.format(sig_duration))
        # limit signal duration
        if sig_duration > MAX_DIFF_TIME_MS:
            sig_duration = MAX_DIFF_TIME_MS

        old_sigval = None
        if event.type == gpiod.LineEvent.RISING_EDGE:
            old_sigval = 0
        elif event.type == gpiod.LineEvent.FALLING_EDGE:
            old_sigval = 1
        else:
            raise TypeError('Invalid event type')

        num_samples = int(sig_duration / SAMPLE_WIDTH_MS)
        #print(num_samples)
        #print(len(self.VALUES))
        # append new values
        self.VALUES.extend([old_sigval for n in range(num_samples)])
        # pop equal number of values
        for i in range(num_samples):
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