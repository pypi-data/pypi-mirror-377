import ctypes
from .LoadDLL import LoadDLL


SDL_VIRTUAL_JOYSTICK_DESC_VERSION = 1

SDL_JOYSTICK_AXIS_MAX = 32767

SDL_JOYSTICK_AXIS_MIN = -32768

SDL_HAT_CENTERED = 0x00

SDL_HAT_UP = 0x01

SDL_HAT_RIGHT = 0x02

SDL_HAT_DOWN = 0x04

SDL_HAT_LEFT = 0x08

class SDL_JoystickType:
	SDL_JOYSTICK_TYPE_UNKNOWN = 0
	SDL_JOYSTICK_TYPE_GAMECONTROLLER = 1
	SDL_JOYSTICK_TYPE_WHEEL = 2
	SDL_JOYSTICK_TYPE_ARCADE_STICK = 3
	SDL_JOYSTICK_TYPE_FLIGHT_STICK = 4
	SDL_JOYSTICK_TYPE_DANCE_PAD = 5
	SDL_JOYSTICK_TYPE_GUITAR = 6
	SDL_JOYSTICK_TYPE_DRUM_KIT = 7
	SDL_JOYSTICK_TYPE_ARCADE_PAD = 8
	SDL_JOYSTICK_TYPE_THROTTLE = 9


class SDL_JoystickPowerLevel:
	SDL_JOYSTICK_POWER_UNKNOWN = -1
	SDL_JOYSTICK_POWER_EMPTY = 0
	SDL_JOYSTICK_POWER_LOW = 1
	SDL_JOYSTICK_POWER_MEDIUM = 2
	SDL_JOYSTICK_POWER_FULL = 3
	SDL_JOYSTICK_POWER_WIRED = 4
	SDL_JOYSTICK_POWER_MAX = 5


class SDL_Joystick(ctypes.Structure): pass


class SDL_VirtualJoystickDesc(ctypes.Structure): pass


class SDL_JoystickGUID(ctypes.Structure):
    _fields_ = [
        ('data', ctypes.c_uint8 * 16),
    ]


LoadDLL.DLL.SDL_LockJoysticks.restype = None
LoadDLL.DLL.SDL_LockJoysticks.argtypes = []

def SDL_LockJoysticks():
	"""
	Args:
		: None.
	Returns:
		res: None.
	"""
	LoadDLL.DLL.SDL_LockJoysticks()


LoadDLL.DLL.SDL_UnlockJoysticks.restype = None
LoadDLL.DLL.SDL_UnlockJoysticks.argtypes = []

def SDL_UnlockJoysticks():
	"""
	Args:
		: None.
	Returns:
		res: None.
	"""
	LoadDLL.DLL.SDL_UnlockJoysticks()


LoadDLL.DLL.SDL_NumJoysticks.restype = ctypes.c_int
LoadDLL.DLL.SDL_NumJoysticks.argtypes = []

def SDL_NumJoysticks():
	"""
	Args:
		: None.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_NumJoysticks()


LoadDLL.DLL.SDL_JoystickNameForIndex.restype = ctypes.c_char_p
LoadDLL.DLL.SDL_JoystickNameForIndex.argtypes = [ctypes.c_int]

def SDL_JoystickNameForIndex(device_index):
	"""
	Args:
		device_index: ctypes.c_int.
	Returns:
		res: ctypes.c_char_p.
	"""
	return LoadDLL.DLL.SDL_JoystickNameForIndex(device_index)


LoadDLL.DLL.SDL_JoystickPathForIndex.restype = ctypes.c_char_p
LoadDLL.DLL.SDL_JoystickPathForIndex.argtypes = [ctypes.c_int]

def SDL_JoystickPathForIndex(device_index):
	"""
	Args:
		device_index: ctypes.c_int.
	Returns:
		res: ctypes.c_char_p.
	"""
	return LoadDLL.DLL.SDL_JoystickPathForIndex(device_index)


LoadDLL.DLL.SDL_JoystickGetDevicePlayerIndex.restype = ctypes.c_int
LoadDLL.DLL.SDL_JoystickGetDevicePlayerIndex.argtypes = [ctypes.c_int]

def SDL_JoystickGetDevicePlayerIndex(device_index):
	"""
	Args:
		device_index: ctypes.c_int.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_JoystickGetDevicePlayerIndex(device_index)


