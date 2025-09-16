import ctypes
from .LoadDLL import LoadDLL


AUDIO_U8 = 0x0008

AUDIO_S8 = 0x8008

AUDIO_U16LSB = 0x0010

AUDIO_S16LSB = 0x8010

AUDIO_U16MSB = 0x1010

AUDIO_S16MSB = 0x9010

AUDIO_U16 = AUDIO_U16LSB

AUDIO_S16 = AUDIO_S16LSB

AUDIO_S32LSB = 0x8020

AUDIO_S32MSB = 0x9020

AUDIO_S32 = AUDIO_S32LSB

AUDIO_F32LSB = 0x8120

AUDIO_F32MSB = 0x9120

AUDIO_F32 = AUDIO_F32LSB

AUDIO_U16SYS = AUDIO_U16LSB

AUDIO_S16SYS = AUDIO_S16LSB

AUDIO_S32SYS = AUDIO_S32LSB

AUDIO_F32SYS = AUDIO_F32LSB

AUDIO_U16SYS = AUDIO_U16MSB

AUDIO_S16SYS = AUDIO_S16MSB

AUDIO_S32SYS = AUDIO_S32MSB

AUDIO_F32SYS = AUDIO_F32MSB

SDL_AUDIO_ALLOW_FREQUENCY_CHANGE = 0x00000001

SDL_AUDIO_ALLOW_FORMAT_CHANGE = 0x00000002

SDL_AUDIO_ALLOW_CHANNELS_CHANGE = 0x00000004

SDL_AUDIO_ALLOW_SAMPLES_CHANGE = 0x00000008

SDL_AUDIOCVT_MAX_FILTERS = 9

SDL_MIX_MAXVOLUME = 128

class SDL_AudioStatus:
	SDL_AUDIO_STOPPED = 0
	SDL_AUDIO_PLAYING = 0
	SDL_AUDIO_PAUSED = 1


class SDL_AudioStream(ctypes.Structure): pass


class SDL_AudioFilter(ctypes.Structure): pass


class SDL_AudioSpec(ctypes.Structure):
	_fields_ = [
		('freq', ctypes.c_int),
		('format', ctypes.c_ushort),
		('channels', ctypes.c_ubyte),
		('silence', ctypes.c_ubyte),
		('samples', ctypes.c_ushort),
		('padding', ctypes.c_ushort),
		('size', ctypes.c_uint),
		('userdata', ctypes.c_void_p),
	]


class SDL_AudioCVT(ctypes.Structure):
	_fields_ = [
		('needed', ctypes.c_int),
		('src_format', ctypes.c_ushort),
		('dst_format', ctypes.c_ushort),
		('rate_incr', ctypes.c_double),
		('buf', ctypes.POINTER(ctypes.c_ubyte)),
		('len', ctypes.c_int),
		('len_cvt', ctypes.c_int),
		('len_mult', ctypes.c_int),
		('len_ratio', ctypes.c_double),
		('filters', SDL_AudioFilter * (SDL_AUDIOCVT_MAX_FILTERS + 1)),
		('filter_index', ctypes.c_int),
	]

LoadDLL.DLL.SDL_GetNumAudioDrivers.restype = ctypes.c_int
LoadDLL.DLL.SDL_GetNumAudioDrivers.argtypes = []

def SDL_GetNumAudioDrivers():
	"""
	Args:
		: None.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_GetNumAudioDrivers()


LoadDLL.DLL.SDL_GetAudioDriver.restype = ctypes.c_char_p
LoadDLL.DLL.SDL_GetAudioDriver.argtypes = [ctypes.c_int]

def SDL_GetAudioDriver(index):
	"""
	Args:
		index: ctypes.c_int.
	Returns:
		res: ctypes.c_char_p.
	"""
	return LoadDLL.DLL.SDL_GetAudioDriver(index)


LoadDLL.DLL.SDL_AudioInit.restype = ctypes.c_int
LoadDLL.DLL.SDL_AudioInit.argtypes = [ctypes.c_char_p]

def SDL_AudioInit(driver_name):
	"""
	Args:
		driver_name: ctypes.c_char_p.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_AudioInit(driver_name)


LoadDLL.DLL.SDL_AudioQuit.restype = None
LoadDLL.DLL.SDL_AudioQuit.argtypes = []

