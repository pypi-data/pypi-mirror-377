import ctypes
from .LoadDLL import LoadDLL


SDL_MAJOR_VERSION = 2

SDL_MINOR_VERSION = 30

SDL_PATCHLEVEL = 11

class SDL_version(ctypes.Structure):
	_fields_ = [
		('major', ctypes.c_ubyte),
		('minor', ctypes.c_ubyte),
		('patch', ctypes.c_ubyte),
	]

LoadDLL.DLL.SDL_GetRevisionNumber.restype = ctypes.c_int
LoadDLL.DLL.SDL_GetRevisionNumber.argtypes = []

def SDL_GetRevisionNumber():
	"""
	Args:
		: None.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_GetRevisionNumber()