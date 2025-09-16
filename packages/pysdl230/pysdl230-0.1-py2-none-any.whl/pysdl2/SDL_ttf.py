import ctypes
from .LoadDLL import TTFDLL
from .SDL_rwops import SDL_RWops
from .SDL_pixels import SDL_Color
from .SDL_surface import SDL_Surface


SDL_TTF_MAJOR_VERSION = 2

SDL_TTF_MINOR_VERSION = 24

SDL_TTF_PATCHLEVEL = 0

TTF_MAJOR_VERSION = SDL_TTF_MAJOR_VERSION

TTF_MINOR_VERSION = SDL_TTF_MINOR_VERSION

TTF_PATCHLEVEL = SDL_TTF_PATCHLEVEL

UNICODE_BOM_NATIVE = 0xFEFF

UNICODE_BOM_SWAPPED = 0xFFFE

TTF_STYLE_NORMAL = 0x00

TTF_STYLE_BOLD = 0x01

TTF_STYLE_ITALIC = 0x02

TTF_STYLE_UNDERLINE = 0x04

TTF_STYLE_STRIKETHROUGH = 0x08

TTF_HINTING_NORMAL = 0

TTF_HINTING_LIGHT = 1

TTF_HINTING_MONO = 2

TTF_HINTING_NONE = 3

TTF_HINTING_LIGHT_SUBPIXEL = 4

TTF_WRAPPED_ALIGN_LEFT = 0

TTF_WRAPPED_ALIGN_CENTER = 1

TTF_WRAPPED_ALIGN_RIGHT = 2


class TTF_Direction:
	TTF_DIRECTION_LTR = 0
	TTF_DIRECTION_RTL = 1
	TTF_DIRECTION_TTB = 2
	TTF_DIRECTION_BTT = 3

    
class TTF_Font(ctypes.Structure): pass


TTFDLL.DLL.TTF_GetHarfBuzzVersion.restype = None
TTFDLL.DLL.TTF_GetHarfBuzzVersion.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]

def TTF_GetHarfBuzzVersion(major, minor, patch):
	"""
	Args:
		major: ctypes.POINTER(ctypes.c_int).
		minor: ctypes.POINTER(ctypes.c_int).
		patch: ctypes.POINTER(ctypes.c_int).
	Returns:
		res: None.
	"""
	TTFDLL.DLL.TTF_GetHarfBuzzVersion(major, minor, patch)


TTFDLL.DLL.TTF_ByteSwappedUNICODE.restype = None
TTFDLL.DLL.TTF_ByteSwappedUNICODE.argtypes = [ctypes.c_int]

def TTF_ByteSwappedUNICODE(swapped):
	"""
	Args:
		swapped: ctypes.c_int.
	Returns:
		res: None.
	"""
	TTFDLL.DLL.TTF_ByteSwappedUNICODE(swapped)


TTFDLL.DLL.TTF_Init.restype = ctypes.c_int
TTFDLL.DLL.TTF_Init.argtypes = []

def TTF_Init():
	"""
	Args:
		: None.
	Returns:
		res: ctypes.c_int.
	"""
	return TTFDLL.DLL.TTF_Init()


TTFDLL.DLL.TTF_Quit.restype = None
TTFDLL.DLL.TTF_Quit.argtypes = []

def TTF_Quit():
    """
	Args:
		: None.
	Returns:
		res: None.
	"""
    TTFDLL.DLL.TTF_Quit()


TTFDLL.DLL.TTF_OpenFont.restype = ctypes.POINTER(TTF_Font)
TTFDLL.DLL.TTF_OpenFont.argtypes = [ctypes.c_char_p, ctypes.c_int]

def TTF_OpenFont(file, ptsize):
	"""
	Args:
		file: ctypes.c_char_p.
		ptsize: ctypes.c_int.
	Returns:
		res: ctypes.POINTER(TTF_Font).
	"""
	return TTFDLL.DLL.TTF_OpenFont(file, ptsize)


TTFDLL.DLL.TTF_CloseFont.restype = None
TTFDLL.DLL.TTF_CloseFont.argtypes = [ctypes.POINTER(TTF_Font)]

def TTF_CloseFont(font):
    """
	Args:
		font: ctypes.POINTER(TTF_Font)
	Returns:
		res: None.
	"""
    TTFDLL.DLL.TTF_CloseFont(font)


TTFDLL.DLL.TTF_OpenFontIndex.restype = ctypes.POINTER(TTF_Font)
TTFDLL.DLL.TTF_OpenFontIndex.argtypes = [ctypes.c_char_p, ctypes.c_int, ctypes.c_long]

def TTF_OpenFontIndex(file, ptsize, index):
	"""
	Args:
		file: ctypes.c_char_p.
		ptsize: ctypes.c_int.
		index: ctypes.c_long.
	Returns:
		res: ctypes.POINTER(TTF_Font).
	"""
	return TTFDLL.DLL.TTF_OpenFontIndex(file, ptsize, index)


TTFDLL.DLL.TTF_OpenFontRW.restype = ctypes.POINTER(TTF_Font)
TTFDLL.DLL.TTF_OpenFontRW.argtypes = [ctypes.POINTER(SDL_RWops), ctypes.c_int, ctypes.c_int]

def TTF_OpenFontRW(src, freesrc, ptsize):
	"""
	Args:
		src: ctypes.POINTER(SDL_RWops).
		freesrc: ctypes.c_int.
		ptsize: ctypes.c_int.
	Returns:
		res: ctypes.POINTER(TTF_Font).
	"""
	return TTFDLL.DLL.TTF_OpenFontRW(src, freesrc, ptsize)


