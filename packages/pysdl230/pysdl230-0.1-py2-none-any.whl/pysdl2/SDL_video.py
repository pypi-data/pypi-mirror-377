import ctypes
from .LoadDLL import LoadDLL
from .SDL_surface import SDL_Surface
from .SDL_rect import SDL_Rect, SDL_Point


SDL_WINDOWPOS_UNDEFINED_MASK = 0x1FFF0000

SDL_WINDOWPOS_CENTERED_MASK = 0x2FFF0000

SDL_WINDOWPOS_CENTERED = 0x2FFF0000


class SDL_WindowFlags:
	SDL_WINDOW_FULLSCREEN = 0x00000001
	SDL_WINDOW_OPENGL = 0x00000002
	SDL_WINDOW_SHOWN = 0x00000004
	SDL_WINDOW_HIDDEN = 0x00000008
	SDL_WINDOW_BORDERLESS = 0x00000010
	SDL_WINDOW_RESIZABLE = 0x00000020
	SDL_WINDOW_MINIMIZED = 0x00000040
	SDL_WINDOW_MAXIMIZED = 0x00000080
	SDL_WINDOW_MOUSE_GRABBED = 0x00000100
	SDL_WINDOW_INPUT_FOCUS = 0x00000200
	SDL_WINDOW_MOUSE_FOCUS = 0x00000400
	SDL_WINDOW_FULLSCREEN_DESKTOP = 0x1001
	SDL_WINDOW_FOREIGN = 0x00000800
	SDL_WINDOW_ALLOW_HIGHDPI = 0x00002000
	SDL_WINDOW_MOUSE_CAPTURE = 0x00004000
	SDL_WINDOW_ALWAYS_ON_TOP = 0x00008000
	SDL_WINDOW_SKIP_TASKBAR = 0x00010000
	SDL_WINDOW_UTILITY = 0x00020000
	SDL_WINDOW_TOOLTIP = 0x00040000
	SDL_WINDOW_POPUP_MENU = 0x00080000
	SDL_WINDOW_KEYBOARD_GRABBED = 0x00100000
	SDL_WINDOW_VULKAN = 0x10000000
	SDL_WINDOW_METAL = 0x20000000
	SDL_WINDOW_INPUT_GRABBED = 0x00000100


class SDL_WindowEventID:
	SDL_WINDOWEVENT_NONE = 0
	SDL_WINDOWEVENT_SHOWN = 1
	SDL_WINDOWEVENT_HIDDEN = 2
	SDL_WINDOWEVENT_EXPOSED = 3
	SDL_WINDOWEVENT_MOVED = 4
	SDL_WINDOWEVENT_RESIZED = 5
	SDL_WINDOWEVENT_SIZE_CHANGED = 6
	SDL_WINDOWEVENT_MINIMIZED = 7
	SDL_WINDOWEVENT_MAXIMIZED = 8
	SDL_WINDOWEVENT_RESTORED = 9
	SDL_WINDOWEVENT_ENTER = 10
	SDL_WINDOWEVENT_LEAVE = 11
	SDL_WINDOWEVENT_FOCUS_GAINED = 12
	SDL_WINDOWEVENT_FOCUS_LOST = 13
	SDL_WINDOWEVENT_CLOSE = 14
	SDL_WINDOWEVENT_TAKE_FOCUS = 15
	SDL_WINDOWEVENT_HIT_TEST = 16
	SDL_WINDOWEVENT_ICCPROF_CHANGED = 17
	SDL_WINDOWEVENT_DISPLAY_CHANGED = 18


class SDL_DisplayEventID:
	SDL_DISPLAYEVENT_NONE = 0
	SDL_DISPLAYEVENT_ORIENTATION = 1
	SDL_DISPLAYEVENT_CONNECTED = 2
	SDL_DISPLAYEVENT_DISCONNECTED = 3
	SDL_DISPLAYEVENT_MOVED = 4


class SDL_DisplayOrientation:
	SDL_ORIENTATION_UNKNOWN = 0
	SDL_ORIENTATION_LANDSCAPE = 1
	SDL_ORIENTATION_LANDSCAPE_FLIPPED = 2
	SDL_ORIENTATION_PORTRAIT = 3
	SDL_ORIENTATION_PORTRAIT_FLIPPED = 4


class SDL_FlashOperation:
	SDL_FLASH_CANCEL = 0
	SDL_FLASH_BRIEFLY = 1
	SDL_FLASH_UNTIL_FOCUSED = 2


