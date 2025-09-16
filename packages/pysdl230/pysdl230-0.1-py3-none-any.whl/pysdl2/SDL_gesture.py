import ctypes
from .LoadDLL import LoadDLL
from .SDL_rwops import SDL_RWops


LoadDLL.DLL.SDL_RecordGesture.restype = ctypes.c_int
LoadDLL.DLL.SDL_RecordGesture.argtypes = [ctypes.c_int32]

def SDL_RecordGesture(touchId):
	"""
	Args:
		touchId: SDL_TouchID.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_RecordGesture(touchId)


LoadDLL.DLL.SDL_SaveAllDollarTemplates.restype = ctypes.c_int
LoadDLL.DLL.SDL_SaveAllDollarTemplates.argtypes = [ctypes.POINTER(SDL_RWops)]

def SDL_SaveAllDollarTemplates(dst):
	"""
	Args:
		dst: ctypes.POINTER(SDL_RWops).
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_SaveAllDollarTemplates(dst)


LoadDLL.DLL.SDL_SaveDollarTemplate.restype = ctypes.c_int
LoadDLL.DLL.SDL_SaveDollarTemplate.argtypes = [ctypes.c_longlong, ctypes.POINTER(SDL_RWops)]

def SDL_SaveDollarTemplate(gestureId, dst):
	"""
	Args:
		gestureId: ctypes.c_longlong.
		dst: ctypes.POINTER(SDL_RWops).
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_SaveDollarTemplate(gestureId, dst)


LoadDLL.DLL.SDL_LoadDollarTemplates.restype = ctypes.c_int
LoadDLL.DLL.SDL_LoadDollarTemplates.argtypes = [ctypes.c_int32, ctypes.POINTER(SDL_RWops)]

def SDL_LoadDollarTemplates(touchId, src):
	"""
	Args:
		touchId: SDL_TouchID.
		src: ctypes.POINTER(SDL_RWops).
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_LoadDollarTemplates(touchId, src)