TTFDLL.DLL.TTF_OpenFontIndexRW.restype = ctypes.POINTER(TTF_Font)
TTFDLL.DLL.TTF_OpenFontIndexRW.argtypes = [ctypes.POINTER(SDL_RWops), ctypes.c_int, ctypes.c_int, ctypes.c_long]

def TTF_OpenFontIndexRW(src, freesrc, ptsize, index):
	"""
	Args:
		src: ctypes.POINTER(SDL_RWops).
		freesrc: ctypes.c_int.
		ptsize: ctypes.c_int.
		index: ctypes.c_long.
	Returns:
		res: ctypes.POINTER(TTF_Font).
	"""
	return TTFDLL.DLL.TTF_OpenFontIndexRW(src, freesrc, ptsize, index)


TTFDLL.DLL.TTF_OpenFontDPI.restype = ctypes.POINTER(TTF_Font)
TTFDLL.DLL.TTF_OpenFontDPI.argtypes = [ctypes.c_char_p, ctypes.c_int, ctypes.c_uint, ctypes.c_uint]

def TTF_OpenFontDPI(file, ptsize, hdpi, vdpi):
	"""
	Args:
		file: ctypes.c_char_p.
		ptsize: ctypes.c_int.
		hdpi: ctypes.c_uint.
		vdpi: ctypes.c_uint.
	Returns:
		res: ctypes.POINTER(TTF_Font).
	"""
	return TTFDLL.DLL.TTF_OpenFontDPI(file, ptsize, hdpi, vdpi)


TTFDLL.DLL.TTF_OpenFontIndexDPI.restype = ctypes.POINTER(TTF_Font)
TTFDLL.DLL.TTF_OpenFontIndexDPI.argtypes = [ctypes.c_char_p, ctypes.c_int, ctypes.c_long, ctypes.c_uint, ctypes.c_uint]

def TTF_OpenFontIndexDPI(file, ptsize, index, hdpi, vdpi):
	"""
	Args:
		file: ctypes.c_char_p.
		ptsize: ctypes.c_int.
		index: ctypes.c_long.
		hdpi: ctypes.c_uint.
		vdpi: ctypes.c_uint.
	Returns:
		res: ctypes.POINTER(TTF_Font).
	"""
	return TTFDLL.DLL.TTF_OpenFontIndexDPI(file, ptsize, index, hdpi, vdpi)


TTFDLL.DLL.TTF_OpenFontDPIRW.restype = ctypes.POINTER(TTF_Font)
TTFDLL.DLL.TTF_OpenFontDPIRW.argtypes = [ctypes.POINTER(SDL_RWops), ctypes.c_int, ctypes.c_int, ctypes.c_uint, ctypes.c_uint]

def TTF_OpenFontDPIRW(src, freesrc, ptsize, hdpi, vdpi):
	"""
	Args:
		src: ctypes.POINTER(SDL_RWops).
		freesrc: ctypes.c_int.
		ptsize: ctypes.c_int.
		hdpi: ctypes.c_uint.
		vdpi: ctypes.c_uint.
	Returns:
		res: ctypes.POINTER(TTF_Font).
	"""
	return TTFDLL.DLL.TTF_OpenFontDPIRW(src, freesrc, ptsize, hdpi, vdpi)


TTFDLL.DLL.TTF_OpenFontIndexDPIRW.restype = ctypes.POINTER(TTF_Font)
TTFDLL.DLL.TTF_OpenFontIndexDPIRW.argtypes = [ctypes.POINTER(SDL_RWops), ctypes.c_int, ctypes.c_int, ctypes.c_long, ctypes.c_uint, ctypes.c_uint]

def TTF_OpenFontIndexDPIRW(src, freesrc, ptsize, index, hdpi, vdpi):
	"""
	Args:
		src: ctypes.POINTER(SDL_RWops).
		freesrc: ctypes.c_int.
		ptsize: ctypes.c_int.
		index: ctypes.c_long.
		hdpi: ctypes.c_uint.
		vdpi: ctypes.c_uint.
	Returns:
		res: ctypes.POINTER(TTF_Font).
	"""
	return TTFDLL.DLL.TTF_OpenFontIndexDPIRW(src, freesrc, ptsize, index, hdpi, vdpi)


TTFDLL.DLL.TTF_SetFontSize.restype = ctypes.c_int
TTFDLL.DLL.TTF_SetFontSize.argtypes = [ctypes.POINTER(TTF_Font), ctypes.c_int]

def TTF_SetFontSize(font, ptsize):
	"""
	Args:
		font: ctypes.POINTER(TTF_Font).
		ptsize: ctypes.c_int.
	Returns:
		res: ctypes.c_int.
	"""
	return TTFDLL.DLL.TTF_SetFontSize(font, ptsize)


TTFDLL.DLL.TTF_SetFontSizeDPI.restype = ctypes.c_int
TTFDLL.DLL.TTF_SetFontSizeDPI.argtypes = [ctypes.POINTER(TTF_Font), ctypes.c_int, ctypes.c_uint, ctypes.c_uint]

def TTF_SetFontSizeDPI(font, ptsize, hdpi, vdpi):
	"""
	Args:
		font: ctypes.POINTER(TTF_Font).
		ptsize: ctypes.c_int.
		hdpi: ctypes.c_uint.
		vdpi: ctypes.c_uint.
	Returns:
		res: ctypes.c_int.
	"""
	return TTFDLL.DLL.TTF_SetFontSizeDPI(font, ptsize, hdpi, vdpi)


