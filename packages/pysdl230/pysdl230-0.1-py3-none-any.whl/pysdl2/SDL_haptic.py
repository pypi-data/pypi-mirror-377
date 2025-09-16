import ctypes
from .LoadDLL import LoadDLL
from .SDL_joystick import SDL_Joystick


SDL_HAPTIC_POLAR = 0

SDL_HAPTIC_CARTESIAN = 1

SDL_HAPTIC_SPHERICAL = 2

SDL_HAPTIC_STEERING_AXIS = 3

SDL_HAPTIC_INFINITY = 4294967295


class SDL_HapticDirection(ctypes.Structure):
	_fields_ = [
		('type', ctypes.c_ubyte),
		('dir', ctypes.c_int32 * 3),
	]


class SDL_HapticConstant(ctypes.Structure):
	_fields_ = [
		('type', ctypes.c_ushort),
		('direction', SDL_HapticDirection),
		('length', ctypes.c_uint),
		('delay', ctypes.c_ushort),
		('button', ctypes.c_ushort),
		('interval', ctypes.c_ushort),
		('level', ctypes.c_int16),
		('attack_length', ctypes.c_ushort),
		('attack_level', ctypes.c_ushort),
		('fade_length', ctypes.c_ushort),
		('fade_level', ctypes.c_ushort),
	]


class SDL_HapticPeriodic(ctypes.Structure):
	_fields_ = [
		('type', ctypes.c_ushort),
		('direction', SDL_HapticDirection),
		('length', ctypes.c_uint),
		('delay', ctypes.c_ushort),
		('button', ctypes.c_ushort),
		('interval', ctypes.c_ushort),
		('period', ctypes.c_ushort),
		('magnitude', ctypes.c_int16),
		('offset', ctypes.c_int16),
		('phase', ctypes.c_ushort),
		('attack_length', ctypes.c_ushort),
		('attack_level', ctypes.c_ushort),
		('fade_length', ctypes.c_ushort),
		('fade_level', ctypes.c_ushort),
	]


class SDL_HapticCondition(ctypes.Structure):
	_fields_ = [
		('type', ctypes.c_ushort),
		('direction', SDL_HapticDirection),
		('length', ctypes.c_uint),
		('delay', ctypes.c_ushort),
		('button', ctypes.c_ushort),
		('interval', ctypes.c_ushort),
		('right_sat', ctypes.c_ushort * 3),
		('left_sat', ctypes.c_ushort * 3),
		('right_coeff', ctypes.c_int16 * 3),
		('left_coeff', ctypes.c_int16 * 3),
		('deadband', ctypes.c_ushort * 3),
		('center', ctypes.c_int16 * 3),
	]


class SDL_HapticRamp(ctypes.Structure):
	_fields_ = [
		('type', ctypes.c_ushort),
		('direction', SDL_HapticDirection),
		('length', ctypes.c_uint),
		('delay', ctypes.c_ushort),
		('button', ctypes.c_ushort),
		('interval', ctypes.c_ushort),
		('start', ctypes.c_int16),
		('end', ctypes.c_int16),
		('attack_length', ctypes.c_ushort),
		('attack_level', ctypes.c_ushort),
		('fade_length', ctypes.c_ushort),
		('fade_level', ctypes.c_ushort),
	]


class SDL_HapticLeftRight(ctypes.Structure):
	_fields_ = [
		('type', ctypes.c_ushort),
		('length', ctypes.c_uint),
		('large_magnitude', ctypes.c_ushort),
		('small_magnitude', ctypes.c_ushort),
	]


class SDL_HapticCustom(ctypes.Structure):
	_fields_ = [
		('type', ctypes.c_ushort),
		('direction', SDL_HapticDirection),
		('length', ctypes.c_uint),
		('delay', ctypes.c_ushort),
		('button', ctypes.c_ushort),
		('interval', ctypes.c_ushort),
		('channels', ctypes.c_ubyte),
		('period', ctypes.c_ushort),
		('samples', ctypes.c_ushort),
		('data', ctypes.POINTER(ctypes.c_ushort)),
		('attack_length', ctypes.c_ushort),
		('attack_level', ctypes.c_ushort),
		('fade_length', ctypes.c_ushort),
		('fade_level', ctypes.c_ushort),
	]


class SDL_Haptic(ctypes.Structure): pass


class SDL_HapticEffect(ctypes.Union):
	_fields_ = [
		('type', ctypes.c_ushort),
		('ant', SDL_HapticConstant),
		('periodic', SDL_HapticPeriodic),
		('condition', SDL_HapticCondition),
		('ramp', SDL_HapticRamp),
		('leftright', SDL_HapticLeftRight),
		('custom', SDL_HapticCustom),
	]


LoadDLL.DLL.SDL_NumHaptics.restype = ctypes.c_int
LoadDLL.DLL.SDL_NumHaptics.argtypes = []

