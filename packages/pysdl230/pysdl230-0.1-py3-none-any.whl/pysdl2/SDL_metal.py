import ctypes
from .LoadDLL import LoadDLL
from .SDL_video import SDL_Window


LoadDLL.DLL.SDL_Metal_CreateView.restype = ctypes.c_void_p
LoadDLL.DLL.SDL_Metal_CreateView.argtypes = [ctypes.POINTER(SDL_Window)]

def SDL_Metal_CreateView(window):
	"""
	Args:
		window: ctypes.POINTER(SDL_Window).
	Returns:
		res: ctypes.c_void_p.
	"""
	return LoadDLL.DLL.SDL_Metal_CreateView(window)


LoadDLL.DLL.SDL_Metal_DestroyView.restype = None
LoadDLL.DLL.SDL_Metal_DestroyView.argtypes = [ctypes.c_void_p]

def SDL_Metal_DestroyView(view):
	"""
	Args:
		view: ctypes.c_void_p.
	Returns:
		res: None.
	"""
	LoadDLL.DLL.SDL_Metal_DestroyView(view)


LoadDLL.DLL.SDL_Metal_GetLayer.restype = ctypes.c_void_p
LoadDLL.DLL.SDL_Metal_GetLayer.argtypes = [ctypes.c_void_p]

def SDL_Metal_GetLayer(view):
	"""
	Args:
		view: ctypes.c_void_p.
	Returns:
		res: ctypes.c_void_p.
	"""
	return LoadDLL.DLL.SDL_Metal_GetLayer(view)


LoadDLL.DLL.SDL_Metal_GetDrawableSize.restype = None
LoadDLL.DLL.SDL_Metal_GetDrawableSize.argtypes = [ctypes.POINTER(SDL_Window), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]

def SDL_Metal_GetDrawableSize(window, w, h):
	"""
	Args:
		window: ctypes.POINTER(SDL_Window).
		w: ctypes.POINTER(ctypes.c_int).
		h: ctypes.POINTER(ctypes.c_int).
	Returns:
		res: None.
	"""
	LoadDLL.DLL.SDL_Metal_GetDrawableSize(window, w, h)