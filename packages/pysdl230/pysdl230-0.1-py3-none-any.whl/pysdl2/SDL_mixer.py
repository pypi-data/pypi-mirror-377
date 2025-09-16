import ctypes
from .LoadDLL import MixerDLL
from .SDL_rwops import SDL_RWops
from .SDL_audio import AUDIO_S16SYS


SDL_MIXER_MAJOR_VERSION = 2

SDL_MIXER_MINOR_VERSION = 8

SDL_MIXER_PATCHLEVEL = 1

MIX_MAJOR_VERSION = SDL_MIXER_MAJOR_VERSION

MIX_MINOR_VERSION = SDL_MIXER_MINOR_VERSION

MIX_DEFAULT_FORMAT = AUDIO_S16SYS

MIX_DEFAULT_CHUNKSIZE = 2048

MIX_PATCHLEVEL = SDL_MIXER_PATCHLEVEL

MIX_CHANNELS = 8

MIX_DEFAULT_FREQUENCY = 44100

MIX_DEFAULT_CHANNELS = 2

MIX_EFFECTSMAXSPEED = "MIX_EFFECTSMAXSPEED"


class MIX_InitFlags:
	MIX_INIT_FLAC = 0x00000001
	MIX_INIT_MOD = 0x00000002
	MIX_INIT_MP3 = 0x00000008
	MIX_INIT_OGG = 0x00000010
	MIX_INIT_MID = 0x00000020
	MIX_INIT_OPUS = 0x00000040
	MIX_INIT_WAVPACK = 0x00000080


class Mix_Fading:
	MIX_NO_FADING = 0
	MIX_FADING_OUT = 1
	MIX_FADING_IN = 2


class Mix_MusicType:
	MUS_NONE = 0
	MUS_CMD = 1
	MUS_WAV = 2
	MUS_MOD = 3
	MUS_MID = 4
	MUS_OGG = 5
	MUS_MP3 = 6
	MUS_MP3_MAD_UNUSED = 7
	MUS_FLAC = 8
	MUS_MODPLUG_UNUSED = 9
	MUS_OPUS = 10
	MUS_WAVPACK = 11
	MUS_GME = 12


class Mix_Music(ctypes.Structure): pass


class Mix_Chunk(ctypes.Structure):
	_fields_ = [
		('allocated', ctypes.c_int),
		('abuf', ctypes.POINTER(ctypes.c_ubyte)),
		('alen', ctypes.c_uint),
		('volume', ctypes.c_ubyte),
	]

MixerDLL.DLL.Mix_Init.restype = ctypes.c_int
MixerDLL.DLL.Mix_Init.argtypes = [ctypes.c_int]

def Mix_Init(flags):
	"""
	Args:
		flags: ctypes.c_int.
	Returns:
		res: ctypes.c_int.
	"""
	return MixerDLL.DLL.Mix_Init(flags)


MixerDLL.DLL.Mix_Quit.restype = None
MixerDLL.DLL.Mix_Quit.argtypes = []

def Mix_Quit():
	"""
	Args:
		: None.
	Returns:
		res: None.
	"""
	MixerDLL.DLL.Mix_Quit()


MixerDLL.DLL.Mix_OpenAudio.restype = ctypes.c_int
MixerDLL.DLL.Mix_OpenAudio.argtypes = [ctypes.c_int, ctypes.c_ushort, ctypes.c_int, ctypes.c_int]

def Mix_OpenAudio(frequency, format, channels, chunksize):
	"""
	Args:
		frequency: ctypes.c_int.
		format: ctypes.c_ushort.
		channels: ctypes.c_int.
		chunksize: ctypes.c_int.
	Returns:
		res: ctypes.c_int.
	"""
	return MixerDLL.DLL.Mix_OpenAudio(frequency, format, channels, chunksize)


MixerDLL.DLL.Mix_OpenAudioDevice.restype = ctypes.c_int
MixerDLL.DLL.Mix_OpenAudioDevice.argtypes = [ctypes.c_int, ctypes.c_ushort, ctypes.c_int, ctypes.c_int, ctypes.c_char_p, ctypes.c_int]

def Mix_OpenAudioDevice(frequency, format, channels, chunksize, device, allowed_changes):
	"""
	Args:
		frequency: ctypes.c_int.
		format: ctypes.c_ushort.
		channels: ctypes.c_int.
		chunksize: ctypes.c_int.
		device: ctypes.c_char_p.
		allowed_changes: ctypes.c_int.
	Returns:
		res: ctypes.c_int.
	"""
	return MixerDLL.DLL.Mix_OpenAudioDevice(frequency, format, channels, chunksize, device, allowed_changes)


MixerDLL.DLL.Mix_PauseAudio.restype = None
MixerDLL.DLL.Mix_PauseAudio.argtypes = [ctypes.c_int]

def Mix_PauseAudio(pause_on):
	"""
	Args:
		pause_on: ctypes.c_int.
	Returns:
		res: None.
	"""
	MixerDLL.DLL.Mix_PauseAudio(pause_on)


MixerDLL.DLL.Mix_QuerySpec.restype = ctypes.c_int
MixerDLL.DLL.Mix_QuerySpec.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_ushort), ctypes.POINTER(ctypes.c_int)]

def Mix_QuerySpec(frequency, format, channels):
	"""
	Args:
		frequency: ctypes.POINTER(ctypes.c_int).
		format: ctypes.POINTER(ctypes.c_ushort).
		channels: ctypes.POINTER(ctypes.c_int).
	Returns:
		res: ctypes.c_int.
	"""
	return MixerDLL.DLL.Mix_QuerySpec(frequency, format, channels)


