import ctypes
from .LoadDLL import LoadDLL


SDL_ALPHA_OPAQUE = 255

SDL_ALPHA_TRANSPARENT = 0


class SDL_Color(ctypes.Structure):
	_fields_ = [
		('r', ctypes.c_ubyte),
		('g', ctypes.c_ubyte),
		('b', ctypes.c_ubyte),
		('a', ctypes.c_ubyte),
	]


SDL_Colour = SDL_Color

class SDL_PixelType:
	SDL_PIXELTYPE_UNKNOWN = 0
	SDL_PIXELTYPE_INDEX1 = 1
	SDL_PIXELTYPE_INDEX4 = 2
	SDL_PIXELTYPE_INDEX8 = 3
	SDL_PIXELTYPE_PACKED8 = 4
	SDL_PIXELTYPE_PACKED16 = 5
	SDL_PIXELTYPE_PACKED32 = 6
	SDL_PIXELTYPE_ARRAYU8 = 7
	SDL_PIXELTYPE_ARRAYU16 = 8
	SDL_PIXELTYPE_ARRAYU32 = 9
	SDL_PIXELTYPE_ARRAYF16 = 10
	SDL_PIXELTYPE_ARRAYF32 = 11
	SDL_PIXELTYPE_INDEX2 = 12


class SDL_BitmapOrder:
	SDL_BITMAPORDER_NONE = 0
	SDL_BITMAPORDER_4321 = 1
	SDL_BITMAPORDER_1234 = 2


class SDL_PackedOrder:
	SDL_PACKEDORDER_NONE = 0
	SDL_PACKEDORDER_XRGB = 1
	SDL_PACKEDORDER_RGBX = 2
	SDL_PACKEDORDER_ARGB = 3
	SDL_PACKEDORDER_RGBA = 4
	SDL_PACKEDORDER_XBGR = 5
	SDL_PACKEDORDER_BGRX = 6
	SDL_PACKEDORDER_ABGR = 7
	SDL_PACKEDORDER_BGRA = 8


class SDL_ArrayOrder:
	SDL_ARRAYORDER_NONE = 0
	SDL_ARRAYORDER_RGB = 1
	SDL_ARRAYORDER_RGBA = 2
	SDL_ARRAYORDER_ARGB = 3
	SDL_ARRAYORDER_BGR = 4
	SDL_ARRAYORDER_BGRA = 5
	SDL_ARRAYORDER_ABGR = 6


class SDL_PackedLayout:
	SDL_PACKEDLAYOUT_NONE = 0
	SDL_PACKEDLAYOUT_332 = 1
	SDL_PACKEDLAYOUT_4444 = 2
	SDL_PACKEDLAYOUT_1555 = 3
	SDL_PACKEDLAYOUT_5551 = 4
	SDL_PACKEDLAYOUT_565 = 5
	SDL_PACKEDLAYOUT_8888 = 6
	SDL_PACKEDLAYOUT_2101010 = 7
	SDL_PACKEDLAYOUT_1010102 = 8


class SDL_Palette(ctypes.Structure):
	_fields_ = [
		('ncolors', ctypes.c_int),
		('colors', ctypes.POINTER(SDL_Color)),
		('version', ctypes.c_uint),
		('refcount', ctypes.c_int),
	]


class SDL_PixelFormat(ctypes.Structure):
	_fields_ = [
		('format', ctypes.c_uint),
		('palette', ctypes.POINTER(SDL_Palette)),
		('BitsPerPixel', ctypes.c_ubyte),
		('BytesPerPixel', ctypes.c_ubyte),
		('padding', ctypes.c_ubyte * 2),
		('Rmask', ctypes.c_uint),
		('Gmask', ctypes.c_uint),
		('Bmask', ctypes.c_uint),
		('Amask', ctypes.c_uint),
		('Rloss', ctypes.c_ubyte),
		('Gloss', ctypes.c_ubyte),
		('Bloss', ctypes.c_ubyte),
		('Aloss', ctypes.c_ubyte),
		('Rshift', ctypes.c_ubyte),
		('Gshift', ctypes.c_ubyte),
		('Bshift', ctypes.c_ubyte),
		('Ashift', ctypes.c_ubyte),
		('refcount', ctypes.c_int),
		('next', ctypes.c_void_p),
	]

LoadDLL.DLL.SDL_GetPixelFormatName.restype = ctypes.c_char_p
LoadDLL.DLL.SDL_GetPixelFormatName.argtypes = [ctypes.c_uint]

def SDL_GetPixelFormatName(format):
	"""
	Args:
		format: ctypes.c_uint.
	Returns:
		res: ctypes.c_char_p.
	"""
	return LoadDLL.DLL.SDL_GetPixelFormatName(format)


LoadDLL.DLL.SDL_PixelFormatEnumToMasks.restype = ctypes.c_int
LoadDLL.DLL.SDL_PixelFormatEnumToMasks.argtypes = [ctypes.c_uint, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_uint), ctypes.POINTER(ctypes.c_uint), ctypes.POINTER(ctypes.c_uint), ctypes.POINTER(ctypes.c_uint)]