LoadDLL.DLL.SDL_JoystickGetDeviceGUID.restype = SDL_JoystickGUID
LoadDLL.DLL.SDL_JoystickGetDeviceGUID.argtypes = [ctypes.c_int]

def SDL_JoystickGetDeviceGUID(device_index):
	"""
	Args:
		device_index: ctypes.c_int.
	Returns:
		res: SDL_JoystickGUID.
	"""
	return LoadDLL.DLL.SDL_JoystickGetDeviceGUID(device_index)


LoadDLL.DLL.SDL_JoystickGetDeviceVendor.restype = ctypes.c_ushort
LoadDLL.DLL.SDL_JoystickGetDeviceVendor.argtypes = [ctypes.c_int]

def SDL_JoystickGetDeviceVendor(device_index):
	"""
	Args:
		device_index: ctypes.c_int.
	Returns:
		res: ctypes.c_ushort.
	"""
	return LoadDLL.DLL.SDL_JoystickGetDeviceVendor(device_index)


LoadDLL.DLL.SDL_JoystickGetDeviceProduct.restype = ctypes.c_ushort
LoadDLL.DLL.SDL_JoystickGetDeviceProduct.argtypes = [ctypes.c_int]

def SDL_JoystickGetDeviceProduct(device_index):
	"""
	Args:
		device_index: ctypes.c_int.
	Returns:
		res: ctypes.c_ushort.
	"""
	return LoadDLL.DLL.SDL_JoystickGetDeviceProduct(device_index)


LoadDLL.DLL.SDL_JoystickGetDeviceProductVersion.restype = ctypes.c_ushort
LoadDLL.DLL.SDL_JoystickGetDeviceProductVersion.argtypes = [ctypes.c_int]

def SDL_JoystickGetDeviceProductVersion(device_index):
	"""
	Args:
		device_index: ctypes.c_int.
	Returns:
		res: ctypes.c_ushort.
	"""
	return LoadDLL.DLL.SDL_JoystickGetDeviceProductVersion(device_index)


LoadDLL.DLL.SDL_JoystickGetDeviceType.restype = ctypes.c_int
LoadDLL.DLL.SDL_JoystickGetDeviceType.argtypes = [ctypes.c_int]

def SDL_JoystickGetDeviceType(device_index):
	"""
	Args:
		device_index: ctypes.c_int.
	Returns:
		res: SDL_JoystickType.
	"""
	return LoadDLL.DLL.SDL_JoystickGetDeviceType(device_index)


LoadDLL.DLL.SDL_JoystickGetDeviceInstanceID.restype = ctypes.c_int32
LoadDLL.DLL.SDL_JoystickGetDeviceInstanceID.argtypes = [ctypes.c_int]

def SDL_JoystickGetDeviceInstanceID(device_index):
	"""
	Args:
		device_index: ctypes.c_int.
	Returns:
		res: ctypes.c_int32.
	"""
	return LoadDLL.DLL.SDL_JoystickGetDeviceInstanceID(device_index)


LoadDLL.DLL.SDL_JoystickOpen.restype = ctypes.POINTER(SDL_Joystick)
LoadDLL.DLL.SDL_JoystickOpen.argtypes = [ctypes.c_int]

def SDL_JoystickOpen(device_index):
	"""
	Args:
		device_index: ctypes.c_int.
	Returns:
		res: ctypes.POINTER(SDL_Joystick).
	"""
	return LoadDLL.DLL.SDL_JoystickOpen(device_index)


LoadDLL.DLL.SDL_JoystickFromInstanceID.restype = ctypes.POINTER(SDL_Joystick)
LoadDLL.DLL.SDL_JoystickFromInstanceID.argtypes = [ctypes.c_int32]

def SDL_JoystickFromInstanceID(instance_id):
	"""
	Args:
		instance_id: ctypes.c_int32.
	Returns:
		res: ctypes.POINTER(SDL_Joystick).
	"""
	return LoadDLL.DLL.SDL_JoystickFromInstanceID(instance_id)