MixerDLL.DLL.Mix_AllocateChannels.restype = ctypes.c_int
MixerDLL.DLL.Mix_AllocateChannels.argtypes = [ctypes.c_int]

def Mix_AllocateChannels(numchans):
	"""
	Args:
		numchans: ctypes.c_int.
	Returns:
		res: ctypes.c_int.
	"""
	return MixerDLL.DLL.Mix_AllocateChannels(numchans)


MixerDLL.DLL.Mix_LoadWAV_RW.restype = ctypes.POINTER(Mix_Chunk)
MixerDLL.DLL.Mix_LoadWAV_RW.argtypes = [ctypes.POINTER(SDL_RWops), ctypes.c_int]

def Mix_LoadWAV_RW(src, freesrc):
	"""
	Args:
		src: ctypes.POINTER(SDL_RWops).
		freesrc: ctypes.c_int.
	Returns:
		res: ctypes.POINTER(Mix_Chunk).
	"""
	return MixerDLL.DLL.Mix_LoadWAV_RW(src, freesrc)


MixerDLL.DLL.Mix_LoadWAV.restype = ctypes.POINTER(Mix_Chunk)
MixerDLL.DLL.Mix_LoadWAV.argtypes = [ctypes.c_char_p]

def Mix_LoadWAV(file):
	"""
	Args:
		file: ctypes.c_char_p.
	Returns:
		res: ctypes.POINTER(Mix_Chunk).
	"""
	return MixerDLL.DLL.Mix_LoadWAV(file)


MixerDLL.DLL.Mix_LoadMUS.restype = ctypes.POINTER(Mix_Music)
MixerDLL.DLL.Mix_LoadMUS.argtypes = [ctypes.c_char_p]

def Mix_LoadMUS(file):
	"""
	Args:
		file: ctypes.c_char_p.
	Returns:
		res: ctypes.POINTER(Mix_Music).
	"""
	return MixerDLL.DLL.Mix_LoadMUS(file)


MixerDLL.DLL.Mix_LoadMUS_RW.restype = ctypes.POINTER(Mix_Music)
MixerDLL.DLL.Mix_LoadMUS_RW.argtypes = [ctypes.POINTER(SDL_RWops), ctypes.c_int]

def Mix_LoadMUS_RW(src, freesrc):
	"""
	Args:
		src: ctypes.POINTER(SDL_RWops).
		freesrc: ctypes.c_int.
	Returns:
		res: ctypes.POINTER(Mix_Music).
	"""
	return MixerDLL.DLL.Mix_LoadMUS_RW(src, freesrc)


MixerDLL.DLL.Mix_LoadMUSType_RW.restype = ctypes.POINTER(Mix_Music)
MixerDLL.DLL.Mix_LoadMUSType_RW.argtypes = [ctypes.POINTER(SDL_RWops), ctypes.c_int, ctypes.c_int]

def Mix_LoadMUSType_RW(src, type, freesrc):
	"""
	Args:
		src: ctypes.POINTER(SDL_RWops).
		type: Mix_MusicType.
		freesrc: ctypes.c_int.
	Returns:
		res: ctypes.POINTER(Mix_Music).
	"""
	return MixerDLL.DLL.Mix_LoadMUSType_RW(src, type, freesrc)


MixerDLL.DLL.Mix_QuickLoad_WAV.restype = ctypes.POINTER(Mix_Chunk)
MixerDLL.DLL.Mix_QuickLoad_WAV.argtypes = [ctypes.POINTER(ctypes.c_ubyte)]

def Mix_QuickLoad_WAV(mem):
	"""
	Args:
		mem: ctypes.POINTER(ctypes.c_ubyte).
	Returns:
		res: ctypes.POINTER(Mix_Chunk).
	"""
	return MixerDLL.DLL.Mix_QuickLoad_WAV(mem)


MixerDLL.DLL.Mix_QuickLoad_RAW.restype = ctypes.POINTER(Mix_Chunk)
MixerDLL.DLL.Mix_QuickLoad_RAW.argtypes = [ctypes.POINTER(ctypes.c_ubyte), ctypes.c_uint]

def Mix_QuickLoad_RAW(mem, len_):
	"""
	Args:
		mem: ctypes.POINTER(ctypes.c_ubyte).
		len_: ctypes.c_uint.
	Returns:
		res: ctypes.POINTER(Mix_Chunk).
	"""
	return MixerDLL.DLL.Mix_QuickLoad_RAW(mem, len_)


MixerDLL.DLL.Mix_FreeChunk.restype = None
MixerDLL.DLL.Mix_FreeChunk.argtypes = [ctypes.POINTER(Mix_Chunk)]

def Mix_FreeChunk(chunk):
	"""
	Args:
		chunk: ctypes.POINTER(Mix_Chunk).
	Returns:
		res: None.
	"""
	MixerDLL.DLL.Mix_FreeChunk(chunk)


MixerDLL.DLL.Mix_FreeMusic.restype = None
MixerDLL.DLL.Mix_FreeMusic.argtypes = [ctypes.POINTER(Mix_Music)]

def Mix_FreeMusic(music):
	"""
	Args:
		music: ctypes.POINTER(Mix_Music).
	Returns:
		res: None.
	"""
	MixerDLL.DLL.Mix_FreeMusic(music)


