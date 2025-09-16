import ctypes
from .LoadDLL import LoadDLL


LoadDLL.DLL.SDL_GetTicks.restype = ctypes.c_uint
LoadDLL.DLL.SDL_GetTicks.argtypes = []

def SDL_GetTicks():
	"""
	Args:
		: None.
	Returns:
		res: ctypes.c_uint.
	"""
	return LoadDLL.DLL.SDL_GetTicks()


LoadDLL.DLL.SDL_GetTicks64.restype = ctypes.c_ulonglong
LoadDLL.DLL.SDL_GetTicks64.argtypes = []

def SDL_GetTicks64():
	"""
	Args:
		: None.
	Returns:
		res: ctypes.c_ulonglong.
	"""
	return LoadDLL.DLL.SDL_GetTicks64()


LoadDLL.DLL.SDL_GetPerformanceCounter.restype = ctypes.c_ulonglong
LoadDLL.DLL.SDL_GetPerformanceCounter.argtypes = []

def SDL_GetPerformanceCounter():
	"""
	Args:
		: None.
	Returns:
		res: ctypes.c_ulonglong.
	"""
	return LoadDLL.DLL.SDL_GetPerformanceCounter()


LoadDLL.DLL.SDL_GetPerformanceFrequency.restype = ctypes.c_ulonglong
LoadDLL.DLL.SDL_GetPerformanceFrequency.argtypes = []

def SDL_GetPerformanceFrequency():
	"""
	Args:
		: None.
	Returns:
		res: ctypes.c_ulonglong.
	"""
	return LoadDLL.DLL.SDL_GetPerformanceFrequency()


LoadDLL.DLL.SDL_Delay.restype = None
LoadDLL.DLL.SDL_Delay.argtypes = [ctypes.c_uint]

def SDL_Delay(ms):
	"""
	Args:
		ms: ctypes.c_uint.
	Returns:
		res: None.
	"""
	LoadDLL.DLL.SDL_Delay(ms)