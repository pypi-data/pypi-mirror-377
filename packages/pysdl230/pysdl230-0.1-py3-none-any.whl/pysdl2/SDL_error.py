import ctypes
from .LoadDLL import LoadDLL


class SDL_errorcode:
	SDL_ENOMEM = 0
	SDL_EFREAD = 1
	SDL_EFWRITE = 2
	SDL_EFSEEK = 3
	SDL_UNSUPPORTED = 4
	SDL_LASTERROR = 5

LoadDLL.DLL.SDL_GetError.restype = ctypes.c_char_p
LoadDLL.DLL.SDL_GetError.argtypes = []

def SDL_GetError():
	"""
	Args:
		: None.
	Returns:
		res: ctypes.c_char_p.
	"""
	return LoadDLL.DLL.SDL_GetError()


LoadDLL.DLL.SDL_GetErrorMsg.restype = ctypes.c_char_p
LoadDLL.DLL.SDL_GetErrorMsg.argtypes = [ctypes.c_char_p, ctypes.c_int]

def SDL_GetErrorMsg(errstr, maxlen):
	"""
	Args:
		errstr: ctypes.c_char_p.
		maxlen: ctypes.c_int.
	Returns:
		res: ctypes.c_char_p.
	"""
	return LoadDLL.DLL.SDL_GetErrorMsg(errstr, maxlen)


LoadDLL.DLL.SDL_ClearError.restype = None
LoadDLL.DLL.SDL_ClearError.argtypes = []

def SDL_ClearError():
	"""
	Args:
		: None.
	Returns:
		res: None.
	"""
	LoadDLL.DLL.SDL_ClearError()


LoadDLL.DLL.SDL_Error.restype = ctypes.c_int
LoadDLL.DLL.SDL_Error.argtypes = [ctypes.c_int]

def SDL_Error(code):
	"""
	Args:
		code: SDL_errorcode.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_Error(code)