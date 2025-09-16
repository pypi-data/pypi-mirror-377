import ctypes
from .LoadDLL import LoadDLL
from .SDL_rect import SDL_Rect
from .SDL_rwops import SDL_RWops
from .SDL_pixels import SDL_Palette, SDL_PixelFormat


SDL_SWSURFACE = 0

SDL_PREALLOC = 0x00000001

SDL_RLEACCEL = 0x00000002

SDL_DONTFREE = 0x00000004

SDL_SIMD_ALIGNED = 0x00000008


class SDL_BlitMap(ctypes.Structure): pass


class SDL_Surface(ctypes.Structure):
	_fields_ = [
		('flags', ctypes.c_uint),
		('format', ctypes.POINTER(SDL_PixelFormat)),
		('w', ctypes.c_int),
		('h', ctypes.c_int),
		('pitch', ctypes.c_int),
		('pixels', ctypes.c_void_p),
		('userdata', ctypes.c_void_p),
		('locked', ctypes.c_int),
		('list_blitmap', ctypes.c_void_p),
		('clip_rect', SDL_Rect),
		('map', ctypes.POINTER(SDL_BlitMap)),
		('refcount', ctypes.c_int),
	]


LoadDLL.DLL.SDL_UpperBlit.restype = ctypes.c_int
LoadDLL.DLL.SDL_UpperBlit.argtypes = [ctypes.POINTER(SDL_Surface), ctypes.POINTER(SDL_Rect), ctypes.POINTER(SDL_Surface), ctypes.POINTER(SDL_Rect)]

def SDL_UpperBlit(src, srcrect, dst, dstrect):
	"""
	Args:
		src: ctypes.POINTER(SDL_Surface).
		srcrect: ctypes.POINTER(SDL_Rect).
		dst: ctypes.POINTER(SDL_Surface).
		dstrect: ctypes.POINTER(SDL_Rect).
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_UpperBlit(src, srcrect, dst, dstrect)


SDL_BlitSurface = SDL_UpperBlit

SDL_YUV_CONVERSION_JPEG = 0
SDL_YUV_CONVERSION_BT601 = 1
SDL_YUV_CONVERSION_BT709 = 2
SDL_YUV_CONVERSION_AUTOMATIC = 3


LoadDLL.DLL.SDL_CreateRGBSurface.restype = ctypes.POINTER(SDL_Surface)
LoadDLL.DLL.SDL_CreateRGBSurface.argtypes = [ctypes.c_uint, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_uint, ctypes.c_uint, ctypes.c_uint, ctypes.c_uint]

def SDL_CreateRGBSurface(flags, width, height, depth, Rmask, Gmask, Bmask, Amask):
	"""
	Args:
		flags: ctypes.c_uint.
		width: ctypes.c_int.
		height: ctypes.c_int.
		depth: ctypes.c_int.
		Rmask: ctypes.c_uint.
		Gmask: ctypes.c_uint.
		Bmask: ctypes.c_uint.
		Amask: ctypes.c_uint.
	Returns:
		res: ctypes.POINTER(SDL_Surface).
	"""
	return LoadDLL.DLL.SDL_CreateRGBSurface(flags, width, height, depth, Rmask, Gmask, Bmask, Amask)


LoadDLL.DLL.SDL_CreateRGBSurfaceFrom.restype = ctypes.POINTER(SDL_Surface)
LoadDLL.DLL.SDL_CreateRGBSurfaceFrom.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_uint, ctypes.c_uint, ctypes.c_uint, ctypes.c_uint]

def SDL_CreateRGBSurfaceFrom(pixels, width, height, depth, pitch, Rmask, Gmask, Bmask, Amask):
	"""
	Args:
		pixels: ctypes.c_void_p.
		width: ctypes.c_int.
		height: ctypes.c_int.
		depth: ctypes.c_int.
		pitch: ctypes.c_int.
		Rmask: ctypes.c_uint.
		Gmask: ctypes.c_uint.
		Bmask: ctypes.c_uint.
		Amask: ctypes.c_uint.
	Returns:
		res: ctypes.POINTER(SDL_Surface).
	"""
	return LoadDLL.DLL.SDL_CreateRGBSurfaceFrom(pixels, width, height, depth, pitch, Rmask, Gmask, Bmask, Amask)


LoadDLL.DLL.SDL_FreeSurface.restype = None
LoadDLL.DLL.SDL_FreeSurface.argtypes = [ctypes.POINTER(SDL_Surface)]

def SDL_FreeSurface(surface):
	"""
	Args:
		surface: ctypes.POINTER(SDL_Surface).
	Returns:
		res: None.
	"""
	LoadDLL.DLL.SDL_FreeSurface(surface)


LoadDLL.DLL.SDL_SetSurfacePalette.restype = ctypes.c_int
LoadDLL.DLL.SDL_SetSurfacePalette.argtypes = [ctypes.POINTER(SDL_Surface), ctypes.POINTER(SDL_Palette)]

def SDL_SetSurfacePalette(surface, palette):
	"""
	Args:
		surface: ctypes.POINTER(SDL_Surface).
		palette: ctypes.POINTER(SDL_Palette).
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_SetSurfacePalette(surface, palette)


