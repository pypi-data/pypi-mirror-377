import ctypes
from .LoadDLL import LoadDLL
from .SDL_video import SDL_Window
from .SDL_pixels import SDL_Color
from .SDL_surface import SDL_Surface
from .SDL_rect import SDL_FRect, SDL_Rect, SDL_FPoint, SDL_Point


class SDL_RendererFlags:
	SDL_RENDERER_SOFTWARE = 0x00000001
	SDL_RENDERER_ACCELERATED = 0x00000002
	SDL_RENDERER_PRESENTVSYNC = 0x00000004
	SDL_RENDERER_TARGETTEXTURE = 0x00000008


class SDL_ScaleMode:
	SDL_ScaleModeNearest = 0
	SDL_ScaleModeLinear = 1
	SDL_ScaleModeBest = 2


class SDL_TextureAccess:
	SDL_TEXTUREACCESS_STATIC = 0
	SDL_TEXTUREACCESS_STREAMING = 1
	SDL_TEXTUREACCESS_TARGET = 2


class SDL_TextureModulate:
	SDL_TEXTUREMODULATE_NONE = 0x00000000
	SDL_TEXTUREMODULATE_COLOR = 0x00000001
	SDL_TEXTUREMODULATE_ALPHA = 0x00000002


class SDL_RendererFlip:
	SDL_FLIP_NONE = 0x00000000
	SDL_FLIP_HORIZONTAL = 0x00000001
	SDL_FLIP_VERTICAL = 0x00000002


class SDL_Renderer(ctypes.Structure): pass


class SDL_Texture(ctypes.Structure): pass


class SDL_RendererInfo(ctypes.Structure):
	_fields_ = [
		('name', ctypes.c_char_p),
		('flags', ctypes.c_uint),
		('num_texture_formats', ctypes.c_uint),
		('texture_formats', ctypes.c_uint * 16),
		('max_texture_width', ctypes.c_int),
		('max_texture_height', ctypes.c_int),
	]


class SDL_Vertex(ctypes.Structure):
	_fields_ = [
		('position', SDL_FPoint),
		('color', SDL_Color),
		('tex_coord', SDL_FPoint),
	]

LoadDLL.DLL.SDL_GetNumRenderDrivers.restype = ctypes.c_int
LoadDLL.DLL.SDL_GetNumRenderDrivers.argtypes = []

def SDL_GetNumRenderDrivers():
	"""
	Args:
		: None.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_GetNumRenderDrivers()


LoadDLL.DLL.SDL_GetRenderDriverInfo.restype = ctypes.c_int
LoadDLL.DLL.SDL_GetRenderDriverInfo.argtypes = [ctypes.c_int, ctypes.POINTER(SDL_RendererInfo)]

def SDL_GetRenderDriverInfo(index, info):
	"""
	Args:
		index: ctypes.c_int.
		info: ctypes.POINTER(SDL_RendererInfo).
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_GetRenderDriverInfo(index, info)


LoadDLL.DLL.SDL_CreateRenderer.restype = ctypes.POINTER(SDL_Renderer)
LoadDLL.DLL.SDL_CreateRenderer.argtypes = [ctypes.POINTER(SDL_Window), ctypes.c_int, ctypes.c_uint]

def SDL_CreateRenderer(window, index, flags):
	"""
	Args:
		window: ctypes.POINTER(SDL_Window).
		index: ctypes.c_int.
		flags: ctypes.c_uint.
	Returns:
		res: ctypes.POINTER(SDL_Renderer).
	"""
	return LoadDLL.DLL.SDL_CreateRenderer(window, index, flags)


LoadDLL.DLL.SDL_GetRenderer.restype = ctypes.POINTER(SDL_Renderer)
LoadDLL.DLL.SDL_GetRenderer.argtypes = [ctypes.POINTER(SDL_Window)]

def SDL_GetRenderer(window):
	"""
	Args:
		window: ctypes.POINTER(SDL_Window).
	Returns:
		res: ctypes.POINTER(SDL_Renderer).
	"""
	return LoadDLL.DLL.SDL_GetRenderer(window)


