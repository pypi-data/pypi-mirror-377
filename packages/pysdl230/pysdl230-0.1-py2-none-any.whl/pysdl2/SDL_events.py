import ctypes
from .LoadDLL import LoadDLL
from .SDL_syswm import SDL_SysWMmsg
from .SDL_keyboard import SDL_Keysym


SDL_RELEASED = 0

SDL_PRESSED = 1

SDL_IGNORE = 0

SDL_DISABLE = 0

SDL_ENABLE = 1

SDL_TEXTEDITINGEVENT_TEXT_SIZE = 79


class SDL_EventType:
	SDL_FIRSTEVENT = 0
	SDL_QUIT = 0x100
	SDL_APP_TERMINATING = 0x101
	SDL_APP_LOWMEMORY = 0x102
	SDL_APP_WILLENTERBACKGROUND = 0x103
	SDL_APP_DIDENTERBACKGROUND = 0x104
	SDL_APP_WILLENTERFOREGROUND = 0x105
	SDL_APP_DIDENTERFOREGROUND = 0x106
	SDL_LOCALECHANGED = 0x107
	SDL_DISPLAYEVENT = 0x150
	SDL_WINDOWEVENT = 0x200
	SDL_SYSWMEVENT = 0x201
	SDL_KEYDOWN = 0x300
	SDL_KEYUP = 0x301
	SDL_TEXTEDITING = 0x302
	SDL_TEXTINPUT = 0x303
	SDL_KEYMAPCHANGED = 0x304
	SDL_TEXTEDITING_EXT = 0x305
	SDL_MOUSEMOTION = 0x400
	SDL_MOUSEBUTTONDOWN = 0x401
	SDL_MOUSEBUTTONUP = 0x402
	SDL_MOUSEWHEEL = 0x403
	SDL_JOYAXISMOTION = 0x600
	SDL_JOYBALLMOTION = 0x601
	SDL_JOYHATMOTION = 0x602
	SDL_JOYBUTTONDOWN = 0x603
	SDL_JOYBUTTONUP = 0x604
	SDL_JOYDEVICEADDED = 0x605
	SDL_JOYDEVICEREMOVED = 0x606
	SDL_JOYBATTERYUPDATED = 0x607
	SDL_CONTROLLERAXISMOTION = 0x650
	SDL_CONTROLLERBUTTONDOWN = 0x651
	SDL_CONTROLLERBUTTONUP = 0x652
	SDL_CONTROLLERDEVICEADDED = 0x653
	SDL_CONTROLLERDEVICEREMOVED = 0x654
	SDL_CONTROLLERDEVICEREMAPPED = 0x655
	SDL_CONTROLLERTOUCHPADDOWN = 0x656
	SDL_CONTROLLERTOUCHPADMOTION = 0x657
	SDL_CONTROLLERTOUCHPADUP = 0x658
	SDL_CONTROLLERSENSORUPDATE = 0x659
	SDL_CONTROLLERUPDATECOMPLETE_RESERVED_FOR_SDL3 = 0x65A
	SDL_CONTROLLERSTEAMHANDLEUPDATED = 0x65B
	SDL_FINGERDOWN = 0x700
	SDL_FINGERUP = 0x701
	SDL_FINGERMOTION = 0x702
	SDL_DOLLARGESTURE = 0x800
	SDL_DOLLARRECORD = 0x801
	SDL_MULTIGESTURE = 0x802
	SDL_CLIPBOARDUPDATE = 0x900
	SDL_DROPFILE = 0x1000
	SDL_DROPTEXT = 0x1001
	SDL_DROPBEGIN = 0x1002
	SDL_DROPCOMPLETE = 0x1003
	SDL_AUDIODEVICEADDED = 0x1100
	SDL_AUDIODEVICEREMOVED = 0x1101
	SDL_SENSORUPDATE = 0x1200
	SDL_RENDER_TARGETS_RESET = 0x2000
	SDL_RENDER_DEVICE_RESET = 0x2001
	SDL_POLLSENTINEL = 0x7F00
	SDL_USEREVENT = 0x8000
	SDL_LASTEVENT = 0xFFFF


class SDL_eventaction:
	SDL_ADDEVENT = 0
	SDL_PEEKEVENT = 1
	SDL_GETEVENT = 2