class SDL_Window(ctypes.Structure): pass


class SDL_DisplayMode(ctypes.Structure):
    _fields_ = [
        ('format', ctypes.c_uint32),
        ('w', ctypes.c_int),
        ('h', ctypes.c_int),
        ('refresh_rate', ctypes.c_int),
        ('driverdata', ctypes.c_void_p),
    ]


LoadDLL.DLL.SDL_GetNumVideoDrivers.restype = ctypes.c_int
LoadDLL.DLL.SDL_GetNumVideoDrivers.argtypes = []

def SDL_GetNumVideoDrivers():
	"""
	Args:
		: None.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_GetNumVideoDrivers()


LoadDLL.DLL.SDL_GetDesktopDisplayMode.restype = ctypes.c_int
LoadDLL.DLL.SDL_GetDesktopDisplayMode.argtypes = [ctypes.c_int, ctypes.POINTER(SDL_DisplayMode)]

def SDL_GetDesktopDisplayMode(displayIndex, mode):
    """
	Args:
		displayIndex: ctypes.c_int.
        mode: ctypes.POINTER(SDL_DisplayMode)
	Returns:
		res: ctypes.c_int.
	"""
    return LoadDLL.DLL.SDL_GetDesktopDisplayMode(displayIndex, mode)


LoadDLL.DLL.SDL_GetVideoDriver.restype = ctypes.c_char_p
LoadDLL.DLL.SDL_GetVideoDriver.argtypes = [ctypes.c_int]

def SDL_GetVideoDriver(index):
	"""
	Args:
		index: ctypes.c_int.
	Returns:
		res: ctypes.c_char_p.
	"""
	return LoadDLL.DLL.SDL_GetVideoDriver(index)


LoadDLL.DLL.SDL_VideoInit.restype = ctypes.c_int
LoadDLL.DLL.SDL_VideoInit.argtypes = [ctypes.c_char_p]

def SDL_VideoInit(driver_name):
	"""
	Args:
		driver_name: ctypes.c_char_p.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_VideoInit(driver_name)


LoadDLL.DLL.SDL_VideoQuit.restype = None
LoadDLL.DLL.SDL_VideoQuit.argtypes = []

def SDL_VideoQuit():
	"""
	Args:
		: None.
	Returns:
		res: None.
	"""
	LoadDLL.DLL.SDL_VideoQuit()


LoadDLL.DLL.SDL_GetCurrentVideoDriver.restype = ctypes.c_char_p
LoadDLL.DLL.SDL_GetCurrentVideoDriver.argtypes = []

def SDL_GetCurrentVideoDriver():
	"""
	Args:
		: None.
	Returns:
		res: ctypes.c_char_p.
	"""
	return LoadDLL.DLL.SDL_GetCurrentVideoDriver()


LoadDLL.DLL.SDL_GetNumVideoDisplays.restype = ctypes.c_int
LoadDLL.DLL.SDL_GetNumVideoDisplays.argtypes = []

def SDL_GetNumVideoDisplays():
	"""
	Args:
		: None.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_GetNumVideoDisplays()


LoadDLL.DLL.SDL_GetDisplayName.restype = ctypes.c_char_p
LoadDLL.DLL.SDL_GetDisplayName.argtypes = [ctypes.c_int]

def SDL_GetDisplayName(displayIndex):
	"""
	Args:
		displayIndex: ctypes.c_int.
	Returns:
		res: ctypes.c_char_p.
	"""
	return LoadDLL.DLL.SDL_GetDisplayName(displayIndex)


LoadDLL.DLL.SDL_GetDisplayBounds.restype = ctypes.c_int
LoadDLL.DLL.SDL_GetDisplayBounds.argtypes = [ctypes.c_int, ctypes.POINTER(SDL_Rect)]

def SDL_GetDisplayBounds(displayIndex, rect):
	"""
	Args:
		displayIndex: ctypes.c_int.
		rect: ctypes.POINTER(SDL_Rect).
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_GetDisplayBounds(displayIndex, rect)


LoadDLL.DLL.SDL_GetDisplayUsableBounds.restype = ctypes.c_int
LoadDLL.DLL.SDL_GetDisplayUsableBounds.argtypes = [ctypes.c_int, ctypes.POINTER(SDL_Rect)]

