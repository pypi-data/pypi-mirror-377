import ctypes
from .LoadDLL import LoadDLL
from .SDL_video import SDL_Window


class SDL_MessageBoxFlags:
	SDL_MESSAGEBOX_ERROR = 0x00000010
	SDL_MESSAGEBOX_WARNING = 0x00000020
	SDL_MESSAGEBOX_INFORMATION = 0x00000040
	SDL_MESSAGEBOX_BUTTONS_LEFT_TO_RIGHT = 0x00000080
	SDL_MESSAGEBOX_BUTTONS_RIGHT_TO_LEFT = 0x00000100


class SDL_MessageBoxButtonFlags:
	SDL_MESSAGEBOX_BUTTON_RETURNKEY_DEFAULT = 0x00000001
	SDL_MESSAGEBOX_BUTTON_ESCAPEKEY_DEFAULT = 0x00000002


class SDL_MessageBoxColorType:
	SDL_MESSAGEBOX_COLOR_BACKGROUND = 0
	SDL_MESSAGEBOX_COLOR_TEXT = 1
	SDL_MESSAGEBOX_COLOR_BUTTON_BORDER = 2
	SDL_MESSAGEBOX_COLOR_BUTTON_BACKGROUND = 3
	SDL_MESSAGEBOX_COLOR_BUTTON_SELECTED = 4
	SDL_MESSAGEBOX_COLOR_MAX = 5


class SDL_MessageBoxButtonData(ctypes.Structure):
	_fields_ = [
		('flags', ctypes.c_uint32),
		('buttonid', ctypes.c_int),
		('text', ctypes.c_char_p),
	]


class SDL_MessageBoxColor(ctypes.Structure):
	_fields_ = [
		('r', ctypes.c_uint8),
		('g', ctypes.c_uint8),
		('b', ctypes.c_uint8),
	]


class SDL_MessageBoxColorScheme(ctypes.Structure):
	_fields_ = [
		('colors', SDL_MessageBoxColor * SDL_MessageBoxColorType.SDL_MESSAGEBOX_COLOR_MAX),
	]


class SDL_MessageBoxData(ctypes.Structure):
	_fields_ = [
		('flags', ctypes.c_uint32),
		('window', ctypes.POINTER(SDL_Window)),
		('title', ctypes.c_char_p),
		('message', ctypes.c_char_p),
		('numbuttons', ctypes.c_int),
		('buttons', ctypes.POINTER(SDL_MessageBoxButtonData)),
		('colorScheme', ctypes.POINTER(SDL_MessageBoxColorScheme)),
	]


LoadDLL.DLL.SDL_ShowMessageBox.restype = ctypes.c_int
LoadDLL.DLL.SDL_ShowMessageBox.argtypes = [ctypes.POINTER(SDL_MessageBoxData), ctypes.POINTER(ctypes.c_int)]

def SDL_ShowMessageBox(messageboxdata, buttonid):
	"""
	Args:
		messageboxdata: ctypes.POINTER(SDL_MessageBoxData).
		buttonid: ctypes.POINTER(ctypes.c_int).
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_ShowMessageBox(messageboxdata, buttonid)


LoadDLL.DLL.SDL_ShowSimpleMessageBox.restype = ctypes.c_int
LoadDLL.DLL.SDL_ShowSimpleMessageBox.argtypes = [ctypes.c_uint, ctypes.c_char_p, ctypes.c_char_p, ctypes.POINTER(SDL_Window)]

def SDL_ShowSimpleMessageBox(flags, title, message, window):
	"""
	Args:
		flags: ctypes.c_uint.
		title: ctypes.c_char_p.
		message: ctypes.c_char_p.
		window: ctypes.POINTER(SDL_Window).
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_ShowSimpleMessageBox(flags, title, message, window)