LoadDLL.DLL.SDL_RenderPresent.restype = None
LoadDLL.DLL.SDL_RenderPresent.argtypes = [ctypes.POINTER(SDL_Renderer)]

def SDL_RenderPresent(renderer):
	"""
	Args:
		renderer: ctypes.POINTER(SDL_Renderer).
	Returns:
		res: None.
	"""
	LoadDLL.DLL.SDL_RenderPresent(renderer)


LoadDLL.DLL.SDL_RenderGetWindow.restype = ctypes.POINTER(SDL_Window)
LoadDLL.DLL.SDL_RenderGetWindow.argtypes = [ctypes.POINTER(SDL_Renderer)]

def SDL_RenderGetWindow(renderer):
	"""
	Args:
		renderer: ctypes.POINTER(SDL_Renderer).
	Returns:
		res: ctypes.POINTER(SDL_Window).
	"""
	return LoadDLL.DLL.SDL_RenderGetWindow(renderer)


LoadDLL.DLL.SDL_GetRendererInfo.restype = ctypes.c_int
LoadDLL.DLL.SDL_GetRendererInfo.argtypes = [ctypes.POINTER(SDL_Renderer), ctypes.POINTER(SDL_RendererInfo)]

def SDL_GetRendererInfo(renderer, info):
	"""
	Args:
		renderer: ctypes.POINTER(SDL_Renderer).
		info: ctypes.POINTER(SDL_RendererInfo).
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_GetRendererInfo(renderer, info)


LoadDLL.DLL.SDL_CreateTexture.restype = ctypes.POINTER(SDL_Texture)
LoadDLL.DLL.SDL_CreateTexture.argtypes = [ctypes.POINTER(SDL_Renderer), ctypes.c_uint, ctypes.c_int, ctypes.c_int, ctypes.c_int]

def SDL_CreateTexture(renderer, format, access, w, h):
	"""
	Args:
		renderer: ctypes.POINTER(SDL_Renderer).
		format: ctypes.c_uint.
		access: ctypes.c_int.
		w: ctypes.c_int.
		h: ctypes.c_int.
	Returns:
		res: ctypes.POINTER(SDL_Texture).
	"""
	return LoadDLL.DLL.SDL_CreateTexture(renderer, format, access, w, h)


LoadDLL.DLL.SDL_CreateTextureFromSurface.restype = ctypes.POINTER(SDL_Texture)
LoadDLL.DLL.SDL_CreateTextureFromSurface.argtypes = [ctypes.POINTER(SDL_Renderer), ctypes.POINTER(SDL_Surface)]

def SDL_CreateTextureFromSurface(renderer, surface):
	"""
	Args:
		renderer: ctypes.POINTER(SDL_Renderer).
		surface: ctypes.POINTER(SDL_Surface).
	Returns:
		res: ctypes.POINTER(SDL_Texture).
	"""
	return LoadDLL.DLL.SDL_CreateTextureFromSurface(renderer, surface)


LoadDLL.DLL.SDL_QueryTexture.restype = ctypes.c_int
LoadDLL.DLL.SDL_QueryTexture.argtypes = [ctypes.POINTER(SDL_Texture), ctypes.POINTER(ctypes.c_uint), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]

def SDL_QueryTexture(texture, format, access, w, h):
	"""
	Args:
		texture: ctypes.POINTER(SDL_Texture).
		format: ctypes.POINTER(ctypes.c_uint).
		access: ctypes.POINTER(ctypes.c_int).
		w: ctypes.POINTER(ctypes.c_int).
		h: ctypes.POINTER(ctypes.c_int).
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_QueryTexture(texture, format, access, w, h)


LoadDLL.DLL.SDL_RenderCopyEx.restype = ctypes.c_int
LoadDLL.DLL.SDL_RenderCopyEx.argtypes = [ctypes.POINTER(SDL_Renderer), ctypes.POINTER(SDL_Texture), ctypes.POINTER(SDL_Rect), ctypes.POINTER(SDL_Rect), ctypes.c_double, ctypes.POINTER(SDL_Point), ctypes.c_int]

