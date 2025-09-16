import ctypes
from .LoadDLL import LoadDLL


LoadDLL.DLL.SDL_GetBasePath.restype = ctypes.c_char_p
LoadDLL.DLL.SDL_GetBasePath.argtypes = []

def SDL_GetBasePath():
	"""
	Args:
		: None.
	Returns:
		res: ctypes.c_char_p.
	"""
	return LoadDLL.DLL.SDL_GetBasePath()


LoadDLL.DLL.SDL_GetPrefPath.restype = ctypes.c_char_p
LoadDLL.DLL.SDL_GetPrefPath.argtypes = [ctypes.c_char_p, ctypes.c_char_p]

def SDL_GetPrefPath(org, app):
	"""
	Args:
		org: ctypes.c_char_p.
		app: ctypes.c_char_p.
	Returns:
		res: ctypes.c_char_p.
	"""
	return LoadDLL.DLL.SDL_GetPrefPath(org, app)