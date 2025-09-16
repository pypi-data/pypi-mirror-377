import ctypes
import sys
from .LoadDLL import LoadDLL


LoadDLL.DLL.SDL_SetMainReady.restype = None
LoadDLL.DLL.SDL_SetMainReady.argtypes = []

def SDL_SetMainReady():
	"""
	Args:
		: None.
	Returns:
		res: None.
	"""
	LoadDLL.DLL.SDL_SetMainReady()


LoadDLL.DLL.SDL_RegisterApp.restype = ctypes.c_int
LoadDLL.DLL.SDL_RegisterApp.argtypes = [ctypes.c_char_p, ctypes.c_uint, ctypes.c_void_p]

def SDL_RegisterApp(name, style, hInst):
	"""
	Args:
		name: ctypes.c_char_p.
		style: ctypes.c_uint.
		hInst: ctypes.c_void_p.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_RegisterApp(name, style, hInst)


SDL_main_func = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.POINTER(ctypes.c_char)))


def sdl_main(func):
	@SDL_main_func
	def wrapper(argc, argv):
		argv_lst = []
		for i in range(argc):
			char_ptr = argv[i]
			byte_str = ctypes.string_at(char_ptr)
			try:
				py_str = byte_str.decode('utf-8')
			except UnicodeDecodeError:
				py_str = byte_str.decode(sys.getfilesystemencoding())
			argv_lst.append(py_str)
		return func(argc, argv_lst)
	return wrapper