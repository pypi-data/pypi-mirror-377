import ctypes
from .LoadDLL import LoadDLL
from .SDL_rwops import SDL_RWops
from .SDL_joystick import SDL_Joystick, SDL_JoystickGUID


class SDL_GameControllerType:
	SDL_CONTROLLER_TYPE_UNKNOWN = 0
	SDL_CONTROLLER_TYPE_XBOX360 = 1
	SDL_CONTROLLER_TYPE_XBOXONE = 2
	SDL_CONTROLLER_TYPE_PS3 = 3
	SDL_CONTROLLER_TYPE_PS4 = 4
	SDL_CONTROLLER_TYPE_NINTENDO_SWITCH_PRO = 5
	SDL_CONTROLLER_TYPE_VIRTUAL = 6
	SDL_CONTROLLER_TYPE_PS5 = 7
	SDL_CONTROLLER_TYPE_AMAZON_LUNA = 8
	SDL_CONTROLLER_TYPE_GOOGLE_STADIA = 9
	SDL_CONTROLLER_TYPE_NVIDIA_SHIELD = 10
	SDL_CONTROLLER_TYPE_NINTENDO_SWITCH_JOYCON_LEFT = 11
	SDL_CONTROLLER_TYPE_NINTENDO_SWITCH_JOYCON_RIGHT = 12
	SDL_CONTROLLER_TYPE_NINTENDO_SWITCH_JOYCON_PAIR = 13
	SDL_CONTROLLER_TYPE_MAX = 14


class SDL_GameControllerBindType:
	SDL_CONTROLLER_BINDTYPE_NONE = 0
	SDL_CONTROLLER_BINDTYPE_BUTTON = 1
	SDL_CONTROLLER_BINDTYPE_AXIS = 2
	SDL_CONTROLLER_BINDTYPE_HAT = 3


class SDL_GameControllerAxis:
	SDL_CONTROLLER_AXIS_INVALID = -1
	SDL_CONTROLLER_AXIS_LEFTX = 0
	SDL_CONTROLLER_AXIS_LEFTY = 1
	SDL_CONTROLLER_AXIS_RIGHTX = 2
	SDL_CONTROLLER_AXIS_RIGHTY = 3
	SDL_CONTROLLER_AXIS_TRIGGERLEFT = 4
	SDL_CONTROLLER_AXIS_TRIGGERRIGHT = 5
	SDL_CONTROLLER_AXIS_MAX = 6


class SDL_GameControllerButton:
	SDL_CONTROLLER_BUTTON_INVALID = -1
	SDL_CONTROLLER_BUTTON_A = 0
	SDL_CONTROLLER_BUTTON_B = 1
	SDL_CONTROLLER_BUTTON_X = 2
	SDL_CONTROLLER_BUTTON_Y = 3
	SDL_CONTROLLER_BUTTON_BACK = 4
	SDL_CONTROLLER_BUTTON_GUIDE = 5
	SDL_CONTROLLER_BUTTON_START = 6
	SDL_CONTROLLER_BUTTON_LEFTSTICK = 7
	SDL_CONTROLLER_BUTTON_RIGHTSTICK = 8
	SDL_CONTROLLER_BUTTON_LEFTSHOULDER = 9
	SDL_CONTROLLER_BUTTON_RIGHTSHOULDER = 10
	SDL_CONTROLLER_BUTTON_DPAD_UP = 11
	SDL_CONTROLLER_BUTTON_DPAD_DOWN = 12
	SDL_CONTROLLER_BUTTON_DPAD_LEFT = 13
	SDL_CONTROLLER_BUTTON_DPAD_RIGHT = 14
	SDL_CONTROLLER_BUTTON_MISC1 = 15
	SDL_CONTROLLER_BUTTON_PADDLE1 = 16
	SDL_CONTROLLER_BUTTON_PADDLE2 = 17
	SDL_CONTROLLER_BUTTON_PADDLE3 = 18
	SDL_CONTROLLER_BUTTON_PADDLE4 = 19
	SDL_CONTROLLER_BUTTON_TOUCHPAD = 20
	SDL_CONTROLLER_BUTTON_MAX = 21


class SDL_GameController(ctypes.Structure): pass


class hat(ctypes.Structure):
	_fields_ = [
		('hat', ctypes.c_int),
		('hat_mask', ctypes.c_int),
	]


