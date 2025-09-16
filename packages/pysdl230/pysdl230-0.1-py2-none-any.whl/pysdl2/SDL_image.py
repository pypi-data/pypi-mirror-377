import ctypes
from .LoadDLL import ImageDLL
from .SDL_rwops import SDL_RWops
from .SDL_surface import SDL_Surface
from .SDL_render import SDL_Renderer, SDL_Texture


SDL_IMAGE_MAJOR_VERSION = 2

SDL_IMAGE_MINOR_VERSION = 8

SDL_IMAGE_PATCHLEVEL = 8


class IMG_InitFlags:
	IMG_INIT_JPG = 0x00000001
	IMG_INIT_PNG = 0x00000002
	IMG_INIT_TIF = 0x00000004
	IMG_INIT_WEBP = 0x00000008
	IMG_INIT_JXL = 0x00000010
	IMG_INIT_AVIF = 0x00000020


class IMG_Animation(ctypes.Structure):
	_fields_ = [
		('w', ctypes.c_int),
		('h', ctypes.c_int),
		('count', ctypes.c_int),
		('frames', ctypes.POINTER(ctypes.POINTER(SDL_Surface))),
		('delays', ctypes.POINTER(ctypes.c_int)),
	]

ImageDLL.DLL.IMG_Init.restype = ctypes.c_int
ImageDLL.DLL.IMG_Init.argtypes = [ctypes.c_int]

def IMG_Init(flags):
	"""
	Args:
		flags: ctypes.c_int.
	Returns:
		res: ctypes.c_int.
	"""
	return ImageDLL.DLL.IMG_Init(flags)


ImageDLL.DLL.IMG_Quit.restype = None
ImageDLL.DLL.IMG_Quit.argtypes = []

def IMG_Quit():
	"""
	Args:
		: None.
	Returns:
		res: None.
	"""
	ImageDLL.DLL.IMG_Quit()


ImageDLL.DLL.IMG_LoadTyped_RW.restype = ctypes.POINTER(SDL_Surface)
ImageDLL.DLL.IMG_LoadTyped_RW.argtypes = [ctypes.POINTER(SDL_RWops), ctypes.c_int, ctypes.c_char_p]

def IMG_LoadTyped_RW(src, freesrc, type):
	"""
	Args:
		src: ctypes.POINTER(SDL_RWops).
		freesrc: ctypes.c_int.
		type: ctypes.c_char_p.
	Returns:
		res: ctypes.POINTER(SDL_Surface).
	"""
	return ImageDLL.DLL.IMG_LoadTyped_RW(src, freesrc, type)


ImageDLL.DLL.IMG_Load.restype = ctypes.POINTER(SDL_Surface)
ImageDLL.DLL.IMG_Load.argtypes = [ctypes.c_char_p]

def IMG_Load(file):
	"""
	Args:
		file: ctypes.c_char_p.
	Returns:
		res: ctypes.POINTER(SDL_Surface).
	"""
	return ImageDLL.DLL.IMG_Load(file)


ImageDLL.DLL.IMG_Load_RW.restype = ctypes.POINTER(SDL_Surface)
ImageDLL.DLL.IMG_Load_RW.argtypes = [ctypes.POINTER(SDL_RWops), ctypes.c_int]

def IMG_Load_RW(src, freesrc):
	"""
	Args:
		src: ctypes.POINTER(SDL_RWops).
		freesrc: ctypes.c_int.
	Returns:
		res: ctypes.POINTER(SDL_Surface).
	"""
	return ImageDLL.DLL.IMG_Load_RW(src, freesrc)


ImageDLL.DLL.IMG_LoadTexture.restype = ctypes.POINTER(SDL_Texture)
ImageDLL.DLL.IMG_LoadTexture.argtypes = [ctypes.POINTER(SDL_Renderer), ctypes.c_char_p]

