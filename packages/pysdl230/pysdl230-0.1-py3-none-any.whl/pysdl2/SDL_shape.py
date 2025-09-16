import ctypes
from .LoadDLL import LoadDLL
from .SDL_pixels import SDL_Color
from .SDL_video import SDL_Window
from .SDL_surface import SDL_Surface


SDL_NONSHAPEABLE_WINDOW = -1

SDL_INVALID_SHAPE_ARGUMENT = -2

SDL_WINDOW_LACKS_SHAPE = -3

class WindowShapeMode:
	ShapeModeDefault = 0
	ShapeModeBinarizeAlpha = 1
	ShapeModeReverseBinarizeAlpha = 2
	ShapeModeColorKey = 3

class SDL_WindowShapeParams(ctypes.Union):
	_fields_ = [
		('binarizationCutoff', ctypes.c_ubyte),
		('colorKey', SDL_Color),
	]

class SDL_WindowShapeMode(ctypes.Structure):
	_fields_ = [
		('mode', ctypes.c_int),
		('parameters', SDL_WindowShapeParams),
	]

LoadDLL.DLL.SDL_CreateShapedWindow.restype = ctypes.POINTER(SDL_Window)
LoadDLL.DLL.SDL_CreateShapedWindow.argtypes = [ctypes.c_char_p, ctypes.c_uint, ctypes.c_uint, ctypes.c_uint, ctypes.c_uint, ctypes.c_uint]

def SDL_CreateShapedWindow(title, x, y, w, h, flags):
	"""
	Args:
		title: ctypes.c_char_p.
		x: ctypes.c_uint.
		y: ctypes.c_uint.
		w: ctypes.c_uint.
		h: ctypes.c_uint.
		flags: ctypes.c_uint.
	Returns:
		res: ctypes.POINTER(SDL_Window).
	"""
	return LoadDLL.DLL.SDL_CreateShapedWindow(title, x, y, w, h, flags)


LoadDLL.DLL.SDL_IsShapedWindow.restype = ctypes.c_int
LoadDLL.DLL.SDL_IsShapedWindow.argtypes = [ctypes.POINTER(SDL_Window)]

def SDL_IsShapedWindow(window):
	"""
	Args:
		window: ctypes.POINTER(SDL_Window).
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_IsShapedWindow(window)


LoadDLL.DLL.SDL_SetWindowShape.restype = ctypes.c_int
LoadDLL.DLL.SDL_SetWindowShape.argtypes = [ctypes.POINTER(SDL_Window), ctypes.POINTER(SDL_Surface), ctypes.POINTER(SDL_WindowShapeMode)]

def SDL_SetWindowShape(window, shape, shape_mode):
	"""
	Args:
		window: ctypes.POINTER(SDL_Window).
		shape: ctypes.POINTER(SDL_Surface).
		shape_mode: ctypes.POINTER(SDL_WindowShapeMode).
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_SetWindowShape(window, shape, shape_mode)


LoadDLL.DLL.SDL_GetShapedWindowMode.restype = ctypes.c_int
LoadDLL.DLL.SDL_GetShapedWindowMode.argtypes = [ctypes.POINTER(SDL_Window), ctypes.POINTER(SDL_WindowShapeMode)]

def SDL_GetShapedWindowMode(window, shape_mode):
	"""
	Args:
		window: ctypes.POINTER(SDL_Window).
		shape_mode: ctypes.POINTER(SDL_WindowShapeMode).
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_GetShapedWindowMode(window, shape_mode)