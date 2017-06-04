import numpy as np
import matplotlib.pyplot as plt
from numpy import genfromtxt

import pandas as pd
headers = ["Index","method","Obs ratio","Target ratio"]
pd1=pd.read_csv("/home/lizi-lab/Dropbox/BITE_DROPBOX/apbite_logger/experiments/analysis9_15.csv",names=headers)


'''
data_2d=pd1[["Obs ratio","Target ratio"]]
data_2d.set_index("Obs ratio", inplace="True")
data_2d.plot()


print data_2d.head()
#print pd1["method"]
plt.show()my_data = genfromtxt("/home/lizi-lab/Dropbox/BITE_DROPBOX/apbite_logger/experiments/analysis9_15.csv", delimiter=',')

print my_data[0:5]
x = np.random.rand(100)
y = np.random.rand(100)
t = np.arange(100)

plt.scatter(x, y, c=t)
plt.show()
'''