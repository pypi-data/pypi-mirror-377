import ctypes
from .LoadDLL import LoadDLL


__AIX__ = 1

__HAIKU__ = 1

__BSDI__ = 1

__DREAMCAST__ = 1

__FREEBSD__ = 1

__HPUX__ = 1

__IRIX__ = 1

__LINUX__ = 1

__ANDROID__ = 1

__NGAGE__ = 1

TARGET_OS_MACCATALYST = 0

TARGET_OSS = 0

TARGET_OS_IPHONE = 0

TARGET_OS_TV = 0

TARGET_OS_SIMULATOR = 0

__TVOS__ = 1

__IPHONEOS__ = 1

__MACOSX__ = 1

__NETBSD__ = 1

__OPENBSD__ = 1

__OS2__ = 1

__OSF__ = 1

__QNXNTO__ = 1

__RISCOS__ = 1

__SOLARIS__ = 1

HAVE_WINAPIFAMILY_H = 1

HAVE_WINAPIFAMILY_H = 0

HAVE_WINAPIFAMILY_H = 1

HAVE_WINAPIFAMILY_H = 0

WINAPI_FAMILY_WINRT = 0

SDL_WINAPI_FAMILY_PHONE = 0

__WINRT__ = 1

__WINGDK__ = 1

__XBOXONE__ = 1

__XBOXSERIES__ = 1

__WINDOWS__ = 1

__WIN32__ = 1

__GDK__ = 1

__PSP__ = 1

__PS2__ = 1

__NACL__ = 1

__PNACL__ = 1

__VITA__ = 1

__3DS__ = 1

LoadDLL.DLL.SDL_GetPlatform.restype = ctypes.c_char_p
LoadDLL.DLL.SDL_GetPlatform.argtypes = []

def SDL_GetPlatform():
	"""
	Args:
		: None.
	Returns:
		res: ctypes.c_char_p.
	"""
	return LoadDLL.DLL.SDL_GetPlatform()