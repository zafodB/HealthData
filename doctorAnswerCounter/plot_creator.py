'''
 * Created by filip on 19/08/2019
'''


# import matplotlib
# matplotlib.use('Agg')
from matplotlib import pyplot as plt
import numpy as np

# Data from program run on all data in ehealthforums (290000+ files)
histogram = {0: 276654, 1: 20042, 2: 314, 3: 15, 4: 7, 5: 3, 7: 2, 9: 2}

fig = plt.figure()
fig.suptitle("Number of doctor replies in single thread.")

plt.bar(list(histogram.keys()), histogram.values(), width=1.0, color='g')

for x, y in zip(list(histogram.keys()),histogram.values()):

    label = "{:.0f}".format(y)

    plt.annotate(label, # this is the text
                 (x,y), # this is the point to label
                 textcoords="offset points", # how to position the text
                 xytext=(0,10), # distance from text to points (x,y)
                 ha='center')

# plt.show()
plt.xticks(np.arange(0, 10, 1))
fig.savefig(fname = "d:/downloads/json/doctor_answers_count.png")