def SDL_RenderCopyEx(renderer, texture, srcrect, dstrect, angle, center, flip):
	"""
	Args:
		renderer: ctypes.POINTER(SDL_Renderer).
		texture: ctypes.POINTER(SDL_Texture).
		srcrect: ctypes.POINTER(SDL_Rect).
		dstrect: ctypes.POINTER(SDL_Rect).
		angle: ctypes.c_double.
		center: ctypes.POINTER(SDL_Point).
		flip: ctypes.c_int.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_RenderCopyEx(renderer, texture, srcrect, dstrect, angle, center, flip)


LoadDLL.DLL.SDL_GetTextureColorMod.restype = ctypes.c_int
LoadDLL.DLL.SDL_GetTextureColorMod.argtypes = [ctypes.POINTER(SDL_Texture), ctypes.POINTER(ctypes.c_ubyte), ctypes.POINTER(ctypes.c_ubyte), ctypes.POINTER(ctypes.c_ubyte)]

def SDL_GetTextureColorMod(texture, r, g, b):
	"""
	Args:
		texture: ctypes.POINTER(SDL_Texture).
		r: ctypes.POINTER(ctypes.c_ubyte).
		g: ctypes.POINTER(ctypes.c_ubyte).
		b: ctypes.POINTER(ctypes.c_ubyte).
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_GetTextureColorMod(texture, r, g, b)


LoadDLL.DLL.SDL_GetTextureAlphaMod.restype = ctypes.c_int
LoadDLL.DLL.SDL_GetTextureAlphaMod.argtypes = [ctypes.POINTER(SDL_Texture), ctypes.POINTER(ctypes.c_ubyte)]

def SDL_GetTextureAlphaMod(texture, alpha):
	"""
	Args:
		texture: ctypes.POINTER(SDL_Texture).
		alpha: ctypes.POINTER(ctypes.c_ubyte).
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_GetTextureAlphaMod(texture, alpha)


LoadDLL.DLL.SDL_GetTextureBlendMode.restype = ctypes.c_int
LoadDLL.DLL.SDL_GetTextureBlendMode.argtypes = [ctypes.POINTER(SDL_Texture), ctypes.POINTER(ctypes.c_int)]

def SDL_GetTextureBlendMode(texture, blendMode):
	"""
	Args:
		texture: ctypes.POINTER(SDL_Texture).
		blendMode: ctypes.POINTER(ctypes.c_int).
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_GetTextureBlendMode(texture, blendMode)


LoadDLL.DLL.SDL_GetTextureScaleMode.restype = ctypes.c_int
LoadDLL.DLL.SDL_GetTextureScaleMode.argtypes = [ctypes.POINTER(SDL_Texture), ctypes.POINTER(ctypes.c_int)]

def SDL_GetTextureScaleMode(texture, scaleMode):
	"""
	Args:
		texture: ctypes.POINTER(SDL_Texture).
		scaleMode: ctypes.POINTER(SDL_ScaleMode).
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_GetTextureScaleMode(texture, scaleMode)


LoadDLL.DLL.SDL_GetTextureUserData.restype = ctypes.c_void_p
LoadDLL.DLL.SDL_GetTextureUserData.argtypes = [ctypes.POINTER(SDL_Texture)]

def SDL_GetTextureUserData(texture):
	"""
	Args:
		texture: ctypes.POINTER(SDL_Texture).
	Returns:
		res: ctypes.c_void_p.
	"""
	return LoadDLL.DLL.SDL_GetTextureUserData(texture)


LoadDLL.DLL.SDL_UpdateTexture.restype = ctypes.c_int
LoadDLL.DLL.SDL_UpdateTexture.argtypes = [ctypes.POINTER(SDL_Texture), ctypes.POINTER(SDL_Rect), ctypes.c_void_p, ctypes.c_int]

def SDL_UpdateTexture(texture, rect, pixels, pitch):
	"""
	Args:
		texture: ctypes.POINTER(SDL_Texture).
		rect: ctypes.POINTER(SDL_Rect).
		pixels: ctypes.c_void_p.
		pitch: ctypes.c_int.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_UpdateTexture(texture, rect, pixels, pitch)