def SDL_GetDisplayUsableBounds(displayIndex, rect):
	"""
	Args:
		displayIndex: ctypes.c_int.
		rect: ctypes.POINTER(SDL_Rect).
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_GetDisplayUsableBounds(displayIndex, rect)


LoadDLL.DLL.SDL_GetDisplayDPI.restype = ctypes.c_int
LoadDLL.DLL.SDL_GetDisplayDPI.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float)]

def SDL_GetDisplayDPI(displayIndex, ddpi, hdpi, vdpi):
	"""
	Args:
		displayIndex: ctypes.c_int.
		ddpi: ctypes.POINTER(ctypes.c_float).
		hdpi: ctypes.POINTER(ctypes.c_float).
		vdpi: ctypes.POINTER(ctypes.c_float).
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_GetDisplayDPI(displayIndex, ddpi, hdpi, vdpi)


LoadDLL.DLL.SDL_GetDisplayOrientation.restype = ctypes.c_int
LoadDLL.DLL.SDL_GetDisplayOrientation.argtypes = [ctypes.c_int]

def SDL_GetDisplayOrientation(displayIndex):
	"""
	Args:
		displayIndex: ctypes.c_int.
	Returns:
		res: SDL_DisplayOrientation.
	"""
	return LoadDLL.DLL.SDL_GetDisplayOrientation(displayIndex)


LoadDLL.DLL.SDL_GetNumDisplayModes.restype = ctypes.c_int
LoadDLL.DLL.SDL_GetNumDisplayModes.argtypes = [ctypes.c_int]

def SDL_GetNumDisplayModes(displayIndex):
	"""
	Args:
		displayIndex: ctypes.c_int.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_GetNumDisplayModes(displayIndex)


LoadDLL.DLL.SDL_GetDisplayMode.restype = ctypes.c_int
LoadDLL.DLL.SDL_GetDisplayMode.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.POINTER(SDL_DisplayMode)]

def SDL_GetDisplayMode(displayIndex, modeIndex, mode):
	"""
	Args:
		displayIndex: ctypes.c_int.
		modeIndex: ctypes.c_int.
		mode: ctypes.POINTER(SDL_DisplayMode).
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_GetDisplayMode(displayIndex, modeIndex, mode)


LoadDLL.DLL.SDL_GetCurrentDisplayMode.restype = ctypes.c_int
LoadDLL.DLL.SDL_GetCurrentDisplayMode.argtypes = [ctypes.c_int, ctypes.POINTER(SDL_DisplayMode)]

def SDL_GetCurrentDisplayMode(displayIndex, mode):
	"""
	Args:
		displayIndex: ctypes.c_int.
		mode: ctypes.POINTER(SDL_DisplayMode).
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_GetCurrentDisplayMode(displayIndex, mode)


LoadDLL.DLL.SDL_GetClosestDisplayMode.restype = ctypes.POINTER(SDL_DisplayMode)
LoadDLL.DLL.SDL_GetClosestDisplayMode.argtypes = [ctypes.c_int, ctypes.POINTER(SDL_DisplayMode), ctypes.POINTER(SDL_DisplayMode)]

def SDL_GetClosestDisplayMode(displayIndex, mode, closest):
	"""
	Args:
		displayIndex: ctypes.c_int.
		mode: ctypes.POINTER(SDL_DisplayMode).
		closest: ctypes.POINTER(SDL_DisplayMode).
	Returns:
		res: ctypes.POINTER(SDL_DisplayMode).
	"""
	return LoadDLL.DLL.SDL_GetClosestDisplayMode(displayIndex, mode, closest)


LoadDLL.DLL.SDL_GetPointDisplayIndex.restype = ctypes.c_int
LoadDLL.DLL.SDL_GetPointDisplayIndex.argtypes = [ctypes.POINTER(SDL_Point)]

def SDL_GetPointDisplayIndex(point):
	"""
	Args:
		point: ctypes.POINTER(SDL_Point).
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_GetPointDisplayIndex(point)


LoadDLL.DLL.SDL_GetRectDisplayIndex.restype = ctypes.c_int
LoadDLL.DLL.SDL_GetRectDisplayIndex.argtypes = [ctypes.POINTER(SDL_Rect)]

