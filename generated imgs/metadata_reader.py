from PIL import Image
from sys import argv

def metatext(filename):	return Image.open(filename).text

if __name__ == "__main__":
	files = argv[1:] if len(argv) > 1 else input("Filenames (separate files with spaces): ").split()
	for filename in files:
		print(metatext(filename))
	input("Enter to exit")