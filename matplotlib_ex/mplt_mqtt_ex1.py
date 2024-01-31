"""
@file mplt_mqtt_ex1.py

@brief Simple animation w. Matplotlib.
"""

import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
import random


UPDATE_INTERVAL_MS = 50    # 50 ms update-interval.

 
# style.use('fivethirtyeight')      # Optional ...


fig = plt.figure()
ax1 = fig.add_subplot(1,1,1)

xs = []
ys = []


def animate(i):
    global xs, ys
    #
    if 0 != i and 0 == i % 10:
        print(f"Got {i} samples ...")
    #
    xs.append(i)
    ys.append(0.25 * random.randint(-10, 10))
    """
    graph_data = open('example.txt','r').read()
    lines = graph_data.split('\n')
    xs = []
    ys = []
    for line in lines:
        if len(line) > 1:
            x, y = line.split(',')
            xs.append(float(x))
            ys.append(float(y))
    """
    #
    ax1.clear()
    ax1.plot(xs, ys)


_ = animation.FuncAnimation(fig, animate, interval=UPDATE_INTERVAL_MS)    # NOTE: 'animation'-object is NOT used elsewhere, i.e. does NOT need a name!

plt.show()