def IMG_LoadTexture(renderer, file):
	"""
	Args:
		renderer: ctypes.POINTER(SDL_Renderer).
		file: ctypes.c_char_p.
	Returns:
		res: ctypes.POINTER(SDL_Texture).
	"""
	return ImageDLL.DLL.IMG_LoadTexture(renderer, file)


ImageDLL.DLL.IMG_LoadTexture_RW.restype = ctypes.POINTER(SDL_Texture)
ImageDLL.DLL.IMG_LoadTexture_RW.argtypes = [ctypes.POINTER(SDL_Renderer), ctypes.POINTER(SDL_RWops), ctypes.c_int]

def IMG_LoadTexture_RW(renderer, src, freesrc):
	"""
	Args:
		renderer: ctypes.POINTER(SDL_Renderer).
		src: ctypes.POINTER(SDL_RWops).
		freesrc: ctypes.c_int.
	Returns:
		res: ctypes.POINTER(SDL_Texture).
	"""
	return ImageDLL.DLL.IMG_LoadTexture_RW(renderer, src, freesrc)


ImageDLL.DLL.IMG_LoadTextureTyped_RW.restype = ctypes.POINTER(SDL_Texture)
ImageDLL.DLL.IMG_LoadTextureTyped_RW.argtypes = [ctypes.POINTER(SDL_Renderer), ctypes.POINTER(SDL_RWops), ctypes.c_int, ctypes.c_char_p]

def IMG_LoadTextureTyped_RW(renderer, src, freesrc, type):
	"""
	Args:
		renderer: ctypes.POINTER(SDL_Renderer).
		src: ctypes.POINTER(SDL_RWops).
		freesrc: ctypes.c_int.
		type: ctypes.c_char_p.
	Returns:
		res: ctypes.POINTER(SDL_Texture).
	"""
	return ImageDLL.DLL.IMG_LoadTextureTyped_RW(renderer, src, freesrc, type)


ImageDLL.DLL.IMG_isAVIF.restype = ctypes.c_int
ImageDLL.DLL.IMG_isAVIF.argtypes = [ctypes.POINTER(SDL_RWops)]

def IMG_isAVIF(src):
	"""
	Args:
		src: ctypes.POINTER(SDL_RWops).
	Returns:
		res: ctypes.c_int.
	"""
	return ImageDLL.DLL.IMG_isAVIF(src)


ImageDLL.DLL.IMG_isICO.restype = ctypes.c_int
ImageDLL.DLL.IMG_isICO.argtypes = [ctypes.POINTER(SDL_RWops)]

def IMG_isICO(src):
	"""
	Args:
		src: ctypes.POINTER(SDL_RWops).
	Returns:
		res: ctypes.c_int.
	"""
	return ImageDLL.DLL.IMG_isICO(src)


ImageDLL.DLL.IMG_isCUR.restype = ctypes.c_int
ImageDLL.DLL.IMG_isCUR.argtypes = [ctypes.POINTER(SDL_RWops)]

def IMG_isCUR(src):
	"""
	Args:
		src: ctypes.POINTER(SDL_RWops).
	Returns:
		res: ctypes.c_int.
	"""
	return ImageDLL.DLL.IMG_isCUR(src)


ImageDLL.DLL.IMG_isBMP.restype = ctypes.c_int
ImageDLL.DLL.IMG_isBMP.argtypes = [ctypes.POINTER(SDL_RWops)]

def IMG_isBMP(src):
	"""
	Args:
		src: ctypes.POINTER(SDL_RWops).
	Returns:
		res: ctypes.c_int.
	"""
	return ImageDLL.DLL.IMG_isBMP(src)


ImageDLL.DLL.IMG_isGIF.restype = ctypes.c_int
ImageDLL.DLL.IMG_isGIF.argtypes = [ctypes.POINTER(SDL_RWops)]

def IMG_isGIF(src):
	"""
	Args:
		src: ctypes.POINTER(SDL_RWops).
	Returns:
		res: ctypes.c_int.
	"""
	return ImageDLL.DLL.IMG_isGIF(src)