class SDL_CommonEvent(ctypes.Structure):
	_fields_ = [
		('type', ctypes.c_uint),
		('timestamp', ctypes.c_uint),
	]


class SDL_DisplayEvent(ctypes.Structure):
	_fields_ = [
		('type', ctypes.c_uint),
		('timestamp', ctypes.c_uint),
		('display', ctypes.c_uint),
		('event', ctypes.c_ubyte),
		('padding1', ctypes.c_ubyte),
		('padding2', ctypes.c_ubyte),
		('padding3', ctypes.c_ubyte),
		('data1', ctypes.c_int32),
	]


class SDL_WindowEvent(ctypes.Structure):
	_fields_ = [
		('type', ctypes.c_uint),
		('timestamp', ctypes.c_uint),
		('windowID', ctypes.c_uint),
		('event', ctypes.c_ubyte),
		('padding1', ctypes.c_ubyte),
		('padding2', ctypes.c_ubyte),
		('padding3', ctypes.c_ubyte),
		('data1', ctypes.c_int32),
		('data2', ctypes.c_int32),
	]


class SDL_KeyboardEvent(ctypes.Structure):
	_fields_ = [
		('type', ctypes.c_uint),
		('timestamp', ctypes.c_uint),
		('windowID', ctypes.c_uint),
		('state', ctypes.c_ubyte),
		('repeat', ctypes.c_ubyte),
		('padding2', ctypes.c_ubyte),
		('padding3', ctypes.c_ubyte),
		('keysym', SDL_Keysym),
	]


class SDL_TextEditingEvent(ctypes.Structure):
	_fields_ = [
		('type', ctypes.c_uint),
		('timestamp', ctypes.c_uint),
		('windowID', ctypes.c_uint),
		('text', ctypes.c_char * SDL_TEXTEDITINGEVENT_TEXT_SIZE),
		('start', ctypes.c_int32),
		('length', ctypes.c_int32),
	]


class SDL_TextEditingExtEvent(ctypes.Structure):
	_fields_ = [
		('type', ctypes.c_uint),
		('timestamp', ctypes.c_uint),
		('windowID', ctypes.c_uint),
		('text', ctypes.c_char_p),
		('start', ctypes.c_int32),
		('length', ctypes.c_int32),
	]


class SDL_TextInputEvent(ctypes.Structure):
	_fields_ = [
		('type', ctypes.c_uint),
		('timestamp', ctypes.c_uint),
		('windowID', ctypes.c_uint),
		('text', ctypes.c_char * SDL_TEXTEDITINGEVENT_TEXT_SIZE),
	]


class SDL_MouseMotionEvent(ctypes.Structure):
	_fields_ = [
		('type', ctypes.c_uint),
		('timestamp', ctypes.c_uint),
		('windowID', ctypes.c_uint),
		('which', ctypes.c_uint),
		('state', ctypes.c_uint),
		('x', ctypes.c_int32),
		('y', ctypes.c_int32),
		('xrel', ctypes.c_int32),
		('yrel', ctypes.c_int32),
	]


class SDL_MouseButtonEvent(ctypes.Structure):
	_fields_ = [
		('type', ctypes.c_uint),
		('timestamp', ctypes.c_uint),
		('windowID', ctypes.c_uint),
		('which', ctypes.c_uint),
		('button', ctypes.c_ubyte),
		('state', ctypes.c_ubyte),
		('clicks', ctypes.c_ubyte),
		('padding1', ctypes.c_ubyte),
		('x', ctypes.c_int32),
		('y', ctypes.c_int32),
	]


class SDL_MouseWheelEvent(ctypes.Structure):
	_fields_ = [
		('type', ctypes.c_uint),
		('timestamp', ctypes.c_uint),
		('windowID', ctypes.c_uint),
		('which', ctypes.c_uint),
		('x', ctypes.c_int32),
		('y', ctypes.c_int32),
		('direction', ctypes.c_uint),
		('preciseX', ctypes.c_float),
		('preciseY', ctypes.c_float),
		('mouseX', ctypes.c_int32),
		('mouseY', ctypes.c_int32),
	]


