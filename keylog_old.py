import curses
from time import perf_counter_ns
from typing import List, Set
from string import ascii_lowercase
from random import randrange
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
used_word: Set[int] = set()

screen = curses.initscr()
curses.noecho()

while True:
    word_i = randrange(all_words_count)
    while word_i in used_word:
        word_i = randrange(all_words_count)
    used_word.add(word_i)

    the_word = all_words[word_i]
    screen.clear()
    screen.addstr(0,0, f'Current word number: {len(used_word)}')
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

total_time = logtimes[-1][-1]-logtimes[0][0]

def rolling_window(a, window) -> np.ndarray :
    shape = a.shape[:-1] + (a.shape[-1] - window + 1, window)
    strides = a.strides + (a.strides[-1],)
    return np.lib.stride_tricks.as_strided(a, shape=shape, strides=strides)

buffer_digrams = []
buffer_trigrams = []
time_digrams = []
time_trigrams = []

for (buffer, logtime) in zip(buffers, logtimes):
    buffer_digrams.append(np.array(np.apply_along_axis(lambda a: a[0]+a[1], 1, rolling_window(buffer, 2))))
    buffer_digrams.append(np.array([' ']))

    buffer_trigrams.append(np.array(np.apply_along_axis(lambda a: a[0]+a[1]+a[2], 1, rolling_window(buffer, 3))))
    buffer_trigrams.append(np.array([' ']))

    time_digrams.append(np.array(np.apply_along_axis(lambda a: a[1] - a[0], 1, rolling_window(logtime,2)), dtype=np.int64))
    time_digrams.append(np.array([0], dtype=np.int64))

    time_trigrams.append(np.array(np.apply_along_axis(lambda a: a[2] - a[0], 1, rolling_window(logtime,3)), dtype=np.int64))
    time_trigrams.append(np.array([0], dtype=np.int64))

buffer_digram = np.concatenate(buffer_digrams)
buffer_trigram = np.concatenate(buffer_trigrams)
time_digram = np.concatenate(time_digrams)
time_trigram = np.concatenate(time_trigrams)

digram = np.concatenate((buffer_digram.reshape((len(buffer_digram),1)), time_digram.reshape((len(buffer_digram),1))), axis=1)
trigram = np.concatenate((buffer_trigram.reshape((len(buffer_trigram),1)), time_trigram.reshape((len(buffer_trigram),1))), axis=1)

import pandas as pd
digramdf = pd.DataFrame(digram, columns=['seq','time'])
trigramdf = pd.DataFrame(trigram, columns=['seq','time'])
digramdf.to_csv('digram.csv')
trigramdf.to_csv('trigram.csv')
with open('total_time.txt', 'w') as f:
    f.write(str(total_time)+'\n')
    f.write(str(len(buffer)))

print(digram)
print(trigram)
print(total_time)