LoadDLL.DLL.SDL_UpdateNVTexture.restype = ctypes.c_int
LoadDLL.DLL.SDL_UpdateNVTexture.argtypes = [ctypes.POINTER(SDL_Texture), ctypes.POINTER(SDL_Rect), ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int]

def SDL_UpdateNVTexture(texture, rect, Yplane, Ypitch, UVplane, UVpitch):
	"""
	Args:
		texture: ctypes.POINTER(SDL_Texture).
		rect: ctypes.POINTER(SDL_Rect).
		Yplane: ctypes.POINTER(ctypes.c_ubyte).
		Ypitch: ctypes.c_int.
		UVplane: ctypes.POINTER(ctypes.c_ubyte).
		UVpitch: ctypes.c_int.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_UpdateNVTexture(texture, rect, Yplane, Ypitch, UVplane, UVpitch)


LoadDLL.DLL.SDL_LockTextureToSurface.restype = ctypes.c_int
LoadDLL.DLL.SDL_LockTextureToSurface.argtypes = [ctypes.POINTER(SDL_Texture), ctypes.POINTER(SDL_Rect), ctypes.POINTER(ctypes.POINTER(SDL_Surface))]

def SDL_LockTextureToSurface(texture, rect, surface):
	"""
	Args:
		texture: ctypes.POINTER(SDL_Texture).
		rect: ctypes.POINTER(SDL_Rect).
		surface: ctypes.POINTER(ctypes.POINTER(SDL_Surface)).
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_LockTextureToSurface(texture, rect, surface)


LoadDLL.DLL.SDL_RenderTargetSupported.restype = ctypes.c_int
LoadDLL.DLL.SDL_RenderTargetSupported.argtypes = [ctypes.POINTER(SDL_Renderer)]

def SDL_RenderTargetSupported(renderer):
	"""
	Args:
		renderer: ctypes.POINTER(SDL_Renderer).
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_RenderTargetSupported(renderer)


LoadDLL.DLL.SDL_SetRenderTarget.restype = ctypes.c_int
LoadDLL.DLL.SDL_SetRenderTarget.argtypes = [ctypes.POINTER(SDL_Renderer), ctypes.POINTER(SDL_Texture)]

def SDL_SetRenderTarget(renderer, texture):
	"""
	Args:
		renderer: ctypes.POINTER(SDL_Renderer).
		texture: ctypes.POINTER(SDL_Texture).
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_SetRenderTarget(renderer, texture)


LoadDLL.DLL.SDL_RenderSetLogicalSize.restype = ctypes.c_int
LoadDLL.DLL.SDL_RenderSetLogicalSize.argtypes = [ctypes.POINTER(SDL_Renderer), ctypes.c_int, ctypes.c_int]

def SDL_RenderSetLogicalSize(renderer, w, h):
	"""
	Args:
		renderer: ctypes.POINTER(SDL_Renderer).
		w: ctypes.c_int.
		h: ctypes.c_int.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_RenderSetLogicalSize(renderer, w, h)


LoadDLL.DLL.SDL_RenderGetLogicalSize.restype = None
LoadDLL.DLL.SDL_RenderGetLogicalSize.argtypes = [ctypes.POINTER(SDL_Renderer), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]

def SDL_RenderGetLogicalSize(renderer, w, h):
	"""
	Args:
		renderer: ctypes.POINTER(SDL_Renderer).
		w: ctypes.POINTER(ctypes.c_int).
		h: ctypes.POINTER(ctypes.c_int).
	Returns:
		res: None.
	"""
	LoadDLL.DLL.SDL_RenderGetLogicalSize(renderer, w, h)


LoadDLL.DLL.SDL_RenderSetIntegerScale.restype = ctypes.c_int
LoadDLL.DLL.SDL_RenderSetIntegerScale.argtypes = [ctypes.POINTER(SDL_Renderer), ctypes.c_int]

def SDL_RenderSetIntegerScale(renderer, enable):
	"""
	Args:
		renderer: ctypes.POINTER(SDL_Renderer).
		enable: ctypes.c_int.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_RenderSetIntegerScale(renderer, enable)