class SDL_JoyAxisEvent(ctypes.Structure):
	_fields_ = [
		('type', ctypes.c_uint),
		('timestamp', ctypes.c_uint),
		('which', ctypes.c_int32),
		('axis', ctypes.c_ubyte),
		('padding1', ctypes.c_ubyte),
		('padding2', ctypes.c_ubyte),
		('padding3', ctypes.c_ubyte),
		('value', ctypes.c_int16),
		('padding4', ctypes.c_ushort),
	]


class SDL_JoyBallEvent(ctypes.Structure):
	_fields_ = [
		('type', ctypes.c_uint),
		('timestamp', ctypes.c_uint),
		('which', ctypes.c_int32),
		('ball', ctypes.c_ubyte),
		('padding1', ctypes.c_ubyte),
		('padding2', ctypes.c_ubyte),
		('padding3', ctypes.c_ubyte),
		('xrel', ctypes.c_int16),
		('yrel', ctypes.c_int16),
	]


class SDL_JoyHatEvent(ctypes.Structure):
	_fields_ = [
		('type', ctypes.c_uint),
		('timestamp', ctypes.c_uint),
		('which', ctypes.c_int32),
		('hat', ctypes.c_ubyte),
		('value', ctypes.c_ubyte),
		('padding1', ctypes.c_ubyte),
		('padding2', ctypes.c_ubyte),
	]


class SDL_JoyButtonEvent(ctypes.Structure):
	_fields_ = [
		('type', ctypes.c_uint),
		('timestamp', ctypes.c_uint),
		('which', ctypes.c_int32),
		('button', ctypes.c_ubyte),
		('state', ctypes.c_ubyte),
		('padding1', ctypes.c_ubyte),
		('padding2', ctypes.c_ubyte),
	]


class SDL_JoyDeviceEvent(ctypes.Structure):
	_fields_ = [
		('type', ctypes.c_uint),
		('timestamp', ctypes.c_uint),
		('which', ctypes.c_int32),
	]


class SDL_JoyBatteryEvent(ctypes.Structure):
	_fields_ = [
		('type', ctypes.c_uint),
		('timestamp', ctypes.c_uint),
		('which', ctypes.c_int32),
		('level', ctypes.c_int),
	]


class SDL_ControllerAxisEvent(ctypes.Structure):
	_fields_ = [
		('type', ctypes.c_uint),
		('timestamp', ctypes.c_uint),
		('which', ctypes.c_int32),
		('axis', ctypes.c_ubyte),
		('padding1', ctypes.c_ubyte),
		('padding2', ctypes.c_ubyte),
		('padding3', ctypes.c_ubyte),
		('value', ctypes.c_int16),
		('padding4', ctypes.c_ushort),
	]


class SDL_ControllerButtonEvent(ctypes.Structure):
	_fields_ = [
		('type', ctypes.c_uint),
		('timestamp', ctypes.c_uint),
		('which', ctypes.c_int32),
		('button', ctypes.c_ubyte),
		('state', ctypes.c_ubyte),
		('padding1', ctypes.c_ubyte),
		('padding2', ctypes.c_ubyte),
	]


class SDL_ControllerDeviceEvent(ctypes.Structure):
	_fields_ = [
		('type', ctypes.c_uint),
		('timestamp', ctypes.c_uint),
		('which', ctypes.c_int32),
	]


class SDL_ControllerTouchpadEvent(ctypes.Structure):
	_fields_ = [
		('type', ctypes.c_uint),
		('timestamp', ctypes.c_uint),
		('which', ctypes.c_int32),
		('touchpad', ctypes.c_int32),
		('finger', ctypes.c_int32),
		('x', ctypes.c_float),
		('y', ctypes.c_float),
		('pressure', ctypes.c_float),
	]


class SDL_ControllerSensorEvent(ctypes.Structure):
	_fields_ = [
		('type', ctypes.c_uint),
		('timestamp', ctypes.c_uint),
		('which', ctypes.c_int32),
		('sensor', ctypes.c_int32),
		('data', ctypes.c_float * 3),
		('timestamp_us', ctypes.c_ulonglong),
	]


class SDL_AudioDeviceEvent(ctypes.Structure):
	_fields_ = [
		('type', ctypes.c_uint),
		('timestamp', ctypes.c_uint),
		('which', ctypes.c_uint),
		('iscapture', ctypes.c_ubyte),
		('padding1', ctypes.c_ubyte),
		('padding2', ctypes.c_ubyte),
		('padding3', ctypes.c_ubyte),
	]