ImageDLL.DLL.IMG_isJPG.restype = ctypes.c_int
ImageDLL.DLL.IMG_isJPG.argtypes = [ctypes.POINTER(SDL_RWops)]

def IMG_isJPG(src):
	"""
	Args:
		src: ctypes.POINTER(SDL_RWops).
	Returns:
		res: ctypes.c_int.
	"""
	return ImageDLL.DLL.IMG_isJPG(src)


ImageDLL.DLL.IMG_isJXL.restype = ctypes.c_int
ImageDLL.DLL.IMG_isJXL.argtypes = [ctypes.POINTER(SDL_RWops)]

def IMG_isJXL(src):
	"""
	Args:
		src: ctypes.POINTER(SDL_RWops).
	Returns:
		res: ctypes.c_int.
	"""
	return ImageDLL.DLL.IMG_isJXL(src)


ImageDLL.DLL.IMG_isLBM.restype = ctypes.c_int
ImageDLL.DLL.IMG_isLBM.argtypes = [ctypes.POINTER(SDL_RWops)]

def IMG_isLBM(src):
	"""
	Args:
		src: ctypes.POINTER(SDL_RWops).
	Returns:
		res: ctypes.c_int.
	"""
	return ImageDLL.DLL.IMG_isLBM(src)


ImageDLL.DLL.IMG_isPCX.restype = ctypes.c_int
ImageDLL.DLL.IMG_isPCX.argtypes = [ctypes.POINTER(SDL_RWops)]

def IMG_isPCX(src):
	"""
	Args:
		src: ctypes.POINTER(SDL_RWops).
	Returns:
		res: ctypes.c_int.
	"""
	return ImageDLL.DLL.IMG_isPCX(src)


ImageDLL.DLL.IMG_isPNG.restype = ctypes.c_int
ImageDLL.DLL.IMG_isPNG.argtypes = [ctypes.POINTER(SDL_RWops)]

def IMG_isPNG(src):
	"""
	Args:
		src: ctypes.POINTER(SDL_RWops).
	Returns:
		res: ctypes.c_int.
	"""
	return ImageDLL.DLL.IMG_isPNG(src)


ImageDLL.DLL.IMG_isPNM.restype = ctypes.c_int
ImageDLL.DLL.IMG_isPNM.argtypes = [ctypes.POINTER(SDL_RWops)]

def IMG_isPNM(src):
	"""
	Args:
		src: ctypes.POINTER(SDL_RWops).
	Returns:
		res: ctypes.c_int.
	"""
	return ImageDLL.DLL.IMG_isPNM(src)


ImageDLL.DLL.IMG_isSVG.restype = ctypes.c_int
ImageDLL.DLL.IMG_isSVG.argtypes = [ctypes.POINTER(SDL_RWops)]

def IMG_isSVG(src):
	"""
	Args:
		src: ctypes.POINTER(SDL_RWops).
	Returns:
		res: ctypes.c_int.
	"""
	return ImageDLL.DLL.IMG_isSVG(src)


ImageDLL.DLL.IMG_isQOI.restype = ctypes.c_int
ImageDLL.DLL.IMG_isQOI.argtypes = [ctypes.POINTER(SDL_RWops)]

def IMG_isQOI(src):
	"""
	Args:
		src: ctypes.POINTER(SDL_RWops).
	Returns:
		res: ctypes.c_int.
	"""
	return ImageDLL.DLL.IMG_isQOI(src)


ImageDLL.DLL.IMG_isTIF.restype = ctypes.c_int
ImageDLL.DLL.IMG_isTIF.argtypes = [ctypes.POINTER(SDL_RWops)]

def IMG_isTIF(src):
	"""
	Args:
		src: ctypes.POINTER(SDL_RWops).
	Returns:
		res: ctypes.c_int.
	"""
	return ImageDLL.DLL.IMG_isTIF(src)