LoadDLL.DLL.SDL_RenderSetViewport.restype = ctypes.c_int
LoadDLL.DLL.SDL_RenderSetViewport.argtypes = [ctypes.POINTER(SDL_Renderer), ctypes.POINTER(SDL_Rect)]

def SDL_RenderSetViewport(renderer, rect):
	"""
	Args:
		renderer: ctypes.POINTER(SDL_Renderer).
		rect: ctypes.POINTER(SDL_Rect).
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_RenderSetViewport(renderer, rect)


LoadDLL.DLL.SDL_RenderSetClipRect.restype = ctypes.c_int
LoadDLL.DLL.SDL_RenderSetClipRect.argtypes = [ctypes.POINTER(SDL_Renderer), ctypes.POINTER(SDL_Rect)]

def SDL_RenderSetClipRect(renderer, rect):
	"""
	Args:
		renderer: ctypes.POINTER(SDL_Renderer).
		rect: ctypes.POINTER(SDL_Rect).
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_RenderSetClipRect(renderer, rect)


LoadDLL.DLL.SDL_RenderIsClipEnabled.restype = ctypes.c_int
LoadDLL.DLL.SDL_RenderIsClipEnabled.argtypes = [ctypes.POINTER(SDL_Renderer)]

def SDL_RenderIsClipEnabled(renderer):
	"""
	Args:
		renderer: ctypes.POINTER(SDL_Renderer).
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_RenderIsClipEnabled(renderer)


LoadDLL.DLL.SDL_RenderSetScale.restype = ctypes.c_int
LoadDLL.DLL.SDL_RenderSetScale.argtypes = [ctypes.POINTER(SDL_Renderer), ctypes.c_float, ctypes.c_float]

def SDL_RenderSetScale(renderer, scaleX, scaleY):
	"""
	Args:
		renderer: ctypes.POINTER(SDL_Renderer).
		scaleX: ctypes.c_float.
		scaleY: ctypes.c_float.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_RenderSetScale(renderer, scaleX, scaleY)


LoadDLL.DLL.SDL_RenderWindowToLogical.restype = None
LoadDLL.DLL.SDL_RenderWindowToLogical.argtypes = [ctypes.POINTER(SDL_Renderer), ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float)]

def SDL_RenderWindowToLogical(renderer, windowX, windowY, logicalX, logicalY):
	"""
	Args:
		renderer: ctypes.POINTER(SDL_Renderer).
		windowX: ctypes.c_int.
		windowY: ctypes.c_int.
		logicalX: ctypes.POINTER(ctypes.c_float).
		logicalY: ctypes.POINTER(ctypes.c_float).
	Returns:
		res: None.
	"""
	LoadDLL.DLL.SDL_RenderWindowToLogical(renderer, windowX, windowY, logicalX, logicalY)


LoadDLL.DLL.SDL_SetRenderDrawColor.restype = ctypes.c_int
LoadDLL.DLL.SDL_SetRenderDrawColor.argtypes = [ctypes.POINTER(SDL_Renderer), ctypes.c_ubyte, ctypes.c_ubyte, ctypes.c_ubyte, ctypes.c_ubyte]

def SDL_SetRenderDrawColor(renderer, r, g, b, a):
	"""
	Args:
		renderer: ctypes.POINTER(SDL_Renderer).
		r: ctypes.c_ubyte.
		g: ctypes.c_ubyte.
		b: ctypes.c_ubyte.
		a: ctypes.c_ubyte.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_SetRenderDrawColor(renderer, r, g, b, a)


LoadDLL.DLL.SDL_SetRenderDrawBlendMode.restype = ctypes.c_int
LoadDLL.DLL.SDL_SetRenderDrawBlendMode.argtypes = [ctypes.POINTER(SDL_Renderer), ctypes.c_int]

def SDL_SetRenderDrawBlendMode(renderer, blendMode):
	"""
	Args:
		renderer: ctypes.POINTER(SDL_Renderer).
		blendMode: ctypes.c_int.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_SetRenderDrawBlendMode(renderer, blendMode)