def SDL_NumHaptics():
	"""
	Args:
		: None.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_NumHaptics()


LoadDLL.DLL.SDL_HapticName.restype = ctypes.c_char_p
LoadDLL.DLL.SDL_HapticName.argtypes = [ctypes.c_int]

def SDL_HapticName(device_index):
	"""
	Args:
		device_index: ctypes.c_int.
	Returns:
		res: ctypes.c_char_p.
	"""
	return LoadDLL.DLL.SDL_HapticName(device_index)


LoadDLL.DLL.SDL_HapticOpen.restype = ctypes.POINTER(SDL_Haptic)
LoadDLL.DLL.SDL_HapticOpen.argtypes = [ctypes.c_int]

def SDL_HapticOpen(device_index):
	"""
	Args:
		device_index: ctypes.c_int.
	Returns:
		res: ctypes.POINTER(SDL_Haptic).
	"""
	return LoadDLL.DLL.SDL_HapticOpen(device_index)


LoadDLL.DLL.SDL_HapticOpened.restype = ctypes.c_int
LoadDLL.DLL.SDL_HapticOpened.argtypes = [ctypes.c_int]

def SDL_HapticOpened(device_index):
	"""
	Args:
		device_index: ctypes.c_int.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_HapticOpened(device_index)


LoadDLL.DLL.SDL_HapticIndex.restype = ctypes.c_int
LoadDLL.DLL.SDL_HapticIndex.argtypes = [ctypes.POINTER(SDL_Haptic)]

def SDL_HapticIndex(haptic):
	"""
	Args:
		haptic: ctypes.POINTER(SDL_Haptic).
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_HapticIndex(haptic)


LoadDLL.DLL.SDL_MouseIsHaptic.restype = ctypes.c_int
LoadDLL.DLL.SDL_MouseIsHaptic.argtypes = []

def SDL_MouseIsHaptic():
	"""
	Args:
		: None.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_MouseIsHaptic()


LoadDLL.DLL.SDL_HapticOpenFromMouse.restype = ctypes.POINTER(SDL_Haptic)
LoadDLL.DLL.SDL_HapticOpenFromMouse.argtypes = []

def SDL_HapticOpenFromMouse():
	"""
	Args:
		: None.
	Returns:
		res: ctypes.POINTER(SDL_Haptic).
	"""
	return LoadDLL.DLL.SDL_HapticOpenFromMouse()


LoadDLL.DLL.SDL_JoystickIsHaptic.restype = ctypes.c_int
LoadDLL.DLL.SDL_JoystickIsHaptic.argtypes = [ctypes.POINTER(SDL_Joystick)]

def SDL_JoystickIsHaptic(joystick):
	"""
	Args:
		joystick: ctypes.POINTER(SDL_Joystick).
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_JoystickIsHaptic(joystick)


LoadDLL.DLL.SDL_HapticOpenFromJoystick.restype = ctypes.POINTER(SDL_Haptic)
LoadDLL.DLL.SDL_HapticOpenFromJoystick.argtypes = [ctypes.POINTER(SDL_Joystick)]

def SDL_HapticOpenFromJoystick(joystick):
	"""
	Args:
		joystick: ctypes.POINTER(SDL_Joystick).
	Returns:
		res: ctypes.POINTER(SDL_Haptic).
	"""
	return LoadDLL.DLL.SDL_HapticOpenFromJoystick(joystick)


LoadDLL.DLL.SDL_HapticNumEffects.restype = ctypes.c_int
LoadDLL.DLL.SDL_HapticNumEffects.argtypes = [ctypes.POINTER(SDL_Haptic)]

def SDL_HapticNumEffects(haptic):
	"""
	Args:
		haptic: ctypes.POINTER(SDL_Haptic).
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_HapticNumEffects(haptic)


LoadDLL.DLL.SDL_HapticNumEffectsPlaying.restype = ctypes.c_int
LoadDLL.DLL.SDL_HapticNumEffectsPlaying.argtypes = [ctypes.POINTER(SDL_Haptic)]

def SDL_HapticNumEffectsPlaying(haptic):
	"""
	Args:
		haptic: ctypes.POINTER(SDL_Haptic).
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_HapticNumEffectsPlaying(haptic)


LoadDLL.DLL.SDL_HapticQuery.restype = ctypes.c_uint
LoadDLL.DLL.SDL_HapticQuery.argtypes = [ctypes.POINTER(SDL_Haptic)]

def SDL_HapticQuery(haptic):
	"""
	Args:
		haptic: ctypes.POINTER(SDL_Haptic).
	Returns:
		res: ctypes.c_uint.
	"""
	return LoadDLL.DLL.SDL_HapticQuery(haptic)


LoadDLL.DLL.SDL_HapticNumAxes.restype = ctypes.c_int
LoadDLL.DLL.SDL_HapticNumAxes.argtypes = [ctypes.POINTER(SDL_Haptic)]

def SDL_HapticNumAxes(haptic):
	"""
	Args:
		haptic: ctypes.POINTER(SDL_Haptic).
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_HapticNumAxes(haptic)