class value(ctypes.Union):
	_fields_ = [
		('button', ctypes.c_int),
		('axis', ctypes.c_int),
		('h_hat', hat),
	]

class SDL_GameControllerButtonBind(ctypes.Structure):
	_fields_ = [
		('bindType', ctypes.c_int),
		('v_value', value),
	]


LoadDLL.DLL.SDL_GameControllerAddMappingsFromRW.restype = ctypes.c_int
LoadDLL.DLL.SDL_GameControllerAddMappingsFromRW.argtypes = [ctypes.POINTER(SDL_RWops), ctypes.c_int]

def SDL_GameControllerAddMappingsFromRW(rw, freerw):
	"""
	Args:
		rw: ctypes.POINTER(SDL_RWops).
		freerw: ctypes.c_int.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_GameControllerAddMappingsFromRW(rw, freerw)


LoadDLL.DLL.SDL_GameControllerAddMapping.restype = ctypes.c_int
LoadDLL.DLL.SDL_GameControllerAddMapping.argtypes = [ctypes.c_char_p]

def SDL_GameControllerAddMapping(mappingString):
	"""
	Args:
		mappingString: ctypes.c_char_p.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_GameControllerAddMapping(mappingString)


LoadDLL.DLL.SDL_GameControllerNumMappings.restype = ctypes.c_int
LoadDLL.DLL.SDL_GameControllerNumMappings.argtypes = []

def SDL_GameControllerNumMappings():
	"""
	Args:
		: None.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_GameControllerNumMappings()


LoadDLL.DLL.SDL_GameControllerMappingForIndex.restype = ctypes.c_char_p
LoadDLL.DLL.SDL_GameControllerMappingForIndex.argtypes = [ctypes.c_int]

def SDL_GameControllerMappingForIndex(mapping_index):
	"""
	Args:
		mapping_index: ctypes.c_int.
	Returns:
		res: ctypes.c_char_p.
	"""
	return LoadDLL.DLL.SDL_GameControllerMappingForIndex(mapping_index)


LoadDLL.DLL.SDL_GameControllerMappingForGUID.restype = ctypes.c_char_p
LoadDLL.DLL.SDL_GameControllerMappingForGUID.argtypes = [SDL_JoystickGUID]

def SDL_GameControllerMappingForGUID(guid):
	"""
	Args:
		guid: SDL_JoystickGUID.
	Returns:
		res: ctypes.c_char_p.
	"""
	return LoadDLL.DLL.SDL_GameControllerMappingForGUID(guid)


LoadDLL.DLL.SDL_GameControllerMapping.restype = ctypes.c_char_p
LoadDLL.DLL.SDL_GameControllerMapping.argtypes = [ctypes.POINTER(SDL_GameController)]

def SDL_GameControllerMapping(gamecontroller):
	"""
	Args:
		gamecontroller: ctypes.POINTER(SDL_GameController).
	Returns:
		res: ctypes.c_char_p.
	"""
	return LoadDLL.DLL.SDL_GameControllerMapping(gamecontroller)


LoadDLL.DLL.SDL_IsGameController.restype = ctypes.c_int
LoadDLL.DLL.SDL_IsGameController.argtypes = [ctypes.c_int]

def SDL_IsGameController(joystick_index):
	"""
	Args:
		joystick_index: ctypes.c_int.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_IsGameController(joystick_index)


LoadDLL.DLL.SDL_GameControllerNameForIndex.restype = ctypes.c_char_p
LoadDLL.DLL.SDL_GameControllerNameForIndex.argtypes = [ctypes.c_int]

def SDL_GameControllerNameForIndex(joystick_index):
	"""
	Args:
		joystick_index: ctypes.c_int.
	Returns:
		res: ctypes.c_char_p.
	"""
	return LoadDLL.DLL.SDL_GameControllerNameForIndex(joystick_index)


LoadDLL.DLL.SDL_GameControllerPathForIndex.restype = ctypes.c_char_p
LoadDLL.DLL.SDL_GameControllerPathForIndex.argtypes = [ctypes.c_int]

def SDL_GameControllerPathForIndex(joystick_index):
	"""
	Args:
		joystick_index: ctypes.c_int.
	Returns:
		res: ctypes.c_char_p.
	"""
	return LoadDLL.DLL.SDL_GameControllerPathForIndex(joystick_index)


