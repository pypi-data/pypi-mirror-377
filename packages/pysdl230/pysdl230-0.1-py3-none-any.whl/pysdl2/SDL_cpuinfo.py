import ctypes
from .LoadDLL import LoadDLL


__ARM_NEON = 1

__ARM_NEON = 1

__ARM_ARCH = 8

SDL_CACHELINE_SIZE = 128

LoadDLL.DLL.SDL_GetCPUCount.restype = ctypes.c_int
LoadDLL.DLL.SDL_GetCPUCount.argtypes = []

def SDL_GetCPUCount():
	"""
	Args:
		: None.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_GetCPUCount()


LoadDLL.DLL.SDL_GetCPUCacheLineSize.restype = ctypes.c_int
LoadDLL.DLL.SDL_GetCPUCacheLineSize.argtypes = []

def SDL_GetCPUCacheLineSize():
	"""
	Args:
		: None.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_GetCPUCacheLineSize()


LoadDLL.DLL.SDL_HasRDTSC.restype = ctypes.c_int
LoadDLL.DLL.SDL_HasRDTSC.argtypes = []

def SDL_HasRDTSC():
	"""
	Args:
		: None.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_HasRDTSC()


LoadDLL.DLL.SDL_HasAltiVec.restype = ctypes.c_int
LoadDLL.DLL.SDL_HasAltiVec.argtypes = []

def SDL_HasAltiVec():
	"""
	Args:
		: None.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_HasAltiVec()


LoadDLL.DLL.SDL_HasMMX.restype = ctypes.c_int
LoadDLL.DLL.SDL_HasMMX.argtypes = []

def SDL_HasMMX():
	"""
	Args:
		: None.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_HasMMX()


LoadDLL.DLL.SDL_Has3DNow.restype = ctypes.c_int
LoadDLL.DLL.SDL_Has3DNow.argtypes = []

def SDL_Has3DNow():
	"""
	Args:
		: None.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_Has3DNow()


LoadDLL.DLL.SDL_HasSSE.restype = ctypes.c_int
LoadDLL.DLL.SDL_HasSSE.argtypes = []

def SDL_HasSSE():
	"""
	Args:
		: None.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_HasSSE()


LoadDLL.DLL.SDL_HasSSE2.restype = ctypes.c_int
LoadDLL.DLL.SDL_HasSSE2.argtypes = []

def SDL_HasSSE2():
	"""
	Args:
		: None.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_HasSSE2()


LoadDLL.DLL.SDL_HasSSE3.restype = ctypes.c_int
LoadDLL.DLL.SDL_HasSSE3.argtypes = []

def SDL_HasSSE3():
	"""
	Args:
		: None.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_HasSSE3()


LoadDLL.DLL.SDL_HasSSE41.restype = ctypes.c_int
LoadDLL.DLL.SDL_HasSSE41.argtypes = []

def SDL_HasSSE41():
	"""
	Args:
		: None.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_HasSSE41()


LoadDLL.DLL.SDL_HasSSE42.restype = ctypes.c_int
LoadDLL.DLL.SDL_HasSSE42.argtypes = []

def SDL_HasSSE42():
	"""
	Args:
		: None.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_HasSSE42()


LoadDLL.DLL.SDL_HasAVX.restype = ctypes.c_int
LoadDLL.DLL.SDL_HasAVX.argtypes = []

def SDL_HasAVX():
	"""
	Args:
		: None.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_HasAVX()


LoadDLL.DLL.SDL_HasAVX2.restype = ctypes.c_int
LoadDLL.DLL.SDL_HasAVX2.argtypes = []

def SDL_HasAVX2():
	"""
	Args:
		: None.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_HasAVX2()


LoadDLL.DLL.SDL_HasAVX512F.restype = ctypes.c_int
LoadDLL.DLL.SDL_HasAVX512F.argtypes = []

def SDL_HasAVX512F():
	"""
	Args:
		: None.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_HasAVX512F()


LoadDLL.DLL.SDL_HasARMSIMD.restype = ctypes.c_int
LoadDLL.DLL.SDL_HasARMSIMD.argtypes = []

def SDL_HasARMSIMD():
	"""
	Args:
		: None.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_HasARMSIMD()


LoadDLL.DLL.SDL_HasNEON.restype = ctypes.c_int
LoadDLL.DLL.SDL_HasNEON.argtypes = []

def SDL_HasNEON():
	"""
	Args:
		: None.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_HasNEON()


LoadDLL.DLL.SDL_HasLSX.restype = ctypes.c_int
LoadDLL.DLL.SDL_HasLSX.argtypes = []

def SDL_HasLSX():
	"""
	Args:
		: None.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_HasLSX()


LoadDLL.DLL.SDL_HasLASX.restype = ctypes.c_int
LoadDLL.DLL.SDL_HasLASX.argtypes = []

def SDL_HasLASX():
	"""
	Args:
		: None.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_HasLASX()


LoadDLL.DLL.SDL_GetSystemRAM.restype = ctypes.c_int
LoadDLL.DLL.SDL_GetSystemRAM.argtypes = []

def SDL_GetSystemRAM():
	"""
	Args:
		: None.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_GetSystemRAM()


LoadDLL.DLL.SDL_SIMDGetAlignment.restype = ctypes.c_ulonglong
LoadDLL.DLL.SDL_SIMDGetAlignment.argtypes = []

def SDL_SIMDGetAlignment():
	"""
	Args:
		: None.
	Returns:
		res: ctypes.c_ulonglong.
	"""
	return LoadDLL.DLL.SDL_SIMDGetAlignment()


LoadDLL.DLL.SDL_SIMDAlloc.restype = ctypes.c_void_p
LoadDLL.DLL.SDL_SIMDAlloc.argtypes = [ctypes.c_ulonglong]

def SDL_SIMDAlloc(len_):
	"""
	Args:
		len_: ctypes.c_ulonglong.
	Returns:
		res: ctypes.c_void_p.
	"""
	return LoadDLL.DLL.SDL_SIMDAlloc(len_)


LoadDLL.DLL.SDL_SIMDRealloc.restype = ctypes.c_void_p
LoadDLL.DLL.SDL_SIMDRealloc.argtypes = [ctypes.c_void_p, ctypes.c_ulonglong]

def SDL_SIMDRealloc(mem, len_):
	"""
	Args:
		mem: ctypes.c_void_p.
		len_: ctypes.c_ulonglong.
	Returns:
		res: ctypes.c_void_p.
	"""
	return LoadDLL.DLL.SDL_SIMDRealloc(mem, len_)


LoadDLL.DLL.SDL_SIMDFree.restype = None
LoadDLL.DLL.SDL_SIMDFree.argtypes = [ctypes.c_void_p]

def SDL_SIMDFree(ptr):
	"""
	Args:
		ptr: ctypes.c_void_p.
	Returns:
		res: None.
	"""
	LoadDLL.DLL.SDL_SIMDFree(ptr)