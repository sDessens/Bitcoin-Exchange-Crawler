import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import math

import random




fig, ax = plt.subplots()

def genRect( x, y, w, h, color ):
    return Polygon( [(x, y), (x+w, y), (x+w, y+h), (x, y+h)], fc=color )

def genPatch( x1, y1, h1, x2, y2, h2, color ):
    return Polygon( [(x1, y1), (x2, y2), (x2, y2+h2), (x1, y1+h1)], alpha=0.1, fc=color, edgecolor='black', lw=1)


current = [0.5] * 13

raw = []

for i in range(7):
    raw.append( current )
    current = [ max(0.1,  c + random.random() - 0.4) for c in current ]

raw = [[2.058,	2.008,	1.758,	1.122,	0.742,	0.601,	2.001,	0.743,	1.484,	2.944,	6,	0.903,	0.447],
[2.058,	1.944,	1.77,	1.122,	0.742,	0.598,	2.001,	0.771,	1.503,	2.75,	6,	0.981,	0.46],
[2.058,	1.954,	1.836,	1.122,	0.737,	0.604,	2.001,	0.797,	1.563,	2.751,	6,	0.99,	0.472],
[2.116,	1.938,	1.838,	1.122,	0.747,	0.611,	2.001,	0.796,	1.606,	2.727,	6,	0.997,	0.46],
[2.146,	2.008,	1.899,	1.122,	0.756,	0.607,	2.001,	0.795,	1.663,	2.882,	6,	1.003,	0.461],
[2.167,	2.102,	1.942,	1.122,	0.755,	0.642,	2.001,	0.801,	1.692,	2.924,	6,	1.005,	0.462],
[2.141,	2.137,	1.967,	1.122,	0.75,	0.646,	2.001,	0.79,	1.694,	2.93,	6,	0.999,	0.466]]


colors = [ plt.get_cmap('Set1')( x/float(len(raw[0])) ) for x in range(len(raw[0])) ]
#colors = [ ax._get_lines.color_cycle.next() for _ in range(len(raw[0])) ]
#colors = [ 'red', 'blue', 'green', 'cyan', 'yellow' ]

w = 0.4
x = 1.0 - w/2


for day in raw:
    colorIndex = 0
    totalHeight = 0
    for height in day:
        color = colors[colorIndex]
        poly = genRect( x, totalHeight, w, height, color )
        plt.gca().add_patch(poly)
        plt.annotate( '{0:.3f}'.format(height), xy=(x + w/2, totalHeight + height / 2), ha='center',
                      va='center' )
        totalHeight += height
        colorIndex += 1
    x += 1



x = 1.0 + w/2
w = 1 - w


for old, new in zip( raw, raw[1:] ):
    colorIndex = 0
    totalLeft = 0
    totalRight = 0
    for left, right in zip( old, new ):
        color = colors[colorIndex]
        poly = genPatch( x, totalLeft, left, x+w, totalRight, right, color )
        plt.gca().add_patch(poly)
        #string = '{0:.1f}%'.format( (right-left) / left * 100.0 ) # percentage
        string = '{0:.0f} mBTC'.format( (right - left) * 1000 )
        l = (totalLeft + left/2)
        r = (totalRight + right/2)
        slope = (totalLeft - totalRight) / w/2
        angle = math.sin(-slope) / math.pi * 180
        angle = 0

        plt.annotate( string , xy=( x + w/2, totalLeft/2 + left/4 + totalRight/2 + right/4 ),
                      ha='center', va='center', rotation=angle )
        totalLeft += left
        totalRight += right
        colorIndex += 1
    x += 1
    print '----------'


ax.set_xlim( 0, 8 )
ax.set_ylim( 0, sum(raw[-1])*1.2 )
plt.show()