LoadDLL.DLL.SDL_RenderClear.restype = ctypes.c_int
LoadDLL.DLL.SDL_RenderClear.argtypes = [ctypes.POINTER(SDL_Renderer)]

def SDL_RenderClear(renderer):
	"""
	Args:
		renderer: ctypes.POINTER(SDL_Renderer).
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_RenderClear(renderer)


LoadDLL.DLL.SDL_RenderDrawPoint.restype = ctypes.c_int
LoadDLL.DLL.SDL_RenderDrawPoint.argtypes = [ctypes.POINTER(SDL_Renderer), ctypes.c_int, ctypes.c_int]

def SDL_RenderDrawPoint(renderer, x, y):
	"""
	Args:
		renderer: ctypes.POINTER(SDL_Renderer).
		x: ctypes.c_int.
		y: ctypes.c_int.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_RenderDrawPoint(renderer, x, y)


LoadDLL.DLL.SDL_RenderDrawLine.restype = ctypes.c_int
LoadDLL.DLL.SDL_RenderDrawLine.argtypes = [ctypes.POINTER(SDL_Renderer), ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]

def SDL_RenderDrawLine(renderer, x1, y1, x2, y2):
	"""
	Args:
		renderer: ctypes.POINTER(SDL_Renderer).
		x1: ctypes.c_int.
		y1: ctypes.c_int.
		x2: ctypes.c_int.
		y2: ctypes.c_int.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_RenderDrawLine(renderer, x1, y1, x2, y2)


LoadDLL.DLL.SDL_RenderDrawRect.restype = ctypes.c_int
LoadDLL.DLL.SDL_RenderDrawRect.argtypes = [ctypes.POINTER(SDL_Renderer), ctypes.POINTER(SDL_Rect)]

def SDL_RenderDrawRect(renderer, rect):
	"""
	Args:
		renderer: ctypes.POINTER(SDL_Renderer).
		rect: ctypes.POINTER(SDL_Rect).
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_RenderDrawRect(renderer, rect)


LoadDLL.DLL.SDL_RenderFillRect.restype = ctypes.c_int
LoadDLL.DLL.SDL_RenderFillRect.argtypes = [ctypes.POINTER(SDL_Renderer), ctypes.POINTER(SDL_Rect)]

def SDL_RenderFillRect(renderer, rect):
	"""
	Args:
		renderer: ctypes.POINTER(SDL_Renderer).
		rect: ctypes.POINTER(SDL_Rect).
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_RenderFillRect(renderer, rect)


LoadDLL.DLL.SDL_RenderCopy.restype = ctypes.c_int
LoadDLL.DLL.SDL_RenderCopy.argtypes = [ctypes.POINTER(SDL_Renderer), ctypes.POINTER(SDL_Texture), ctypes.POINTER(SDL_Rect), ctypes.POINTER(SDL_Rect)]

def SDL_RenderCopy(renderer, texture, srcrect, dstrect):
	"""
	Args:
		renderer: ctypes.POINTER(SDL_Renderer).
		texture: ctypes.POINTER(SDL_Texture).
		srcrect: ctypes.POINTER(SDL_Rect).
		dstrect: ctypes.POINTER(SDL_Rect).
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_RenderCopy(renderer, texture, srcrect, dstrect)


LoadDLL.DLL.SDL_RenderDrawPointF.restype = ctypes.c_int
LoadDLL.DLL.SDL_RenderDrawPointF.argtypes = [ctypes.POINTER(SDL_Renderer), ctypes.c_float, ctypes.c_float]

