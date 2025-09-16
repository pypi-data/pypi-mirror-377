import ctypes
from .LoadDLL import LoadDLL


LoadDLL.DLL.SDL_LoadObject.restype = ctypes.c_void_p
LoadDLL.DLL.SDL_LoadObject.argtypes = [ctypes.c_char_p]

def SDL_LoadObject(sofile):
	"""
	Args:
		sofile: ctypes.c_char_p.
	Returns:
		res: ctypes.c_void_p.
	"""
	return LoadDLL.DLL.SDL_LoadObject(sofile)


LoadDLL.DLL.SDL_LoadFunction.restype = ctypes.c_void_p
LoadDLL.DLL.SDL_LoadFunction.argtypes = [ctypes.c_void_p, ctypes.c_char_p]

def SDL_LoadFunction(handle, name):
	"""
	Args:
		handle: ctypes.c_void_p.
		name: ctypes.c_char_p.
	Returns:
		res: ctypes.c_void_p.
	"""
	return LoadDLL.DLL.SDL_LoadFunction(handle, name)