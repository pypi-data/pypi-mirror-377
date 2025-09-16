import ctypes
from .LoadDLL import LoadDLL


SDL_INIT_TIMER = 0x00000001

SDL_INIT_AUDIO = 0x00000010

SDL_INIT_VIDEO = 0x00000020

SDL_INIT_JOYSTICK = 0x00000200

SDL_INIT_HAPTIC = 0x00001000

SDL_INIT_GAMECONTROLLER = 0x00002000

SDL_INIT_EVENTS = 0x00004000

SDL_INIT_SENSOR = 0x00008000

SDL_INIT_NOPARACHUTE = 0x00100000

SDL_INIT_EVERYTHING = 0xFFFFFFFF


LoadDLL.DLL.SDL_Init.restype = ctypes.c_int
LoadDLL.DLL.SDL_Init.argtypes = [ctypes.c_uint]

def SDL_Init(flags):
	"""
	Args:
		flags: ctypes.c_uint.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_Init(flags)


LoadDLL.DLL.SDL_InitSubSystem.restype = ctypes.c_int
LoadDLL.DLL.SDL_InitSubSystem.argtypes = [ctypes.c_uint]

def SDL_InitSubSystem(flags):
	"""
	Args:
		flags: ctypes.c_uint.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_InitSubSystem(flags)


LoadDLL.DLL.SDL_QuitSubSystem.restype = None
LoadDLL.DLL.SDL_QuitSubSystem.argtypes = [ctypes.c_uint]

def SDL_QuitSubSystem(flags):
	"""
	Args:
		flags: ctypes.c_uint.
	Returns:
		res: None.
	"""
	LoadDLL.DLL.SDL_QuitSubSystem(flags)


LoadDLL.DLL.SDL_WasInit.restype = ctypes.c_uint
LoadDLL.DLL.SDL_WasInit.argtypes = [ctypes.c_uint]

def SDL_WasInit(flags):
	"""
	Args:
		flags: ctypes.c_uint.
	Returns:
		res: ctypes.c_uint.
	"""
	return LoadDLL.DLL.SDL_WasInit(flags)


LoadDLL.DLL.SDL_Quit.restype = None
LoadDLL.DLL.SDL_Quit.argtypes = []

def SDL_Quit():
	"""
	Args:
		: None.
	Returns:
		res: None.
	"""
	LoadDLL.DLL.SDL_Quit()