LoadDLL.DLL.SDL_HapticEffectSupported.restype = ctypes.c_int
LoadDLL.DLL.SDL_HapticEffectSupported.argtypes = [ctypes.POINTER(SDL_Haptic), ctypes.POINTER(SDL_HapticEffect)]

def SDL_HapticEffectSupported(haptic, effect):
	"""
	Args:
		haptic: ctypes.POINTER(SDL_Haptic).
		effect: ctypes.POINTER(SDL_HapticEffect).
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_HapticEffectSupported(haptic, effect)


LoadDLL.DLL.SDL_HapticUpdateEffect.restype = ctypes.c_int
LoadDLL.DLL.SDL_HapticUpdateEffect.argtypes = [ctypes.POINTER(SDL_Haptic), ctypes.c_int, ctypes.POINTER(SDL_HapticEffect)]

def SDL_HapticUpdateEffect(haptic, effect, data):
	"""
	Args:
		haptic: ctypes.POINTER(SDL_Haptic).
		effect: ctypes.c_int.
		data: ctypes.POINTER(SDL_HapticEffect).
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_HapticUpdateEffect(haptic, effect, data)


LoadDLL.DLL.SDL_HapticStopEffect.restype = ctypes.c_int
LoadDLL.DLL.SDL_HapticStopEffect.argtypes = [ctypes.POINTER(SDL_Haptic), ctypes.c_int]

def SDL_HapticStopEffect(haptic, effect):
	"""
	Args:
		haptic: ctypes.POINTER(SDL_Haptic).
		effect: ctypes.c_int.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_HapticStopEffect(haptic, effect)


LoadDLL.DLL.SDL_HapticGetEffectStatus.restype = ctypes.c_int
LoadDLL.DLL.SDL_HapticGetEffectStatus.argtypes = [ctypes.POINTER(SDL_Haptic), ctypes.c_int]

def SDL_HapticGetEffectStatus(haptic, effect):
	"""
	Args:
		haptic: ctypes.POINTER(SDL_Haptic).
		effect: ctypes.c_int.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_HapticGetEffectStatus(haptic, effect)


LoadDLL.DLL.SDL_HapticSetAutocenter.restype = ctypes.c_int
LoadDLL.DLL.SDL_HapticSetAutocenter.argtypes = [ctypes.POINTER(SDL_Haptic), ctypes.c_int]

def SDL_HapticSetAutocenter(haptic, autocenter):
	"""
	Args:
		haptic: ctypes.POINTER(SDL_Haptic).
		autocenter: ctypes.c_int.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_HapticSetAutocenter(haptic, autocenter)


LoadDLL.DLL.SDL_HapticUnpause.restype = ctypes.c_int
LoadDLL.DLL.SDL_HapticUnpause.argtypes = [ctypes.POINTER(SDL_Haptic)]

def SDL_HapticUnpause(haptic):
	"""
	Args:
		haptic: ctypes.POINTER(SDL_Haptic).
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_HapticUnpause(haptic)


LoadDLL.DLL.SDL_HapticStopAll.restype = ctypes.c_int
LoadDLL.DLL.SDL_HapticStopAll.argtypes = [ctypes.POINTER(SDL_Haptic)]

def SDL_HapticStopAll(haptic):
	"""
	Args:
		haptic: ctypes.POINTER(SDL_Haptic).
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_HapticStopAll(haptic)


LoadDLL.DLL.SDL_HapticRumbleSupported.restype = ctypes.c_int
LoadDLL.DLL.SDL_HapticRumbleSupported.argtypes = [ctypes.POINTER(SDL_Haptic)]

def SDL_HapticRumbleSupported(haptic):
	"""
	Args:
		haptic: ctypes.POINTER(SDL_Haptic).
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_HapticRumbleSupported(haptic)


LoadDLL.DLL.SDL_HapticRumbleInit.restype = ctypes.c_int
LoadDLL.DLL.SDL_HapticRumbleInit.argtypes = [ctypes.POINTER(SDL_Haptic)]

def SDL_HapticRumbleInit(haptic):
	"""
	Args:
		haptic: ctypes.POINTER(SDL_Haptic).
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_HapticRumbleInit(haptic)


LoadDLL.DLL.SDL_HapticRumblePlay.restype = ctypes.c_int
LoadDLL.DLL.SDL_HapticRumblePlay.argtypes = [ctypes.POINTER(SDL_Haptic), ctypes.c_float, ctypes.c_uint]

def SDL_HapticRumblePlay(haptic, strength, length):
	"""
	Args:
		haptic: ctypes.POINTER(SDL_Haptic).
		strength: ctypes.c_float.
		length: ctypes.c_uint.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_HapticRumblePlay(haptic, strength, length)


LoadDLL.DLL.SDL_HapticRumbleStop.restype = ctypes.c_int
LoadDLL.DLL.SDL_HapticRumbleStop.argtypes = [ctypes.POINTER(SDL_Haptic)]

def SDL_HapticRumbleStop(haptic):
	"""
	Args:
		haptic: ctypes.POINTER(SDL_Haptic).
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_HapticRumbleStop(haptic)