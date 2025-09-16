import ctypes
from .LoadDLL import LoadDLL


class SDL_Point(ctypes.Structure):
	_fields_ = [
		('x', ctypes.c_int),
		('y', ctypes.c_int),
	]


class SDL_FPoint(ctypes.Structure):
	_fields_ = [
		('x', ctypes.c_float),
		('y', ctypes.c_float),
	]


class SDL_Rect(ctypes.Structure):
	_fields_ = [
		('x', ctypes.c_int),
		('y', ctypes.c_int),
		('w', ctypes.c_int),
		('h', ctypes.c_int),
	]


class SDL_FRect(ctypes.Structure):
	_fields_ = [
		('x', ctypes.c_float),
		('y', ctypes.c_float),
		('w', ctypes.c_float),
		('h', ctypes.c_float),
	]


def SDL_PointInRect(p, r):
    """
	Args:
		p: ctypes.POINTER(SDL_Point).
		r: ctypes.POINTER(SDL_Rect).
	Returns:
		res: bool.
	"""
    left, right = r.contents.x, r.contents.x + r.contents.w
    top, bottom = r.contents.y, r.contents.y + r.contents.h
    x, y = p.contents.x, p.contents.y
    return (x >= left and x <= right) and (y >= top and y <= bottom)


def SDL_PointInFRect(p, r):
    """
	Args:
		p: ctypes.POINTER(SDL_Point).
		r: ctypes.POINTER(SDL_FRect).
	Returns:
		res: bool.
	"""
    left, right = r.contents.x, r.contents.x + r.contents.w
    top, bottom = r.contents.y, r.contents.y + r.contents.h
    x, y = p.contents.x, p.contents.y
    return (x >= left and x <= right) and (y >= top and y <= bottom)


def SDL_RectEquals(a, b):
    """
	Args:
		a: ctypes.POINTER(SDL_Rect).
		b: ctypes.POINTER(SDL_Rect).
	Returns:
		res: bool.
	"""
    x1, y1 = a.contents.x, a.contents.y
    x2, y2 = b.contents.x, b.contents.y
    if x1 != x2 or y1 != y2:
        return False
    w1, h1 = a.contents.w, a.contents.h
    w2, h2 = b.contents.w, b.contents.h
    return w1 == w2 and h1 == h2


def SDL_FRectEquals(a, b):
    """
	Args:
		a: ctypes.POINTER(SDL_FRect).
		b: ctypes.POINTER(SDL_FRect).
	Returns:
		res: bool.
	"""
    x1, y1 = a.contents.x, a.contents.y
    x2, y2 = b.contents.x, b.contents.y
    if x1 != x2 or y1 != y2:
        return False
    w1, h1 = a.contents.w, a.contents.h
    w2, h2 = b.contents.w, b.contents.h
    return w1 == w2 and h1 == h2

# LoadDLL.DLL.SDL_PointInRect.restype = ctypes.c_int
# LoadDLL.DLL.SDL_PointInRect.argtypes = [ctypes.POINTER(SDL_Point), ctypes.POINTER(SDL_Rect)]

# def SDL_PointInRect(p, r):
	# """
	# Args:
		# p: ctypes.POINTER(SDL_Point).
		# r: ctypes.POINTER(SDL_Rect).
	# Returns:
		# res: ctypes.c_int.
	# """
	# return LoadDLL.DLL.SDL_PointInRect(p, r)


# LoadDLL.DLL.SDL_RectEmpty.restype = ctypes.c_int
# LoadDLL.DLL.SDL_RectEmpty.argtypes = [ctypes.POINTER(SDL_Rect)]

# def SDL_RectEmpty(r):
	# """
	# Args:
		# r: ctypes.POINTER(SDL_Rect).
	# Returns:
		# res: ctypes.c_int.
	# """
	# return LoadDLL.DLL.SDL_RectEmpty(r)


# LoadDLL.DLL.SDL_RectEquals.restype = ctypes.c_int
# LoadDLL.DLL.SDL_RectEquals.argtypes = [ctypes.POINTER(SDL_Rect), ctypes.POINTER(SDL_Rect)]

# def SDL_RectEquals(a, b):
	# """
	# Args:
		# a: ctypes.POINTER(SDL_Rect).
		# b: ctypes.POINTER(SDL_Rect).
	# Returns:
		# res: ctypes.c_int.
	# """
	# return LoadDLL.DLL.SDL_RectEquals(a, b)


LoadDLL.DLL.SDL_HasIntersection.restype = ctypes.c_int
LoadDLL.DLL.SDL_HasIntersection.argtypes = [ctypes.POINTER(SDL_Rect), ctypes.POINTER(SDL_Rect)]