TTFDLL.DLL.TTF_GetFontStyle.restype = ctypes.c_int
TTFDLL.DLL.TTF_GetFontStyle.argtypes = [ctypes.POINTER(TTF_Font)]

def TTF_GetFontStyle(font):
	"""
	Args:
		font: ctypes.POINTER(TTF_Font).
	Returns:
		res: ctypes.c_int.
	"""
	return TTFDLL.DLL.TTF_GetFontStyle(font)


TTFDLL.DLL.TTF_SetFontStyle.restype = None
TTFDLL.DLL.TTF_SetFontStyle.argtypes = [ctypes.POINTER(TTF_Font), ctypes.c_int]

def TTF_SetFontStyle(font, style):
	"""
	Args:
		font: ctypes.POINTER(TTF_Font).
		style: ctypes.c_int.
	Returns:
		res: None.
	"""
	TTFDLL.DLL.TTF_SetFontStyle(font, style)


TTFDLL.DLL.TTF_GetFontOutline.restype = ctypes.c_int
TTFDLL.DLL.TTF_GetFontOutline.argtypes = [ctypes.POINTER(TTF_Font)]

def TTF_GetFontOutline(font):
	"""
	Args:
		font: ctypes.POINTER(TTF_Font).
	Returns:
		res: ctypes.c_int.
	"""
	return TTFDLL.DLL.TTF_GetFontOutline(font)


TTFDLL.DLL.TTF_SetFontOutline.restype = None
TTFDLL.DLL.TTF_SetFontOutline.argtypes = [ctypes.POINTER(TTF_Font), ctypes.c_int]

def TTF_SetFontOutline(font, outline):
	"""
	Args:
		font: ctypes.POINTER(TTF_Font).
		outline: ctypes.c_int.
	Returns:
		res: None.
	"""
	TTFDLL.DLL.TTF_SetFontOutline(font, outline)


TTFDLL.DLL.TTF_GetFontHinting.restype = ctypes.c_int
TTFDLL.DLL.TTF_GetFontHinting.argtypes = [ctypes.POINTER(TTF_Font)]

def TTF_GetFontHinting(font):
	"""
	Args:
		font: ctypes.POINTER(TTF_Font).
	Returns:
		res: ctypes.c_int.
	"""
	return TTFDLL.DLL.TTF_GetFontHinting(font)


TTFDLL.DLL.TTF_SetFontHinting.restype = None
TTFDLL.DLL.TTF_SetFontHinting.argtypes = [ctypes.POINTER(TTF_Font), ctypes.c_int]

def TTF_SetFontHinting(font, hinting):
	"""
	Args:
		font: ctypes.POINTER(TTF_Font).
		hinting: ctypes.c_int.
	Returns:
		res: None.
	"""
	TTFDLL.DLL.TTF_SetFontHinting(font, hinting)


TTFDLL.DLL.TTF_GetFontWrappedAlign.restype = ctypes.c_int
TTFDLL.DLL.TTF_GetFontWrappedAlign.argtypes = [ctypes.POINTER(TTF_Font)]

def TTF_GetFontWrappedAlign(font):
	"""
	Args:
		font: ctypes.POINTER(TTF_Font).
	Returns:
		res: ctypes.c_int.
	"""
	return TTFDLL.DLL.TTF_GetFontWrappedAlign(font)


TTFDLL.DLL.TTF_SetFontWrappedAlign.restype = None
TTFDLL.DLL.TTF_SetFontWrappedAlign.argtypes = [ctypes.POINTER(TTF_Font), ctypes.c_int]

def TTF_SetFontWrappedAlign(font, align):
	"""
	Args:
		font: ctypes.POINTER(TTF_Font).
		align: ctypes.c_int.
	Returns:
		res: None.
	"""
	TTFDLL.DLL.TTF_SetFontWrappedAlign(font, align)


TTFDLL.DLL.TTF_FontHeight.restype = ctypes.c_int
TTFDLL.DLL.TTF_FontHeight.argtypes = [ctypes.POINTER(TTF_Font)]

def TTF_FontHeight(font):
	"""
	Args:
		font: ctypes.POINTER(TTF_Font).
	Returns:
		res: ctypes.c_int.
	"""
	return TTFDLL.DLL.TTF_FontHeight(font)


TTFDLL.DLL.TTF_FontAscent.restype = ctypes.c_int
TTFDLL.DLL.TTF_FontAscent.argtypes = [ctypes.POINTER(TTF_Font)]

def TTF_FontAscent(font):
	"""
	Args:
		font: ctypes.POINTER(TTF_Font).
	Returns:
		res: ctypes.c_int.
	"""
	return TTFDLL.DLL.TTF_FontAscent(font)


TTFDLL.DLL.TTF_FontDescent.restype = ctypes.c_int
TTFDLL.DLL.TTF_FontDescent.argtypes = [ctypes.POINTER(TTF_Font)]

def TTF_FontDescent(font):
	"""
	Args:
		font: ctypes.POINTER(TTF_Font).
	Returns:
		res: ctypes.c_int.
	"""
	return TTFDLL.DLL.TTF_FontDescent(font)


TTFDLL.DLL.TTF_FontLineSkip.restype = ctypes.c_int
TTFDLL.DLL.TTF_FontLineSkip.argtypes = [ctypes.POINTER(TTF_Font)]