def SDL_RenderDrawPointF(renderer, x, y):
	"""
	Args:
		renderer: ctypes.POINTER(SDL_Renderer).
		x: ctypes.c_float.
		y: ctypes.c_float.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_RenderDrawPointF(renderer, x, y)


LoadDLL.DLL.SDL_RenderDrawLineF.restype = ctypes.c_int
LoadDLL.DLL.SDL_RenderDrawLineF.argtypes = [ctypes.POINTER(SDL_Renderer), ctypes.c_float, ctypes.c_float, ctypes.c_float, ctypes.c_float]

def SDL_RenderDrawLineF(renderer, x1, y1, x2, y2):
	"""
	Args:
		renderer: ctypes.POINTER(SDL_Renderer).
		x1: ctypes.c_float.
		y1: ctypes.c_float.
		x2: ctypes.c_float.
		y2: ctypes.c_float.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_RenderDrawLineF(renderer, x1, y1, x2, y2)


LoadDLL.DLL.SDL_RenderDrawRectF.restype = ctypes.c_int
LoadDLL.DLL.SDL_RenderDrawRectF.argtypes = [ctypes.POINTER(SDL_Renderer), ctypes.POINTER(SDL_FRect)]

def SDL_RenderDrawRectF(renderer, rect):
	"""
	Args:
		renderer: ctypes.POINTER(SDL_Renderer).
		rect: ctypes.POINTER(SDL_FRect).
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_RenderDrawRectF(renderer, rect)


LoadDLL.DLL.SDL_RenderFillRectF.restype = ctypes.c_int
LoadDLL.DLL.SDL_RenderFillRectF.argtypes = [ctypes.POINTER(SDL_Renderer), ctypes.POINTER(SDL_FRect)]

def SDL_RenderFillRectF(renderer, rect):
	"""
	Args:
		renderer: ctypes.POINTER(SDL_Renderer).
		rect: ctypes.POINTER(SDL_FRect).
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_RenderFillRectF(renderer, rect)


LoadDLL.DLL.SDL_RenderCopyF.restype = ctypes.c_int
LoadDLL.DLL.SDL_RenderCopyF.argtypes = [ctypes.POINTER(SDL_Renderer), ctypes.POINTER(SDL_Texture), ctypes.POINTER(SDL_Rect), ctypes.POINTER(SDL_FRect)]

def SDL_RenderCopyF(renderer, texture, srcrect, dstrect):
	"""
	Args:
		renderer: ctypes.POINTER(SDL_Renderer).
		texture: ctypes.POINTER(SDL_Texture).
		srcrect: ctypes.POINTER(SDL_Rect).
		dstrect: ctypes.POINTER(SDL_FRect).
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_RenderCopyF(renderer, texture, srcrect, dstrect)


LoadDLL.DLL.SDL_RenderGeometry.restype = ctypes.c_int
LoadDLL.DLL.SDL_RenderGeometry.argtypes = [ctypes.POINTER(SDL_Renderer), ctypes.POINTER(SDL_Texture), ctypes.POINTER(SDL_Vertex), ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.c_int]

def SDL_RenderGeometry(renderer, texture, vertices, num_vertices, indices, num_indices):
	"""
	Args:
		renderer: ctypes.POINTER(SDL_Renderer).
		texture: ctypes.POINTER(SDL_Texture).
		vertices: ctypes.POINTER(SDL_Vertex).
		num_vertices: ctypes.c_int.
		indices: ctypes.POINTER(ctypes.c_int).
		num_indices: ctypes.c_int.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_RenderGeometry(renderer, texture, vertices, num_vertices, indices, num_indices)


LoadDLL.DLL.SDL_RenderReadPixels.restype = ctypes.c_int
LoadDLL.DLL.SDL_RenderReadPixels.argtypes = [ctypes.POINTER(SDL_Renderer), ctypes.POINTER(SDL_Rect), ctypes.c_uint, ctypes.c_void_p, ctypes.c_int]