ImageDLL.DLL.IMG_isXCF.restype = ctypes.c_int
ImageDLL.DLL.IMG_isXCF.argtypes = [ctypes.POINTER(SDL_RWops)]

def IMG_isXCF(src):
	"""
	Args:
		src: ctypes.POINTER(SDL_RWops).
	Returns:
		res: ctypes.c_int.
	"""
	return ImageDLL.DLL.IMG_isXCF(src)


ImageDLL.DLL.IMG_isXPM.restype = ctypes.c_int
ImageDLL.DLL.IMG_isXPM.argtypes = [ctypes.POINTER(SDL_RWops)]

def IMG_isXPM(src):
	"""
	Args:
		src: ctypes.POINTER(SDL_RWops).
	Returns:
		res: ctypes.c_int.
	"""
	return ImageDLL.DLL.IMG_isXPM(src)


ImageDLL.DLL.IMG_isXV.restype = ctypes.c_int
ImageDLL.DLL.IMG_isXV.argtypes = [ctypes.POINTER(SDL_RWops)]

def IMG_isXV(src):
	"""
	Args:
		src: ctypes.POINTER(SDL_RWops).
	Returns:
		res: ctypes.c_int.
	"""
	return ImageDLL.DLL.IMG_isXV(src)


ImageDLL.DLL.IMG_isWEBP.restype = ctypes.c_int
ImageDLL.DLL.IMG_isWEBP.argtypes = [ctypes.POINTER(SDL_RWops)]

def IMG_isWEBP(src):
	"""
	Args:
		src: ctypes.POINTER(SDL_RWops).
	Returns:
		res: ctypes.c_int.
	"""
	return ImageDLL.DLL.IMG_isWEBP(src)


ImageDLL.DLL.IMG_LoadAVIF_RW.restype = ctypes.POINTER(SDL_Surface)
ImageDLL.DLL.IMG_LoadAVIF_RW.argtypes = [ctypes.POINTER(SDL_RWops)]

def IMG_LoadAVIF_RW(src):
	"""
	Args:
		src: ctypes.POINTER(SDL_RWops).
	Returns:
		res: ctypes.POINTER(SDL_Surface).
	"""
	return ImageDLL.DLL.IMG_LoadAVIF_RW(src)


ImageDLL.DLL.IMG_LoadICO_RW.restype = ctypes.POINTER(SDL_Surface)
ImageDLL.DLL.IMG_LoadICO_RW.argtypes = [ctypes.POINTER(SDL_RWops)]

def IMG_LoadICO_RW(src):
	"""
	Args:
		src: ctypes.POINTER(SDL_RWops).
	Returns:
		res: ctypes.POINTER(SDL_Surface).
	"""
	return ImageDLL.DLL.IMG_LoadICO_RW(src)


ImageDLL.DLL.IMG_LoadCUR_RW.restype = ctypes.POINTER(SDL_Surface)
ImageDLL.DLL.IMG_LoadCUR_RW.argtypes = [ctypes.POINTER(SDL_RWops)]

def IMG_LoadCUR_RW(src):
	"""
	Args:
		src: ctypes.POINTER(SDL_RWops).
	Returns:
		res: ctypes.POINTER(SDL_Surface).
	"""
	return ImageDLL.DLL.IMG_LoadCUR_RW(src)


ImageDLL.DLL.IMG_LoadBMP_RW.restype = ctypes.POINTER(SDL_Surface)
ImageDLL.DLL.IMG_LoadBMP_RW.argtypes = [ctypes.POINTER(SDL_RWops)]

def IMG_LoadBMP_RW(src):
	"""
	Args:
		src: ctypes.POINTER(SDL_RWops).
	Returns:
		res: ctypes.POINTER(SDL_Surface).
	"""
	return ImageDLL.DLL.IMG_LoadBMP_RW(src)