class SDL_TouchFingerEvent(ctypes.Structure):
	_fields_ = [
		('type', ctypes.c_uint),
		('timestamp', ctypes.c_uint),
		('touchId', ctypes.c_int32),
		('fingerId', ctypes.c_int32),
		('x', ctypes.c_float),
		('y', ctypes.c_float),
		('dx', ctypes.c_float),
		('dy', ctypes.c_float),
		('pressure', ctypes.c_float),
		('windowID', ctypes.c_uint),
	]


class SDL_MultiGestureEvent(ctypes.Structure):
	_fields_ = [
		('type', ctypes.c_uint),
		('timestamp', ctypes.c_uint),
		('touchId', ctypes.c_int32),
		('dTheta', ctypes.c_float),
		('dDist', ctypes.c_float),
		('x', ctypes.c_float),
		('y', ctypes.c_float),
		('numFingers', ctypes.c_ushort),
		('padding', ctypes.c_ushort),
	]


class SDL_DollarGestureEvent(ctypes.Structure):
	_fields_ = [
		('type', ctypes.c_uint),
		('timestamp', ctypes.c_uint),
		('touchId', ctypes.c_int32),
		('gestureId', ctypes.c_longlong),
		('numFingers', ctypes.c_uint),
		('error', ctypes.c_float),
		('x', ctypes.c_float),
		('y', ctypes.c_float),
	]


class SDL_DropEvent(ctypes.Structure):
	_fields_ = [
		('type', ctypes.c_uint),
		('timestamp', ctypes.c_uint),
		('file', ctypes.c_char_p),
		('windowID', ctypes.c_uint),
	]


class SDL_SensorEvent(ctypes.Structure):
	_fields_ = [
		('type', ctypes.c_uint),
		('timestamp', ctypes.c_uint),
		('which', ctypes.c_int32),
		('data[6]', ctypes.c_float),
		('timestamp_us', ctypes.c_ulonglong),
	]


class SDL_QuitEvent(ctypes.Structure):
	_fields_ = [
		('type', ctypes.c_uint),
		('timestamp', ctypes.c_uint),
	]


class SDL_UserEvent(ctypes.Structure):
	_fields_ = [
		('type', ctypes.c_uint),
		('timestamp', ctypes.c_uint),
		('windowID', ctypes.c_uint),
		('code', ctypes.c_int32),
		('data1', ctypes.c_void_p),
		('data2', ctypes.c_void_p),
	]


class SDL_SysWMEvent(ctypes.Structure):
	_fields_ = [
		('type', ctypes.c_uint),
		('timestamp', ctypes.c_uint),
		('msg', ctypes.POINTER(SDL_SysWMmsg)),
	]


class SDL_Event(ctypes.Union):
	_fields_ = [
		('type', ctypes.c_uint),
		('common', SDL_CommonEvent),
		('display', SDL_DisplayEvent),
		('window', SDL_WindowEvent),
		('key', SDL_KeyboardEvent),
		('edit', SDL_TextEditingEvent),
		('editExt', SDL_TextEditingExtEvent),
		('text', SDL_TextInputEvent),
		('motion', SDL_MouseMotionEvent),
		('button', SDL_MouseButtonEvent),
		('wheel', SDL_MouseWheelEvent),
		('jaxis', SDL_JoyAxisEvent),
		('jball', SDL_JoyBallEvent),
		('jhat', SDL_JoyHatEvent),
		('jbutton', SDL_JoyButtonEvent),
		('jdevice', SDL_JoyDeviceEvent),
		('jbattery', SDL_JoyBatteryEvent),
		('caxis', SDL_ControllerAxisEvent),
		('cbutton', SDL_ControllerButtonEvent),
		('cdevice', SDL_ControllerDeviceEvent),
		('ctouchpad', SDL_ControllerTouchpadEvent),
		('csensor', SDL_ControllerSensorEvent),
		('adevice', SDL_AudioDeviceEvent),
		('sensor', SDL_SensorEvent),
		('quit', SDL_QuitEvent),
		('user', SDL_UserEvent),
		('syswm', SDL_SysWMEvent),
		('tfinger', SDL_TouchFingerEvent),
		('mgesture', SDL_MultiGestureEvent),
		('dgesture', SDL_DollarGestureEvent),
		('drop', SDL_DropEvent),
		('padding', ctypes.c_uint8),
	]

