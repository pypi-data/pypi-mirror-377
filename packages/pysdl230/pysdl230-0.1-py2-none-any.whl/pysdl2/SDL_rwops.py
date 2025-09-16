import ctypes
from .LoadDLL import LoadDLL


SDL_RWOPS_UNKNOWN = 0

SDL_RWOPS_WINFILE = 1

SDL_RWOPS_STDFILE = 2

SDL_RWOPS_JNIFILE = 3

SDL_RWOPS_MEMORY = 4

SDL_RWOPS_MEMORY_RO = 5

RW_SEEK_SET = 0

RW_SEEK_CUR = 1

RW_SEEK_END = 2


class SDL_RWops(ctypes.Structure): pass


LoadDLL.DLL.SDL_RWFromFile.restype = ctypes.POINTER(SDL_RWops)
LoadDLL.DLL.SDL_RWFromFile.argtypes = [ctypes.c_char_p, ctypes.c_char_p]

def SDL_RWFromFile(file, mode):
	"""
	Args:
		file: ctypes.c_char_p.
		mode: ctypes.c_char_p.
	Returns:
		res: ctypes.POINTER(SDL_RWops).
	"""
	return LoadDLL.DLL.SDL_RWFromFile(file, mode)


LoadDLL.DLL.SDL_RWFromFP.restype = ctypes.POINTER(SDL_RWops)
LoadDLL.DLL.SDL_RWFromFP.argtypes = [ctypes.c_void_p, ctypes.c_int]

def SDL_RWFromFP(fp, autoclose):
	"""
	Args:
		fp: ctypes.c_void_p.
		autoclose: ctypes.c_int.
	Returns:
		res: ctypes.POINTER(SDL_RWops).
	"""
	return LoadDLL.DLL.SDL_RWFromFP(fp, autoclose)


LoadDLL.DLL.SDL_RWFromConstMem.restype = ctypes.POINTER(SDL_RWops)
LoadDLL.DLL.SDL_RWFromConstMem.argtypes = [ctypes.c_void_p, ctypes.c_int]

def SDL_RWFromConstMem(mem, size):
	"""
	Args:
		mem: ctypes.c_void_p.
		size: ctypes.c_int.
	Returns:
		res: ctypes.POINTER(SDL_RWops).
	"""
	return LoadDLL.DLL.SDL_RWFromConstMem(mem, size)


LoadDLL.DLL.SDL_FreeRW.restype = None
LoadDLL.DLL.SDL_FreeRW.argtypes = [ctypes.POINTER(SDL_RWops)]

def SDL_FreeRW(area):
	"""
	Args:
		area: ctypes.POINTER(SDL_RWops).
	Returns:
		res: None.
	"""
	LoadDLL.DLL.SDL_FreeRW(area)


LoadDLL.DLL.SDL_RWsize.restype = ctypes.c_longlong
LoadDLL.DLL.SDL_RWsize.argtypes = [ctypes.POINTER(SDL_RWops)]

def SDL_RWsize(context):
	"""
	Args:
		context: ctypes.POINTER(SDL_RWops).
	Returns:
		res: ctypes.c_longlong.
	"""
	return LoadDLL.DLL.SDL_RWsize(context)


LoadDLL.DLL.SDL_RWseek.restype = ctypes.c_longlong
LoadDLL.DLL.SDL_RWseek.argtypes = [ctypes.POINTER(SDL_RWops), ctypes.c_longlong, ctypes.c_int]

def SDL_RWseek(context, offset, whence):
	"""
	Args:
		context: ctypes.POINTER(SDL_RWops).
		offset: ctypes.c_longlong.
		whence: ctypes.c_int.
	Returns:
		res: ctypes.c_longlong.
	"""
	return LoadDLL.DLL.SDL_RWseek(context, offset, whence)


LoadDLL.DLL.SDL_RWread.restype = ctypes.c_ulonglong
LoadDLL.DLL.SDL_RWread.argtypes = [ctypes.POINTER(SDL_RWops), ctypes.c_void_p, ctypes.c_ulonglong, ctypes.c_ulonglong]