LoadDLL.DLL.SDL_GameControllerTypeForIndex.restype = ctypes.c_int
LoadDLL.DLL.SDL_GameControllerTypeForIndex.argtypes = [ctypes.c_int]

def SDL_GameControllerTypeForIndex(joystick_index):
	"""
	Args:
		joystick_index: ctypes.c_int.
	Returns:
		res: SDL_GameControllerType.
	"""
	return LoadDLL.DLL.SDL_GameControllerTypeForIndex(joystick_index)


LoadDLL.DLL.SDL_GameControllerMappingForDeviceIndex.restype = ctypes.c_char_p
LoadDLL.DLL.SDL_GameControllerMappingForDeviceIndex.argtypes = [ctypes.c_int]

def SDL_GameControllerMappingForDeviceIndex(joystick_index):
	"""
	Args:
		joystick_index: ctypes.c_int.
	Returns:
		res: ctypes.c_char_p.
	"""
	return LoadDLL.DLL.SDL_GameControllerMappingForDeviceIndex(joystick_index)


LoadDLL.DLL.SDL_GameControllerOpen.restype = ctypes.POINTER(SDL_GameController)
LoadDLL.DLL.SDL_GameControllerOpen.argtypes = [ctypes.c_int]

def SDL_GameControllerOpen(joystick_index):
	"""
	Args:
		joystick_index: ctypes.c_int.
	Returns:
		res: ctypes.POINTER(SDL_GameController).
	"""
	return LoadDLL.DLL.SDL_GameControllerOpen(joystick_index)


LoadDLL.DLL.SDL_GameControllerFromInstanceID.restype = ctypes.POINTER(SDL_GameController)
LoadDLL.DLL.SDL_GameControllerFromInstanceID.argtypes = [ctypes.c_int32]

def SDL_GameControllerFromInstanceID(joyid):
	"""
	Args:
		joyid: ctypes.c_int32.
	Returns:
		res: ctypes.POINTER(SDL_GameController).
	"""
	return LoadDLL.DLL.SDL_GameControllerFromInstanceID(joyid)


LoadDLL.DLL.SDL_GameControllerFromPlayerIndex.restype = ctypes.POINTER(SDL_GameController)
LoadDLL.DLL.SDL_GameControllerFromPlayerIndex.argtypes = [ctypes.c_int]

def SDL_GameControllerFromPlayerIndex(player_index):
	"""
	Args:
		player_index: ctypes.c_int.
	Returns:
		res: ctypes.POINTER(SDL_GameController).
	"""
	return LoadDLL.DLL.SDL_GameControllerFromPlayerIndex(player_index)


LoadDLL.DLL.SDL_GameControllerName.restype = ctypes.c_char_p
LoadDLL.DLL.SDL_GameControllerName.argtypes = [ctypes.POINTER(SDL_GameController)]

def SDL_GameControllerName(gamecontroller):
	"""
	Args:
		gamecontroller: ctypes.POINTER(SDL_GameController).
	Returns:
		res: ctypes.c_char_p.
	"""
	return LoadDLL.DLL.SDL_GameControllerName(gamecontroller)


LoadDLL.DLL.SDL_GameControllerPath.restype = ctypes.c_char_p
LoadDLL.DLL.SDL_GameControllerPath.argtypes = [ctypes.POINTER(SDL_GameController)]

def SDL_GameControllerPath(gamecontroller):
	"""
	Args:
		gamecontroller: ctypes.POINTER(SDL_GameController).
	Returns:
		res: ctypes.c_char_p.
	"""
	return LoadDLL.DLL.SDL_GameControllerPath(gamecontroller)


LoadDLL.DLL.SDL_GameControllerGetType.restype = ctypes.c_int
LoadDLL.DLL.SDL_GameControllerGetType.argtypes = [ctypes.POINTER(SDL_GameController)]

def SDL_GameControllerGetType(gamecontroller):
	"""
	Args:
		gamecontroller: ctypes.POINTER(SDL_GameController).
	Returns:
		res: SDL_GameControllerType.
	"""
	return LoadDLL.DLL.SDL_GameControllerGetType(gamecontroller)


LoadDLL.DLL.SDL_GameControllerGetPlayerIndex.restype = ctypes.c_int
LoadDLL.DLL.SDL_GameControllerGetPlayerIndex.argtypes = [ctypes.POINTER(SDL_GameController)]

