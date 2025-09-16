import ctypes
from .LoadDLL import LoadDLL


class SDL_AssertState:
	SDL_ASSERTION_RETRY = 0
	SDL_ASSERTION_BREAK = 1
	SDL_ASSERTION_ABORT = 2
	SDL_ASSERTION_IGNORE = 3
	SDL_ASSERTION_ALWAYS_IGNORE = 4


SDL_DEFAULT_ASSERT_LEVEL = 0

SDL_ASSERT_LEVEL = SDL_DEFAULT_ASSERT_LEVEL

SDL_ASSERT_LEVEL = 2

SDL_ASSERT_LEVEL = 1

SDL_assert_state = SDL_AssertState


class SDL_AssertData(ctypes.Structure):
	_fields_ = [
		('always_ignore', ctypes.c_int),
		('trigger_count', ctypes.c_uint),
		('condition', ctypes.c_char_p),
		('filename', ctypes.c_char_p),
		('linenum', ctypes.c_int),
		('function', ctypes.c_char_p),
		('next', ctypes.c_void_p),
	]


SDL_assert_data = SDL_AssertData


LoadDLL.DLL.SDL_ReportAssertion.restype = ctypes.c_int
LoadDLL.DLL.SDL_ReportAssertion.argtypes = [ctypes.POINTER(SDL_AssertData), ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int]

def SDL_ReportAssertion(a, b, c, d):
	"""
	Args:
		a: ctypes.POINTER(SDL_AssertData).
		b: ctypes.c_char_p.
		c: ctypes.c_char_p.
		d: ctypes.c_int.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_ReportAssertion(a, b, c, d)


LoadDLL.DLL.SDL_GetDefaultAssertionHandler.restype = ctypes.c_int
LoadDLL.DLL.SDL_GetDefaultAssertionHandler.argtypes = []

def SDL_GetDefaultAssertionHandler():
	"""
	Args:
		: None.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_GetDefaultAssertionHandler()


LoadDLL.DLL.SDL_GetAssertionHandler.restype = ctypes.c_int
LoadDLL.DLL.SDL_GetAssertionHandler.argtypes = [ctypes.POINTER(ctypes.c_void_p)]

def SDL_GetAssertionHandler(puserdata):
	"""
	Args:
		puserdata: ctypes.POINTER(ctypes.c_void_p).
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_GetAssertionHandler(puserdata)


LoadDLL.DLL.SDL_GetAssertionReport.restype = ctypes.POINTER(SDL_AssertData)
LoadDLL.DLL.SDL_GetAssertionReport.argtypes = []

def SDL_GetAssertionReport():
	"""
	Args:
		: None.
	Returns:
		res: ctypes.POINTER(SDL_AssertData).
	"""
	return LoadDLL.DLL.SDL_GetAssertionReport()


LoadDLL.DLL.SDL_ResetAssertionReport.restype = None
LoadDLL.DLL.SDL_ResetAssertionReport.argtypes = []

def SDL_ResetAssertionReport():
	"""
	Args:
		: None.
	Returns:
		res: None.
	"""
	LoadDLL.DLL.SDL_ResetAssertionReport()