LoadDLL.DLL.SDL_UnlockSurface.restype = None
LoadDLL.DLL.SDL_UnlockSurface.argtypes = [ctypes.POINTER(SDL_Surface)]

def SDL_UnlockSurface(surface):
	"""
	Args:
		surface: ctypes.POINTER(SDL_Surface).
	Returns:
		res: None.
	"""
	LoadDLL.DLL.SDL_UnlockSurface(surface)


LoadDLL.DLL.SDL_LoadBMP_RW.restype = ctypes.POINTER(SDL_Surface)
LoadDLL.DLL.SDL_LoadBMP_RW.argtypes = [ctypes.POINTER(SDL_RWops), ctypes.c_int]

def SDL_LoadBMP_RW(src, freesrc):
	"""
	Args:
		src: ctypes.POINTER(SDL_RWops).
		freesrc: ctypes.c_int.
	Returns:
		res: ctypes.POINTER(SDL_Surface).
	"""
	return LoadDLL.DLL.SDL_LoadBMP_RW(src, freesrc)


LoadDLL.DLL.SDL_SaveBMP_RW.restype = ctypes.c_int
LoadDLL.DLL.SDL_SaveBMP_RW.argtypes = [ctypes.POINTER(SDL_Surface), ctypes.POINTER(SDL_RWops), ctypes.c_int]

def SDL_SaveBMP_RW(surface, dst, freedst):
	"""
	Args:
		surface: ctypes.POINTER(SDL_Surface).
		dst: ctypes.POINTER(SDL_RWops).
		freedst: ctypes.c_int.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_SaveBMP_RW(surface, dst, freedst)


LoadDLL.DLL.SDL_SetColorKey.restype = ctypes.c_int
LoadDLL.DLL.SDL_SetColorKey.argtypes = [ctypes.POINTER(SDL_Surface), ctypes.c_int, ctypes.c_uint]

def SDL_SetColorKey(surface, flag, key):
	"""
	Args:
		surface: ctypes.POINTER(SDL_Surface).
		flag: ctypes.c_int.
		key: ctypes.c_uint.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_SetColorKey(surface, flag, key)


LoadDLL.DLL.SDL_GetColorKey.restype = ctypes.c_int
LoadDLL.DLL.SDL_GetColorKey.argtypes = [ctypes.POINTER(SDL_Surface), ctypes.POINTER(ctypes.c_uint)]

def SDL_GetColorKey(surface, key):
	"""
	Args:
		surface: ctypes.POINTER(SDL_Surface).
		key: ctypes.POINTER(ctypes.c_uint).
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_GetColorKey(surface, key)


LoadDLL.DLL.SDL_GetSurfaceColorMod.restype = ctypes.c_int
LoadDLL.DLL.SDL_GetSurfaceColorMod.argtypes = [ctypes.POINTER(SDL_Surface), ctypes.POINTER(ctypes.c_ubyte), ctypes.POINTER(ctypes.c_ubyte), ctypes.POINTER(ctypes.c_ubyte)]

def SDL_GetSurfaceColorMod(surface, r, g, b):
	"""
	Args:
		surface: ctypes.POINTER(SDL_Surface).
		r: ctypes.POINTER(ctypes.c_ubyte).
		g: ctypes.POINTER(ctypes.c_ubyte).
		b: ctypes.POINTER(ctypes.c_ubyte).
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_GetSurfaceColorMod(surface, r, g, b)


LoadDLL.DLL.SDL_GetSurfaceAlphaMod.restype = ctypes.c_int
LoadDLL.DLL.SDL_GetSurfaceAlphaMod.argtypes = [ctypes.POINTER(SDL_Surface), ctypes.POINTER(ctypes.c_ubyte)]