def SDL_GameControllerGetPlayerIndex(gamecontroller):
	"""
	Args:
		gamecontroller: ctypes.POINTER(SDL_GameController).
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_GameControllerGetPlayerIndex(gamecontroller)


LoadDLL.DLL.SDL_GameControllerSetPlayerIndex.restype = None
LoadDLL.DLL.SDL_GameControllerSetPlayerIndex.argtypes = [ctypes.POINTER(SDL_GameController), ctypes.c_int]

def SDL_GameControllerSetPlayerIndex(gamecontroller, player_index):
	"""
	Args:
		gamecontroller: ctypes.POINTER(SDL_GameController).
		player_index: ctypes.c_int.
	Returns:
		res: None.
	"""
	LoadDLL.DLL.SDL_GameControllerSetPlayerIndex(gamecontroller, player_index)


LoadDLL.DLL.SDL_GameControllerGetVendor.restype = ctypes.c_ushort
LoadDLL.DLL.SDL_GameControllerGetVendor.argtypes = [ctypes.POINTER(SDL_GameController)]

def SDL_GameControllerGetVendor(gamecontroller):
	"""
	Args:
		gamecontroller: ctypes.POINTER(SDL_GameController).
	Returns:
		res: ctypes.c_ushort.
	"""
	return LoadDLL.DLL.SDL_GameControllerGetVendor(gamecontroller)


LoadDLL.DLL.SDL_GameControllerGetProduct.restype = ctypes.c_ushort
LoadDLL.DLL.SDL_GameControllerGetProduct.argtypes = [ctypes.POINTER(SDL_GameController)]

def SDL_GameControllerGetProduct(gamecontroller):
	"""
	Args:
		gamecontroller: ctypes.POINTER(SDL_GameController).
	Returns:
		res: ctypes.c_ushort.
	"""
	return LoadDLL.DLL.SDL_GameControllerGetProduct(gamecontroller)


LoadDLL.DLL.SDL_GameControllerGetProductVersion.restype = ctypes.c_ushort
LoadDLL.DLL.SDL_GameControllerGetProductVersion.argtypes = [ctypes.POINTER(SDL_GameController)]

def SDL_GameControllerGetProductVersion(gamecontroller):
	"""
	Args:
		gamecontroller: ctypes.POINTER(SDL_GameController).
	Returns:
		res: ctypes.c_ushort.
	"""
	return LoadDLL.DLL.SDL_GameControllerGetProductVersion(gamecontroller)


LoadDLL.DLL.SDL_GameControllerGetFirmwareVersion.restype = ctypes.c_ushort
LoadDLL.DLL.SDL_GameControllerGetFirmwareVersion.argtypes = [ctypes.POINTER(SDL_GameController)]

def SDL_GameControllerGetFirmwareVersion(gamecontroller):
	"""
	Args:
		gamecontroller: ctypes.POINTER(SDL_GameController).
	Returns:
		res: ctypes.c_ushort.
	"""
	return LoadDLL.DLL.SDL_GameControllerGetFirmwareVersion(gamecontroller)


LoadDLL.DLL.SDL_GameControllerGetSerial.restype = ctypes.c_char_p
LoadDLL.DLL.SDL_GameControllerGetSerial.argtypes = [ctypes.POINTER(SDL_GameController)]

def SDL_GameControllerGetSerial(gamecontroller):
	"""
	Args:
		gamecontroller: ctypes.POINTER(SDL_GameController).
	Returns:
		res: ctypes.c_char_p.
	"""
	return LoadDLL.DLL.SDL_GameControllerGetSerial(gamecontroller)


LoadDLL.DLL.SDL_GameControllerGetSteamHandle.restype = ctypes.c_ulonglong
LoadDLL.DLL.SDL_GameControllerGetSteamHandle.argtypes = [ctypes.POINTER(SDL_GameController)]

def SDL_GameControllerGetSteamHandle(gamecontroller):
	"""
	Args:
		gamecontroller: ctypes.POINTER(SDL_GameController).
	Returns:
		res: ctypes.c_ulonglong.
	"""
	return LoadDLL.DLL.SDL_GameControllerGetSteamHandle(gamecontroller)


LoadDLL.DLL.SDL_GameControllerGetAttached.restype = ctypes.c_int
LoadDLL.DLL.SDL_GameControllerGetAttached.argtypes = [ctypes.POINTER(SDL_GameController)]

def SDL_GameControllerGetAttached(gamecontroller):
	"""
	Args:
		gamecontroller: ctypes.POINTER(SDL_GameController).
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_GameControllerGetAttached(gamecontroller)