MixerDLL.DLL.Mix_GetNumChunkDecoders.restype = ctypes.c_int
MixerDLL.DLL.Mix_GetNumChunkDecoders.argtypes = []

def Mix_GetNumChunkDecoders():
	"""
	Args:
		: None.
	Returns:
		res: ctypes.c_int.
	"""
	return MixerDLL.DLL.Mix_GetNumChunkDecoders()


MixerDLL.DLL.Mix_GetChunkDecoder.restype = ctypes.c_char_p
MixerDLL.DLL.Mix_GetChunkDecoder.argtypes = [ctypes.c_int]

def Mix_GetChunkDecoder(index):
	"""
	Args:
		index: ctypes.c_int.
	Returns:
		res: ctypes.c_char_p.
	"""
	return MixerDLL.DLL.Mix_GetChunkDecoder(index)


MixerDLL.DLL.Mix_HasChunkDecoder.restype = ctypes.c_int
MixerDLL.DLL.Mix_HasChunkDecoder.argtypes = [ctypes.c_char_p]

def Mix_HasChunkDecoder(name):
	"""
	Args:
		name: ctypes.c_char_p.
	Returns:
		res: ctypes.c_int.
	"""
	return MixerDLL.DLL.Mix_HasChunkDecoder(name)


MixerDLL.DLL.Mix_GetNumMusicDecoders.restype = ctypes.c_int
MixerDLL.DLL.Mix_GetNumMusicDecoders.argtypes = []

def Mix_GetNumMusicDecoders():
	"""
	Args:
		: None.
	Returns:
		res: ctypes.c_int.
	"""
	return MixerDLL.DLL.Mix_GetNumMusicDecoders()


MixerDLL.DLL.Mix_GetMusicDecoder.restype = ctypes.c_char_p
MixerDLL.DLL.Mix_GetMusicDecoder.argtypes = [ctypes.c_int]

def Mix_GetMusicDecoder(index):
	"""
	Args:
		index: ctypes.c_int.
	Returns:
		res: ctypes.c_char_p.
	"""
	return MixerDLL.DLL.Mix_GetMusicDecoder(index)


MixerDLL.DLL.Mix_HasMusicDecoder.restype = ctypes.c_int
MixerDLL.DLL.Mix_HasMusicDecoder.argtypes = [ctypes.c_char_p]

def Mix_HasMusicDecoder(name):
	"""
	Args:
		name: ctypes.c_char_p.
	Returns:
		res: ctypes.c_int.
	"""
	return MixerDLL.DLL.Mix_HasMusicDecoder(name)


MixerDLL.DLL.Mix_GetMusicType.restype = ctypes.c_int
MixerDLL.DLL.Mix_GetMusicType.argtypes = [ctypes.POINTER(Mix_Music)]

def Mix_GetMusicType(music):
	"""
	Args:
		music: ctypes.POINTER(Mix_Music).
	Returns:
		res: Mix_MusicType.
	"""
	return MixerDLL.DLL.Mix_GetMusicType(music)


MixerDLL.DLL.Mix_GetMusicTitle.restype = ctypes.c_char_p
MixerDLL.DLL.Mix_GetMusicTitle.argtypes = [ctypes.POINTER(Mix_Music)]

def Mix_GetMusicTitle(music):
	"""
	Args:
		music: ctypes.POINTER(Mix_Music).
	Returns:
		res: ctypes.c_char_p.
	"""
	return MixerDLL.DLL.Mix_GetMusicTitle(music)


MixerDLL.DLL.Mix_GetMusicTitleTag.restype = ctypes.c_char_p
MixerDLL.DLL.Mix_GetMusicTitleTag.argtypes = [ctypes.POINTER(Mix_Music)]

def Mix_GetMusicTitleTag(music):
	"""
	Args:
		music: ctypes.POINTER(Mix_Music).
	Returns:
		res: ctypes.c_char_p.
	"""
	return MixerDLL.DLL.Mix_GetMusicTitleTag(music)


MixerDLL.DLL.Mix_GetMusicArtistTag.restype = ctypes.c_char_p
MixerDLL.DLL.Mix_GetMusicArtistTag.argtypes = [ctypes.POINTER(Mix_Music)]

def Mix_GetMusicArtistTag(music):
	"""
	Args:
		music: ctypes.POINTER(Mix_Music).
	Returns:
		res: ctypes.c_char_p.
	"""
	return MixerDLL.DLL.Mix_GetMusicArtistTag(music)


MixerDLL.DLL.Mix_GetMusicAlbumTag.restype = ctypes.c_char_p
MixerDLL.DLL.Mix_GetMusicAlbumTag.argtypes = [ctypes.POINTER(Mix_Music)]

def Mix_GetMusicAlbumTag(music):
	"""
	Args:
		music: ctypes.POINTER(Mix_Music).
	Returns:
		res: ctypes.c_char_p.
	"""
	return MixerDLL.DLL.Mix_GetMusicAlbumTag(music)


MixerDLL.DLL.Mix_GetMusicCopyrightTag.restype = ctypes.c_char_p
MixerDLL.DLL.Mix_GetMusicCopyrightTag.argtypes = [ctypes.POINTER(Mix_Music)]

def Mix_GetMusicCopyrightTag(music):
	"""
	Args:
		music: ctypes.POINTER(Mix_Music).
	Returns:
		res: ctypes.c_char_p.
	"""
	return MixerDLL.DLL.Mix_GetMusicCopyrightTag(music)


