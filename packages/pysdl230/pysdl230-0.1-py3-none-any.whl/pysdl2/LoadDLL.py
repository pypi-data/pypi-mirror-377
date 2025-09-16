import ctypes
import sys
import os


def get_ext():
	if sys.platform.startswith('win'):
		return 'dll'
	else:
		return 'so'


class LoadDLL:
	
	DLL_PATH = ''
	DLL = None
	LOADED = False
	
	@staticmethod
	def search_dll(start_dir, name):
		fullname = '{}.{}'.format(name, get_ext())
		if not os.path.isdir(start_dir):
			sys.stdout.write('{} is not a directory!\n'.format(start_dir))
			sys.exit()
		for root, dirs, files in os.walk(start_dir):
			for item in files:
				if fullname in item:
					LoadDLL.DLL_PATH = os.path.join(root, item).replace('\\', '/')
					sys.stdout.write('{} found at {}!\n'.format(fullname, LoadDLL.DLL_PATH))
					return
		sys.stdout.write('{} not found!\n'.format(fullname))
		sys.exit()
	
	@staticmethod
	def load_dll():
		if LoadDLL.LOADED:
			sys.stdout.write('{} already loaded!\n'.format(LoadDLL.DLL_PATH))
			return
		if not os.path.isfile(LoadDLL.DLL_PATH):
			sys.stdout.write('{} is not a file!\n'.format(LoadDLL.DLL_PATH))
			sys.exit()
		LoadDLL.DLL = ctypes.CDLL(LoadDLL.DLL_PATH)
		sys.stdout.write('{} loaded!\n'.format(LoadDLL.DLL_PATH))
		LoadDLL.LOADED = True



class TTFDLL:
	
	DLL_PATH = ''
	DLL = None
	LOADED = False
	
	@staticmethod
	def search_dll(start_dir, name):
		fullname = '{}.{}'.format(name, get_ext())
		if not os.path.isdir(start_dir):
			sys.stdout.write('{} is not a directory!\n'.format(start_dir))
			sys.exit()
		for root, dirs, files in os.walk(start_dir):
			for item in files:
				if fullname in item:
					TTFDLL.DLL_PATH = os.path.join(root, item).replace('\\', '/')
					sys.stdout.write('{} found at {}!\n'.format(fullname, TTFDLL.DLL_PATH))
					return
		sys.stdout.write('{} not found!\n'.format(fullname))
		sys.exit()
	
	@staticmethod
	def load_dll():
		if TTFDLL.LOADED:
			sys.stdout.write('{} already loaded!\n'.format(TTFDLL.DLL_PATH))
			return
		if not os.path.isfile(TTFDLL.DLL_PATH):
			sys.stdout.write('{} is not a file!\n'.format(TTFDLL.DLL_PATH))
			sys.exit()
		TTFDLL.DLL = ctypes.CDLL(TTFDLL.DLL_PATH)
		sys.stdout.write('{} loaded!\n'.format(TTFDLL.DLL_PATH))
		TTFDLL.LOADED = True




class ImageDLL:
	
	DLL_PATH = ''
	DLL = None
	LOADED = False
	
	@staticmethod
	def search_dll(start_dir, name):
		fullname = '{}.{}'.format(name, get_ext())
		if not os.path.isdir(start_dir):
			sys.stdout.write('{} is not a directory!\n'.format(start_dir))
			sys.exit()
		for root, dirs, files in os.walk(start_dir):
			for item in files:
				if fullname in item:
					ImageDLL.DLL_PATH = os.path.join(root, item).replace('\\', '/')
					sys.stdout.write('{} found at {}!\n'.format(fullname, ImageDLL.DLL_PATH))
					return
		sys.stdout.write('{} not found!\n'.format(fullname))
		sys.exit()
	
	@staticmethod
	def load_dll():
		if ImageDLL.LOADED:
			sys.stdout.write('{} already loaded!\n'.format(ImageDLL.DLL_PATH))
			return
		if not os.path.isfile(ImageDLL.DLL_PATH):
			sys.stdout.write('{} is not a file!\n'.format(ImageDLL.DLL_PATH))
			sys.exit()
		ImageDLL.DLL = ctypes.CDLL(ImageDLL.DLL_PATH)
		sys.stdout.write('{} loaded!\n'.format(ImageDLL.DLL_PATH))
		ImageDLL.LOADED = True




class MixerDLL:
	
	DLL_PATH = ''
	DLL = None
	LOADED = False
	
	@staticmethod
	def search_dll(start_dir, name):
		fullname = '{}.{}'.format(name, get_ext())
		if not os.path.isdir(start_dir):
			sys.stdout.write('{} is not a directory!\n'.format(start_dir))
			sys.exit()
		for root, dirs, files in os.walk(start_dir):
			for item in files:
				if fullname in item:
					MixerDLL.DLL_PATH = os.path.join(root, item).replace('\\', '/')
					sys.stdout.write('{} found at {}!\n'.format(fullname, MixerDLL.DLL_PATH))
					return
		sys.stdout.write('{} not found!\n'.format(fullname))
		sys.exit()
	
	@staticmethod
	def load_dll():
		if MixerDLL.LOADED:
			sys.stdout.write('{} already loaded!\n'.format(MixerDLL.DLL_PATH))
			return
		if not os.path.isfile(MixerDLL.DLL_PATH):
			sys.stdout.write('{} is not a file!\n'.format(MixerDLL.DLL_PATH))
			sys.exit()
		MixerDLL.DLL = ctypes.CDLL(MixerDLL.DLL_PATH)
		sys.stdout.write('{} loaded!\n'.format(MixerDLL.DLL_PATH))
		MixerDLL.LOADED = True