LoadDLL.DLL.SDL_JoystickFromPlayerIndex.restype = ctypes.POINTER(SDL_Joystick)
LoadDLL.DLL.SDL_JoystickFromPlayerIndex.argtypes = [ctypes.c_int]

def SDL_JoystickFromPlayerIndex(player_index):
	"""
	Args:
		player_index: ctypes.c_int.
	Returns:
		res: ctypes.POINTER(SDL_Joystick).
	"""
	return LoadDLL.DLL.SDL_JoystickFromPlayerIndex(player_index)


LoadDLL.DLL.SDL_JoystickAttachVirtual.restype = ctypes.c_int
LoadDLL.DLL.SDL_JoystickAttachVirtual.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]

def SDL_JoystickAttachVirtual(type, naxes, nbuttons, nhats):
	"""
	Args:
		type: SDL_JoystickType.
		naxes: ctypes.c_int.
		nbuttons: ctypes.c_int.
		nhats: ctypes.c_int.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_JoystickAttachVirtual(type, naxes, nbuttons, nhats)


LoadDLL.DLL.SDL_JoystickAttachVirtualEx.restype = ctypes.c_int
LoadDLL.DLL.SDL_JoystickAttachVirtualEx.argtypes = [ctypes.POINTER(SDL_VirtualJoystickDesc)]

def SDL_JoystickAttachVirtualEx(desc):
	"""
	Args:
		desc: ctypes.POINTER(SDL_VirtualJoystickDesc).
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_JoystickAttachVirtualEx(desc)


LoadDLL.DLL.SDL_JoystickDetachVirtual.restype = ctypes.c_int
LoadDLL.DLL.SDL_JoystickDetachVirtual.argtypes = [ctypes.c_int]

def SDL_JoystickDetachVirtual(device_index):
	"""
	Args:
		device_index: ctypes.c_int.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_JoystickDetachVirtual(device_index)


LoadDLL.DLL.SDL_JoystickIsVirtual.restype = ctypes.c_int
LoadDLL.DLL.SDL_JoystickIsVirtual.argtypes = [ctypes.c_int]

def SDL_JoystickIsVirtual(device_index):
	"""
	Args:
		device_index: ctypes.c_int.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_JoystickIsVirtual(device_index)


LoadDLL.DLL.SDL_JoystickSetVirtualAxis.restype = ctypes.c_int
LoadDLL.DLL.SDL_JoystickSetVirtualAxis.argtypes = [ctypes.POINTER(SDL_Joystick), ctypes.c_int, ctypes.c_int16]

def SDL_JoystickSetVirtualAxis(joystick, axis, value):
	"""
	Args:
		joystick: ctypes.POINTER(SDL_Joystick).
		axis: ctypes.c_int.
		value: ctypes.c_int16.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_JoystickSetVirtualAxis(joystick, axis, value)


LoadDLL.DLL.SDL_JoystickSetVirtualButton.restype = ctypes.c_int
LoadDLL.DLL.SDL_JoystickSetVirtualButton.argtypes = [ctypes.POINTER(SDL_Joystick), ctypes.c_int, ctypes.c_ubyte]

def SDL_JoystickSetVirtualButton(joystick, button, value):
	"""
	Args:
		joystick: ctypes.POINTER(SDL_Joystick).
		button: ctypes.c_int.
		value: ctypes.c_ubyte.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_JoystickSetVirtualButton(joystick, button, value)


LoadDLL.DLL.SDL_JoystickSetVirtualHat.restype = ctypes.c_int
LoadDLL.DLL.SDL_JoystickSetVirtualHat.argtypes = [ctypes.POINTER(SDL_Joystick), ctypes.c_int, ctypes.c_ubyte]