MixerDLL.DLL.Mix_GetMusicHookData.restype = ctypes.c_void_p
MixerDLL.DLL.Mix_GetMusicHookData.argtypes = []

def Mix_GetMusicHookData():
	"""
	Args:
		: None.
	Returns:
		res: ctypes.c_void_p.
	"""
	return MixerDLL.DLL.Mix_GetMusicHookData()


MixerDLL.DLL.Mix_SetPanning.restype = ctypes.c_int
MixerDLL.DLL.Mix_SetPanning.argtypes = [ctypes.c_int, ctypes.c_ubyte, ctypes.c_ubyte]

def Mix_SetPanning(channel, left, right):
	"""
	Args:
		channel: ctypes.c_int.
		left: ctypes.c_ubyte.
		right: ctypes.c_ubyte.
	Returns:
		res: ctypes.c_int.
	"""
	return MixerDLL.DLL.Mix_SetPanning(channel, left, right)


MixerDLL.DLL.Mix_SetPosition.restype = ctypes.c_int
MixerDLL.DLL.Mix_SetPosition.argtypes = [ctypes.c_int, ctypes.c_int16, ctypes.c_ubyte]

def Mix_SetPosition(channel, angle, distance):
	"""
	Args:
		channel: ctypes.c_int.
		angle: ctypes.c_int16.
		distance: ctypes.c_ubyte.
	Returns:
		res: ctypes.c_int.
	"""
	return MixerDLL.DLL.Mix_SetPosition(channel, angle, distance)


MixerDLL.DLL.Mix_SetDistance.restype = ctypes.c_int
MixerDLL.DLL.Mix_SetDistance.argtypes = [ctypes.c_int, ctypes.c_ubyte]

def Mix_SetDistance(channel, distance):
	"""
	Args:
		channel: ctypes.c_int.
		distance: ctypes.c_ubyte.
	Returns:
		res: ctypes.c_int.
	"""
	return MixerDLL.DLL.Mix_SetDistance(channel, distance)


MixerDLL.DLL.Mix_SetReverseStereo.restype = ctypes.c_int
MixerDLL.DLL.Mix_SetReverseStereo.argtypes = [ctypes.c_int, ctypes.c_int]

def Mix_SetReverseStereo(channel, flip):
	"""
	Args:
		channel: ctypes.c_int.
		flip: ctypes.c_int.
	Returns:
		res: ctypes.c_int.
	"""
	return MixerDLL.DLL.Mix_SetReverseStereo(channel, flip)


MixerDLL.DLL.Mix_ReserveChannels.restype = ctypes.c_int
MixerDLL.DLL.Mix_ReserveChannels.argtypes = [ctypes.c_int]

def Mix_ReserveChannels(num):
	"""
	Args:
		num: ctypes.c_int.
	Returns:
		res: ctypes.c_int.
	"""
	return MixerDLL.DLL.Mix_ReserveChannels(num)


MixerDLL.DLL.Mix_GroupChannel.restype = ctypes.c_int
MixerDLL.DLL.Mix_GroupChannel.argtypes = [ctypes.c_int, ctypes.c_int]

def Mix_GroupChannel(which, tag):
	"""
	Args:
		which: ctypes.c_int.
		tag: ctypes.c_int.
	Returns:
		res: ctypes.c_int.
	"""
	return MixerDLL.DLL.Mix_GroupChannel(which, tag)


MixerDLL.DLL.Mix_GroupChannels.restype = ctypes.c_int
MixerDLL.DLL.Mix_GroupChannels.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int]

def Mix_GroupChannels(from_, to, tag):
	"""
	Args:
		from: ctypes.c_int.
		to: ctypes.c_int.
		tag: ctypes.c_int.
	Returns:
		res: ctypes.c_int.
	"""
	return MixerDLL.DLL.Mix_GroupChannels(from_, to, tag)


MixerDLL.DLL.Mix_GroupAvailable.restype = ctypes.c_int
MixerDLL.DLL.Mix_GroupAvailable.argtypes = [ctypes.c_int]

def Mix_GroupAvailable(tag):
	"""
	Args:
		tag: ctypes.c_int.
	Returns:
		res: ctypes.c_int.
	"""
	return MixerDLL.DLL.Mix_GroupAvailable(tag)


MixerDLL.DLL.Mix_GroupCount.restype = ctypes.c_int
MixerDLL.DLL.Mix_GroupCount.argtypes = [ctypes.c_int]

def Mix_GroupCount(tag):
	"""
	Args:
		tag: ctypes.c_int.
	Returns:
		res: ctypes.c_int.
	"""
	return MixerDLL.DLL.Mix_GroupCount(tag)


MixerDLL.DLL.Mix_GroupOldest.restype = ctypes.c_int
MixerDLL.DLL.Mix_GroupOldest.argtypes = [ctypes.c_int]

def Mix_GroupOldest(tag):
	"""
	Args:
		tag: ctypes.c_int.
	Returns:
		res: ctypes.c_int.
	"""
	return MixerDLL.DLL.Mix_GroupOldest(tag)


MixerDLL.DLL.Mix_GroupNewer.restype = ctypes.c_int
MixerDLL.DLL.Mix_GroupNewer.argtypes = [ctypes.c_int]

def Mix_GroupNewer(tag):
	"""
	Args:
		tag: ctypes.c_int.
	Returns:
		res: ctypes.c_int.
	"""
	return MixerDLL.DLL.Mix_GroupNewer(tag)


