import ctypes
from .LoadDLL import LoadDLL


class SDL_BlendMode:
	SDL_BLENDMODE_NONE = 0x00000000
	SDL_BLENDMODE_BLEND = 0x00000001
	SDL_BLENDMODE_ADD = 0x00000002
	SDL_BLENDMODE_MOD = 0x00000004
	SDL_BLENDMODE_MUL = 0x00000008
	SDL_BLENDMODE_INVALID = 0x7FFFFFFF


class SDL_BlendOperation:
	SDL_BLENDOPERATION_ADD = 0x1
	SDL_BLENDOPERATION_SUBTRACT = 0x2
	SDL_BLENDOPERATION_REV_SUBTRACT = 0x3
	SDL_BLENDOPERATION_MINIMUM = 0x4
	SDL_BLENDOPERATION_MAXIMUM = 0x5


class SDL_BlendFactor:
	SDL_BLENDFACTOR_ZERO = 0x1
	SDL_BLENDFACTOR_ONE = 0x2
	SDL_BLENDFACTOR_SRC_COLOR = 0x3
	SDL_BLENDFACTOR_ONE_MINUS_SRC_COLOR = 0x4
	SDL_BLENDFACTOR_SRC_ALPHA = 0x5
	SDL_BLENDFACTOR_ONE_MINUS_SRC_ALPHA = 0x6
	SDL_BLENDFACTOR_DST_COLOR = 0x7
	SDL_BLENDFACTOR_ONE_MINUS_DST_COLOR = 0x8
	SDL_BLENDFACTOR_DST_ALPHA = 0x9
	SDL_BLENDFACTOR_ONE_MINUS_DST_ALPHA = 0xA


LoadDLL.DLL.SDL_ComposeCustomBlendMode.restype = ctypes.c_int
LoadDLL.DLL.SDL_ComposeCustomBlendMode.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]

def SDL_ComposeCustomBlendMode(srcColorFactor, dstColorFactor, colorOperation, srcAlphaFactor, dstAlphaFactor, alphaOperation):
	"""
	Args:
		srcColorFactor: SDL_BlendFactor.
		dstColorFactor: SDL_BlendFactor.
		colorOperation: SDL_BlendOperation.
		srcAlphaFactor: SDL_BlendFactor.
		dstAlphaFactor: SDL_BlendFactor.
		alphaOperation: SDL_BlendOperation.
	Returns:
		res: SDL_BlendMode.
	"""
	return LoadDLL.DLL.SDL_ComposeCustomBlendMode(srcColorFactor, dstColorFactor, colorOperation, srcAlphaFactor, dstAlphaFactor, alphaOperation)