import ctypes
from .LoadDLL import LoadDLL
from .SDL_video import SDL_Window
from .SDL_version import SDL_version


SDL_METALVIEW_TAG = 255

class SDL_SYSWM_TYPE:
	SDL_SYSWM_UNKNOWN = 0
	SDL_SYSWM_WINDOWS = 1
	SDL_SYSWM_X11 = 2
	SDL_SYSWM_DIRECTFB = 3
	SDL_SYSWM_COCOA = 4
	SDL_SYSWM_UIKIT = 5
	SDL_SYSWM_WAYLAND = 6
	SDL_SYSWM_MIR = 7
	SDL_SYSWM_WINRT = 8
	SDL_SYSWM_ANDROID = 9
	SDL_SYSWM_VIVANTE = 10
	SDL_SYSWM_OS2 = 11
	SDL_SYSWM_HAIKU = 12
	SDL_SYSWM_KMSDRM = 13
	SDL_SYSWM_RISCOS = 14


class SDL_SysWMmsg(ctypes.Structure):
	_fields_ = [
		('version', SDL_version),
		('subsystem', ctypes.c_int),
	]


class SDL_SysWMinfo(ctypes.Structure):
	_fields_ = [
		('version', SDL_version),
		('subsystem', ctypes.c_int),
	]


LoadDLL.DLL.SDL_GetWindowWMInfo.restype = ctypes.c_int
LoadDLL.DLL.SDL_GetWindowWMInfo.argtypes = [ctypes.POINTER(SDL_Window), ctypes.POINTER(SDL_SysWMinfo)]

def SDL_GetWindowWMInfo(window, info):
	"""
	Args:
		window: ctypes.POINTER(SDL_Window).
		info: ctypes.POINTER(SDL_SysWMinfo).
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_GetWindowWMInfo(window, info)