MixerDLL.DLL.Mix_PlayChannel.restype = ctypes.c_int
MixerDLL.DLL.Mix_PlayChannel.argtypes = [ctypes.c_int, ctypes.POINTER(Mix_Chunk), ctypes.c_int]

def Mix_PlayChannel(channel, chunk, loops):
	"""
	Args:
		channel: ctypes.c_int.
		chunk: ctypes.POINTER(Mix_Chunk).
		loops: ctypes.c_int.
	Returns:
		res: ctypes.c_int.
	"""
	return MixerDLL.DLL.Mix_PlayChannel(channel, chunk, loops)


MixerDLL.DLL.Mix_PlayChannelTimed.restype = ctypes.c_int
MixerDLL.DLL.Mix_PlayChannelTimed.argtypes = [ctypes.c_int, ctypes.POINTER(Mix_Chunk), ctypes.c_int, ctypes.c_int]

def Mix_PlayChannelTimed(channel, chunk, loops, ticks):
	"""
	Args:
		channel: ctypes.c_int.
		chunk: ctypes.POINTER(Mix_Chunk).
		loops: ctypes.c_int.
		ticks: ctypes.c_int.
	Returns:
		res: ctypes.c_int.
	"""
	return MixerDLL.DLL.Mix_PlayChannelTimed(channel, chunk, loops, ticks)


MixerDLL.DLL.Mix_PlayMusic.restype = ctypes.c_int
MixerDLL.DLL.Mix_PlayMusic.argtypes = [ctypes.POINTER(Mix_Music), ctypes.c_int]

def Mix_PlayMusic(music, loops):
	"""
	Args:
		music: ctypes.POINTER(Mix_Music).
		loops: ctypes.c_int.
	Returns:
		res: ctypes.c_int.
	"""
	return MixerDLL.DLL.Mix_PlayMusic(music, loops)


MixerDLL.DLL.Mix_FadeInMusic.restype = ctypes.c_int
MixerDLL.DLL.Mix_FadeInMusic.argtypes = [ctypes.POINTER(Mix_Music), ctypes.c_int, ctypes.c_int]

def Mix_FadeInMusic(music, loops, ms):
	"""
	Args:
		music: ctypes.POINTER(Mix_Music).
		loops: ctypes.c_int.
		ms: ctypes.c_int.
	Returns:
		res: ctypes.c_int.
	"""
	return MixerDLL.DLL.Mix_FadeInMusic(music, loops, ms)


MixerDLL.DLL.Mix_FadeInMusicPos.restype = ctypes.c_int
MixerDLL.DLL.Mix_FadeInMusicPos.argtypes = [ctypes.POINTER(Mix_Music), ctypes.c_int, ctypes.c_int, ctypes.c_double]

def Mix_FadeInMusicPos(music, loops, ms, position):
	"""
	Args:
		music: ctypes.POINTER(Mix_Music).
		loops: ctypes.c_int.
		ms: ctypes.c_int.
		position: ctypes.c_double.
	Returns:
		res: ctypes.c_int.
	"""
	return MixerDLL.DLL.Mix_FadeInMusicPos(music, loops, ms, position)


MixerDLL.DLL.Mix_FadeInChannel.restype = ctypes.c_int
MixerDLL.DLL.Mix_FadeInChannel.argtypes = [ctypes.c_int, ctypes.POINTER(Mix_Chunk), ctypes.c_int, ctypes.c_int]

def Mix_FadeInChannel(channel, chunk, loops, ms):
	"""
	Args:
		channel: ctypes.c_int.
		chunk: ctypes.POINTER(Mix_Chunk).
		loops: ctypes.c_int.
		ms: ctypes.c_int.
	Returns:
		res: ctypes.c_int.
	"""
	return MixerDLL.DLL.Mix_FadeInChannel(channel, chunk, loops, ms)


MixerDLL.DLL.Mix_FadeInChannelTimed.restype = ctypes.c_int
MixerDLL.DLL.Mix_FadeInChannelTimed.argtypes = [ctypes.c_int, ctypes.POINTER(Mix_Chunk), ctypes.c_int, ctypes.c_int, ctypes.c_int]

def Mix_FadeInChannelTimed(channel, chunk, loops, ms, ticks):
	"""
	Args:
		channel: ctypes.c_int.
		chunk: ctypes.POINTER(Mix_Chunk).
		loops: ctypes.c_int.
		ms: ctypes.c_int.
		ticks: ctypes.c_int.
	Returns:
		res: ctypes.c_int.
	"""
	return MixerDLL.DLL.Mix_FadeInChannelTimed(channel, chunk, loops, ms, ticks)


MixerDLL.DLL.Mix_Volume.restype = ctypes.c_int
MixerDLL.DLL.Mix_Volume.argtypes = [ctypes.c_int, ctypes.c_int]

def Mix_Volume(channel, volume):
	"""
	Args:
		channel: ctypes.c_int.
		volume: ctypes.c_int.
	Returns:
		res: ctypes.c_int.
	"""
	return MixerDLL.DLL.Mix_Volume(channel, volume)


MixerDLL.DLL.Mix_VolumeChunk.restype = ctypes.c_int
MixerDLL.DLL.Mix_VolumeChunk.argtypes = [ctypes.POINTER(Mix_Chunk), ctypes.c_int]