ImageDLL.DLL.IMG_LoadGIF_RW.restype = ctypes.POINTER(SDL_Surface)
ImageDLL.DLL.IMG_LoadGIF_RW.argtypes = [ctypes.POINTER(SDL_RWops)]

def IMG_LoadGIF_RW(src):
	"""
	Args:
		src: ctypes.POINTER(SDL_RWops).
	Returns:
		res: ctypes.POINTER(SDL_Surface).
	"""
	return ImageDLL.DLL.IMG_LoadGIF_RW(src)


ImageDLL.DLL.IMG_LoadJPG_RW.restype = ctypes.POINTER(SDL_Surface)
ImageDLL.DLL.IMG_LoadJPG_RW.argtypes = [ctypes.POINTER(SDL_RWops)]

def IMG_LoadJPG_RW(src):
	"""
	Args:
		src: ctypes.POINTER(SDL_RWops).
	Returns:
		res: ctypes.POINTER(SDL_Surface).
	"""
	return ImageDLL.DLL.IMG_LoadJPG_RW(src)


ImageDLL.DLL.IMG_LoadJXL_RW.restype = ctypes.POINTER(SDL_Surface)
ImageDLL.DLL.IMG_LoadJXL_RW.argtypes = [ctypes.POINTER(SDL_RWops)]

def IMG_LoadJXL_RW(src):
	"""
	Args:
		src: ctypes.POINTER(SDL_RWops).
	Returns:
		res: ctypes.POINTER(SDL_Surface).
	"""
	return ImageDLL.DLL.IMG_LoadJXL_RW(src)


ImageDLL.DLL.IMG_LoadLBM_RW.restype = ctypes.POINTER(SDL_Surface)
ImageDLL.DLL.IMG_LoadLBM_RW.argtypes = [ctypes.POINTER(SDL_RWops)]

def IMG_LoadLBM_RW(src):
	"""
	Args:
		src: ctypes.POINTER(SDL_RWops).
	Returns:
		res: ctypes.POINTER(SDL_Surface).
	"""
	return ImageDLL.DLL.IMG_LoadLBM_RW(src)


ImageDLL.DLL.IMG_LoadPCX_RW.restype = ctypes.POINTER(SDL_Surface)
ImageDLL.DLL.IMG_LoadPCX_RW.argtypes = [ctypes.POINTER(SDL_RWops)]

def IMG_LoadPCX_RW(src):
	"""
	Args:
		src: ctypes.POINTER(SDL_RWops).
	Returns:
		res: ctypes.POINTER(SDL_Surface).
	"""
	return ImageDLL.DLL.IMG_LoadPCX_RW(src)


ImageDLL.DLL.IMG_LoadPNG_RW.restype = ctypes.POINTER(SDL_Surface)
ImageDLL.DLL.IMG_LoadPNG_RW.argtypes = [ctypes.POINTER(SDL_RWops)]

def IMG_LoadPNG_RW(src):
	"""
	Args:
		src: ctypes.POINTER(SDL_RWops).
	Returns:
		res: ctypes.POINTER(SDL_Surface).
	"""
	return ImageDLL.DLL.IMG_LoadPNG_RW(src)


ImageDLL.DLL.IMG_LoadPNM_RW.restype = ctypes.POINTER(SDL_Surface)
ImageDLL.DLL.IMG_LoadPNM_RW.argtypes = [ctypes.POINTER(SDL_RWops)]

def IMG_LoadPNM_RW(src):
	"""
	Args:
		src: ctypes.POINTER(SDL_RWops).
	Returns:
		res: ctypes.POINTER(SDL_Surface).
	"""
	return ImageDLL.DLL.IMG_LoadPNM_RW(src)


ImageDLL.DLL.IMG_LoadSVG_RW.restype = ctypes.POINTER(SDL_Surface)
ImageDLL.DLL.IMG_LoadSVG_RW.argtypes = [ctypes.POINTER(SDL_RWops)]