def TTF_FontLineSkip(font):
	"""
	Args:
		font: ctypes.POINTER(TTF_Font).
	Returns:
		res: ctypes.c_int.
	"""
	return TTFDLL.DLL.TTF_FontLineSkip(font)


TTFDLL.DLL.TTF_SetFontLineSkip.restype = None
TTFDLL.DLL.TTF_SetFontLineSkip.argtypes = [ctypes.POINTER(TTF_Font), ctypes.c_int]

def TTF_SetFontLineSkip(font, lineskip):
	"""
	Args:
		font: ctypes.POINTER(TTF_Font).
		lineskip: ctypes.c_int.
	Returns:
		res: None.
	"""
	TTFDLL.DLL.TTF_SetFontLineSkip(font, lineskip)


TTFDLL.DLL.TTF_GetFontKerning.restype = ctypes.c_int
TTFDLL.DLL.TTF_GetFontKerning.argtypes = [ctypes.POINTER(TTF_Font)]

def TTF_GetFontKerning(font):
	"""
	Args:
		font: ctypes.POINTER(TTF_Font).
	Returns:
		res: ctypes.c_int.
	"""
	return TTFDLL.DLL.TTF_GetFontKerning(font)


TTFDLL.DLL.TTF_SetFontKerning.restype = None
TTFDLL.DLL.TTF_SetFontKerning.argtypes = [ctypes.POINTER(TTF_Font), ctypes.c_int]

def TTF_SetFontKerning(font, allowed):
	"""
	Args:
		font: ctypes.POINTER(TTF_Font).
		allowed: ctypes.c_int.
	Returns:
		res: None.
	"""
	TTFDLL.DLL.TTF_SetFontKerning(font, allowed)


TTFDLL.DLL.TTF_FontFaces.restype = ctypes.c_long
TTFDLL.DLL.TTF_FontFaces.argtypes = [ctypes.POINTER(TTF_Font)]

def TTF_FontFaces(font):
	"""
	Args:
		font: ctypes.POINTER(TTF_Font).
	Returns:
		res: ctypes.c_long.
	"""
	return TTFDLL.DLL.TTF_FontFaces(font)


TTFDLL.DLL.TTF_FontFaceIsFixedWidth.restype = ctypes.c_int
TTFDLL.DLL.TTF_FontFaceIsFixedWidth.argtypes = [ctypes.POINTER(TTF_Font)]

def TTF_FontFaceIsFixedWidth(font):
	"""
	Args:
		font: ctypes.POINTER(TTF_Font).
	Returns:
		res: ctypes.c_int.
	"""
	return TTFDLL.DLL.TTF_FontFaceIsFixedWidth(font)


TTFDLL.DLL.TTF_FontFaceFamilyName.restype = ctypes.c_char_p
TTFDLL.DLL.TTF_FontFaceFamilyName.argtypes = [ctypes.POINTER(TTF_Font)]

def TTF_FontFaceFamilyName(font):
	"""
	Args:
		font: ctypes.POINTER(TTF_Font).
	Returns:
		res: ctypes.c_char_p.
	"""
	return TTFDLL.DLL.TTF_FontFaceFamilyName(font)


TTFDLL.DLL.TTF_FontFaceStyleName.restype = ctypes.c_char_p
TTFDLL.DLL.TTF_FontFaceStyleName.argtypes = [ctypes.POINTER(TTF_Font)]

def TTF_FontFaceStyleName(font):
	"""
	Args:
		font: ctypes.POINTER(TTF_Font).
	Returns:
		res: ctypes.c_char_p.
	"""
	return TTFDLL.DLL.TTF_FontFaceStyleName(font)


TTFDLL.DLL.TTF_GlyphIsProvided.restype = ctypes.c_int
TTFDLL.DLL.TTF_GlyphIsProvided.argtypes = [ctypes.POINTER(TTF_Font), ctypes.c_ushort]

def TTF_GlyphIsProvided(font, ch):
	"""
	Args:
		font: ctypes.POINTER(TTF_Font).
		ch: ctypes.c_ushort.
	Returns:
		res: ctypes.c_int.
	"""
	return TTFDLL.DLL.TTF_GlyphIsProvided(font, ch)


TTFDLL.DLL.TTF_GlyphIsProvided32.restype = ctypes.c_int
TTFDLL.DLL.TTF_GlyphIsProvided32.argtypes = [ctypes.POINTER(TTF_Font), ctypes.c_uint]

def TTF_GlyphIsProvided32(font, ch):
	"""
	Args:
		font: ctypes.POINTER(TTF_Font).
		ch: ctypes.c_uint.
	Returns:
		res: ctypes.c_int.
	"""
	return TTFDLL.DLL.TTF_GlyphIsProvided32(font, ch)


TTFDLL.DLL.TTF_GlyphMetrics.restype = ctypes.c_int
TTFDLL.DLL.TTF_GlyphMetrics.argtypes = [ctypes.POINTER(TTF_Font), ctypes.c_ushort, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]

def TTF_GlyphMetrics(font, ch, minx, maxx, miny, maxy, advance):
	"""
	Args:
		font: ctypes.POINTER(TTF_Font).
		ch: ctypes.c_ushort.
		minx: ctypes.POINTER(ctypes.c_int).
		maxx: ctypes.POINTER(ctypes.c_int).
		miny: ctypes.POINTER(ctypes.c_int).
		maxy: ctypes.POINTER(ctypes.c_int).
		advance: ctypes.POINTER(ctypes.c_int).
	Returns:
		res: ctypes.c_int.
	"""
	return TTFDLL.DLL.TTF_GlyphMetrics(font, ch, minx, maxx, miny, maxy, advance)


