import ctypes
from .LoadDLL import LoadDLL


LoadDLL.DLL.SDL_OpenURL.restype = ctypes.c_int
LoadDLL.DLL.SDL_OpenURL.argtypes = [ctypes.c_char_p]

def SDL_OpenURL(url):
	"""
	Args:
		url: ctypes.c_char_p.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_OpenURL(url)