def IMG_LoadSVG_RW(src):
	"""
	Args:
		src: ctypes.POINTER(SDL_RWops).
	Returns:
		res: ctypes.POINTER(SDL_Surface).
	"""
	return ImageDLL.DLL.IMG_LoadSVG_RW(src)


ImageDLL.DLL.IMG_LoadQOI_RW.restype = ctypes.POINTER(SDL_Surface)
ImageDLL.DLL.IMG_LoadQOI_RW.argtypes = [ctypes.POINTER(SDL_RWops)]

def IMG_LoadQOI_RW(src):
	"""
	Args:
		src: ctypes.POINTER(SDL_RWops).
	Returns:
		res: ctypes.POINTER(SDL_Surface).
	"""
	return ImageDLL.DLL.IMG_LoadQOI_RW(src)


ImageDLL.DLL.IMG_LoadTGA_RW.restype = ctypes.POINTER(SDL_Surface)
ImageDLL.DLL.IMG_LoadTGA_RW.argtypes = [ctypes.POINTER(SDL_RWops)]

def IMG_LoadTGA_RW(src):
	"""
	Args:
		src: ctypes.POINTER(SDL_RWops).
	Returns:
		res: ctypes.POINTER(SDL_Surface).
	"""
	return ImageDLL.DLL.IMG_LoadTGA_RW(src)


ImageDLL.DLL.IMG_LoadTIF_RW.restype = ctypes.POINTER(SDL_Surface)
ImageDLL.DLL.IMG_LoadTIF_RW.argtypes = [ctypes.POINTER(SDL_RWops)]

def IMG_LoadTIF_RW(src):
	"""
	Args:
		src: ctypes.POINTER(SDL_RWops).
	Returns:
		res: ctypes.POINTER(SDL_Surface).
	"""
	return ImageDLL.DLL.IMG_LoadTIF_RW(src)


ImageDLL.DLL.IMG_LoadXCF_RW.restype = ctypes.POINTER(SDL_Surface)
ImageDLL.DLL.IMG_LoadXCF_RW.argtypes = [ctypes.POINTER(SDL_RWops)]

def IMG_LoadXCF_RW(src):
	"""
	Args:
		src: ctypes.POINTER(SDL_RWops).
	Returns:
		res: ctypes.POINTER(SDL_Surface).
	"""
	return ImageDLL.DLL.IMG_LoadXCF_RW(src)


ImageDLL.DLL.IMG_LoadXPM_RW.restype = ctypes.POINTER(SDL_Surface)
ImageDLL.DLL.IMG_LoadXPM_RW.argtypes = [ctypes.POINTER(SDL_RWops)]

def IMG_LoadXPM_RW(src):
	"""
	Args:
		src: ctypes.POINTER(SDL_RWops).
	Returns:
		res: ctypes.POINTER(SDL_Surface).
	"""
	return ImageDLL.DLL.IMG_LoadXPM_RW(src)


ImageDLL.DLL.IMG_LoadXV_RW.restype = ctypes.POINTER(SDL_Surface)
ImageDLL.DLL.IMG_LoadXV_RW.argtypes = [ctypes.POINTER(SDL_RWops)]

def IMG_LoadXV_RW(src):
	"""
	Args:
		src: ctypes.POINTER(SDL_RWops).
	Returns:
		res: ctypes.POINTER(SDL_Surface).
	"""
	return ImageDLL.DLL.IMG_LoadXV_RW(src)


ImageDLL.DLL.IMG_LoadWEBP_RW.restype = ctypes.POINTER(SDL_Surface)
ImageDLL.DLL.IMG_LoadWEBP_RW.argtypes = [ctypes.POINTER(SDL_RWops)]

def IMG_LoadWEBP_RW(src):
	"""
	Args:
		src: ctypes.POINTER(SDL_RWops).
	Returns:
		res: ctypes.POINTER(SDL_Surface).
	"""
	return ImageDLL.DLL.IMG_LoadWEBP_RW(src)