LoadDLL.DLL.SDL_GameControllerGetJoystick.restype = ctypes.POINTER(SDL_Joystick)
LoadDLL.DLL.SDL_GameControllerGetJoystick.argtypes = [ctypes.POINTER(SDL_GameController)]

def SDL_GameControllerGetJoystick(gamecontroller):
	"""
	Args:
		gamecontroller: ctypes.POINTER(SDL_GameController).
	Returns:
		res: ctypes.POINTER(SDL_Joystick).
	"""
	return LoadDLL.DLL.SDL_GameControllerGetJoystick(gamecontroller)


LoadDLL.DLL.SDL_GameControllerEventState.restype = ctypes.c_int
LoadDLL.DLL.SDL_GameControllerEventState.argtypes = [ctypes.c_int]

def SDL_GameControllerEventState(state):
	"""
	Args:
		state: ctypes.c_int.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_GameControllerEventState(state)


LoadDLL.DLL.SDL_GameControllerUpdate.restype = None
LoadDLL.DLL.SDL_GameControllerUpdate.argtypes = []

def SDL_GameControllerUpdate():
	"""
	Args:
		: None.
	Returns:
		res: None.
	"""
	LoadDLL.DLL.SDL_GameControllerUpdate()


LoadDLL.DLL.SDL_GameControllerGetAxisFromString.restype = ctypes.c_int
LoadDLL.DLL.SDL_GameControllerGetAxisFromString.argtypes = [ctypes.c_char_p]

def SDL_GameControllerGetAxisFromString(str):
	"""
	Args:
		str: ctypes.c_char_p.
	Returns:
		res: SDL_GameControllerAxis.
	"""
	return LoadDLL.DLL.SDL_GameControllerGetAxisFromString(str)


LoadDLL.DLL.SDL_GameControllerGetStringForAxis.restype = ctypes.c_char_p
LoadDLL.DLL.SDL_GameControllerGetStringForAxis.argtypes = [ctypes.c_int]

def SDL_GameControllerGetStringForAxis(axis):
	"""
	Args:
		axis: SDL_GameControllerAxis.
	Returns:
		res: ctypes.c_char_p.
	"""
	return LoadDLL.DLL.SDL_GameControllerGetStringForAxis(axis)


LoadDLL.DLL.SDL_GameControllerGetBindForAxis.restype = SDL_GameControllerButtonBind
LoadDLL.DLL.SDL_GameControllerGetBindForAxis.argtypes = [ctypes.POINTER(SDL_GameController), ctypes.c_int]

def SDL_GameControllerGetBindForAxis(gamecontroller, axis):
	"""
	Args:
		gamecontroller: ctypes.POINTER(SDL_GameController).
		axis: SDL_GameControllerAxis.
	Returns:
		res: SDL_GameControllerButtonBind.
	"""
	return LoadDLL.DLL.SDL_GameControllerGetBindForAxis(gamecontroller, axis)


LoadDLL.DLL.SDL_GameControllerGetAxis.restype = ctypes.c_int16
LoadDLL.DLL.SDL_GameControllerGetAxis.argtypes = [ctypes.POINTER(SDL_GameController), ctypes.c_int]

def SDL_GameControllerGetAxis(gamecontroller, axis):
	"""
	Args:
		gamecontroller: ctypes.POINTER(SDL_GameController).
		axis: SDL_GameControllerAxis.
	Returns:
		res: ctypes.c_int16.
	"""
	return LoadDLL.DLL.SDL_GameControllerGetAxis(gamecontroller, axis)


LoadDLL.DLL.SDL_GameControllerGetButtonFromString.restype = ctypes.c_int
LoadDLL.DLL.SDL_GameControllerGetButtonFromString.argtypes = [ctypes.c_char_p]

def SDL_GameControllerGetButtonFromString(str):
	"""
	Args:
		str: ctypes.c_char_p.
	Returns:
		res: SDL_GameControllerButton.
	"""
	return LoadDLL.DLL.SDL_GameControllerGetButtonFromString(str)


LoadDLL.DLL.SDL_GameControllerGetStringForButton.restype = ctypes.c_char_p
LoadDLL.DLL.SDL_GameControllerGetStringForButton.argtypes = [ctypes.c_int]

def SDL_GameControllerGetStringForButton(button):
	"""
	Args:
		button: SDL_GameControllerButton.
	Returns:
		res: ctypes.c_char_p.
	"""
	return LoadDLL.DLL.SDL_GameControllerGetStringForButton(button)


LoadDLL.DLL.SDL_GameControllerGetBindForButton.restype = SDL_GameControllerButtonBind
LoadDLL.DLL.SDL_GameControllerGetBindForButton.argtypes = [ctypes.POINTER(SDL_GameController), ctypes.c_int]

def SDL_GameControllerGetBindForButton(gamecontroller, button):
	"""
	Args:
		gamecontroller: ctypes.POINTER(SDL_GameController).
		button: SDL_GameControllerButton.
	Returns:
		res: SDL_GameControllerButtonBind.
	"""
	return LoadDLL.DLL.SDL_GameControllerGetBindForButton(gamecontroller, button)


LoadDLL.DLL.SDL_GameControllerGetButton.restype = ctypes.c_ubyte
LoadDLL.DLL.SDL_GameControllerGetButton.argtypes = [ctypes.POINTER(SDL_GameController), ctypes.c_int]

def SDL_GameControllerGetButton(gamecontroller, button):
	"""
	Args:
		gamecontroller: ctypes.POINTER(SDL_GameController).
		button: SDL_GameControllerButton.
	Returns:
		res: ctypes.c_ubyte.
	"""
	return LoadDLL.DLL.SDL_GameControllerGetButton(gamecontroller, button)


LoadDLL.DLL.SDL_GameControllerGetNumTouchpadFingers.restype = ctypes.c_int
LoadDLL.DLL.SDL_GameControllerGetNumTouchpadFingers.argtypes = [ctypes.POINTER(SDL_GameController), ctypes.c_int]

def SDL_GameControllerGetNumTouchpadFingers(gamecontroller, touchpad):
	"""
	Args:
		gamecontroller: ctypes.POINTER(SDL_GameController).
		touchpad: ctypes.c_int.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_GameControllerGetNumTouchpadFingers(gamecontroller, touchpad)


