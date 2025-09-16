import ctypes
from .LoadDLL import LoadDLL


LoadDLL.DLL.SDL_SetClipboardText.restype = ctypes.c_int
LoadDLL.DLL.SDL_SetClipboardText.argtypes = [ctypes.c_char_p]

def SDL_SetClipboardText(text):
	"""
	Args:
		text: ctypes.c_char_p.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_SetClipboardText(text)


LoadDLL.DLL.SDL_GetClipboardText.restype = ctypes.c_char_p
LoadDLL.DLL.SDL_GetClipboardText.argtypes = []

def SDL_GetClipboardText():
	"""
	Args:
		: None.
	Returns:
		res: ctypes.c_char_p.
	"""
	return LoadDLL.DLL.SDL_GetClipboardText()


LoadDLL.DLL.SDL_HasClipboardText.restype = ctypes.c_int
LoadDLL.DLL.SDL_HasClipboardText.argtypes = []

def SDL_HasClipboardText():
	"""
	Args:
		: None.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_HasClipboardText()


LoadDLL.DLL.SDL_SetPrimarySelectionText.restype = ctypes.c_int
LoadDLL.DLL.SDL_SetPrimarySelectionText.argtypes = [ctypes.c_char_p]

def SDL_SetPrimarySelectionText(text):
	"""
	Args:
		text: ctypes.c_char_p.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_SetPrimarySelectionText(text)


LoadDLL.DLL.SDL_GetPrimarySelectionText.restype = ctypes.c_char_p
LoadDLL.DLL.SDL_GetPrimarySelectionText.argtypes = []

def SDL_GetPrimarySelectionText():
	"""
	Args:
		: None.
	Returns:
		res: ctypes.c_char_p.
	"""
	return LoadDLL.DLL.SDL_GetPrimarySelectionText()


LoadDLL.DLL.SDL_HasPrimarySelectionText.restype = ctypes.c_int
LoadDLL.DLL.SDL_HasPrimarySelectionText.argtypes = []

def SDL_HasPrimarySelectionText():
	"""
	Args:
		: None.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_HasPrimarySelectionText()