def SDL_JoystickSetVirtualHat(joystick, hat, value):
	"""
	Args:
		joystick: ctypes.POINTER(SDL_Joystick).
		hat: ctypes.c_int.
		value: ctypes.c_ubyte.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_JoystickSetVirtualHat(joystick, hat, value)


LoadDLL.DLL.SDL_JoystickName.restype = ctypes.c_char_p
LoadDLL.DLL.SDL_JoystickName.argtypes = [ctypes.POINTER(SDL_Joystick)]

def SDL_JoystickName(joystick):
	"""
	Args:
		joystick: ctypes.POINTER(SDL_Joystick).
	Returns:
		res: ctypes.c_char_p.
	"""
	return LoadDLL.DLL.SDL_JoystickName(joystick)


LoadDLL.DLL.SDL_JoystickPath.restype = ctypes.c_char_p
LoadDLL.DLL.SDL_JoystickPath.argtypes = [ctypes.POINTER(SDL_Joystick)]

def SDL_JoystickPath(joystick):
	"""
	Args:
		joystick: ctypes.POINTER(SDL_Joystick).
	Returns:
		res: ctypes.c_char_p.
	"""
	return LoadDLL.DLL.SDL_JoystickPath(joystick)


LoadDLL.DLL.SDL_JoystickGetPlayerIndex.restype = ctypes.c_int
LoadDLL.DLL.SDL_JoystickGetPlayerIndex.argtypes = [ctypes.POINTER(SDL_Joystick)]

def SDL_JoystickGetPlayerIndex(joystick):
	"""
	Args:
		joystick: ctypes.POINTER(SDL_Joystick).
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_JoystickGetPlayerIndex(joystick)


LoadDLL.DLL.SDL_JoystickSetPlayerIndex.restype = None
LoadDLL.DLL.SDL_JoystickSetPlayerIndex.argtypes = [ctypes.POINTER(SDL_Joystick), ctypes.c_int]

def SDL_JoystickSetPlayerIndex(joystick, player_index):
	"""
	Args:
		joystick: ctypes.POINTER(SDL_Joystick).
		player_index: ctypes.c_int.
	Returns:
		res: None.
	"""
	LoadDLL.DLL.SDL_JoystickSetPlayerIndex(joystick, player_index)


LoadDLL.DLL.SDL_JoystickGetGUID.restype = SDL_JoystickGUID
LoadDLL.DLL.SDL_JoystickGetGUID.argtypes = [ctypes.POINTER(SDL_Joystick)]

def SDL_JoystickGetGUID(joystick):
	"""
	Args:
		joystick: ctypes.POINTER(SDL_Joystick).
	Returns:
		res: SDL_JoystickGUID.
	"""
	return LoadDLL.DLL.SDL_JoystickGetGUID(joystick)


LoadDLL.DLL.SDL_JoystickGetVendor.restype = ctypes.c_ushort
LoadDLL.DLL.SDL_JoystickGetVendor.argtypes = [ctypes.POINTER(SDL_Joystick)]

def SDL_JoystickGetVendor(joystick):
	"""
	Args:
		joystick: ctypes.POINTER(SDL_Joystick).
	Returns:
		res: ctypes.c_ushort.
	"""
	return LoadDLL.DLL.SDL_JoystickGetVendor(joystick)


LoadDLL.DLL.SDL_JoystickGetProduct.restype = ctypes.c_ushort
LoadDLL.DLL.SDL_JoystickGetProduct.argtypes = [ctypes.POINTER(SDL_Joystick)]

def SDL_JoystickGetProduct(joystick):
	"""
	Args:
		joystick: ctypes.POINTER(SDL_Joystick).
	Returns:
		res: ctypes.c_ushort.
	"""
	return LoadDLL.DLL.SDL_JoystickGetProduct(joystick)


LoadDLL.DLL.SDL_JoystickGetProductVersion.restype = ctypes.c_ushort
LoadDLL.DLL.SDL_JoystickGetProductVersion.argtypes = [ctypes.POINTER(SDL_Joystick)]

def SDL_JoystickGetProductVersion(joystick):
	"""
	Args:
		joystick: ctypes.POINTER(SDL_Joystick).
	Returns:
		res: ctypes.c_ushort.
	"""
	return LoadDLL.DLL.SDL_JoystickGetProductVersion(joystick)


LoadDLL.DLL.SDL_JoystickGetFirmwareVersion.restype = ctypes.c_ushort
LoadDLL.DLL.SDL_JoystickGetFirmwareVersion.argtypes = [ctypes.POINTER(SDL_Joystick)]