def SDL_GetRectDisplayIndex(rect):
	"""
	Args:
		rect: ctypes.POINTER(SDL_Rect).
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_GetRectDisplayIndex(rect)


LoadDLL.DLL.SDL_GetWindowDisplayIndex.restype = ctypes.c_int
LoadDLL.DLL.SDL_GetWindowDisplayIndex.argtypes = [ctypes.POINTER(SDL_Window)]

def SDL_GetWindowDisplayIndex(window):
	"""
	Args:
		window: ctypes.POINTER(SDL_Window).
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_GetWindowDisplayIndex(window)


LoadDLL.DLL.SDL_SetWindowDisplayMode.restype = ctypes.c_int
LoadDLL.DLL.SDL_SetWindowDisplayMode.argtypes = [ctypes.POINTER(SDL_Window), ctypes.POINTER(SDL_DisplayMode)]

def SDL_SetWindowDisplayMode(window, mode):
	"""
	Args:
		window: ctypes.POINTER(SDL_Window).
		mode: ctypes.POINTER(SDL_DisplayMode).
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_SetWindowDisplayMode(window, mode)


LoadDLL.DLL.SDL_GetWindowICCProfile.restype = ctypes.c_void_p
LoadDLL.DLL.SDL_GetWindowICCProfile.argtypes = [ctypes.POINTER(SDL_Window), ctypes.POINTER(ctypes.c_ulonglong)]

def SDL_GetWindowICCProfile(window, size):
	"""
	Args:
		window: ctypes.POINTER(SDL_Window).
		size: ctypes.POINTER(ctypes.c_ulonglong).
	Returns:
		res: ctypes.c_void_p.
	"""
	return LoadDLL.DLL.SDL_GetWindowICCProfile(window, size)


LoadDLL.DLL.SDL_GetWindowPixelFormat.restype = ctypes.c_uint
LoadDLL.DLL.SDL_GetWindowPixelFormat.argtypes = [ctypes.POINTER(SDL_Window)]

def SDL_GetWindowPixelFormat(window):
	"""
	Args:
		window: ctypes.POINTER(SDL_Window).
	Returns:
		res: ctypes.c_uint.
	"""
	return LoadDLL.DLL.SDL_GetWindowPixelFormat(window)


LoadDLL.DLL.SDL_CreateWindow.restype = ctypes.POINTER(SDL_Window)
LoadDLL.DLL.SDL_CreateWindow.argtypes = [ctypes.c_char_p, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_uint]

def SDL_CreateWindow(title, x, y, w, h, flags):
	"""
	Args:
		title: ctypes.c_char_p.
		x: ctypes.c_int.
		y: ctypes.c_int.
		w: ctypes.c_int.
		h: ctypes.c_int.
		flags: ctypes.c_uint.
	Returns:
		res: ctypes.POINTER(SDL_Window).
	"""
	return LoadDLL.DLL.SDL_CreateWindow(title, x, y, w, h, flags)


LoadDLL.DLL.SDL_GetWindowID.restype = ctypes.c_uint
LoadDLL.DLL.SDL_GetWindowID.argtypes = [ctypes.POINTER(SDL_Window)]

def SDL_GetWindowID(window):
	"""
	Args:
		window: ctypes.POINTER(SDL_Window).
	Returns:
		res: ctypes.c_uint.
	"""
	return LoadDLL.DLL.SDL_GetWindowID(window)


LoadDLL.DLL.SDL_GetWindowFromID.restype = ctypes.POINTER(SDL_Window)
LoadDLL.DLL.SDL_GetWindowFromID.argtypes = [ctypes.c_uint]

def SDL_GetWindowFromID(id):
	"""
	Args:
		id: ctypes.c_uint.
	Returns:
		res: ctypes.POINTER(SDL_Window).
	"""
	return LoadDLL.DLL.SDL_GetWindowFromID(id)


LoadDLL.DLL.SDL_GetWindowFlags.restype = ctypes.c_uint
LoadDLL.DLL.SDL_GetWindowFlags.argtypes = [ctypes.POINTER(SDL_Window)]

def SDL_GetWindowFlags(window):
	"""
	Args:
		window: ctypes.POINTER(SDL_Window).
	Returns:
		res: ctypes.c_uint.
	"""
	return LoadDLL.DLL.SDL_GetWindowFlags(window)


LoadDLL.DLL.SDL_SetWindowTitle.restype = None
LoadDLL.DLL.SDL_SetWindowTitle.argtypes = [ctypes.POINTER(SDL_Window), ctypes.c_char_p]

def SDL_SetWindowTitle(window, title):
	"""
	Args:
		window: ctypes.POINTER(SDL_Window).
		title: ctypes.c_char_p.
	Returns:
		res: None.
	"""
	LoadDLL.DLL.SDL_SetWindowTitle(window, title)


LoadDLL.DLL.SDL_SetWindowIcon.restype = None
LoadDLL.DLL.SDL_SetWindowIcon.argtypes = [ctypes.POINTER(SDL_Window), ctypes.POINTER(SDL_Surface)]

def SDL_SetWindowIcon(window, icon):
	"""
	Args:
		window: ctypes.POINTER(SDL_Window).
		icon: ctypes.POINTER(SDL_Surface).
	Returns:
		res: None.
	"""
	LoadDLL.DLL.SDL_SetWindowIcon(window, icon)


LoadDLL.DLL.SDL_GetWindowData.restype = ctypes.c_void_p
LoadDLL.DLL.SDL_GetWindowData.argtypes = [ctypes.POINTER(SDL_Window), ctypes.c_char_p]

def SDL_GetWindowData(window, name):
	"""
	Args:
		window: ctypes.POINTER(SDL_Window).
		name: ctypes.c_char_p.
	Returns:
		res: ctypes.c_void_p.
	"""
	return LoadDLL.DLL.SDL_GetWindowData(window, name)


LoadDLL.DLL.SDL_GetWindowPosition.restype = None
LoadDLL.DLL.SDL_GetWindowPosition.argtypes = [ctypes.POINTER(SDL_Window), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]

def SDL_GetWindowPosition(window, x, y):
	"""
	Args:
		window: ctypes.POINTER(SDL_Window).
		x: ctypes.POINTER(ctypes.c_int).
		y: ctypes.POINTER(ctypes.c_int).
	Returns:
		res: None.
	"""
	LoadDLL.DLL.SDL_GetWindowPosition(window, x, y)


LoadDLL.DLL.SDL_GetWindowSize.restype = None
LoadDLL.DLL.SDL_GetWindowSize.argtypes = [ctypes.POINTER(SDL_Window), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]

def SDL_GetWindowSize(window, w, h):
	"""
	Args:
		window: ctypes.POINTER(SDL_Window).
		w: ctypes.POINTER(ctypes.c_int).
		h: ctypes.POINTER(ctypes.c_int).
	Returns:
		res: None.
	"""
	LoadDLL.DLL.SDL_GetWindowSize(window, w, h)


LoadDLL.DLL.SDL_GetWindowSizeInPixels.restype = None
LoadDLL.DLL.SDL_GetWindowSizeInPixels.argtypes = [ctypes.POINTER(SDL_Window), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]

def SDL_GetWindowSizeInPixels(window, w, h):
	"""
	Args:
		window: ctypes.POINTER(SDL_Window).
		w: ctypes.POINTER(ctypes.c_int).
		h: ctypes.POINTER(ctypes.c_int).
	Returns:
		res: None.
	"""
	LoadDLL.DLL.SDL_GetWindowSizeInPixels(window, w, h)


LoadDLL.DLL.SDL_GetWindowMinimumSize.restype = None
LoadDLL.DLL.SDL_GetWindowMinimumSize.argtypes = [ctypes.POINTER(SDL_Window), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]

def SDL_GetWindowMinimumSize(window, w, h):
	"""
	Args:
		window: ctypes.POINTER(SDL_Window).
		w: ctypes.POINTER(ctypes.c_int).
		h: ctypes.POINTER(ctypes.c_int).
	Returns:
		res: None.
	"""
	LoadDLL.DLL.SDL_GetWindowMinimumSize(window, w, h)


LoadDLL.DLL.SDL_GetWindowMaximumSize.restype = None
LoadDLL.DLL.SDL_GetWindowMaximumSize.argtypes = [ctypes.POINTER(SDL_Window), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]

def SDL_GetWindowMaximumSize(window, w, h):
	"""
	Args:
		window: ctypes.POINTER(SDL_Window).
		w: ctypes.POINTER(ctypes.c_int).
		h: ctypes.POINTER(ctypes.c_int).
	Returns:
		res: None.
	"""
	LoadDLL.DLL.SDL_GetWindowMaximumSize(window, w, h)


LoadDLL.DLL.SDL_SetWindowResizable.restype = None
LoadDLL.DLL.SDL_SetWindowResizable.argtypes = [ctypes.POINTER(SDL_Window), ctypes.c_int]

def SDL_SetWindowResizable(window, resizable):
	"""
	Args:
		window: ctypes.POINTER(SDL_Window).
		resizable: ctypes.c_int.
	Returns:
		res: None.
	"""
	LoadDLL.DLL.SDL_SetWindowResizable(window, resizable)


LoadDLL.DLL.SDL_ShowWindow.restype = None
LoadDLL.DLL.SDL_ShowWindow.argtypes = [ctypes.POINTER(SDL_Window)]

def SDL_ShowWindow(window):
	"""
	Args:
		window: ctypes.POINTER(SDL_Window).
	Returns:
		res: None.
	"""
	LoadDLL.DLL.SDL_ShowWindow(window)


LoadDLL.DLL.SDL_HideWindow.restype = None
LoadDLL.DLL.SDL_HideWindow.argtypes = [ctypes.POINTER(SDL_Window)]

def SDL_HideWindow(window):
	"""
	Args:
		window: ctypes.POINTER(SDL_Window).
	Returns:
		res: None.
	"""
	LoadDLL.DLL.SDL_HideWindow(window)


LoadDLL.DLL.SDL_RaiseWindow.restype = None
LoadDLL.DLL.SDL_RaiseWindow.argtypes = [ctypes.POINTER(SDL_Window)]

def SDL_RaiseWindow(window):
	"""
	Args:
		window: ctypes.POINTER(SDL_Window).
	Returns:
		res: None.
	"""
	LoadDLL.DLL.SDL_RaiseWindow(window)


LoadDLL.DLL.SDL_MaximizeWindow.restype = None
LoadDLL.DLL.SDL_MaximizeWindow.argtypes = [ctypes.POINTER(SDL_Window)]

def SDL_MaximizeWindow(window):
	"""
	Args:
		window: ctypes.POINTER(SDL_Window).
	Returns:
		res: None.
	"""
	LoadDLL.DLL.SDL_MaximizeWindow(window)


LoadDLL.DLL.SDL_MinimizeWindow.restype = None
LoadDLL.DLL.SDL_MinimizeWindow.argtypes = [ctypes.POINTER(SDL_Window)]

def SDL_MinimizeWindow(window):
	"""
	Args:
		window: ctypes.POINTER(SDL_Window).
	Returns:
		res: None.
	"""
	LoadDLL.DLL.SDL_MinimizeWindow(window)


LoadDLL.DLL.SDL_RestoreWindow.restype = None
LoadDLL.DLL.SDL_RestoreWindow.argtypes = [ctypes.POINTER(SDL_Window)]

def SDL_RestoreWindow(window):
	"""
	Args:
		window: ctypes.POINTER(SDL_Window).
	Returns:
		res: None.
	"""
	LoadDLL.DLL.SDL_RestoreWindow(window)


LoadDLL.DLL.SDL_SetWindowFullscreen.restype = ctypes.c_int
LoadDLL.DLL.SDL_SetWindowFullscreen.argtypes = [ctypes.POINTER(SDL_Window), ctypes.c_uint]

def SDL_SetWindowFullscreen(window, flags):
	"""
	Args:
		window: ctypes.POINTER(SDL_Window).
		flags: ctypes.c_uint.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_SetWindowFullscreen(window, flags)