ImageDLL.DLL.IMG_LoadSizedSVG_RW.restype = ctypes.POINTER(SDL_Surface)
ImageDLL.DLL.IMG_LoadSizedSVG_RW.argtypes = [ctypes.POINTER(SDL_RWops), ctypes.c_int, ctypes.c_int]

def IMG_LoadSizedSVG_RW(src, width, height):
	"""
	Args:
		src: ctypes.POINTER(SDL_RWops).
		width: ctypes.c_int.
		height: ctypes.c_int.
	Returns:
		res: ctypes.POINTER(SDL_Surface).
	"""
	return ImageDLL.DLL.IMG_LoadSizedSVG_RW(src, width, height)


ImageDLL.DLL.IMG_ReadXPMFromArray.restype = ctypes.POINTER(SDL_Surface)
ImageDLL.DLL.IMG_ReadXPMFromArray.argtypes = [ctypes.POINTER(ctypes.POINTER(ctypes.c_char))]

def IMG_ReadXPMFromArray(xpm):
	"""
	Args:
		xpm: ctypes.POINTER(ctypes.POINTER(ctypes.c_char)).
	Returns:
		res: ctypes.POINTER(SDL_Surface).
	"""
	return ImageDLL.DLL.IMG_ReadXPMFromArray(xpm)


ImageDLL.DLL.IMG_ReadXPMFromArrayToRGB888.restype = ctypes.POINTER(SDL_Surface)
ImageDLL.DLL.IMG_ReadXPMFromArrayToRGB888.argtypes = [ctypes.POINTER(ctypes.POINTER(ctypes.c_char))]

def IMG_ReadXPMFromArrayToRGB888(xpm):
	"""
	Args:
		xpm: ctypes.POINTER(ctypes.POINTER(ctypes.c_char)).
	Returns:
		res: ctypes.POINTER(SDL_Surface).
	"""
	return ImageDLL.DLL.IMG_ReadXPMFromArrayToRGB888(xpm)


ImageDLL.DLL.IMG_SavePNG.restype = ctypes.c_int
ImageDLL.DLL.IMG_SavePNG.argtypes = [ctypes.POINTER(SDL_Surface), ctypes.c_char_p]

def IMG_SavePNG(surface, file):
	"""
	Args:
		surface: ctypes.POINTER(SDL_Surface).
		file: ctypes.c_char_p.
	Returns:
		res: ctypes.c_int.
	"""
	return ImageDLL.DLL.IMG_SavePNG(surface, file)


ImageDLL.DLL.IMG_SavePNG_RW.restype = ctypes.c_int
ImageDLL.DLL.IMG_SavePNG_RW.argtypes = [ctypes.POINTER(SDL_Surface), ctypes.POINTER(SDL_RWops), ctypes.c_int]

def IMG_SavePNG_RW(surface, dst, freedst):
	"""
	Args:
		surface: ctypes.POINTER(SDL_Surface).
		dst: ctypes.POINTER(SDL_RWops).
		freedst: ctypes.c_int.
	Returns:
		res: ctypes.c_int.
	"""
	return ImageDLL.DLL.IMG_SavePNG_RW(surface, dst, freedst)


ImageDLL.DLL.IMG_SaveJPG.restype = ctypes.c_int
ImageDLL.DLL.IMG_SaveJPG.argtypes = [ctypes.POINTER(SDL_Surface), ctypes.c_char_p, ctypes.c_int]

def IMG_SaveJPG(surface, file, quality):
	"""
	Args:
		surface: ctypes.POINTER(SDL_Surface).
		file: ctypes.c_char_p.
		quality: ctypes.c_int.
	Returns:
		res: ctypes.c_int.
	"""
	return ImageDLL.DLL.IMG_SaveJPG(surface, file, quality)


ImageDLL.DLL.IMG_SaveJPG_RW.restype = ctypes.c_int
ImageDLL.DLL.IMG_SaveJPG_RW.argtypes = [ctypes.POINTER(SDL_Surface), ctypes.POINTER(SDL_RWops), ctypes.c_int, ctypes.c_int]

