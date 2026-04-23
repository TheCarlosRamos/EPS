import time

def build(events):
    return sorted(events, key=lambda x: x.get('ts',time.time()))
