import ctypes
from .LoadDLL import LoadDLL


class SDL_GUID(ctypes.Structure):
    _fields_ = [
        ('data', ctypes.c_uint8 * 16),
    ]


LoadDLL.DLL.SDL_GUIDToString.restype = None
LoadDLL.DLL.SDL_GUIDToString.argtypes = [SDL_GUID, ctypes.c_char_p, ctypes.c_int]

def SDL_GUIDToString(guid, pszGUID, cbGUID):
	"""
	Args:
		guid: SDL_GUID.
		pszGUID: ctypes.c_char_p.
		cbGUID: ctypes.c_int.
	Returns:
		res: None.
	"""
	LoadDLL.DLL.SDL_GUIDToString(guid, pszGUID, cbGUID)


LoadDLL.DLL.SDL_GUIDFromString.restype = SDL_GUID
LoadDLL.DLL.SDL_GUIDFromString.argtypes = [ctypes.c_char_p]

def SDL_GUIDFromString(pchGUID):
	"""
	Args:
		pchGUID: ctypes.c_char_p.
	Returns:
		res: SDL_GUID.
	"""
	return LoadDLL.DLL.SDL_GUIDFromString(pchGUID)