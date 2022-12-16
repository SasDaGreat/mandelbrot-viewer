import numpy as np
from matplotlib import pyplot as pl, colors
from sys import argv
from random import randint

# calculates mean and stddev of a benchmark file, and plots the distribution. pretty general so can be used for other programs that generate data

FILENAMES = argv[1:] if len(argv) > 1 else [input("Filename: ")]
BINS = 10
HUES = np.linspace(0, 1, len(FILENAMES), endpoint=False)
USE_RELATIVE_FREQ = True

for i, filename in enumerate(FILENAMES):
	try:
		filename_short = filename[-filename[::-1].find("\\"):-4]
		with open(filename, "r") as f:
			nums = np.asarray(f.read().split("\n")[2:], dtype=float)

		print(f"{filename_short} - mean: {round(np.mean(nums), 5)}; standard devn: {round(np.std(nums), 6)}")

		freqs, bins = np.histogram(nums, bins=BINS)
		if USE_RELATIVE_FREQ: freqs = freqs/freqs.max()
		pl.plot(bins[:-1], freqs, color=colors.hsv_to_rgb((HUES[i], 1, 0.9)), label=filename_short)
	except Exception as e:
		print(e)

pl.title("Time distribution")
pl.xlabel("Generation time (seconds)")
pl.ylabel("Relative frequency" if USE_RELATIVE_FREQ else "Frequency")
pl.grid(True)
pl.legend(loc="best")

pl.show()