LoadDLL.DLL.SDL_GetWindowSurface.restype = ctypes.POINTER(SDL_Surface)
LoadDLL.DLL.SDL_GetWindowSurface.argtypes = [ctypes.POINTER(SDL_Window)]

def SDL_GetWindowSurface(window):
	"""
	Args:
		window: ctypes.POINTER(SDL_Window).
	Returns:
		res: ctypes.POINTER(SDL_Surface).
	"""
	return LoadDLL.DLL.SDL_GetWindowSurface(window)


LoadDLL.DLL.SDL_UpdateWindowSurface.restype = ctypes.c_int
LoadDLL.DLL.SDL_UpdateWindowSurface.argtypes = [ctypes.POINTER(SDL_Window)]

def SDL_UpdateWindowSurface(window):
	"""
	Args:
		window: ctypes.POINTER(SDL_Window).
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_UpdateWindowSurface(window)


LoadDLL.DLL.SDL_UpdateWindowSurfaceRects.restype = ctypes.c_int
LoadDLL.DLL.SDL_UpdateWindowSurfaceRects.argtypes = [ctypes.POINTER(SDL_Window), ctypes.POINTER(SDL_Rect), ctypes.c_int]

def SDL_UpdateWindowSurfaceRects(window, rects, numrects):
	"""
	Args:
		window: ctypes.POINTER(SDL_Window).
		rects: ctypes.POINTER(SDL_Rect).
		numrects: ctypes.c_int.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_UpdateWindowSurfaceRects(window, rects, numrects)


