import curses
from time import perf_counter_ns
from typing import List
from string import ascii_lowercase
import numpy as np

def is_okay(x: str) -> bool:
    if len(x) < 3:
        return False
    for c in x:
        if c not in ascii_lowercase:
            return False
    return True


with open('./dict.txt') as f:
    all_words = [x.strip() for x in f.readlines() if is_okay(x.strip())]
all_words_count = len(all_words)


buffers: List[str] = []
logtimes: List[List[int]] = []
num_word = 0

screen = curses.initscr()
curses.noecho()

for the_word in all_words[:100]:
    num_word += 1
    screen.clear()
    screen.addstr(0,0, f'Current word number: {num_word}')
    screen.addstr(1,0, the_word)
    screen.refresh()

    buffer: str = ""
    logtime: List[int] = []

    screen.move(2,0)
    while buffer != the_word:
        screen.refresh()
        s = screen.getch()
        c = chr(s)
        if s == 3:
            break
        if c == the_word[len(buffer)]:
            logtime.append(perf_counter_ns())
            buffer += c
            screen.addstr(c)
            screen.move(2,len(buffer))
    
    if buffer == the_word:
        buffers.append(np.array([c for c in buffer]))
        logtimes.append(np.array(logtime, dtype=np.int64))
    else:
        break

curses.endwin()

import pickle
with open('./buffers.pkl', 'wb') as f:
    pickle.dump(buffers, f)
with open('./logtimes.pkl', 'wb') as f:
    pickle.dump(logtimes, f)
