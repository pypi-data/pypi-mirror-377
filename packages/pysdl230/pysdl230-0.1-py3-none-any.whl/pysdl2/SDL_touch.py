import ctypes
from .LoadDLL import LoadDLL


class SDL_TouchDeviceType:
	SDL_TOUCH_DEVICE_INVALID = -1
	SDL_TOUCH_DEVICE_DIRECT = 0
	SDL_TOUCH_DEVICE_INDIRECT_ABSOLUTE = 1
	SDL_TOUCH_DEVICE_INDIRECT_RELATIVE = 2

class SDL_Finger(ctypes.Structure):
	_fields_ = [
		('id', ctypes.c_uint64),
		('x', ctypes.c_float),
		('y', ctypes.c_float),
		('pressure', ctypes.c_float),
	]

LoadDLL.DLL.SDL_GetNumTouchDevices.restype = ctypes.c_int
LoadDLL.DLL.SDL_GetNumTouchDevices.argtypes = []

def SDL_GetNumTouchDevices():
	"""
	Args:
		: None.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_GetNumTouchDevices()


LoadDLL.DLL.SDL_GetTouchDevice.restype = ctypes.c_uint64
LoadDLL.DLL.SDL_GetTouchDevice.argtypes = [ctypes.c_int]

def SDL_GetTouchDevice(index):
	"""
	Args:
		index: ctypes.c_int.
	Returns:
		res: ctypes.c_uint64.
	"""
	return LoadDLL.DLL.SDL_GetTouchDevice(index)


LoadDLL.DLL.SDL_GetTouchName.restype = ctypes.c_char_p
LoadDLL.DLL.SDL_GetTouchName.argtypes = [ctypes.c_int]

def SDL_GetTouchName(index):
	"""
	Args:
		index: ctypes.c_int.
	Returns:
		res: ctypes.c_char_p.
	"""
	return LoadDLL.DLL.SDL_GetTouchName(index)


LoadDLL.DLL.SDL_GetTouchDeviceType.restype = ctypes.c_int
LoadDLL.DLL.SDL_GetTouchDeviceType.argtypes = [ctypes.c_uint64]

def SDL_GetTouchDeviceType(touchID):
	"""
	Args:
		touchID: ctypes.c_uint64.
	Returns:
		res: SDL_TouchDeviceType.
	"""
	return LoadDLL.DLL.SDL_GetTouchDeviceType(touchID)


LoadDLL.DLL.SDL_GetNumTouchFingers.restype = ctypes.c_int
LoadDLL.DLL.SDL_GetNumTouchFingers.argtypes = [ctypes.c_uint64]

def SDL_GetNumTouchFingers(touchID):
	"""
	Args:
		touchID: ctypes.c_uint64.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_GetNumTouchFingers(touchID)


LoadDLL.DLL.SDL_GetTouchFinger.restype = ctypes.POINTER(SDL_Finger)
LoadDLL.DLL.SDL_GetTouchFinger.argtypes = [ctypes.c_uint64, ctypes.c_int]

def SDL_GetTouchFinger(touchID, index):
	"""
	Args:
		touchID: ctypes.c_uint64.
		index: ctypes.c_int.
	Returns:
		res: ctypes.POINTER(SDL_Finger).
	"""
	return LoadDLL.DLL.SDL_GetTouchFinger(touchID, index)