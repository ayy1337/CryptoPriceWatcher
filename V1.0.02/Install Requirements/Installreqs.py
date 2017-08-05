#!/usr/bin/python3

import pip, importlib, os

def install(package):
	pip.main(['install', package])

def installed(package):
	res = importlib.util.find_spec(package)
	return res is not None

if __name__ == "__main__":
	modules = ['playsound', 'PyQt5', 'requests']
	if os.name == "nt":
		modules.append("pypiwin32")
		modules.append("win10toast")
	for module in modules:
		if not installed(module):
			print("Module: {} not found, installing...".format(module))
			install(module)