LoadDLL.DLL.SDL_SetWindowGrab.restype = None
LoadDLL.DLL.SDL_SetWindowGrab.argtypes = [ctypes.POINTER(SDL_Window), ctypes.c_int]

def SDL_SetWindowGrab(window, grabbed):
	"""
	Args:
		window: ctypes.POINTER(SDL_Window).
		grabbed: ctypes.c_int.
	Returns:
		res: None.
	"""
	LoadDLL.DLL.SDL_SetWindowGrab(window, grabbed)


LoadDLL.DLL.SDL_SetWindowMouseGrab.restype = None
LoadDLL.DLL.SDL_SetWindowMouseGrab.argtypes = [ctypes.POINTER(SDL_Window), ctypes.c_int]

def SDL_SetWindowMouseGrab(window, grabbed):
	"""
	Args:
		window: ctypes.POINTER(SDL_Window).
		grabbed: ctypes.c_int.
	Returns:
		res: None.
	"""
	LoadDLL.DLL.SDL_SetWindowMouseGrab(window, grabbed)


LoadDLL.DLL.SDL_GetWindowKeyboardGrab.restype = ctypes.c_int
LoadDLL.DLL.SDL_GetWindowKeyboardGrab.argtypes = [ctypes.POINTER(SDL_Window)]