def IMG_SaveJPG_RW(surface, dst, freedst, quality):
	"""
	Args:
		surface: ctypes.POINTER(SDL_Surface).
		dst: ctypes.POINTER(SDL_RWops).
		freedst: ctypes.c_int.
		quality: ctypes.c_int.
	Returns:
		res: ctypes.c_int.
	"""
	return ImageDLL.DLL.IMG_SaveJPG_RW(surface, dst, freedst, quality)


ImageDLL.DLL.IMG_LoadAnimation.restype = ctypes.POINTER(IMG_Animation)
ImageDLL.DLL.IMG_LoadAnimation.argtypes = [ctypes.c_char_p]

def IMG_LoadAnimation(file):
	"""
	Args:
		file: ctypes.c_char_p.
	Returns:
		res: ctypes.POINTER(IMG_Animation).
	"""
	return ImageDLL.DLL.IMG_LoadAnimation(file)


ImageDLL.DLL.IMG_LoadAnimation_RW.restype = ctypes.POINTER(IMG_Animation)
ImageDLL.DLL.IMG_LoadAnimation_RW.argtypes = [ctypes.POINTER(SDL_RWops), ctypes.c_int]

def IMG_LoadAnimation_RW(src, freesrc):
	"""
	Args:
		src: ctypes.POINTER(SDL_RWops).
		freesrc: ctypes.c_int.
	Returns:
		res: ctypes.POINTER(IMG_Animation).
	"""
	return ImageDLL.DLL.IMG_LoadAnimation_RW(src, freesrc)


ImageDLL.DLL.IMG_LoadAnimationTyped_RW.restype = ctypes.POINTER(IMG_Animation)
ImageDLL.DLL.IMG_LoadAnimationTyped_RW.argtypes = [ctypes.POINTER(SDL_RWops), ctypes.c_int, ctypes.c_char_p]

def IMG_LoadAnimationTyped_RW(src, freesrc, type):
	"""
	Args:
		src: ctypes.POINTER(SDL_RWops).
		freesrc: ctypes.c_int.
		type: ctypes.c_char_p.
	Returns:
		res: ctypes.POINTER(IMG_Animation).
	"""
	return ImageDLL.DLL.IMG_LoadAnimationTyped_RW(src, freesrc, type)


ImageDLL.DLL.IMG_FreeAnimation.restype = None
ImageDLL.DLL.IMG_FreeAnimation.argtypes = [ctypes.POINTER(IMG_Animation)]

def IMG_FreeAnimation(anim):
	"""
	Args:
		anim: ctypes.POINTER(IMG_Animation).
	Returns:
		res: None.
	"""
	ImageDLL.DLL.IMG_FreeAnimation(anim)


ImageDLL.DLL.IMG_LoadGIFAnimation_RW.restype = ctypes.POINTER(IMG_Animation)
ImageDLL.DLL.IMG_LoadGIFAnimation_RW.argtypes = [ctypes.POINTER(SDL_RWops)]

def IMG_LoadGIFAnimation_RW(src):
	"""
	Args:
		src: ctypes.POINTER(SDL_RWops).
	Returns:
		res: ctypes.POINTER(IMG_Animation).
	"""
	return ImageDLL.DLL.IMG_LoadGIFAnimation_RW(src)


ImageDLL.DLL.IMG_LoadWEBPAnimation_RW.restype = ctypes.POINTER(IMG_Animation)
ImageDLL.DLL.IMG_LoadWEBPAnimation_RW.argtypes = [ctypes.POINTER(SDL_RWops)]

def IMG_LoadWEBPAnimation_RW(src):
	"""
	Args:
		src: ctypes.POINTER(SDL_RWops).
	Returns:
		res: ctypes.POINTER(IMG_Animation).
	"""
	return ImageDLL.DLL.IMG_LoadWEBPAnimation_RW(src)