def SDL_JoystickGetFirmwareVersion(joystick):
	"""
	Args:
		joystick: ctypes.POINTER(SDL_Joystick).
	Returns:
		res: ctypes.c_ushort.
	"""
	return LoadDLL.DLL.SDL_JoystickGetFirmwareVersion(joystick)


LoadDLL.DLL.SDL_JoystickGetSerial.restype = ctypes.c_char_p
LoadDLL.DLL.SDL_JoystickGetSerial.argtypes = [ctypes.POINTER(SDL_Joystick)]

def SDL_JoystickGetSerial(joystick):
	"""
	Args:
		joystick: ctypes.POINTER(SDL_Joystick).
	Returns:
		res: ctypes.c_char_p.
	"""
	return LoadDLL.DLL.SDL_JoystickGetSerial(joystick)


LoadDLL.DLL.SDL_JoystickGetType.restype = ctypes.c_int
LoadDLL.DLL.SDL_JoystickGetType.argtypes = [ctypes.POINTER(SDL_Joystick)]

def SDL_JoystickGetType(joystick):
	"""
	Args:
		joystick: ctypes.POINTER(SDL_Joystick).
	Returns:
		res: SDL_JoystickType.
	"""
	return LoadDLL.DLL.SDL_JoystickGetType(joystick)


LoadDLL.DLL.SDL_JoystickGetGUIDString.restype = None
LoadDLL.DLL.SDL_JoystickGetGUIDString.argtypes = [SDL_JoystickGUID, ctypes.c_char_p, ctypes.c_int]

def SDL_JoystickGetGUIDString(guid, pszGUID, cbGUID):
	"""
	Args:
		guid: SDL_JoystickGUID.
		pszGUID: ctypes.c_char_p.
		cbGUID: ctypes.c_int.
	Returns:
		res: None.
	"""
	LoadDLL.DLL.SDL_JoystickGetGUIDString(guid, pszGUID, cbGUID)


LoadDLL.DLL.SDL_JoystickGetGUIDFromString.restype = SDL_JoystickGUID
LoadDLL.DLL.SDL_JoystickGetGUIDFromString.argtypes = [ctypes.c_char_p]

def SDL_JoystickGetGUIDFromString(pchGUID):
	"""
	Args:
		pchGUID: ctypes.c_char_p.
	Returns:
		res: SDL_JoystickGUID.
	"""
	return LoadDLL.DLL.SDL_JoystickGetGUIDFromString(pchGUID)


LoadDLL.DLL.SDL_GetJoystickGUIDInfo.restype = None
LoadDLL.DLL.SDL_GetJoystickGUIDInfo.argtypes = [SDL_JoystickGUID, ctypes.POINTER(ctypes.c_ushort), ctypes.POINTER(ctypes.c_ushort), ctypes.POINTER(ctypes.c_ushort), ctypes.POINTER(ctypes.c_ushort)]

def SDL_GetJoystickGUIDInfo(guid, vendor, product, version, crc16):
	"""
	Args:
		guid: SDL_JoystickGUID.
		vendor: ctypes.POINTER(ctypes.c_ushort).
		product: ctypes.POINTER(ctypes.c_ushort).
		version: ctypes.POINTER(ctypes.c_ushort).
		crc16: ctypes.POINTER(ctypes.c_ushort).
	Returns:
		res: None.
	"""
	LoadDLL.DLL.SDL_GetJoystickGUIDInfo(guid, vendor, product, version, crc16)


LoadDLL.DLL.SDL_JoystickGetAttached.restype = ctypes.c_int
LoadDLL.DLL.SDL_JoystickGetAttached.argtypes = [ctypes.POINTER(SDL_Joystick)]

