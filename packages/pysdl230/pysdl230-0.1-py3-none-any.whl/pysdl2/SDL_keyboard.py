import ctypes
from .LoadDLL import LoadDLL
from .SDL_rect import SDL_Rect
from .SDL_video import SDL_Window


class SDL_Keysym(ctypes.Structure):
	_fields_ = [
		('scancode', ctypes.c_int),
		('sym', ctypes.c_int32),
		('mod', ctypes.c_ushort),
		('unused', ctypes.c_uint),
	]

LoadDLL.DLL.SDL_GetKeyboardFocus.restype = ctypes.POINTER(SDL_Window)
LoadDLL.DLL.SDL_GetKeyboardFocus.argtypes = []

def SDL_GetKeyboardFocus():
	"""
	Args:
		: None.
	Returns:
		res: ctypes.POINTER(SDL_Window).
	"""
	return LoadDLL.DLL.SDL_GetKeyboardFocus()


LoadDLL.DLL.SDL_GetKeyboardState.restype = ctypes.POINTER(ctypes.c_ubyte)
LoadDLL.DLL.SDL_GetKeyboardState.argtypes = [ctypes.POINTER(ctypes.c_int)]

def SDL_GetKeyboardState(numkeys):
	"""
	Args:
		numkeys: ctypes.POINTER(ctypes.c_int).
	Returns:
		res: ctypes.POINTER(ctypes.c_ubyte).
	"""
	return LoadDLL.DLL.SDL_GetKeyboardState(numkeys)


LoadDLL.DLL.SDL_ResetKeyboard.restype = None
LoadDLL.DLL.SDL_ResetKeyboard.argtypes = []

def SDL_ResetKeyboard():
	"""
	Args:
		: None.
	Returns:
		res: None.
	"""
	LoadDLL.DLL.SDL_ResetKeyboard()


LoadDLL.DLL.SDL_GetModState.restype = ctypes.c_int
LoadDLL.DLL.SDL_GetModState.argtypes = []

def SDL_GetModState():
	"""
	Args:
		: None.
	Returns:
		res: SDL_Keymod.
	"""
	return LoadDLL.DLL.SDL_GetModState()


LoadDLL.DLL.SDL_SetModState.restype = None
LoadDLL.DLL.SDL_SetModState.argtypes = [ctypes.c_int]

def SDL_SetModState(modstate):
	"""
	Args:
		modstate: SDL_Keymod.
	Returns:
		res: None.
	"""
	LoadDLL.DLL.SDL_SetModState(modstate)


LoadDLL.DLL.SDL_GetKeyFromScancode.restype = ctypes.c_int32
LoadDLL.DLL.SDL_GetKeyFromScancode.argtypes = [ctypes.c_int]

def SDL_GetKeyFromScancode(scancode):
	"""
	Args:
		scancode: SDL_Scancode.
	Returns:
		res: ctypes.c_int32.
	"""
	return LoadDLL.DLL.SDL_GetKeyFromScancode(scancode)


LoadDLL.DLL.SDL_GetScancodeFromKey.restype = ctypes.c_int
LoadDLL.DLL.SDL_GetScancodeFromKey.argtypes = [ctypes.c_int32]

def SDL_GetScancodeFromKey(key):
	"""
	Args:
		key: ctypes.c_int32.
	Returns:
		res: SDL_Scancode.
	"""
	return LoadDLL.DLL.SDL_GetScancodeFromKey(key)


LoadDLL.DLL.SDL_GetScancodeName.restype = ctypes.c_char_p
LoadDLL.DLL.SDL_GetScancodeName.argtypes = [ctypes.c_int]

def SDL_GetScancodeName(scancode):
	"""
	Args:
		scancode: SDL_Scancode.
	Returns:
		res: ctypes.c_char_p.
	"""
	return LoadDLL.DLL.SDL_GetScancodeName(scancode)


