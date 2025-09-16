import ctypes
from .LoadDLL import LoadDLL
from .SDL_video import SDL_Window


SDL_BUTTON_LEFT = 1

SDL_BUTTON_MIDDLE = 2

SDL_BUTTON_RIGHT = 3

SDL_BUTTON_X1 = 4

SDL_BUTTON_X2 = 5

class SDL_SystemCursor:
	SDL_SYSTEM_CURSOR_ARROW = 0
	SDL_SYSTEM_CURSOR_IBEAM = 1
	SDL_SYSTEM_CURSOR_WAIT = 2
	SDL_SYSTEM_CURSOR_CROSSHAIR = 3
	SDL_SYSTEM_CURSOR_WAITARROW = 4
	SDL_SYSTEM_CURSOR_SIZENWSE = 5
	SDL_SYSTEM_CURSOR_SIZENESW = 6
	SDL_SYSTEM_CURSOR_SIZEWE = 7
	SDL_SYSTEM_CURSOR_SIZENS = 8
	SDL_SYSTEM_CURSOR_SIZEALL = 9
	SDL_SYSTEM_CURSOR_NO = 10
	SDL_SYSTEM_CURSOR_HAND = 11
	SDL_NUM_SYSTEM_CURSORS = 12


class SDL_MouseWheelDirection:
	SDL_MOUSEWHEEL_NORMAL = 0
	SDL_MOUSEWHEEL_FLIPPED = 1


class SDL_Cursor(ctypes.Structure): pass


LoadDLL.DLL.SDL_GetMouseFocus.restype = ctypes.POINTER(SDL_Window)
LoadDLL.DLL.SDL_GetMouseFocus.argtypes = []

def SDL_GetMouseFocus():
	"""
	Args:
		: None.
	Returns:
		res: ctypes.POINTER(SDL_Window).
	"""
	return LoadDLL.DLL.SDL_GetMouseFocus()


LoadDLL.DLL.SDL_GetMouseState.restype = ctypes.c_uint
LoadDLL.DLL.SDL_GetMouseState.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]

def SDL_GetMouseState(x, y):
	"""
	Args:
		x: ctypes.POINTER(ctypes.c_int).
		y: ctypes.POINTER(ctypes.c_int).
	Returns:
		res: ctypes.c_uint.
	"""
	return LoadDLL.DLL.SDL_GetMouseState(x, y)


LoadDLL.DLL.SDL_GetGlobalMouseState.restype = ctypes.c_uint
LoadDLL.DLL.SDL_GetGlobalMouseState.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]

def SDL_GetGlobalMouseState(x, y):
	"""
	Args:
		x: ctypes.POINTER(ctypes.c_int).
		y: ctypes.POINTER(ctypes.c_int).
	Returns:
		res: ctypes.c_uint.
	"""
	return LoadDLL.DLL.SDL_GetGlobalMouseState(x, y)


LoadDLL.DLL.SDL_GetRelativeMouseState.restype = ctypes.c_uint
LoadDLL.DLL.SDL_GetRelativeMouseState.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]

def SDL_GetRelativeMouseState(x, y):
	"""
	Args:
		x: ctypes.POINTER(ctypes.c_int).
		y: ctypes.POINTER(ctypes.c_int).
	Returns:
		res: ctypes.c_uint.
	"""
	return LoadDLL.DLL.SDL_GetRelativeMouseState(x, y)


LoadDLL.DLL.SDL_WarpMouseInWindow.restype = None
LoadDLL.DLL.SDL_WarpMouseInWindow.argtypes = [ctypes.POINTER(SDL_Window), ctypes.c_int, ctypes.c_int]

def SDL_WarpMouseInWindow(window, x, y):
	"""
	Args:
		window: ctypes.POINTER(SDL_Window).
		x: ctypes.c_int.
		y: ctypes.c_int.
	Returns:
		res: None.
	"""
	LoadDLL.DLL.SDL_WarpMouseInWindow(window, x, y)


LoadDLL.DLL.SDL_SetRelativeMouseMode.restype = ctypes.c_int
LoadDLL.DLL.SDL_SetRelativeMouseMode.argtypes = [ctypes.c_int]

