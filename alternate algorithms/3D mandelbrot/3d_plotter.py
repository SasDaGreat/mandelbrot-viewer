import numpy as np
import matplotlib.pyplot as plt
from sys import argv

FILENAME = argv[1] if len(argv) > 1 else "mandel_3dw_c-(INITIAL_Z)_i100_t(-2.0, 1.5)_QVciwf.npy" #input("Filename: ")
data = np.load(FILENAME)[::,::,::]

try:
	ax = plt.figure().add_subplot(projection='3d')
	ax.voxels(data)

	plt.show()
except Exception as e:
	input(e)