def SDL_RenderReadPixels(renderer, rect, format, pixels, pitch):
	"""
	Args:
		renderer: ctypes.POINTER(SDL_Renderer).
		rect: ctypes.POINTER(SDL_Rect).
		format: ctypes.c_uint.
		pixels: ctypes.c_void_p.
		pitch: ctypes.c_int.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_RenderReadPixels(renderer, rect, format, pixels, pitch)


LoadDLL.DLL.SDL_DestroyTexture.restype = None
LoadDLL.DLL.SDL_DestroyTexture.argtypes = [ctypes.POINTER(SDL_Texture)]

def SDL_DestroyTexture(texture):
	"""
	Args:
		texture: ctypes.POINTER(SDL_Texture).
	Returns:
		res: None.
	"""
	LoadDLL.DLL.SDL_DestroyTexture(texture)


LoadDLL.DLL.SDL_DestroyRenderer.restype = None
LoadDLL.DLL.SDL_DestroyRenderer.argtypes = [ctypes.POINTER(SDL_Renderer)]

def SDL_DestroyRenderer(renderer):
	"""
	Args:
		renderer: ctypes.POINTER(SDL_Renderer).
	Returns:
		res: None.
	"""
	LoadDLL.DLL.SDL_DestroyRenderer(renderer)


LoadDLL.DLL.SDL_RenderFlush.restype = ctypes.c_int
LoadDLL.DLL.SDL_RenderFlush.argtypes = [ctypes.POINTER(SDL_Renderer)]

def SDL_RenderFlush(renderer):
	"""
	Args:
		renderer: ctypes.POINTER(SDL_Renderer).
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_RenderFlush(renderer)


LoadDLL.DLL.SDL_GL_BindTexture.restype = ctypes.c_int
LoadDLL.DLL.SDL_GL_BindTexture.argtypes = [ctypes.POINTER(SDL_Texture), ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float)]

def SDL_GL_BindTexture(texture, texw, texh):
	"""
	Args:
		texture: ctypes.POINTER(SDL_Texture).
		texw: ctypes.POINTER(ctypes.c_float).
		texh: ctypes.POINTER(ctypes.c_float).
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_GL_BindTexture(texture, texw, texh)


LoadDLL.DLL.SDL_GL_UnbindTexture.restype = ctypes.c_int
LoadDLL.DLL.SDL_GL_UnbindTexture.argtypes = [ctypes.POINTER(SDL_Texture)]

def SDL_GL_UnbindTexture(texture):
	"""
	Args:
		texture: ctypes.POINTER(SDL_Texture).
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_GL_UnbindTexture(texture)


LoadDLL.DLL.SDL_RenderGetMetalLayer.restype = ctypes.c_void_p
LoadDLL.DLL.SDL_RenderGetMetalLayer.argtypes = [ctypes.POINTER(SDL_Renderer)]

def SDL_RenderGetMetalLayer(renderer):
	"""
	Args:
		renderer: ctypes.POINTER(SDL_Renderer).
	Returns:
		res: ctypes.c_void_p.
	"""
	return LoadDLL.DLL.SDL_RenderGetMetalLayer(renderer)


LoadDLL.DLL.SDL_RenderGetMetalCommandEncoder.restype = ctypes.c_void_p
LoadDLL.DLL.SDL_RenderGetMetalCommandEncoder.argtypes = [ctypes.POINTER(SDL_Renderer)]

def SDL_RenderGetMetalCommandEncoder(renderer):
	"""
	Args:
		renderer: ctypes.POINTER(SDL_Renderer).
	Returns:
		res: ctypes.c_void_p.
	"""
	return LoadDLL.DLL.SDL_RenderGetMetalCommandEncoder(renderer)


LoadDLL.DLL.SDL_RenderSetVSync.restype = ctypes.c_int
LoadDLL.DLL.SDL_RenderSetVSync.argtypes = [ctypes.POINTER(SDL_Renderer), ctypes.c_int]

def SDL_RenderSetVSync(renderer, vsync):
	"""
	Args:
		renderer: ctypes.POINTER(SDL_Renderer).
		vsync: ctypes.c_int.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_RenderSetVSync(renderer, vsync)