def SDL_JoystickGetAttached(joystick):
	"""
	Args:
		joystick: ctypes.POINTER(SDL_Joystick).
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_JoystickGetAttached(joystick)


LoadDLL.DLL.SDL_JoystickInstanceID.restype = ctypes.c_int32
LoadDLL.DLL.SDL_JoystickInstanceID.argtypes = [ctypes.POINTER(SDL_Joystick)]

def SDL_JoystickInstanceID(joystick):
	"""
	Args:
		joystick: ctypes.POINTER(SDL_Joystick).
	Returns:
		res: ctypes.c_int32.
	"""
	return LoadDLL.DLL.SDL_JoystickInstanceID(joystick)


LoadDLL.DLL.SDL_JoystickNumAxes.restype = ctypes.c_int
LoadDLL.DLL.SDL_JoystickNumAxes.argtypes = [ctypes.POINTER(SDL_Joystick)]

def SDL_JoystickNumAxes(joystick):
	"""
	Args:
		joystick: ctypes.POINTER(SDL_Joystick).
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_JoystickNumAxes(joystick)


LoadDLL.DLL.SDL_JoystickNumBalls.restype = ctypes.c_int
LoadDLL.DLL.SDL_JoystickNumBalls.argtypes = [ctypes.POINTER(SDL_Joystick)]

def SDL_JoystickNumBalls(joystick):
	"""
	Args:
		joystick: ctypes.POINTER(SDL_Joystick).
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_JoystickNumBalls(joystick)


LoadDLL.DLL.SDL_JoystickNumHats.restype = ctypes.c_int
LoadDLL.DLL.SDL_JoystickNumHats.argtypes = [ctypes.POINTER(SDL_Joystick)]

def SDL_JoystickNumHats(joystick):
	"""
	Args:
		joystick: ctypes.POINTER(SDL_Joystick).
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_JoystickNumHats(joystick)


LoadDLL.DLL.SDL_JoystickNumButtons.restype = ctypes.c_int
LoadDLL.DLL.SDL_JoystickNumButtons.argtypes = [ctypes.POINTER(SDL_Joystick)]

def SDL_JoystickNumButtons(joystick):
	"""
	Args:
		joystick: ctypes.POINTER(SDL_Joystick).
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_JoystickNumButtons(joystick)


LoadDLL.DLL.SDL_JoystickUpdate.restype = None
LoadDLL.DLL.SDL_JoystickUpdate.argtypes = []

def SDL_JoystickUpdate():
	"""
	Args:
		: None.
	Returns:
		res: None.
	"""
	LoadDLL.DLL.SDL_JoystickUpdate()


LoadDLL.DLL.SDL_JoystickEventState.restype = ctypes.c_int
LoadDLL.DLL.SDL_JoystickEventState.argtypes = [ctypes.c_int]

def SDL_JoystickEventState(state):
	"""
	Args:
		state: ctypes.c_int.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_JoystickEventState(state)


LoadDLL.DLL.SDL_JoystickGetAxis.restype = ctypes.c_int16
LoadDLL.DLL.SDL_JoystickGetAxis.argtypes = [ctypes.POINTER(SDL_Joystick), ctypes.c_int]

def SDL_JoystickGetAxis(joystick, axis):
	"""
	Args:
		joystick: ctypes.POINTER(SDL_Joystick).
		axis: ctypes.c_int.
	Returns:
		res: ctypes.c_int16.
	"""
	return LoadDLL.DLL.SDL_JoystickGetAxis(joystick, axis)


LoadDLL.DLL.SDL_JoystickGetHat.restype = ctypes.c_ubyte
LoadDLL.DLL.SDL_JoystickGetHat.argtypes = [ctypes.POINTER(SDL_Joystick), ctypes.c_int]

def SDL_JoystickGetHat(joystick, hat):
	"""
	Args:
		joystick: ctypes.POINTER(SDL_Joystick).
		hat: ctypes.c_int.
	Returns:
		res: ctypes.c_ubyte.
	"""
	return LoadDLL.DLL.SDL_JoystickGetHat(joystick, hat)


LoadDLL.DLL.SDL_JoystickGetButton.restype = ctypes.c_ubyte
LoadDLL.DLL.SDL_JoystickGetButton.argtypes = [ctypes.POINTER(SDL_Joystick), ctypes.c_int]

def SDL_JoystickGetButton(joystick, button):
	"""
	Args:
		joystick: ctypes.POINTER(SDL_Joystick).
		button: ctypes.c_int.
	Returns:
		res: ctypes.c_ubyte.
	"""
	return LoadDLL.DLL.SDL_JoystickGetButton(joystick, button)


