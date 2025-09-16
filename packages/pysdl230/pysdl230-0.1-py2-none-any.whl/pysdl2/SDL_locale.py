import ctypes
from .LoadDLL import LoadDLL


class SDL_Locale(ctypes.Structure):
	_fields_ = [
		('language', ctypes.c_char_p),
		('country', ctypes.c_char_p),
	]


LoadDLL.DLL.SDL_GetPreferredLocales.restype = ctypes.POINTER(SDL_Locale)
LoadDLL.DLL.SDL_GetPreferredLocales.argtypes = []

def SDL_GetPreferredLocales():
	"""
	Args:
		: None.
	Returns:
		res: ctypes.POINTER(SDL_Locale).
	"""
	return LoadDLL.DLL.SDL_GetPreferredLocales()