def Mix_VolumeChunk(chunk, volume):
	"""
	Args:
		chunk: ctypes.POINTER(Mix_Chunk).
		volume: ctypes.c_int.
	Returns:
		res: ctypes.c_int.
	"""
	return MixerDLL.DLL.Mix_VolumeChunk(chunk, volume)


MixerDLL.DLL.Mix_VolumeMusic.restype = ctypes.c_int
MixerDLL.DLL.Mix_VolumeMusic.argtypes = [ctypes.c_int]

def Mix_VolumeMusic(volume):
	"""
	Args:
		volume: ctypes.c_int.
	Returns:
		res: ctypes.c_int.
	"""
	return MixerDLL.DLL.Mix_VolumeMusic(volume)


MixerDLL.DLL.Mix_GetMusicVolume.restype = ctypes.c_int
MixerDLL.DLL.Mix_GetMusicVolume.argtypes = [ctypes.POINTER(Mix_Music)]

def Mix_GetMusicVolume(music):
	"""
	Args:
		music: ctypes.POINTER(Mix_Music).
	Returns:
		res: ctypes.c_int.
	"""
	return MixerDLL.DLL.Mix_GetMusicVolume(music)


MixerDLL.DLL.Mix_MasterVolume.restype = ctypes.c_int
MixerDLL.DLL.Mix_MasterVolume.argtypes = [ctypes.c_int]

def Mix_MasterVolume(volume):
	"""
	Args:
		volume: ctypes.c_int.
	Returns:
		res: ctypes.c_int.
	"""
	return MixerDLL.DLL.Mix_MasterVolume(volume)


MixerDLL.DLL.Mix_HaltChannel.restype = ctypes.c_int
MixerDLL.DLL.Mix_HaltChannel.argtypes = [ctypes.c_int]

def Mix_HaltChannel(channel):
	"""
	Args:
		channel: ctypes.c_int.
	Returns:
		res: ctypes.c_int.
	"""
	return MixerDLL.DLL.Mix_HaltChannel(channel)


MixerDLL.DLL.Mix_HaltGroup.restype = ctypes.c_int
MixerDLL.DLL.Mix_HaltGroup.argtypes = [ctypes.c_int]

def Mix_HaltGroup(tag):
	"""
	Args:
		tag: ctypes.c_int.
	Returns:
		res: ctypes.c_int.
	"""
	return MixerDLL.DLL.Mix_HaltGroup(tag)


MixerDLL.DLL.Mix_HaltMusic.restype = ctypes.c_int
MixerDLL.DLL.Mix_HaltMusic.argtypes = []

def Mix_HaltMusic():
	"""
	Args:
		: None.
	Returns:
		res: ctypes.c_int.
	"""
	return MixerDLL.DLL.Mix_HaltMusic()


MixerDLL.DLL.Mix_ExpireChannel.restype = ctypes.c_int
MixerDLL.DLL.Mix_ExpireChannel.argtypes = [ctypes.c_int, ctypes.c_int]

def Mix_ExpireChannel(channel, ticks):
	"""
	Args:
		channel: ctypes.c_int.
		ticks: ctypes.c_int.
	Returns:
		res: ctypes.c_int.
	"""
	return MixerDLL.DLL.Mix_ExpireChannel(channel, ticks)


MixerDLL.DLL.Mix_FadeOutChannel.restype = ctypes.c_int
MixerDLL.DLL.Mix_FadeOutChannel.argtypes = [ctypes.c_int, ctypes.c_int]

def Mix_FadeOutChannel(which, ms):
	"""
	Args:
		which: ctypes.c_int.
		ms: ctypes.c_int.
	Returns:
		res: ctypes.c_int.
	"""
	return MixerDLL.DLL.Mix_FadeOutChannel(which, ms)


MixerDLL.DLL.Mix_FadeOutGroup.restype = ctypes.c_int
MixerDLL.DLL.Mix_FadeOutGroup.argtypes = [ctypes.c_int, ctypes.c_int]

def Mix_FadeOutGroup(tag, ms):
	"""
	Args:
		tag: ctypes.c_int.
		ms: ctypes.c_int.
	Returns:
		res: ctypes.c_int.
	"""
	return MixerDLL.DLL.Mix_FadeOutGroup(tag, ms)


MixerDLL.DLL.Mix_FadeOutMusic.restype = ctypes.c_int
MixerDLL.DLL.Mix_FadeOutMusic.argtypes = [ctypes.c_int]

def Mix_FadeOutMusic(ms):
	"""
	Args:
		ms: ctypes.c_int.
	Returns:
		res: ctypes.c_int.
	"""
	return MixerDLL.DLL.Mix_FadeOutMusic(ms)


MixerDLL.DLL.Mix_FadingMusic.restype = ctypes.c_int
MixerDLL.DLL.Mix_FadingMusic.argtypes = []

def Mix_FadingMusic():
	"""
	Args:
		: None.
	Returns:
		res: Mix_Fading.
	"""
	return MixerDLL.DLL.Mix_FadingMusic()


MixerDLL.DLL.Mix_FadingChannel.restype = ctypes.c_int
MixerDLL.DLL.Mix_FadingChannel.argtypes = [ctypes.c_int]

def Mix_FadingChannel(which):
	"""
	Args:
		which: ctypes.c_int.
	Returns:
		res: Mix_Fading.
	"""
	return MixerDLL.DLL.Mix_FadingChannel(which)