def SDL_AudioQuit():
	"""
	Args:
		: None.
	Returns:
		res: None.
	"""
	LoadDLL.DLL.SDL_AudioQuit()


LoadDLL.DLL.SDL_GetCurrentAudioDriver.restype = ctypes.c_char_p
LoadDLL.DLL.SDL_GetCurrentAudioDriver.argtypes = []

def SDL_GetCurrentAudioDriver():
	"""
	Args:
		: None.
	Returns:
		res: ctypes.c_char_p.
	"""
	return LoadDLL.DLL.SDL_GetCurrentAudioDriver()


LoadDLL.DLL.SDL_OpenAudio.restype = ctypes.c_int
LoadDLL.DLL.SDL_OpenAudio.argtypes = [ctypes.POINTER(SDL_AudioSpec), ctypes.POINTER(SDL_AudioSpec)]

def SDL_OpenAudio(desired, obtained):
	"""
	Args:
		desired: ctypes.POINTER(SDL_AudioSpec).
		obtained: ctypes.POINTER(SDL_AudioSpec).
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_OpenAudio(desired, obtained)


LoadDLL.DLL.SDL_GetNumAudioDevices.restype = ctypes.c_int
LoadDLL.DLL.SDL_GetNumAudioDevices.argtypes = [ctypes.c_int]

def SDL_GetNumAudioDevices(iscapture):
	"""
	Args:
		iscapture: ctypes.c_int.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_GetNumAudioDevices(iscapture)


LoadDLL.DLL.SDL_GetAudioDeviceName.restype = ctypes.c_char_p
LoadDLL.DLL.SDL_GetAudioDeviceName.argtypes = [ctypes.c_int, ctypes.c_int]

def SDL_GetAudioDeviceName(index, iscapture):
	"""
	Args:
		index: ctypes.c_int.
		iscapture: ctypes.c_int.
	Returns:
		res: ctypes.c_char_p.
	"""
	return LoadDLL.DLL.SDL_GetAudioDeviceName(index, iscapture)


LoadDLL.DLL.SDL_GetDefaultAudioInfo.restype = ctypes.c_int
LoadDLL.DLL.SDL_GetDefaultAudioInfo.argtypes = [ctypes.POINTER(ctypes.POINTER(ctypes.c_char)), ctypes.POINTER(SDL_AudioSpec), ctypes.c_int]

def SDL_GetDefaultAudioInfo(name, spec, iscapture):
	"""
	Args:
		name: ctypes.POINTER(ctypes.POINTER(ctypes.c_char)).
		spec: ctypes.POINTER(SDL_AudioSpec).
		iscapture: ctypes.c_int.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_GetDefaultAudioInfo(name, spec, iscapture)


LoadDLL.DLL.SDL_GetAudioStatus.restype = ctypes.c_int
LoadDLL.DLL.SDL_GetAudioStatus.argtypes = []

def SDL_GetAudioStatus():
	"""
	Args:
		: None.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_GetAudioStatus()


LoadDLL.DLL.SDL_GetAudioDeviceStatus.restype = ctypes.c_int
LoadDLL.DLL.SDL_GetAudioDeviceStatus.argtypes = [ctypes.c_uint]

def SDL_GetAudioDeviceStatus(dev):
	"""
	Args:
		dev: ctypes.c_uint.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_GetAudioDeviceStatus(dev)


LoadDLL.DLL.SDL_PauseAudio.restype = None
LoadDLL.DLL.SDL_PauseAudio.argtypes = [ctypes.c_int]

def SDL_PauseAudio(pause_on):
	"""
	Args:
		pause_on: ctypes.c_int.
	Returns:
		res: None.
	"""
	LoadDLL.DLL.SDL_PauseAudio(pause_on)


LoadDLL.DLL.SDL_PauseAudioDevice.restype = None
LoadDLL.DLL.SDL_PauseAudioDevice.argtypes = [ctypes.c_uint, ctypes.c_int]

def SDL_PauseAudioDevice(dev, pause_on):
	"""
	Args:
		dev: ctypes.c_uint.
		pause_on: ctypes.c_int.
	Returns:
		res: None.
	"""
	LoadDLL.DLL.SDL_PauseAudioDevice(dev, pause_on)


LoadDLL.DLL.SDL_ConvertAudio.restype = ctypes.c_int
LoadDLL.DLL.SDL_ConvertAudio.argtypes = [ctypes.POINTER(SDL_AudioCVT)]

def SDL_ConvertAudio(cvt):
	"""
	Args:
		cvt: ctypes.POINTER(SDL_AudioCVT).
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_ConvertAudio(cvt)