TTFDLL.DLL.TTF_SizeText.restype = ctypes.c_int
TTFDLL.DLL.TTF_SizeText.argtypes = [ctypes.POINTER(TTF_Font), ctypes.c_char_p, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]

def TTF_SizeText(font, text, w, h):
	"""
	Args:
		font: ctypes.POINTER(TTF_Font).
		text: ctypes.c_char_p.
		w: ctypes.POINTER(ctypes.c_int).
		h: ctypes.POINTER(ctypes.c_int).
	Returns:
		res: ctypes.c_int.
	"""
	return TTFDLL.DLL.TTF_SizeText(font, text, w, h)


TTFDLL.DLL.TTF_SizeUTF8.restype = ctypes.c_int
TTFDLL.DLL.TTF_SizeUTF8.argtypes = [ctypes.POINTER(TTF_Font), ctypes.c_char_p, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]

def TTF_SizeUTF8(font, text, w, h):
	"""
	Args:
		font: ctypes.POINTER(TTF_Font).
		text: ctypes.c_char_p.
		w: ctypes.POINTER(ctypes.c_int).
		h: ctypes.POINTER(ctypes.c_int).
	Returns:
		res: ctypes.c_int.
	"""
	return TTFDLL.DLL.TTF_SizeUTF8(font, text, w, h)


TTFDLL.DLL.TTF_SizeUNICODE.restype = ctypes.c_int
TTFDLL.DLL.TTF_SizeUNICODE.argtypes = [ctypes.POINTER(TTF_Font), ctypes.POINTER(ctypes.c_ushort), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]

def TTF_SizeUNICODE(font, text, w, h):
	"""
	Args:
		font: ctypes.POINTER(TTF_Font).
		text: ctypes.POINTER(ctypes.c_ushort).
		w: ctypes.POINTER(ctypes.c_int).
		h: ctypes.POINTER(ctypes.c_int).
	Returns:
		res: ctypes.c_int.
	"""
	return TTFDLL.DLL.TTF_SizeUNICODE(font, text, w, h)


TTFDLL.DLL.TTF_MeasureText.restype = ctypes.c_int
TTFDLL.DLL.TTF_MeasureText.argtypes = [ctypes.POINTER(TTF_Font), ctypes.c_char_p, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]

def TTF_MeasureText(font, text, measure_width, extent, count):
	"""
	Args:
		font: ctypes.POINTER(TTF_Font).
		text: ctypes.c_char_p.
		measure_width: ctypes.c_int.
		extent: ctypes.POINTER(ctypes.c_int).
		count: ctypes.POINTER(ctypes.c_int).
	Returns:
		res: ctypes.c_int.
	"""
	return TTFDLL.DLL.TTF_MeasureText(font, text, measure_width, extent, count)


TTFDLL.DLL.TTF_MeasureUTF8.restype = ctypes.c_int
TTFDLL.DLL.TTF_MeasureUTF8.argtypes = [ctypes.POINTER(TTF_Font), ctypes.c_char_p, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]

def TTF_MeasureUTF8(font, text, measure_width, extent, count):
	"""
	Args:
		font: ctypes.POINTER(TTF_Font).
		text: ctypes.c_char_p.
		measure_width: ctypes.c_int.
		extent: ctypes.POINTER(ctypes.c_int).
		count: ctypes.POINTER(ctypes.c_int).
	Returns:
		res: ctypes.c_int.
	"""
	return TTFDLL.DLL.TTF_MeasureUTF8(font, text, measure_width, extent, count)


TTFDLL.DLL.TTF_MeasureUNICODE.restype = ctypes.c_int
TTFDLL.DLL.TTF_MeasureUNICODE.argtypes = [ctypes.POINTER(TTF_Font), ctypes.POINTER(ctypes.c_ushort), ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]

def TTF_MeasureUNICODE(font, text, measure_width, extent, count):
	"""
	Args:
		font: ctypes.POINTER(TTF_Font).
		text: ctypes.POINTER(ctypes.c_ushort).
		measure_width: ctypes.c_int.
		extent: ctypes.POINTER(ctypes.c_int).
		count: ctypes.POINTER(ctypes.c_int).
	Returns:
		res: ctypes.c_int.
	"""
	return TTFDLL.DLL.TTF_MeasureUNICODE(font, text, measure_width, extent, count)


TTFDLL.DLL.TTF_RenderText_Solid.restype = ctypes.POINTER(SDL_Surface)
TTFDLL.DLL.TTF_RenderText_Solid.argtypes = [ctypes.POINTER(TTF_Font), ctypes.c_char_p, SDL_Color]

def TTF_RenderText_Solid(font, text, fg):
	"""
	Args:
		font: ctypes.POINTER(TTF_Font).
		text: ctypes.c_char_p.
		fg: SDL_Color.
	Returns:
		res: ctypes.POINTER(SDL_Surface).
	"""
	return TTFDLL.DLL.TTF_RenderText_Solid(font, text, fg)


TTFDLL.DLL.TTF_RenderUNICODE_Solid.restype = ctypes.POINTER(SDL_Surface)
TTFDLL.DLL.TTF_RenderUNICODE_Solid.argtypes = [ctypes.POINTER(TTF_Font), ctypes.POINTER(ctypes.c_ushort), SDL_Color]