MixerDLL.DLL.Mix_Pause.restype = None
MixerDLL.DLL.Mix_Pause.argtypes = [ctypes.c_int]

def Mix_Pause(channel):
	"""
	Args:
		channel: ctypes.c_int.
	Returns:
		res: None.
	"""
	MixerDLL.DLL.Mix_Pause(channel)


MixerDLL.DLL.Mix_Resume.restype = None
MixerDLL.DLL.Mix_Resume.argtypes = [ctypes.c_int]

def Mix_Resume(channel):
	"""
	Args:
		channel: ctypes.c_int.
	Returns:
		res: None.
	"""
	MixerDLL.DLL.Mix_Resume(channel)


MixerDLL.DLL.Mix_Paused.restype = ctypes.c_int
MixerDLL.DLL.Mix_Paused.argtypes = [ctypes.c_int]

def Mix_Paused(channel):
	"""
	Args:
		channel: ctypes.c_int.
	Returns:
		res: ctypes.c_int.
	"""
	return MixerDLL.DLL.Mix_Paused(channel)


MixerDLL.DLL.Mix_PauseMusic.restype = None
MixerDLL.DLL.Mix_PauseMusic.argtypes = []

def Mix_PauseMusic():
	"""
	Args:
		: None.
	Returns:
		res: None.
	"""
	MixerDLL.DLL.Mix_PauseMusic()


MixerDLL.DLL.Mix_ResumeMusic.restype = None
MixerDLL.DLL.Mix_ResumeMusic.argtypes = []

def Mix_ResumeMusic():
	"""
	Args:
		: None.
	Returns:
		res: None.
	"""
	MixerDLL.DLL.Mix_ResumeMusic()


MixerDLL.DLL.Mix_RewindMusic.restype = None
MixerDLL.DLL.Mix_RewindMusic.argtypes = []

def Mix_RewindMusic():
	"""
	Args:
		: None.
	Returns:
		res: None.
	"""
	MixerDLL.DLL.Mix_RewindMusic()


MixerDLL.DLL.Mix_PausedMusic.restype = ctypes.c_int
MixerDLL.DLL.Mix_PausedMusic.argtypes = []

def Mix_PausedMusic():
	"""
	Args:
		: None.
	Returns:
		res: ctypes.c_int.
	"""
	return MixerDLL.DLL.Mix_PausedMusic()


MixerDLL.DLL.Mix_ModMusicJumpToOrder.restype = ctypes.c_int
MixerDLL.DLL.Mix_ModMusicJumpToOrder.argtypes = [ctypes.c_int]

def Mix_ModMusicJumpToOrder(order):
	"""
	Args:
		order: ctypes.c_int.
	Returns:
		res: ctypes.c_int.
	"""
	return MixerDLL.DLL.Mix_ModMusicJumpToOrder(order)


MixerDLL.DLL.Mix_StartTrack.restype = ctypes.c_int
MixerDLL.DLL.Mix_StartTrack.argtypes = [ctypes.POINTER(Mix_Music), ctypes.c_int]

def Mix_StartTrack(music, track):
	"""
	Args:
		music: ctypes.POINTER(Mix_Music).
		track: ctypes.c_int.
	Returns:
		res: ctypes.c_int.
	"""
	return MixerDLL.DLL.Mix_StartTrack(music, track)


MixerDLL.DLL.Mix_GetNumTracks.restype = ctypes.c_int
MixerDLL.DLL.Mix_GetNumTracks.argtypes = [ctypes.POINTER(Mix_Music)]

def Mix_GetNumTracks(music):
	"""
	Args:
		music: ctypes.POINTER(Mix_Music).
	Returns:
		res: ctypes.c_int.
	"""
	return MixerDLL.DLL.Mix_GetNumTracks(music)


MixerDLL.DLL.Mix_SetMusicPosition.restype = ctypes.c_int
MixerDLL.DLL.Mix_SetMusicPosition.argtypes = [ctypes.c_double]

def Mix_SetMusicPosition(position):
	"""
	Args:
		position: ctypes.c_double.
	Returns:
		res: ctypes.c_int.
	"""
	return MixerDLL.DLL.Mix_SetMusicPosition(position)


MixerDLL.DLL.Mix_GetMusicPosition.restype = ctypes.c_double
MixerDLL.DLL.Mix_GetMusicPosition.argtypes = [ctypes.POINTER(Mix_Music)]

def Mix_GetMusicPosition(music):
	"""
	Args:
		music: ctypes.POINTER(Mix_Music).
	Returns:
		res: ctypes.c_double.
	"""
	return MixerDLL.DLL.Mix_GetMusicPosition(music)


MixerDLL.DLL.Mix_MusicDuration.restype = ctypes.c_double
MixerDLL.DLL.Mix_MusicDuration.argtypes = [ctypes.POINTER(Mix_Music)]

def Mix_MusicDuration(music):
	"""
	Args:
		music: ctypes.POINTER(Mix_Music).
	Returns:
		res: ctypes.c_double.
	"""
	return MixerDLL.DLL.Mix_MusicDuration(music)


MixerDLL.DLL.Mix_GetMusicLoopStartTime.restype = ctypes.c_double
MixerDLL.DLL.Mix_GetMusicLoopStartTime.argtypes = [ctypes.POINTER(Mix_Music)]

def Mix_GetMusicLoopStartTime(music):
	"""
	Args:
		music: ctypes.POINTER(Mix_Music).
	Returns:
		res: ctypes.c_double.
	"""
	return MixerDLL.DLL.Mix_GetMusicLoopStartTime(music)