LoadDLL.DLL.SDL_NewAudioStream.restype = ctypes.POINTER(SDL_AudioStream)
LoadDLL.DLL.SDL_NewAudioStream.argtypes = [ctypes.c_ushort, ctypes.c_ubyte, ctypes.c_int, ctypes.c_ushort, ctypes.c_ubyte, ctypes.c_int]

def SDL_NewAudioStream(src_format, src_channels, src_rate, dst_format, dst_channels, dst_rate):
	"""
	Args:
		src_format: ctypes.c_ushort.
		src_channels: ctypes.c_ubyte.
		src_rate: ctypes.c_int.
		dst_format: ctypes.c_ushort.
		dst_channels: ctypes.c_ubyte.
		dst_rate: ctypes.c_int.
	Returns:
		res: ctypes.POINTER(SDL_AudioStream).
	"""
	return LoadDLL.DLL.SDL_NewAudioStream(src_format, src_channels, src_rate, dst_format, dst_channels, dst_rate)


LoadDLL.DLL.SDL_AudioStreamGet.restype = ctypes.c_int
LoadDLL.DLL.SDL_AudioStreamGet.argtypes = [ctypes.POINTER(SDL_AudioStream), ctypes.c_void_p, ctypes.c_int]

def SDL_AudioStreamGet(stream, buf, len):
	"""
	Args:
		stream: ctypes.POINTER(SDL_AudioStream).
		buf: ctypes.c_void_p.
		len: ctypes.c_int.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_AudioStreamGet(stream, buf, len)


LoadDLL.DLL.SDL_AudioStreamAvailable.restype = ctypes.c_int
LoadDLL.DLL.SDL_AudioStreamAvailable.argtypes = [ctypes.POINTER(SDL_AudioStream)]

def SDL_AudioStreamAvailable(stream):
	"""
	Args:
		stream: ctypes.POINTER(SDL_AudioStream).
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_AudioStreamAvailable(stream)


LoadDLL.DLL.SDL_AudioStreamFlush.restype = ctypes.c_int
LoadDLL.DLL.SDL_AudioStreamFlush.argtypes = [ctypes.POINTER(SDL_AudioStream)]

def SDL_AudioStreamFlush(stream):
	"""
	Args:
		stream: ctypes.POINTER(SDL_AudioStream).
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_AudioStreamFlush(stream)


LoadDLL.DLL.SDL_AudioStreamClear.restype = None
LoadDLL.DLL.SDL_AudioStreamClear.argtypes = [ctypes.POINTER(SDL_AudioStream)]

def SDL_AudioStreamClear(stream):
	"""
	Args:
		stream: ctypes.POINTER(SDL_AudioStream).
	Returns:
		res: None.
	"""
	LoadDLL.DLL.SDL_AudioStreamClear(stream)


LoadDLL.DLL.SDL_FreeAudioStream.restype = None
LoadDLL.DLL.SDL_FreeAudioStream.argtypes = [ctypes.POINTER(SDL_AudioStream)]

def SDL_FreeAudioStream(stream):
	"""
	Args:
		stream: ctypes.POINTER(SDL_AudioStream).
	Returns:
		res: None.
	"""
	LoadDLL.DLL.SDL_FreeAudioStream(stream)


LoadDLL.DLL.SDL_MixAudio.restype = None
LoadDLL.DLL.SDL_MixAudio.argtypes = [ctypes.POINTER(ctypes.c_ubyte), ctypes.POINTER(ctypes.c_ubyte), ctypes.c_uint, ctypes.c_int]

def SDL_MixAudio(dst, src, len, volume):
	"""
	Args:
		dst: ctypes.POINTER(ctypes.c_ubyte).
		src: ctypes.POINTER(ctypes.c_ubyte).
		len: ctypes.c_uint.
		volume: ctypes.c_int.
	Returns:
		res: None.
	"""
	LoadDLL.DLL.SDL_MixAudio(dst, src, len, volume)


LoadDLL.DLL.SDL_QueueAudio.restype = ctypes.c_int
LoadDLL.DLL.SDL_QueueAudio.argtypes = [ctypes.c_uint, ctypes.c_void_p, ctypes.c_uint]

def SDL_QueueAudio(dev, data, len):
	"""
	Args:
		dev: ctypes.c_uint.
		data: ctypes.c_void_p.
		len: ctypes.c_uint.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_QueueAudio(dev, data, len)