def SDL_GetWindowKeyboardGrab(window):
	"""
	Args:
		window: ctypes.POINTER(SDL_Window).
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_GetWindowKeyboardGrab(window)


LoadDLL.DLL.SDL_GetWindowMouseGrab.restype = ctypes.c_int
LoadDLL.DLL.SDL_GetWindowMouseGrab.argtypes = [ctypes.POINTER(SDL_Window)]

def SDL_GetWindowMouseGrab(window):
	"""
	Args:
		window: ctypes.POINTER(SDL_Window).
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_GetWindowMouseGrab(window)


LoadDLL.DLL.SDL_GetGrabbedWindow.restype = ctypes.POINTER(SDL_Window)
LoadDLL.DLL.SDL_GetGrabbedWindow.argtypes = []

def SDL_GetGrabbedWindow():
	"""
	Args:
		: None.
	Returns:
		res: ctypes.POINTER(SDL_Window).
	"""
	return LoadDLL.DLL.SDL_GetGrabbedWindow()


LoadDLL.DLL.SDL_SetWindowMouseRect.restype = ctypes.c_int
LoadDLL.DLL.SDL_SetWindowMouseRect.argtypes = [ctypes.POINTER(SDL_Window), ctypes.POINTER(SDL_Rect)]

def SDL_SetWindowMouseRect(window, rect):
	"""
	Args:
		window: ctypes.POINTER(SDL_Window).
		rect: ctypes.POINTER(SDL_Rect).
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_SetWindowMouseRect(window, rect)


LoadDLL.DLL.SDL_GetWindowMouseRect.restype = ctypes.POINTER(SDL_Rect)
LoadDLL.DLL.SDL_GetWindowMouseRect.argtypes = [ctypes.POINTER(SDL_Window)]

def SDL_GetWindowMouseRect(window):
	"""
	Args:
		window: ctypes.POINTER(SDL_Window).
	Returns:
		res: ctypes.POINTER(SDL_Rect).
	"""
	return LoadDLL.DLL.SDL_GetWindowMouseRect(window)


LoadDLL.DLL.SDL_SetWindowBrightness.restype = ctypes.c_int
LoadDLL.DLL.SDL_SetWindowBrightness.argtypes = [ctypes.POINTER(SDL_Window), ctypes.c_float]

def SDL_SetWindowBrightness(window, brightness):
	"""
	Args:
		window: ctypes.POINTER(SDL_Window).
		brightness: ctypes.c_float.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_SetWindowBrightness(window, brightness)


LoadDLL.DLL.SDL_GetWindowBrightness.restype = ctypes.c_float
LoadDLL.DLL.SDL_GetWindowBrightness.argtypes = [ctypes.POINTER(SDL_Window)]