def SDL_SetRelativeMouseMode(enabled):
	"""
	Args:
		enabled: ctypes.c_int.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_SetRelativeMouseMode(enabled)


LoadDLL.DLL.SDL_CaptureMouse.restype = ctypes.c_int
LoadDLL.DLL.SDL_CaptureMouse.argtypes = [ctypes.c_int]

def SDL_CaptureMouse(enabled):
	"""
	Args:
		enabled: ctypes.c_int.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_CaptureMouse(enabled)


LoadDLL.DLL.SDL_GetRelativeMouseMode.restype = ctypes.c_int
LoadDLL.DLL.SDL_GetRelativeMouseMode.argtypes = []

def SDL_GetRelativeMouseMode():
	"""
	Args:
		: None.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_GetRelativeMouseMode()


LoadDLL.DLL.SDL_CreateCursor.restype = ctypes.POINTER(SDL_Cursor)
LoadDLL.DLL.SDL_CreateCursor.argtypes = [ctypes.POINTER(ctypes.c_ubyte), ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]

def SDL_CreateCursor(data, mask, w, h, hot_x, hot_y):
	"""
	Args:
		data: ctypes.POINTER(ctypes.c_ubyte).
		mask: ctypes.POINTER(ctypes.c_ubyte).
		w: ctypes.c_int.
		h: ctypes.c_int.
		hot_x: ctypes.c_int.
		hot_y: ctypes.c_int.
	Returns:
		res: ctypes.POINTER(SDL_Cursor).
	"""
	return LoadDLL.DLL.SDL_CreateCursor(data, mask, w, h, hot_x, hot_y)


LoadDLL.DLL.SDL_CreateSystemCursor.restype = ctypes.POINTER(SDL_Cursor)
LoadDLL.DLL.SDL_CreateSystemCursor.argtypes = [ctypes.c_int]

def SDL_CreateSystemCursor(id):
	"""
	Args:
		id: SDL_SystemCursor.
	Returns:
		res: ctypes.POINTER(SDL_Cursor).
	"""
	return LoadDLL.DLL.SDL_CreateSystemCursor(id)


LoadDLL.DLL.SDL_SetCursor.restype = None
LoadDLL.DLL.SDL_SetCursor.argtypes = [ctypes.POINTER(SDL_Cursor)]

def SDL_SetCursor(cursor):
	"""
	Args:
		cursor: ctypes.POINTER(SDL_Cursor).
	Returns:
		res: None.
	"""
	LoadDLL.DLL.SDL_SetCursor(cursor)


LoadDLL.DLL.SDL_GetCursor.restype = ctypes.POINTER(SDL_Cursor)
LoadDLL.DLL.SDL_GetCursor.argtypes = []

def SDL_GetCursor():
	"""
	Args:
		: None.
	Returns:
		res: ctypes.POINTER(SDL_Cursor).
	"""
	return LoadDLL.DLL.SDL_GetCursor()


LoadDLL.DLL.SDL_GetDefaultCursor.restype = ctypes.POINTER(SDL_Cursor)
LoadDLL.DLL.SDL_GetDefaultCursor.argtypes = []

def SDL_GetDefaultCursor():
	"""
	Args:
		: None.
	Returns:
		res: ctypes.POINTER(SDL_Cursor).
	"""
	return LoadDLL.DLL.SDL_GetDefaultCursor()


LoadDLL.DLL.SDL_FreeCursor.restype = None
LoadDLL.DLL.SDL_FreeCursor.argtypes = [ctypes.POINTER(SDL_Cursor)]

def SDL_FreeCursor(cursor):
	"""
	Args:
		cursor: ctypes.POINTER(SDL_Cursor).
	Returns:
		res: None.
	"""
	LoadDLL.DLL.SDL_FreeCursor(cursor)


LoadDLL.DLL.SDL_ShowCursor.restype = ctypes.c_int
LoadDLL.DLL.SDL_ShowCursor.argtypes = [ctypes.c_int]

def SDL_ShowCursor(toggle):
	"""
	Args:
		toggle: ctypes.c_int.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_ShowCursor(toggle)