def SDL_PixelFormatEnumToMasks(format, bpp, Rmask, Gmask, Bmask, Amask):
	"""
	Args:
		format: ctypes.c_uint.
		bpp: ctypes.POINTER(ctypes.c_int).
		Rmask: ctypes.POINTER(ctypes.c_uint).
		Gmask: ctypes.POINTER(ctypes.c_uint).
		Bmask: ctypes.POINTER(ctypes.c_uint).
		Amask: ctypes.POINTER(ctypes.c_uint).
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_PixelFormatEnumToMasks(format, bpp, Rmask, Gmask, Bmask, Amask)


LoadDLL.DLL.SDL_AllocFormat.restype = ctypes.POINTER(SDL_PixelFormat)
LoadDLL.DLL.SDL_AllocFormat.argtypes = [ctypes.c_uint]

def SDL_AllocFormat(pixel_format):
	"""
	Args:
		pixel_format: ctypes.c_uint.
	Returns:
		res: ctypes.POINTER(SDL_PixelFormat).
	"""
	return LoadDLL.DLL.SDL_AllocFormat(pixel_format)


LoadDLL.DLL.SDL_FreeFormat.restype = None
LoadDLL.DLL.SDL_FreeFormat.argtypes = [ctypes.POINTER(SDL_PixelFormat)]

def SDL_FreeFormat(format):
	"""
	Args:
		format: ctypes.POINTER(SDL_PixelFormat).
	Returns:
		res: None.
	"""
	LoadDLL.DLL.SDL_FreeFormat(format)


LoadDLL.DLL.SDL_AllocPalette.restype = ctypes.POINTER(SDL_Palette)
LoadDLL.DLL.SDL_AllocPalette.argtypes = [ctypes.c_int]

def SDL_AllocPalette(ncolors):
	"""
	Args:
		ncolors: ctypes.c_int.
	Returns:
		res: ctypes.POINTER(SDL_Palette).
	"""
	return LoadDLL.DLL.SDL_AllocPalette(ncolors)


LoadDLL.DLL.SDL_SetPixelFormatPalette.restype = ctypes.c_int
LoadDLL.DLL.SDL_SetPixelFormatPalette.argtypes = [ctypes.POINTER(SDL_PixelFormat), ctypes.POINTER(SDL_Palette)]

def SDL_SetPixelFormatPalette(format, palette):
	"""
	Args:
		format: ctypes.POINTER(SDL_PixelFormat).
		palette: ctypes.POINTER(SDL_Palette).
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_SetPixelFormatPalette(format, palette)


LoadDLL.DLL.SDL_FreePalette.restype = None
LoadDLL.DLL.SDL_FreePalette.argtypes = [ctypes.POINTER(SDL_Palette)]

def SDL_FreePalette(palette):
	"""
	Args:
		palette: ctypes.POINTER(SDL_Palette).
	Returns:
		res: None.
	"""
	LoadDLL.DLL.SDL_FreePalette(palette)


LoadDLL.DLL.SDL_MapRGB.restype = ctypes.c_uint
LoadDLL.DLL.SDL_MapRGB.argtypes = [ctypes.POINTER(SDL_PixelFormat), ctypes.c_ubyte, ctypes.c_ubyte, ctypes.c_ubyte]

def SDL_MapRGB(format, r, g, b):
	"""
	Args:
		format: ctypes.POINTER(SDL_PixelFormat).
		r: ctypes.c_ubyte.
		g: ctypes.c_ubyte.
		b: ctypes.c_ubyte.
	Returns:
		res: ctypes.c_uint.
	"""
	return LoadDLL.DLL.SDL_MapRGB(format, r, g, b)


LoadDLL.DLL.SDL_GetRGB.restype = None
LoadDLL.DLL.SDL_GetRGB.argtypes = [ctypes.c_uint, ctypes.POINTER(SDL_PixelFormat), ctypes.POINTER(ctypes.c_ubyte), ctypes.POINTER(ctypes.c_ubyte), ctypes.POINTER(ctypes.c_ubyte)]

def SDL_GetRGB(pixel, format, r, g, b):
	"""
	Args:
		pixel: ctypes.c_uint.
		format: ctypes.POINTER(SDL_PixelFormat).
		r: ctypes.POINTER(ctypes.c_ubyte).
		g: ctypes.POINTER(ctypes.c_ubyte).
		b: ctypes.POINTER(ctypes.c_ubyte).
	Returns:
		res: None.
	"""
	LoadDLL.DLL.SDL_GetRGB(pixel, format, r, g, b)


LoadDLL.DLL.SDL_CalculateGammaRamp.restype = None
LoadDLL.DLL.SDL_CalculateGammaRamp.argtypes = [ctypes.c_float, ctypes.POINTER(ctypes.c_ushort)]

def SDL_CalculateGammaRamp(gamma, ramp):
	"""
	Args:
		gamma: ctypes.c_float.
		ramp: ctypes.POINTER(ctypes.c_ushort).
	Returns:
		res: None.
	"""
	LoadDLL.DLL.SDL_CalculateGammaRamp(gamma, ramp)