MixerDLL.DLL.Mix_GetMusicLoopEndTime.restype = ctypes.c_double
MixerDLL.DLL.Mix_GetMusicLoopEndTime.argtypes = [ctypes.POINTER(Mix_Music)]

def Mix_GetMusicLoopEndTime(music):
	"""
	Args:
		music: ctypes.POINTER(Mix_Music).
	Returns:
		res: ctypes.c_double.
	"""
	return MixerDLL.DLL.Mix_GetMusicLoopEndTime(music)


MixerDLL.DLL.Mix_GetMusicLoopLengthTime.restype = ctypes.c_double
MixerDLL.DLL.Mix_GetMusicLoopLengthTime.argtypes = [ctypes.POINTER(Mix_Music)]

def Mix_GetMusicLoopLengthTime(music):
	"""
	Args:
		music: ctypes.POINTER(Mix_Music).
	Returns:
		res: ctypes.c_double.
	"""
	return MixerDLL.DLL.Mix_GetMusicLoopLengthTime(music)


MixerDLL.DLL.Mix_Playing.restype = ctypes.c_int
MixerDLL.DLL.Mix_Playing.argtypes = [ctypes.c_int]

def Mix_Playing(channel):
	"""
	Args:
		channel: ctypes.c_int.
	Returns:
		res: ctypes.c_int.
	"""
	return MixerDLL.DLL.Mix_Playing(channel)


MixerDLL.DLL.Mix_PlayingMusic.restype = ctypes.c_int
MixerDLL.DLL.Mix_PlayingMusic.argtypes = []

def Mix_PlayingMusic():
	"""
	Args:
		: None.
	Returns:
		res: ctypes.c_int.
	"""
	return MixerDLL.DLL.Mix_PlayingMusic()


MixerDLL.DLL.Mix_SetMusicCMD.restype = ctypes.c_int
MixerDLL.DLL.Mix_SetMusicCMD.argtypes = [ctypes.c_char_p]

def Mix_SetMusicCMD(command):
	"""
	Args:
		command: ctypes.c_char_p.
	Returns:
		res: ctypes.c_int.
	"""
	return MixerDLL.DLL.Mix_SetMusicCMD(command)


MixerDLL.DLL.Mix_SetSynchroValue.restype = ctypes.c_int
MixerDLL.DLL.Mix_SetSynchroValue.argtypes = [ctypes.c_int]

def Mix_SetSynchroValue(value):
	"""
	Args:
		value: ctypes.c_int.
	Returns:
		res: ctypes.c_int.
	"""
	return MixerDLL.DLL.Mix_SetSynchroValue(value)


MixerDLL.DLL.Mix_GetSynchroValue.restype = ctypes.c_int
MixerDLL.DLL.Mix_GetSynchroValue.argtypes = []

def Mix_GetSynchroValue():
	"""
	Args:
		: None.
	Returns:
		res: ctypes.c_int.
	"""
	return MixerDLL.DLL.Mix_GetSynchroValue()


MixerDLL.DLL.Mix_SetSoundFonts.restype = ctypes.c_int
MixerDLL.DLL.Mix_SetSoundFonts.argtypes = [ctypes.c_char_p]

def Mix_SetSoundFonts(paths):
	"""
	Args:
		paths: ctypes.c_char_p.
	Returns:
		res: ctypes.c_int.
	"""
	return MixerDLL.DLL.Mix_SetSoundFonts(paths)


MixerDLL.DLL.Mix_GetSoundFonts.restype = ctypes.c_char_p
MixerDLL.DLL.Mix_GetSoundFonts.argtypes = []

def Mix_GetSoundFonts():
	"""
	Args:
		: None.
	Returns:
		res: ctypes.c_char_p.
	"""
	return MixerDLL.DLL.Mix_GetSoundFonts()


MixerDLL.DLL.Mix_SetTimidityCfg.restype = ctypes.c_int
MixerDLL.DLL.Mix_SetTimidityCfg.argtypes = [ctypes.c_char_p]

def Mix_SetTimidityCfg(path):
	"""
	Args:
		path: ctypes.c_char_p.
	Returns:
		res: ctypes.c_int.
	"""
	return MixerDLL.DLL.Mix_SetTimidityCfg(path)


MixerDLL.DLL.Mix_GetTimidityCfg.restype = ctypes.c_char_p
MixerDLL.DLL.Mix_GetTimidityCfg.argtypes = []

def Mix_GetTimidityCfg():
	"""
	Args:
		: None.
	Returns:
		res: ctypes.c_char_p.
	"""
	return MixerDLL.DLL.Mix_GetTimidityCfg()


MixerDLL.DLL.Mix_GetChunk.restype = ctypes.POINTER(Mix_Chunk)
MixerDLL.DLL.Mix_GetChunk.argtypes = [ctypes.c_int]

def Mix_GetChunk(channel):
	"""
	Args:
		channel: ctypes.c_int.
	Returns:
		res: ctypes.POINTER(Mix_Chunk).
	"""
	return MixerDLL.DLL.Mix_GetChunk(channel)


MixerDLL.DLL.Mix_CloseAudio.restype = None
MixerDLL.DLL.Mix_CloseAudio.argtypes = []

def Mix_CloseAudio():
	"""
	Args:
		: None.
	Returns:
		res: None.
	"""
	MixerDLL.DLL.Mix_CloseAudio()