def SDL_HasIntersection(A, B):
	"""
	Args:
		A: ctypes.POINTER(SDL_Rect).
		B: ctypes.POINTER(SDL_Rect).
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_HasIntersection(A, B)


LoadDLL.DLL.SDL_UnionRect.restype = None
LoadDLL.DLL.SDL_UnionRect.argtypes = [ctypes.POINTER(SDL_Rect), ctypes.POINTER(SDL_Rect), ctypes.POINTER(SDL_Rect)]

def SDL_UnionRect(A, B, result):
	"""
	Args:
		A: ctypes.POINTER(SDL_Rect).
		B: ctypes.POINTER(SDL_Rect).
		result: ctypes.POINTER(SDL_Rect).
	Returns:
		res: None.
	"""
	LoadDLL.DLL.SDL_UnionRect(A, B, result)


LoadDLL.DLL.SDL_IntersectRectAndLine.restype = ctypes.c_int
LoadDLL.DLL.SDL_IntersectRectAndLine.argtypes = [ctypes.POINTER(SDL_Rect), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]

def SDL_IntersectRectAndLine(rect, X1, Y1, X2, Y2):
	"""
	Args:
		rect: ctypes.POINTER(SDL_Rect).
		X1: ctypes.POINTER(ctypes.c_int).
		Y1: ctypes.POINTER(ctypes.c_int).
		X2: ctypes.POINTER(ctypes.c_int).
		Y2: ctypes.POINTER(ctypes.c_int).
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_IntersectRectAndLine(rect, X1, Y1, X2, Y2)


# LoadDLL.DLL.SDL_FRectEmpty.restype = ctypes.c_int
# LoadDLL.DLL.SDL_FRectEmpty.argtypes = [ctypes.POINTER(SDL_FRect)]

# def SDL_FRectEmpty(r):
	# """
	# Args:
		# r: ctypes.POINTER(SDL_FRect).
	# Returns:
		# res: ctypes.c_int.
	# """
	# return LoadDLL.DLL.SDL_FRectEmpty(r)


# LoadDLL.DLL.SDL_FRectEquals.restype = ctypes.c_int
# LoadDLL.DLL.SDL_FRectEquals.argtypes = [ctypes.POINTER(SDL_FRect), ctypes.POINTER(SDL_FRect)]

# def SDL_FRectEquals(a, b):
	# """
	# Args:
		# a: ctypes.POINTER(SDL_FRect).
		# b: ctypes.POINTER(SDL_FRect).
	# Returns:
		# res: ctypes.c_int.
	# """
	# return LoadDLL.DLL.SDL_FRectEquals(a, b)


# LoadDLL.DLL.SDL_HasIntersectionF.restype = ctypes.c_int
# LoadDLL.DLL.SDL_HasIntersectionF.argtypes = [ctypes.POINTER(SDL_FRect), ctypes.POINTER(SDL_FRect)]

def SDL_HasIntersectionF(A, B):
	"""
	Args:
		A: ctypes.POINTER(SDL_FRect).
		B: ctypes.POINTER(SDL_FRect).
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_HasIntersectionF(A, B)


LoadDLL.DLL.SDL_UnionFRect.restype = None
LoadDLL.DLL.SDL_UnionFRect.argtypes = [ctypes.POINTER(SDL_FRect), ctypes.POINTER(SDL_FRect), ctypes.POINTER(SDL_FRect)]

def SDL_UnionFRect(A, B, result):
	"""
	Args:
		A: ctypes.POINTER(SDL_FRect).
		B: ctypes.POINTER(SDL_FRect).
		result: ctypes.POINTER(SDL_FRect).
	Returns:
		res: None.
	"""
	LoadDLL.DLL.SDL_UnionFRect(A, B, result)


LoadDLL.DLL.SDL_IntersectFRectAndLine.restype = ctypes.c_int
LoadDLL.DLL.SDL_IntersectFRectAndLine.argtypes = [ctypes.POINTER(SDL_FRect), ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float)]

def SDL_IntersectFRectAndLine(rect, X1, Y1, X2, Y2):
	"""
	Args:
		rect: ctypes.POINTER(SDL_FRect).
		X1: ctypes.POINTER(ctypes.c_float).
		Y1: ctypes.POINTER(ctypes.c_float).
		X2: ctypes.POINTER(ctypes.c_float).
		Y2: ctypes.POINTER(ctypes.c_float).
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_IntersectFRectAndLine(rect, X1, Y1, X2, Y2)