LoadDLL.DLL.SDL_GetScancodeFromName.restype = ctypes.c_int
LoadDLL.DLL.SDL_GetScancodeFromName.argtypes = [ctypes.c_char_p]

def SDL_GetScancodeFromName(name):
	"""
	Args:
		name: ctypes.c_char_p.
	Returns:
		res: SDL_Scancode.
	"""
	return LoadDLL.DLL.SDL_GetScancodeFromName(name)


LoadDLL.DLL.SDL_GetKeyName.restype = ctypes.c_char_p
LoadDLL.DLL.SDL_GetKeyName.argtypes = [ctypes.c_int32]

def SDL_GetKeyName(key):
	"""
	Args:
		key: ctypes.c_int32.
	Returns:
		res: ctypes.c_char_p.
	"""
	return LoadDLL.DLL.SDL_GetKeyName(key)


LoadDLL.DLL.SDL_GetKeyFromName.restype = ctypes.c_int32
LoadDLL.DLL.SDL_GetKeyFromName.argtypes = [ctypes.c_char_p]

def SDL_GetKeyFromName(name):
	"""
	Args:
		name: ctypes.c_char_p.
	Returns:
		res: ctypes.c_int32.
	"""
	return LoadDLL.DLL.SDL_GetKeyFromName(name)


LoadDLL.DLL.SDL_StartTextInput.restype = None
LoadDLL.DLL.SDL_StartTextInput.argtypes = []

def SDL_StartTextInput():
	"""
	Args:
		: None.
	Returns:
		res: None.
	"""
	LoadDLL.DLL.SDL_StartTextInput()


LoadDLL.DLL.SDL_IsTextInputActive.restype = ctypes.c_int
LoadDLL.DLL.SDL_IsTextInputActive.argtypes = []

def SDL_IsTextInputActive():
	"""
	Args:
		: None.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_IsTextInputActive()


LoadDLL.DLL.SDL_StopTextInput.restype = None
LoadDLL.DLL.SDL_StopTextInput.argtypes = []

def SDL_StopTextInput():
	"""
	Args:
		: None.
	Returns:
		res: None.
	"""
	LoadDLL.DLL.SDL_StopTextInput()


LoadDLL.DLL.SDL_ClearComposition.restype = None
LoadDLL.DLL.SDL_ClearComposition.argtypes = []

def SDL_ClearComposition():
	"""
	Args:
		: None.
	Returns:
		res: None.
	"""
	LoadDLL.DLL.SDL_ClearComposition()


LoadDLL.DLL.SDL_IsTextInputShown.restype = ctypes.c_int
LoadDLL.DLL.SDL_IsTextInputShown.argtypes = []

def SDL_IsTextInputShown():
	"""
	Args:
		: None.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_IsTextInputShown()


LoadDLL.DLL.SDL_SetTextInputRect.restype = None
LoadDLL.DLL.SDL_SetTextInputRect.argtypes = [ctypes.POINTER(SDL_Rect)]

def SDL_SetTextInputRect(rect):
	"""
	Args:
		rect: ctypes.POINTER(SDL_Rect).
	Returns:
		res: None.
	"""
	LoadDLL.DLL.SDL_SetTextInputRect(rect)


LoadDLL.DLL.SDL_HasScreenKeyboardSupport.restype = ctypes.c_int
LoadDLL.DLL.SDL_HasScreenKeyboardSupport.argtypes = []

def SDL_HasScreenKeyboardSupport():
	"""
	Args:
		: None.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_HasScreenKeyboardSupport()


LoadDLL.DLL.SDL_IsScreenKeyboardShown.restype = ctypes.c_int
LoadDLL.DLL.SDL_IsScreenKeyboardShown.argtypes = [ctypes.POINTER(SDL_Window)]

def SDL_IsScreenKeyboardShown(window):
	"""
	Args:
		window: ctypes.POINTER(SDL_Window).
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_IsScreenKeyboardShown(window)