def TTF_RenderUNICODE_Solid(font, text, fg):
	"""
	Args:
		font: ctypes.POINTER(TTF_Font).
		text: ctypes.POINTER(ctypes.c_ushort).
		fg: SDL_Color.
	Returns:
		res: ctypes.POINTER(SDL_Surface).
	"""
	return TTFDLL.DLL.TTF_RenderUNICODE_Solid(font, text, fg)


TTFDLL.DLL.TTF_RenderUTF8_Solid_Wrapped.restype = ctypes.POINTER(SDL_Surface)
TTFDLL.DLL.TTF_RenderUTF8_Solid_Wrapped.argtypes = [ctypes.POINTER(TTF_Font), ctypes.c_char_p, SDL_Color, ctypes.c_uint]

def TTF_RenderUTF8_Solid_Wrapped(font, text, fg, wrapLength):
	"""
	Args:
		font: ctypes.POINTER(TTF_Font).
		text: ctypes.c_char_p.
		fg: SDL_Color.
		wrapLength: ctypes.c_uint.
	Returns:
		res: ctypes.POINTER(SDL_Surface).
	"""
	return TTFDLL.DLL.TTF_RenderUTF8_Solid_Wrapped(font, text, fg, wrapLength)


TTFDLL.DLL.TTF_RenderGlyph_Solid.restype = ctypes.POINTER(SDL_Surface)
TTFDLL.DLL.TTF_RenderGlyph_Solid.argtypes = [ctypes.POINTER(TTF_Font), ctypes.c_ushort, SDL_Color]

def TTF_RenderGlyph_Solid(font, ch, fg):
	"""
	Args:
		font: ctypes.POINTER(TTF_Font).
		ch: ctypes.c_ushort.
		fg: SDL_Color.
	Returns:
		res: ctypes.POINTER(SDL_Surface).
	"""
	return TTFDLL.DLL.TTF_RenderGlyph_Solid(font, ch, fg)


TTFDLL.DLL.TTF_RenderText_Shaded.restype = ctypes.POINTER(SDL_Surface)
TTFDLL.DLL.TTF_RenderText_Shaded.argtypes = [ctypes.POINTER(TTF_Font), ctypes.c_char_p, SDL_Color, SDL_Color]

def TTF_RenderText_Shaded(font, text, fg, bg):
	"""
	Args:
		font: ctypes.POINTER(TTF_Font).
		text: ctypes.c_char_p.
		fg: SDL_Color.
		bg: SDL_Color.
	Returns:
		res: ctypes.POINTER(SDL_Surface).
	"""
	return TTFDLL.DLL.TTF_RenderText_Shaded(font, text, fg, bg)


TTFDLL.DLL.TTF_RenderUNICODE_Shaded.restype = ctypes.POINTER(SDL_Surface)
TTFDLL.DLL.TTF_RenderUNICODE_Shaded.argtypes = [ctypes.POINTER(TTF_Font), ctypes.POINTER(ctypes.c_ushort), SDL_Color, SDL_Color]

def TTF_RenderUNICODE_Shaded(font, text, fg, bg):
	"""
	Args:
		font: ctypes.POINTER(TTF_Font).
		text: ctypes.POINTER(ctypes.c_ushort).
		fg: SDL_Color.
		bg: SDL_Color.
	Returns:
		res: ctypes.POINTER(SDL_Surface).
	"""
	return TTFDLL.DLL.TTF_RenderUNICODE_Shaded(font, text, fg, bg)


TTFDLL.DLL.TTF_RenderUTF8_Shaded_Wrapped.restype = ctypes.POINTER(SDL_Surface)
TTFDLL.DLL.TTF_RenderUTF8_Shaded_Wrapped.argtypes = [ctypes.POINTER(TTF_Font), ctypes.c_char_p, SDL_Color, SDL_Color, ctypes.c_uint]

def TTF_RenderUTF8_Shaded_Wrapped(font, text, fg, bg, wrapLength):
	"""
	Args:
		font: ctypes.POINTER(TTF_Font).
		text: ctypes.c_char_p.
		fg: SDL_Color.
		bg: SDL_Color.
		wrapLength: ctypes.c_uint.
	Returns:
		res: ctypes.POINTER(SDL_Surface).
	"""
	return TTFDLL.DLL.TTF_RenderUTF8_Shaded_Wrapped(font, text, fg, bg, wrapLength)


TTFDLL.DLL.TTF_RenderGlyph_Shaded.restype = ctypes.POINTER(SDL_Surface)
TTFDLL.DLL.TTF_RenderGlyph_Shaded.argtypes = [ctypes.POINTER(TTF_Font), ctypes.c_ushort, SDL_Color, SDL_Color]

def TTF_RenderGlyph_Shaded(font, ch, fg, bg):
	"""
	Args:
		font: ctypes.POINTER(TTF_Font).
		ch: ctypes.c_ushort.
		fg: SDL_Color.
		bg: SDL_Color.
	Returns:
		res: ctypes.POINTER(SDL_Surface).
	"""
	return TTFDLL.DLL.TTF_RenderGlyph_Shaded(font, ch, fg, bg)


TTFDLL.DLL.TTF_RenderText_Blended.restype = ctypes.POINTER(SDL_Surface)
TTFDLL.DLL.TTF_RenderText_Blended.argtypes = [ctypes.POINTER(TTF_Font), ctypes.c_char_p, SDL_Color]