def SDL_RWread(context, ptr, size, maxnum):
	"""
	Args:
		context: ctypes.POINTER(SDL_RWops).
		ptr: ctypes.c_void_p.
		size: ctypes.c_ulonglong.
		maxnum: ctypes.c_ulonglong.
	Returns:
		res: ctypes.c_ulonglong.
	"""
	return LoadDLL.DLL.SDL_RWread(context, ptr, size, maxnum)


LoadDLL.DLL.SDL_RWclose.restype = ctypes.c_int
LoadDLL.DLL.SDL_RWclose.argtypes = [ctypes.POINTER(SDL_RWops)]

def SDL_RWclose(context):
	"""
	Args:
		context: ctypes.POINTER(SDL_RWops).
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_RWclose(context)


LoadDLL.DLL.SDL_LoadFile_RW.restype = ctypes.c_void_p
LoadDLL.DLL.SDL_LoadFile_RW.argtypes = [ctypes.POINTER(SDL_RWops), ctypes.POINTER(ctypes.c_ulonglong), ctypes.c_int]

def SDL_LoadFile_RW(src, datasize, freesrc):
	"""
	Args:
		src: ctypes.POINTER(SDL_RWops).
		datasize: ctypes.POINTER(ctypes.c_ulonglong).
		freesrc: ctypes.c_int.
	Returns:
		res: ctypes.c_void_p.
	"""
	return LoadDLL.DLL.SDL_LoadFile_RW(src, datasize, freesrc)


LoadDLL.DLL.SDL_ReadU8.restype = ctypes.c_ubyte
LoadDLL.DLL.SDL_ReadU8.argtypes = [ctypes.POINTER(SDL_RWops)]

def SDL_ReadU8(src):
	"""
	Args:
		src: ctypes.POINTER(SDL_RWops).
	Returns:
		res: ctypes.c_ubyte.
	"""
	return LoadDLL.DLL.SDL_ReadU8(src)


LoadDLL.DLL.SDL_ReadLE16.restype = ctypes.c_ushort
LoadDLL.DLL.SDL_ReadLE16.argtypes = [ctypes.POINTER(SDL_RWops)]

def SDL_ReadLE16(src):
	"""
	Args:
		src: ctypes.POINTER(SDL_RWops).
	Returns:
		res: ctypes.c_ushort.
	"""
	return LoadDLL.DLL.SDL_ReadLE16(src)


LoadDLL.DLL.SDL_ReadBE16.restype = ctypes.c_ushort
LoadDLL.DLL.SDL_ReadBE16.argtypes = [ctypes.POINTER(SDL_RWops)]

def SDL_ReadBE16(src):
	"""
	Args:
		src: ctypes.POINTER(SDL_RWops).
	Returns:
		res: ctypes.c_ushort.
	"""
	return LoadDLL.DLL.SDL_ReadBE16(src)


LoadDLL.DLL.SDL_ReadLE32.restype = ctypes.c_uint
LoadDLL.DLL.SDL_ReadLE32.argtypes = [ctypes.POINTER(SDL_RWops)]

def SDL_ReadLE32(src):
	"""
	Args:
		src: ctypes.POINTER(SDL_RWops).
	Returns:
		res: ctypes.c_uint.
	"""
	return LoadDLL.DLL.SDL_ReadLE32(src)


LoadDLL.DLL.SDL_ReadBE32.restype = ctypes.c_uint
LoadDLL.DLL.SDL_ReadBE32.argtypes = [ctypes.POINTER(SDL_RWops)]

def SDL_ReadBE32(src):
	"""
	Args:
		src: ctypes.POINTER(SDL_RWops).
	Returns:
		res: ctypes.c_uint.
	"""
	return LoadDLL.DLL.SDL_ReadBE32(src)


LoadDLL.DLL.SDL_ReadLE64.restype = ctypes.c_ulonglong
LoadDLL.DLL.SDL_ReadLE64.argtypes = [ctypes.POINTER(SDL_RWops)]

def SDL_ReadLE64(src):
	"""
	Args:
		src: ctypes.POINTER(SDL_RWops).
	Returns:
		res: ctypes.c_ulonglong.
	"""
	return LoadDLL.DLL.SDL_ReadLE64(src)


LoadDLL.DLL.SDL_ReadBE64.restype = ctypes.c_ulonglong
LoadDLL.DLL.SDL_ReadBE64.argtypes = [ctypes.POINTER(SDL_RWops)]

def SDL_ReadBE64(src):
	"""
	Args:
		src: ctypes.POINTER(SDL_RWops).
	Returns:
		res: ctypes.c_ulonglong.
	"""
	return LoadDLL.DLL.SDL_ReadBE64(src)


LoadDLL.DLL.SDL_WriteU8.restype = ctypes.c_ulonglong
LoadDLL.DLL.SDL_WriteU8.argtypes = [ctypes.POINTER(SDL_RWops), ctypes.c_ubyte]

def SDL_WriteU8(dst, value):
	"""
	Args:
		dst: ctypes.POINTER(SDL_RWops).
		value: ctypes.c_ubyte.
	Returns:
		res: ctypes.c_ulonglong.
	"""
	return LoadDLL.DLL.SDL_WriteU8(dst, value)


LoadDLL.DLL.SDL_WriteLE16.restype = ctypes.c_ulonglong
LoadDLL.DLL.SDL_WriteLE16.argtypes = [ctypes.POINTER(SDL_RWops), ctypes.c_ushort]

def SDL_WriteLE16(dst, value):
	"""
	Args:
		dst: ctypes.POINTER(SDL_RWops).
		value: ctypes.c_ushort.
	Returns:
		res: ctypes.c_ulonglong.
	"""
	return LoadDLL.DLL.SDL_WriteLE16(dst, value)


LoadDLL.DLL.SDL_WriteBE16.restype = ctypes.c_ulonglong
LoadDLL.DLL.SDL_WriteBE16.argtypes = [ctypes.POINTER(SDL_RWops), ctypes.c_ushort]

def SDL_WriteBE16(dst, value):
	"""
	Args:
		dst: ctypes.POINTER(SDL_RWops).
		value: ctypes.c_ushort.
	Returns:
		res: ctypes.c_ulonglong.
	"""
	return LoadDLL.DLL.SDL_WriteBE16(dst, value)


LoadDLL.DLL.SDL_WriteLE32.restype = ctypes.c_ulonglong
LoadDLL.DLL.SDL_WriteLE32.argtypes = [ctypes.POINTER(SDL_RWops), ctypes.c_uint]

def SDL_WriteLE32(dst, value):
	"""
	Args:
		dst: ctypes.POINTER(SDL_RWops).
		value: ctypes.c_uint.
	Returns:
		res: ctypes.c_ulonglong.
	"""
	return LoadDLL.DLL.SDL_WriteLE32(dst, value)


LoadDLL.DLL.SDL_WriteBE32.restype = ctypes.c_ulonglong
LoadDLL.DLL.SDL_WriteBE32.argtypes = [ctypes.POINTER(SDL_RWops), ctypes.c_uint]

def SDL_WriteBE32(dst, value):
	"""
	Args:
		dst: ctypes.POINTER(SDL_RWops).
		value: ctypes.c_uint.
	Returns:
		res: ctypes.c_ulonglong.
	"""
	return LoadDLL.DLL.SDL_WriteBE32(dst, value)


LoadDLL.DLL.SDL_WriteLE64.restype = ctypes.c_ulonglong
LoadDLL.DLL.SDL_WriteLE64.argtypes = [ctypes.POINTER(SDL_RWops), ctypes.c_ulonglong]

def SDL_WriteLE64(dst, value):
	"""
	Args:
		dst: ctypes.POINTER(SDL_RWops).
		value: ctypes.c_ulonglong.
	Returns:
		res: ctypes.c_ulonglong.
	"""
	return LoadDLL.DLL.SDL_WriteLE64(dst, value)


LoadDLL.DLL.SDL_WriteBE64.restype = ctypes.c_ulonglong
LoadDLL.DLL.SDL_WriteBE64.argtypes = [ctypes.POINTER(SDL_RWops), ctypes.c_ulonglong]

def SDL_WriteBE64(dst, value):
	"""
	Args:
		dst: ctypes.POINTER(SDL_RWops).
		value: ctypes.c_ulonglong.
	Returns:
		res: ctypes.c_ulonglong.
	"""
	return LoadDLL.DLL.SDL_WriteBE64(dst, value)