LoadDLL.DLL.SDL_GameControllerGetTouchpadFinger.restype = ctypes.c_int
LoadDLL.DLL.SDL_GameControllerGetTouchpadFinger.argtypes = [ctypes.POINTER(SDL_GameController), ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float)]

def SDL_GameControllerGetTouchpadFinger(gamecontroller, touchpad, finger, state, x, y, pressure):
	"""
	Args:
		gamecontroller: ctypes.POINTER(SDL_GameController).
		touchpad: ctypes.c_int.
		finger: ctypes.c_int.
		state: ctypes.POINTER(ctypes.c_ubyte).
		x: ctypes.POINTER(ctypes.c_float).
		y: ctypes.POINTER(ctypes.c_float).
		pressure: ctypes.POINTER(ctypes.c_float).
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_GameControllerGetTouchpadFinger(gamecontroller, touchpad, finger, state, x, y, pressure)


LoadDLL.DLL.SDL_GameControllerHasSensor.restype = ctypes.c_int
LoadDLL.DLL.SDL_GameControllerHasSensor.argtypes = [ctypes.POINTER(SDL_GameController), ctypes.c_int]

def SDL_GameControllerHasSensor(gamecontroller, type_):
	"""
	Args:
		gamecontroller: ctypes.POINTER(SDL_GameController).
		type_: SDL_SensorType.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_GameControllerHasSensor(gamecontroller, type_)


LoadDLL.DLL.SDL_GameControllerSetSensorEnabled.restype = ctypes.c_int
LoadDLL.DLL.SDL_GameControllerSetSensorEnabled.argtypes = [ctypes.POINTER(SDL_GameController), ctypes.c_int, ctypes.c_int]

def SDL_GameControllerSetSensorEnabled(gamecontroller, type_, enabled):
	"""
	Args:
		gamecontroller: ctypes.POINTER(SDL_GameController).
		type_: SDL_SensorType.
		enabled: ctypes.c_int.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_GameControllerSetSensorEnabled(gamecontroller, type_, enabled)


LoadDLL.DLL.SDL_GameControllerIsSensorEnabled.restype = ctypes.c_int
LoadDLL.DLL.SDL_GameControllerIsSensorEnabled.argtypes = [ctypes.POINTER(SDL_GameController), ctypes.c_int]

def SDL_GameControllerIsSensorEnabled(gamecontroller, type_):
	"""
	Args:
		gamecontroller: ctypes.POINTER(SDL_GameController).
		type_: SDL_SensorType.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_GameControllerIsSensorEnabled(gamecontroller, type_)