def SDL_GetSurfaceAlphaMod(surface, alpha):
	"""
	Args:
		surface: ctypes.POINTER(SDL_Surface).
		alpha: ctypes.POINTER(ctypes.c_ubyte).
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_GetSurfaceAlphaMod(surface, alpha)


LoadDLL.DLL.SDL_GetSurfaceBlendMode.restype = ctypes.c_int
LoadDLL.DLL.SDL_GetSurfaceBlendMode.argtypes = [ctypes.POINTER(SDL_Surface), ctypes.POINTER(ctypes.c_int)]

def SDL_GetSurfaceBlendMode(surface, blendMode):
	"""
	Args:
		surface: ctypes.POINTER(SDL_Surface).
		blendMode: ctypes.POINTER(ctypes.c_int).
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_GetSurfaceBlendMode(surface, blendMode)


LoadDLL.DLL.SDL_GetClipRect.restype = None
LoadDLL.DLL.SDL_GetClipRect.argtypes = [ctypes.POINTER(SDL_Surface), ctypes.POINTER(SDL_Rect)]

def SDL_GetClipRect(surface, rect):
	"""
	Args:
		surface: ctypes.POINTER(SDL_Surface).
		rect: ctypes.POINTER(SDL_Rect).
	Returns:
		res: None.
	"""
	LoadDLL.DLL.SDL_GetClipRect(surface, rect)


LoadDLL.DLL.SDL_ConvertSurface.restype = ctypes.POINTER(SDL_Surface)
LoadDLL.DLL.SDL_ConvertSurface.argtypes = [ctypes.POINTER(SDL_Surface), ctypes.POINTER(SDL_PixelFormat), ctypes.c_uint]

def SDL_ConvertSurface(src, fmt, flags):
	"""
	Args:
		src: ctypes.POINTER(SDL_Surface).
		fmt: ctypes.POINTER(SDL_PixelFormat).
		flags: ctypes.c_uint.
	Returns:
		res: ctypes.POINTER(SDL_Surface).
	"""
	return LoadDLL.DLL.SDL_ConvertSurface(src, fmt, flags)


LoadDLL.DLL.SDL_ConvertPixels.restype = ctypes.c_int
LoadDLL.DLL.SDL_ConvertPixels.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_uint, ctypes.c_void_p, ctypes.c_int, ctypes.c_uint, ctypes.c_void_p, ctypes.c_int]

def SDL_ConvertPixels(width, height, src_format, src, src_pitch, dst_format, dst, dst_pitch):
	"""
	Args:
		width: ctypes.c_int.
		height: ctypes.c_int.
		src_format: ctypes.c_uint.
		src: ctypes.c_void_p.
		src_pitch: ctypes.c_int.
		dst_format: ctypes.c_uint.
		dst: ctypes.c_void_p.
		dst_pitch: ctypes.c_int.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_ConvertPixels(width, height, src_format, src, src_pitch, dst_format, dst, dst_pitch)


LoadDLL.DLL.SDL_FillRect.restype = ctypes.c_int
LoadDLL.DLL.SDL_FillRect.argtypes = [ctypes.POINTER(SDL_Surface), ctypes.POINTER(SDL_Rect), ctypes.c_uint]

def SDL_FillRect(dst, rect, color):
	"""
	Args:
		dst: ctypes.POINTER(SDL_Surface).
		rect: ctypes.POINTER(SDL_Rect).
		color: ctypes.c_uint.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_FillRect(dst, rect, color)


LoadDLL.DLL.SDL_SoftStretchLinear.restype = ctypes.c_int
LoadDLL.DLL.SDL_SoftStretchLinear.argtypes = [ctypes.POINTER(SDL_Surface), ctypes.POINTER(SDL_Rect), ctypes.POINTER(SDL_Surface), ctypes.POINTER(SDL_Rect)]

def SDL_SoftStretchLinear(src, srcrect, dst, dstrect):
	"""
	Args:
		src: ctypes.POINTER(SDL_Surface).
		srcrect: ctypes.POINTER(SDL_Rect).
		dst: ctypes.POINTER(SDL_Surface).
		dstrect: ctypes.POINTER(SDL_Rect).
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_SoftStretchLinear(src, srcrect, dst, dstrect)


LoadDLL.DLL.SDL_UpperBlitScaled.restype = ctypes.c_int
LoadDLL.DLL.SDL_UpperBlitScaled.argtypes = [ctypes.POINTER(SDL_Surface), ctypes.POINTER(SDL_Rect), ctypes.POINTER(SDL_Surface), ctypes.POINTER(SDL_Rect)]

def SDL_UpperBlitScaled(src, srcrect, dst, dstrect):
	"""
	Args:
		src: ctypes.POINTER(SDL_Surface).
		srcrect: ctypes.POINTER(SDL_Rect).
		dst: ctypes.POINTER(SDL_Surface).
		dstrect: ctypes.POINTER(SDL_Rect).
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_UpperBlitScaled(src, srcrect, dst, dstrect)