LoadDLL.DLL.SDL_PumpEvents.restype = None
LoadDLL.DLL.SDL_PumpEvents.argtypes = []

def SDL_PumpEvents():
	"""
	Args:
		: None.
	Returns:
		res: None.
	"""
	LoadDLL.DLL.SDL_PumpEvents()


LoadDLL.DLL.SDL_PeepEvents.restype = ctypes.c_int
LoadDLL.DLL.SDL_PeepEvents.argtypes = [ctypes.POINTER(SDL_Event), ctypes.c_int, ctypes.c_int, ctypes.c_uint, ctypes.c_uint]

def SDL_PeepEvents(events, numevents, action, minType, maxType):
	"""
	Args:
		events: ctypes.POINTER(SDL_Event).
		numevents: ctypes.c_int.
		action: SDL_eventaction.
		minType: ctypes.c_uint.
		maxType: ctypes.c_uint.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_PeepEvents(events, numevents, action, minType, maxType)


LoadDLL.DLL.SDL_HasEvents.restype = ctypes.c_int
LoadDLL.DLL.SDL_HasEvents.argtypes = [ctypes.c_uint, ctypes.c_uint]

def SDL_HasEvents(minType, maxType):
	"""
	Args:
		minType: ctypes.c_uint.
		maxType: ctypes.c_uint.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_HasEvents(minType, maxType)


LoadDLL.DLL.SDL_FlushEvent.restype = None
LoadDLL.DLL.SDL_FlushEvent.argtypes = [ctypes.c_uint]

def SDL_FlushEvent(type):
	"""
	Args:
		type: ctypes.c_uint.
	Returns:
		res: None.
	"""
	LoadDLL.DLL.SDL_FlushEvent(type)


LoadDLL.DLL.SDL_FlushEvents.restype = None
LoadDLL.DLL.SDL_FlushEvents.argtypes = [ctypes.c_uint, ctypes.c_uint]

def SDL_FlushEvents(minType, maxType):
	"""
	Args:
		minType: ctypes.c_uint.
		maxType: ctypes.c_uint.
	Returns:
		res: None.
	"""
	LoadDLL.DLL.SDL_FlushEvents(minType, maxType)


LoadDLL.DLL.SDL_PollEvent.restype = ctypes.c_int
LoadDLL.DLL.SDL_PollEvent.argtypes = [ctypes.POINTER(SDL_Event)]

def SDL_PollEvent(event):
	"""
	Args:
		event: ctypes.POINTER(SDL_Event).
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_PollEvent(event)


LoadDLL.DLL.SDL_WaitEvent.restype = ctypes.c_int
LoadDLL.DLL.SDL_WaitEvent.argtypes = [ctypes.POINTER(SDL_Event)]

def SDL_WaitEvent(event):
	"""
	Args:
		event: ctypes.POINTER(SDL_Event).
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_WaitEvent(event)


LoadDLL.DLL.SDL_WaitEventTimeout.restype = ctypes.c_int
LoadDLL.DLL.SDL_WaitEventTimeout.argtypes = [ctypes.POINTER(SDL_Event), ctypes.c_int]

def SDL_WaitEventTimeout(event, timeout):
	"""
	Args:
		event: ctypes.POINTER(SDL_Event).
		timeout: ctypes.c_int.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_WaitEventTimeout(event, timeout)


LoadDLL.DLL.SDL_EventState.restype = ctypes.c_ubyte
LoadDLL.DLL.SDL_EventState.argtypes = [ctypes.c_uint, ctypes.c_int]

def SDL_EventState(type, state):
	"""
	Args:
		type: ctypes.c_uint.
		state: ctypes.c_int.
	Returns:
		res: ctypes.c_ubyte.
	"""
	return LoadDLL.DLL.SDL_EventState(type, state)


LoadDLL.DLL.SDL_RegisterEvents.restype = ctypes.c_uint
LoadDLL.DLL.SDL_RegisterEvents.argtypes = [ctypes.c_int]

def SDL_RegisterEvents(numevents):
	"""
	Args:
		numevents: ctypes.c_int.
	Returns:
		res: ctypes.c_uint.
	"""
	return LoadDLL.DLL.SDL_RegisterEvents(numevents)