LoadDLL.DLL.SDL_JoystickRumbleTriggers.restype = ctypes.c_int
LoadDLL.DLL.SDL_JoystickRumbleTriggers.argtypes = [ctypes.POINTER(SDL_Joystick), ctypes.c_ushort, ctypes.c_ushort, ctypes.c_uint]

def SDL_JoystickRumbleTriggers(joystick, left_rumble, right_rumble, duration_ms):
	"""
	Args:
		joystick: ctypes.POINTER(SDL_Joystick).
		left_rumble: ctypes.c_ushort.
		right_rumble: ctypes.c_ushort.
		duration_ms: ctypes.c_uint.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_JoystickRumbleTriggers(joystick, left_rumble, right_rumble, duration_ms)


LoadDLL.DLL.SDL_JoystickHasLED.restype = ctypes.c_int
LoadDLL.DLL.SDL_JoystickHasLED.argtypes = [ctypes.POINTER(SDL_Joystick)]

def SDL_JoystickHasLED(joystick):
	"""
	Args:
		joystick: ctypes.POINTER(SDL_Joystick).
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_JoystickHasLED(joystick)


LoadDLL.DLL.SDL_JoystickHasRumble.restype = ctypes.c_int
LoadDLL.DLL.SDL_JoystickHasRumble.argtypes = [ctypes.POINTER(SDL_Joystick)]

def SDL_JoystickHasRumble(joystick):
	"""
	Args:
		joystick: ctypes.POINTER(SDL_Joystick).
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_JoystickHasRumble(joystick)


LoadDLL.DLL.SDL_JoystickHasRumbleTriggers.restype = ctypes.c_int
LoadDLL.DLL.SDL_JoystickHasRumbleTriggers.argtypes = [ctypes.POINTER(SDL_Joystick)]

def SDL_JoystickHasRumbleTriggers(joystick):
	"""
	Args:
		joystick: ctypes.POINTER(SDL_Joystick).
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_JoystickHasRumbleTriggers(joystick)


LoadDLL.DLL.SDL_JoystickSetLED.restype = ctypes.c_int
LoadDLL.DLL.SDL_JoystickSetLED.argtypes = [ctypes.POINTER(SDL_Joystick), ctypes.c_ubyte, ctypes.c_ubyte, ctypes.c_ubyte]

def SDL_JoystickSetLED(joystick, red, green, blue):
	"""
	Args:
		joystick: ctypes.POINTER(SDL_Joystick).
		red: ctypes.c_ubyte.
		green: ctypes.c_ubyte.
		blue: ctypes.c_ubyte.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_JoystickSetLED(joystick, red, green, blue)


LoadDLL.DLL.SDL_JoystickSendEffect.restype = ctypes.c_int
LoadDLL.DLL.SDL_JoystickSendEffect.argtypes = [ctypes.POINTER(SDL_Joystick), ctypes.c_void_p, ctypes.c_int]

def SDL_JoystickSendEffect(joystick, data, size):
	"""
	Args:
		joystick: ctypes.POINTER(SDL_Joystick).
		data: ctypes.c_void_p.
		size: ctypes.c_int.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_JoystickSendEffect(joystick, data, size)


LoadDLL.DLL.SDL_JoystickClose.restype = None
LoadDLL.DLL.SDL_JoystickClose.argtypes = [ctypes.POINTER(SDL_Joystick)]

def SDL_JoystickClose(joystick):
	"""
	Args:
		joystick: ctypes.POINTER(SDL_Joystick).
	Returns:
		res: None.
	"""
	LoadDLL.DLL.SDL_JoystickClose(joystick)


LoadDLL.DLL.SDL_JoystickCurrentPowerLevel.restype = ctypes.c_int
LoadDLL.DLL.SDL_JoystickCurrentPowerLevel.argtypes = [ctypes.POINTER(SDL_Joystick)]

def SDL_JoystickCurrentPowerLevel(joystick):
	"""
	Args:
		joystick: ctypes.POINTER(SDL_Joystick).
	Returns:
		res: SDL_JoystickPowerLevel.
	"""
	return LoadDLL.DLL.SDL_JoystickCurrentPowerLevel(joystick)