def TTF_RenderText_Blended(font, text, fg):
	"""
	Args:
		font: ctypes.POINTER(TTF_Font).
		text: ctypes.c_char_p.
		fg: SDL_Color.
	Returns:
		res: ctypes.POINTER(SDL_Surface).
	"""
	return TTFDLL.DLL.TTF_RenderText_Blended(font, text, fg)


TTFDLL.DLL.TTF_RenderUNICODE_Blended.restype = ctypes.POINTER(SDL_Surface)
TTFDLL.DLL.TTF_RenderUNICODE_Blended.argtypes = [ctypes.POINTER(TTF_Font), ctypes.POINTER(ctypes.c_ushort), SDL_Color]

def TTF_RenderUNICODE_Blended(font, text, fg):
	"""
	Args:
		font: ctypes.POINTER(TTF_Font).
		text: ctypes.POINTER(ctypes.c_ushort).
		fg: SDL_Color.
	Returns:
		res: ctypes.POINTER(SDL_Surface).
	"""
	return TTFDLL.DLL.TTF_RenderUNICODE_Blended(font, text, fg)


TTFDLL.DLL.TTF_RenderUTF8_Blended_Wrapped.restype = ctypes.POINTER(SDL_Surface)
TTFDLL.DLL.TTF_RenderUTF8_Blended_Wrapped.argtypes = [ctypes.POINTER(TTF_Font), ctypes.c_char_p, SDL_Color, ctypes.c_uint]

def TTF_RenderUTF8_Blended_Wrapped(font, text, fg, wrapLength):
	"""
	Args:
		font: ctypes.POINTER(TTF_Font).
		text: ctypes.c_char_p.
		fg: SDL_Color.
		wrapLength: ctypes.c_uint.
	Returns:
		res: ctypes.POINTER(SDL_Surface).
	"""
	return TTFDLL.DLL.TTF_RenderUTF8_Blended_Wrapped(font, text, fg, wrapLength)


TTFDLL.DLL.TTF_RenderGlyph_Blended.restype = ctypes.POINTER(SDL_Surface)
TTFDLL.DLL.TTF_RenderGlyph_Blended.argtypes = [ctypes.POINTER(TTF_Font), ctypes.c_ushort, SDL_Color]

def TTF_RenderGlyph_Blended(font, ch, fg):
	"""
	Args:
		font: ctypes.POINTER(TTF_Font).
		ch: ctypes.c_ushort.
		fg: SDL_Color.
	Returns:
		res: ctypes.POINTER(SDL_Surface).
	"""
	return TTFDLL.DLL.TTF_RenderGlyph_Blended(font, ch, fg)


TTFDLL.DLL.TTF_RenderText_LCD.restype = ctypes.POINTER(SDL_Surface)
TTFDLL.DLL.TTF_RenderText_LCD.argtypes = [ctypes.POINTER(TTF_Font), ctypes.c_char_p, SDL_Color, SDL_Color]

def TTF_RenderText_LCD(font, text, fg, bg):
	"""
	Args:
		font: ctypes.POINTER(TTF_Font).
		text: ctypes.c_char_p.
		fg: SDL_Color.
		bg: SDL_Color.
	Returns:
		res: ctypes.POINTER(SDL_Surface).
	"""
	return TTFDLL.DLL.TTF_RenderText_LCD(font, text, fg, bg)


TTFDLL.DLL.TTF_RenderUNICODE_LCD.restype = ctypes.POINTER(SDL_Surface)
TTFDLL.DLL.TTF_RenderUNICODE_LCD.argtypes = [ctypes.POINTER(TTF_Font), ctypes.POINTER(ctypes.c_ushort), SDL_Color, SDL_Color]

def TTF_RenderUNICODE_LCD(font, text, fg, bg):
	"""
	Args:
		font: ctypes.POINTER(TTF_Font).
		text: ctypes.POINTER(ctypes.c_ushort).
		fg: SDL_Color.
		bg: SDL_Color.
	Returns:
		res: ctypes.POINTER(SDL_Surface).
	"""
	return TTFDLL.DLL.TTF_RenderUNICODE_LCD(font, text, fg, bg)


TTFDLL.DLL.TTF_RenderUTF8_LCD_Wrapped.restype = ctypes.POINTER(SDL_Surface)
TTFDLL.DLL.TTF_RenderUTF8_LCD_Wrapped.argtypes = [ctypes.POINTER(TTF_Font), ctypes.c_char_p, SDL_Color, SDL_Color, ctypes.c_uint]

def TTF_RenderUTF8_LCD_Wrapped(font, text, fg, bg, wrapLength):
	"""
	Args:
		font: ctypes.POINTER(TTF_Font).
		text: ctypes.c_char_p.
		fg: SDL_Color.
		bg: SDL_Color.
		wrapLength: ctypes.c_uint.
	Returns:
		res: ctypes.POINTER(SDL_Surface).
	"""
	return TTFDLL.DLL.TTF_RenderUTF8_LCD_Wrapped(font, text, fg, bg, wrapLength)


TTFDLL.DLL.TTF_RenderGlyph_LCD.restype = ctypes.POINTER(SDL_Surface)
TTFDLL.DLL.TTF_RenderGlyph_LCD.argtypes = [ctypes.POINTER(TTF_Font), ctypes.c_ushort, SDL_Color, SDL_Color]

