import ctypes
from .LoadDLL import LoadDLL


SDL_MAX_LOG_MESSAGE = 4096

class SDL_LogCategory:
	SDL_LOG_CATEGORY_APPLICATION = 0
	SDL_LOG_CATEGORY_ERROR = 1
	SDL_LOG_CATEGORY_ASSERT = 2
	SDL_LOG_CATEGORY_SYSTEM = 3
	SDL_LOG_CATEGORY_AUDIO = 4
	SDL_LOG_CATEGORY_VIDEO = 5
	SDL_LOG_CATEGORY_RENDER = 6
	SDL_LOG_CATEGORY_INPUT = 7
	SDL_LOG_CATEGORY_TEST = 8
	SDL_LOG_CATEGORY_RESERVED1 = 9
	SDL_LOG_CATEGORY_RESERVED2 = 10
	SDL_LOG_CATEGORY_RESERVED3 = 11
	SDL_LOG_CATEGORY_RESERVED4 = 12
	SDL_LOG_CATEGORY_RESERVED5 = 13
	SDL_LOG_CATEGORY_RESERVED6 = 14
	SDL_LOG_CATEGORY_RESERVED7 = 15
	SDL_LOG_CATEGORY_RESERVED8 = 16
	SDL_LOG_CATEGORY_RESERVED9 = 17
	SDL_LOG_CATEGORY_RESERVED10 = 18
	SDL_LOG_CATEGORY_CUSTOM = 19


class SDL_LogPriority:
	SDL_LOG_PRIORITY_VERBOSE = 1
	SDL_LOG_PRIORITY_DEBUG = 2
	SDL_LOG_PRIORITY_INFO = 3
	SDL_LOG_PRIORITY_WARN = 4
	SDL_LOG_PRIORITY_ERROR = 5
	SDL_LOG_PRIORITY_CRITICAL = 6
	SDL_NUM_LOG_PRIORITIES = 7

LoadDLL.DLL.SDL_LogSetAllPriority.restype = None
LoadDLL.DLL.SDL_LogSetAllPriority.argtypes = [ctypes.c_int]

def SDL_LogSetAllPriority(priority):
	"""
	Args:
		priority: SDL_LogPriority.
	Returns:
		res: None.
	"""
	LoadDLL.DLL.SDL_LogSetAllPriority(priority)


LoadDLL.DLL.SDL_LogSetPriority.restype = None
LoadDLL.DLL.SDL_LogSetPriority.argtypes = [ctypes.c_int, ctypes.c_int]

def SDL_LogSetPriority(category, priority):
	"""
	Args:
		category: ctypes.c_int.
		priority: SDL_LogPriority.
	Returns:
		res: None.
	"""
	LoadDLL.DLL.SDL_LogSetPriority(category, priority)


LoadDLL.DLL.SDL_LogResetPriorities.restype = None
LoadDLL.DLL.SDL_LogResetPriorities.argtypes = []

def SDL_LogResetPriorities():
	"""
	Args:
		: None.
	Returns:
		res: None.
	"""
	LoadDLL.DLL.SDL_LogResetPriorities()