LoadDLL.DLL.SDL_GameControllerGetSensorDataRate.restype = ctypes.c_float
LoadDLL.DLL.SDL_GameControllerGetSensorDataRate.argtypes = [ctypes.POINTER(SDL_GameController), ctypes.c_int]

def SDL_GameControllerGetSensorDataRate(gamecontroller, type_):
	"""
	Args:
		gamecontroller: ctypes.POINTER(SDL_GameController).
		type_: SDL_SensorType.
	Returns:
		res: ctypes.c_float.
	"""
	return LoadDLL.DLL.SDL_GameControllerGetSensorDataRate(gamecontroller, type_)


LoadDLL.DLL.SDL_GameControllerGetSensorData.restype = ctypes.c_int
LoadDLL.DLL.SDL_GameControllerGetSensorData.argtypes = [ctypes.POINTER(SDL_GameController), ctypes.c_int, ctypes.POINTER(ctypes.c_float), ctypes.c_int]

def SDL_GameControllerGetSensorData(gamecontroller, type_, data, num_values):
	"""
	Args:
		gamecontroller: ctypes.POINTER(SDL_GameController).
		type_: SDL_SensorType.
		data: ctypes.POINTER(ctypes.c_float).
		num_values: ctypes.c_int.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_GameControllerGetSensorData(gamecontroller, type_, data, num_values)


LoadDLL.DLL.SDL_GameControllerGetSensorDataWithTimestamp.restype = ctypes.c_int
LoadDLL.DLL.SDL_GameControllerGetSensorDataWithTimestamp.argtypes = [ctypes.POINTER(SDL_GameController), ctypes.c_int, ctypes.POINTER(ctypes.c_ulonglong), ctypes.POINTER(ctypes.c_float), ctypes.c_int]

def SDL_GameControllerGetSensorDataWithTimestamp(gamecontroller, type_, timestamp, data, num_values):
	"""
	Args:
		gamecontroller: ctypes.POINTER(SDL_GameController).
		type_: SDL_SensorType.
		timestamp: ctypes.POINTER(ctypes.c_ulonglong).
		data: ctypes.POINTER(ctypes.c_float).
		num_values: ctypes.c_int.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_GameControllerGetSensorDataWithTimestamp(gamecontroller, type_, timestamp, data, num_values)


LoadDLL.DLL.SDL_GameControllerRumble.restype = ctypes.c_int
LoadDLL.DLL.SDL_GameControllerRumble.argtypes = [ctypes.POINTER(SDL_GameController), ctypes.c_ushort, ctypes.c_ushort, ctypes.c_uint]

def SDL_GameControllerRumble(gamecontroller, low_frequency_rumble, high_frequency_rumble, duration_ms):
	"""
	Args:
		gamecontroller: ctypes.POINTER(SDL_GameController).
		low_frequency_rumble: ctypes.c_ushort.
		high_frequency_rumble: ctypes.c_ushort.
		duration_ms: ctypes.c_uint.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_GameControllerRumble(gamecontroller, low_frequency_rumble, high_frequency_rumble, duration_ms)


LoadDLL.DLL.SDL_GameControllerRumbleTriggers.restype = ctypes.c_int
LoadDLL.DLL.SDL_GameControllerRumbleTriggers.argtypes = [ctypes.POINTER(SDL_GameController), ctypes.c_ushort, ctypes.c_ushort, ctypes.c_uint]

def SDL_GameControllerRumbleTriggers(gamecontroller, left_rumble, right_rumble, duration_ms):
	"""
	Args:
		gamecontroller: ctypes.POINTER(SDL_GameController).
		left_rumble: ctypes.c_ushort.
		right_rumble: ctypes.c_ushort.
		duration_ms: ctypes.c_uint.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_GameControllerRumbleTriggers(gamecontroller, left_rumble, right_rumble, duration_ms)


LoadDLL.DLL.SDL_GameControllerHasLED.restype = ctypes.c_int
LoadDLL.DLL.SDL_GameControllerHasLED.argtypes = [ctypes.POINTER(SDL_GameController)]