LoadDLL.DLL.SDL_DequeueAudio.restype = ctypes.c_uint
LoadDLL.DLL.SDL_DequeueAudio.argtypes = [ctypes.c_uint, ctypes.c_void_p, ctypes.c_uint]

def SDL_DequeueAudio(dev, data, len):
	"""
	Args:
		dev: ctypes.c_uint.
		data: ctypes.c_void_p.
		len: ctypes.c_uint.
	Returns:
		res: ctypes.c_uint.
	"""
	return LoadDLL.DLL.SDL_DequeueAudio(dev, data, len)


LoadDLL.DLL.SDL_GetQueuedAudioSize.restype = ctypes.c_uint
LoadDLL.DLL.SDL_GetQueuedAudioSize.argtypes = [ctypes.c_uint]

def SDL_GetQueuedAudioSize(dev):
	"""
	Args:
		dev: ctypes.c_uint.
	Returns:
		res: ctypes.c_uint.
	"""
	return LoadDLL.DLL.SDL_GetQueuedAudioSize(dev)


LoadDLL.DLL.SDL_ClearQueuedAudio.restype = None
LoadDLL.DLL.SDL_ClearQueuedAudio.argtypes = [ctypes.c_uint]

def SDL_ClearQueuedAudio(dev):
	"""
	Args:
		dev: ctypes.c_uint.
	Returns:
		res: None.
	"""
	LoadDLL.DLL.SDL_ClearQueuedAudio(dev)


LoadDLL.DLL.SDL_LockAudio.restype = None
LoadDLL.DLL.SDL_LockAudio.argtypes = []

def SDL_LockAudio():
	"""
	Args:
		: None.
	Returns:
		res: None.
	"""
	LoadDLL.DLL.SDL_LockAudio()


LoadDLL.DLL.SDL_LockAudioDevice.restype = None
LoadDLL.DLL.SDL_LockAudioDevice.argtypes = [ctypes.c_uint]

def SDL_LockAudioDevice(dev):
	"""
	Args:
		dev: ctypes.c_uint.
	Returns:
		res: None.
	"""
	LoadDLL.DLL.SDL_LockAudioDevice(dev)


LoadDLL.DLL.SDL_UnlockAudio.restype = None
LoadDLL.DLL.SDL_UnlockAudio.argtypes = []

def SDL_UnlockAudio():
	"""
	Args:
		: None.
	Returns:
		res: None.
	"""
	LoadDLL.DLL.SDL_UnlockAudio()


LoadDLL.DLL.SDL_UnlockAudioDevice.restype = None
LoadDLL.DLL.SDL_UnlockAudioDevice.argtypes = [ctypes.c_uint]

def SDL_UnlockAudioDevice(dev):
	"""
	Args:
		dev: ctypes.c_uint.
	Returns:
		res: None.
	"""
	LoadDLL.DLL.SDL_UnlockAudioDevice(dev)


LoadDLL.DLL.SDL_CloseAudio.restype = None
LoadDLL.DLL.SDL_CloseAudio.argtypes = []

def SDL_CloseAudio():
	"""
	Args:
		: None.
	Returns:
		res: None.
	"""
	LoadDLL.DLL.SDL_CloseAudio()


LoadDLL.DLL.SDL_CloseAudioDevice.restype = None
LoadDLL.DLL.SDL_CloseAudioDevice.argtypes = [ctypes.c_uint]

def SDL_CloseAudioDevice(dev):
	"""
	Args:
		dev: ctypes.c_uint.
	Returns:
		res: None.
	"""
	LoadDLL.DLL.SDL_CloseAudioDevice(dev)