def TTF_RenderGlyph_LCD(font, ch, fg, bg):
	"""
	Args:
		font: ctypes.POINTER(TTF_Font).
		ch: ctypes.c_ushort.
		fg: SDL_Color.
		bg: SDL_Color.
	Returns:
		res: ctypes.POINTER(SDL_Surface).
	"""
	return TTFDLL.DLL.TTF_RenderGlyph_LCD(font, ch, fg, bg)


TTFDLL.DLL.TTF_WasInit.restype = ctypes.c_int
TTFDLL.DLL.TTF_WasInit.argtypes = []

def TTF_WasInit():
	"""
	Args:
		: None.
	Returns:
		res: ctypes.c_int.
	"""
	return TTFDLL.DLL.TTF_WasInit()


TTFDLL.DLL.TTF_GetFontKerningSize.restype = ctypes.c_int
TTFDLL.DLL.TTF_GetFontKerningSize.argtypes = [ctypes.POINTER(TTF_Font), ctypes.c_int, ctypes.c_int]

def TTF_GetFontKerningSize(font, prev_index, index):
	"""
	Args:
		font: ctypes.POINTER(TTF_Font).
		prev_index: ctypes.c_int.
		index: ctypes.c_int.
	Returns:
		res: ctypes.c_int.
	"""
	return TTFDLL.DLL.TTF_GetFontKerningSize(font, prev_index, index)


TTFDLL.DLL.TTF_GetFontKerningSizeGlyphs.restype = ctypes.c_int
TTFDLL.DLL.TTF_GetFontKerningSizeGlyphs.argtypes = [ctypes.POINTER(TTF_Font), ctypes.c_ushort, ctypes.c_ushort]

def TTF_GetFontKerningSizeGlyphs(font, previous_ch, ch):
	"""
	Args:
		font: ctypes.POINTER(TTF_Font).
		previous_ch: ctypes.c_ushort.
		ch: ctypes.c_ushort.
	Returns:
		res: ctypes.c_int.
	"""
	return TTFDLL.DLL.TTF_GetFontKerningSizeGlyphs(font, previous_ch, ch)


TTFDLL.DLL.TTF_GetFontKerningSizeGlyphs32.restype = ctypes.c_int
TTFDLL.DLL.TTF_GetFontKerningSizeGlyphs32.argtypes = [ctypes.POINTER(TTF_Font), ctypes.c_uint, ctypes.c_uint]

def TTF_GetFontKerningSizeGlyphs32(font, previous_ch, ch):
	"""
	Args:
		font: ctypes.POINTER(TTF_Font).
		previous_ch: ctypes.c_uint.
		ch: ctypes.c_uint.
	Returns:
		res: ctypes.c_int.
	"""
	return TTFDLL.DLL.TTF_GetFontKerningSizeGlyphs32(font, previous_ch, ch)


TTFDLL.DLL.TTF_SetFontSDF.restype = ctypes.c_int
TTFDLL.DLL.TTF_SetFontSDF.argtypes = [ctypes.POINTER(TTF_Font), ctypes.c_int]

def TTF_SetFontSDF(font, on_off):
	"""
	Args:
		font: ctypes.POINTER(TTF_Font).
		on_off: ctypes.c_int.
	Returns:
		res: ctypes.c_int.
	"""
	return TTFDLL.DLL.TTF_SetFontSDF(font, on_off)


TTFDLL.DLL.TTF_GetFontSDF.restype = ctypes.c_int
TTFDLL.DLL.TTF_GetFontSDF.argtypes = [ctypes.POINTER(TTF_Font)]

def TTF_GetFontSDF(font):
	"""
	Args:
		font: ctypes.POINTER(TTF_Font).
	Returns:
		res: ctypes.c_int.
	"""
	return TTFDLL.DLL.TTF_GetFontSDF(font)


TTFDLL.DLL.TTF_SetDirection.restype = ctypes.c_int
TTFDLL.DLL.TTF_SetDirection.argtypes = [ctypes.c_int]

def TTF_SetDirection(direction):
	"""
	Args:
		direction: ctypes.c_int.
	Returns:
		res: ctypes.c_int.
	"""
	return TTFDLL.DLL.TTF_SetDirection(direction)


TTFDLL.DLL.TTF_SetScript.restype = ctypes.c_int
TTFDLL.DLL.TTF_SetScript.argtypes = [ctypes.c_int]

def TTF_SetScript(script):
	"""
	Args:
		script: ctypes.c_int.
	Returns:
		res: ctypes.c_int.
	"""
	return TTFDLL.DLL.TTF_SetScript(script)


TTFDLL.DLL.TTF_SetFontDirection.restype = ctypes.c_int
TTFDLL.DLL.TTF_SetFontDirection.argtypes = [ctypes.POINTER(TTF_Font), ctypes.c_int]

def TTF_SetFontDirection(font, direction):
	"""
	Args:
		font: ctypes.POINTER(TTF_Font).
		direction: TTF_Direction.
	Returns:
		res: ctypes.c_int.
	"""
	return TTFDLL.DLL.TTF_SetFontDirection(font, direction)


TTFDLL.DLL.TTF_SetFontScriptName.restype = ctypes.c_int
TTFDLL.DLL.TTF_SetFontScriptName.argtypes = [ctypes.POINTER(TTF_Font), ctypes.c_char_p]

def TTF_SetFontScriptName(font, script):
	"""
	Args:
		font: ctypes.POINTER(TTF_Font).
		script: ctypes.c_char_p.
	Returns:
		res: ctypes.c_int.
	"""
	return TTFDLL.DLL.TTF_SetFontScriptName(font, script)