def SDL_GameControllerHasLED(gamecontroller):
	"""
	Args:
		gamecontroller: ctypes.POINTER(SDL_GameController).
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_GameControllerHasLED(gamecontroller)


LoadDLL.DLL.SDL_GameControllerHasRumble.restype = ctypes.c_int
LoadDLL.DLL.SDL_GameControllerHasRumble.argtypes = [ctypes.POINTER(SDL_GameController)]

def SDL_GameControllerHasRumble(gamecontroller):
	"""
	Args:
		gamecontroller: ctypes.POINTER(SDL_GameController).
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_GameControllerHasRumble(gamecontroller)


LoadDLL.DLL.SDL_GameControllerHasRumbleTriggers.restype = ctypes.c_int
LoadDLL.DLL.SDL_GameControllerHasRumbleTriggers.argtypes = [ctypes.POINTER(SDL_GameController)]

def SDL_GameControllerHasRumbleTriggers(gamecontroller):
	"""
	Args:
		gamecontroller: ctypes.POINTER(SDL_GameController).
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_GameControllerHasRumbleTriggers(gamecontroller)


LoadDLL.DLL.SDL_GameControllerSetLED.restype = ctypes.c_int
LoadDLL.DLL.SDL_GameControllerSetLED.argtypes = [ctypes.POINTER(SDL_GameController), ctypes.c_ubyte, ctypes.c_ubyte, ctypes.c_ubyte]

def SDL_GameControllerSetLED(gamecontroller, red, green, blue):
	"""
	Args:
		gamecontroller: ctypes.POINTER(SDL_GameController).
		red: ctypes.c_ubyte.
		green: ctypes.c_ubyte.
		blue: ctypes.c_ubyte.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_GameControllerSetLED(gamecontroller, red, green, blue)


LoadDLL.DLL.SDL_GameControllerSendEffect.restype = ctypes.c_int
LoadDLL.DLL.SDL_GameControllerSendEffect.argtypes = [ctypes.POINTER(SDL_GameController), ctypes.c_void_p, ctypes.c_int]

def SDL_GameControllerSendEffect(gamecontroller, data, size):
	"""
	Args:
		gamecontroller: ctypes.POINTER(SDL_GameController).
		data: ctypes.c_void_p.
		size: ctypes.c_int.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_GameControllerSendEffect(gamecontroller, data, size)


LoadDLL.DLL.SDL_GameControllerClose.restype = None
LoadDLL.DLL.SDL_GameControllerClose.argtypes = [ctypes.POINTER(SDL_GameController)]

def SDL_GameControllerClose(gamecontroller):
	"""
	Args:
		gamecontroller: ctypes.POINTER(SDL_GameController).
	Returns:
		res: None.
	"""
	LoadDLL.DLL.SDL_GameControllerClose(gamecontroller)


LoadDLL.DLL.SDL_GameControllerGetAppleSFSymbolsNameForButton.restype = ctypes.c_char_p
LoadDLL.DLL.SDL_GameControllerGetAppleSFSymbolsNameForButton.argtypes = [ctypes.POINTER(SDL_GameController), ctypes.c_int]

def SDL_GameControllerGetAppleSFSymbolsNameForButton(gamecontroller, button):
	"""
	Args:
		gamecontroller: ctypes.POINTER(SDL_GameController).
		button: SDL_GameControllerButton.
	Returns:
		res: ctypes.c_char_p.
	"""
	return LoadDLL.DLL.SDL_GameControllerGetAppleSFSymbolsNameForButton(gamecontroller, button)


LoadDLL.DLL.SDL_GameControllerGetAppleSFSymbolsNameForAxis.restype = ctypes.c_char_p
LoadDLL.DLL.SDL_GameControllerGetAppleSFSymbolsNameForAxis.argtypes = [ctypes.POINTER(SDL_GameController), ctypes.c_int]

def SDL_GameControllerGetAppleSFSymbolsNameForAxis(gamecontroller, axis):
	"""
	Args:
		gamecontroller: ctypes.POINTER(SDL_GameController).
		axis: SDL_GameControllerAxis.
	Returns:
		res: ctypes.c_char_p.
	"""
	return LoadDLL.DLL.SDL_GameControllerGetAppleSFSymbolsNameForAxis(gamecontroller, axis)