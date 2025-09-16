import ctypes
from .LoadDLL import LoadDLL


class SDL_PowerState:
	SDL_POWERSTATE_UNKNOWN = 0
	SDL_POWERSTATE_ON_BATTERY = 1
	SDL_POWERSTATE_NO_BATTERY = 2
	SDL_POWERSTATE_CHARGING = 3
	SDL_POWERSTATE_CHARGED = 4

LoadDLL.DLL.SDL_GetPowerInfo.restype = ctypes.c_int
LoadDLL.DLL.SDL_GetPowerInfo.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]

def SDL_GetPowerInfo(seconds, percent):
	"""
	Args:
		seconds: ctypes.POINTER(ctypes.c_int).
		percent: ctypes.POINTER(ctypes.c_int).
	Returns:
		res: SDL_PowerState.
	"""
	return LoadDLL.DLL.SDL_GetPowerInfo(seconds, percent)