def SDL_GetWindowBrightness(window):
	"""
	Args:
		window: ctypes.POINTER(SDL_Window).
	Returns:
		res: ctypes.c_float.
	"""
	return LoadDLL.DLL.SDL_GetWindowBrightness(window)


LoadDLL.DLL.SDL_SetWindowOpacity.restype = ctypes.c_int
LoadDLL.DLL.SDL_SetWindowOpacity.argtypes = [ctypes.POINTER(SDL_Window), ctypes.c_float]

def SDL_SetWindowOpacity(window, opacity):
	"""
	Args:
		window: ctypes.POINTER(SDL_Window).
		opacity: ctypes.c_float.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_SetWindowOpacity(window, opacity)


LoadDLL.DLL.SDL_GetWindowOpacity.restype = ctypes.c_int
LoadDLL.DLL.SDL_GetWindowOpacity.argtypes = [ctypes.POINTER(SDL_Window), ctypes.POINTER(ctypes.c_float)]

def SDL_GetWindowOpacity(window, out_opacity):
	"""
	Args:
		window: ctypes.POINTER(SDL_Window).
		out_opacity: ctypes.POINTER(ctypes.c_float).
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_GetWindowOpacity(window, out_opacity)


LoadDLL.DLL.SDL_SetWindowModalFor.restype = ctypes.c_int
LoadDLL.DLL.SDL_SetWindowModalFor.argtypes = [ctypes.POINTER(SDL_Window), ctypes.POINTER(SDL_Window)]

def SDL_SetWindowModalFor(modal_window, parent_window):
	"""
	Args:
		modal_window: ctypes.POINTER(SDL_Window).
		parent_window: ctypes.POINTER(SDL_Window).
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_SetWindowModalFor(modal_window, parent_window)


LoadDLL.DLL.SDL_SetWindowInputFocus.restype = ctypes.c_int
LoadDLL.DLL.SDL_SetWindowInputFocus.argtypes = [ctypes.POINTER(SDL_Window)]

def SDL_SetWindowInputFocus(window):
	"""
	Args:
		window: ctypes.POINTER(SDL_Window).
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_SetWindowInputFocus(window)


LoadDLL.DLL.SDL_SetWindowGammaRamp.restype = ctypes.c_int
LoadDLL.DLL.SDL_SetWindowGammaRamp.argtypes = [ctypes.POINTER(SDL_Window), ctypes.POINTER(ctypes.c_ushort), ctypes.POINTER(ctypes.c_ushort), ctypes.POINTER(ctypes.c_ushort)]

def SDL_SetWindowGammaRamp(window, red, green, blue):
	"""
	Args:
		window: ctypes.POINTER(SDL_Window).
		red: ctypes.POINTER(ctypes.c_ushort).
		green: ctypes.POINTER(ctypes.c_ushort).
		blue: ctypes.POINTER(ctypes.c_ushort).
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_SetWindowGammaRamp(window, red, green, blue)


LoadDLL.DLL.SDL_DestroyWindow.restype = None
LoadDLL.DLL.SDL_DestroyWindow.argtypes = [ctypes.POINTER(SDL_Window)]

def SDL_DestroyWindow(window):
	"""
	Args:
		window: ctypes.POINTER(SDL_Window).
	Returns:
		res: None.
	"""
	LoadDLL.DLL.SDL_DestroyWindow(window)


LoadDLL.DLL.SDL_IsScreenSaverEnabled.restype = ctypes.c_int
LoadDLL.DLL.SDL_IsScreenSaverEnabled.argtypes = []

def SDL_IsScreenSaverEnabled():
	"""
	Args:
		: None.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_IsScreenSaverEnabled()


LoadDLL.DLL.SDL_EnableScreenSaver.restype = None
LoadDLL.DLL.SDL_EnableScreenSaver.argtypes = []

def SDL_EnableScreenSaver():
	"""
	Args:
		: None.
	Returns:
		res: None.
	"""
	LoadDLL.DLL.SDL_EnableScreenSaver()


LoadDLL.DLL.SDL_DisableScreenSaver.restype = None
LoadDLL.DLL.SDL_DisableScreenSaver.argtypes = []

def SDL_DisableScreenSaver():
	"""
	Args:
		: None.
	Returns:
		res: None.
	"""
	LoadDLL.DLL.SDL_DisableScreenSaver()