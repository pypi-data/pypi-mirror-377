import ctypes
from .LoadDLL import LoadDLL


class SDL_hid_device(ctypes.Structure): pass


class SDL_hid_device_info(ctypes.Structure):
	_fields_ = [
		('path', ctypes.c_char_p),
		('vendor_id', ctypes.c_ushort),
		('product_id', ctypes.c_ushort),
		('serial_number', ctypes.c_wchar_p),
		('release_number', ctypes.c_ushort),
		('manufacturer_string', ctypes.c_wchar_p),
		('product_string', ctypes.c_wchar_p),
		('usage_page', ctypes.c_ushort),
		('usage', ctypes.c_ushort),
		('interface_number', ctypes.c_int),
		('interface_class', ctypes.c_int),
		('interface_subclass', ctypes.c_int),
		('interface_protocol', ctypes.c_int),
		('next', ctypes.c_void_p),
	]

LoadDLL.DLL.SDL_hid_init.restype = ctypes.c_int
LoadDLL.DLL.SDL_hid_init.argtypes = []

def SDL_hid_init():
	"""
	Args:
		: None.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_hid_init()


LoadDLL.DLL.SDL_hid_exit.restype = ctypes.c_int
LoadDLL.DLL.SDL_hid_exit.argtypes = []

def SDL_hid_exit():
	"""
	Args:
		: None.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_hid_exit()


LoadDLL.DLL.SDL_hid_device_change_count.restype = ctypes.c_uint
LoadDLL.DLL.SDL_hid_device_change_count.argtypes = []

def SDL_hid_device_change_count():
	"""
	Args:
		: None.
	Returns:
		res: ctypes.c_uint.
	"""
	return LoadDLL.DLL.SDL_hid_device_change_count()


LoadDLL.DLL.SDL_hid_enumerate.restype = ctypes.POINTER(SDL_hid_device_info)
LoadDLL.DLL.SDL_hid_enumerate.argtypes = [ctypes.c_ushort, ctypes.c_ushort]

def SDL_hid_enumerate(vendor_id, product_id):
	"""
	Args:
		vendor_id: ctypes.c_ushort.
		product_id: ctypes.c_ushort.
	Returns:
		res: ctypes.POINTER(SDL_hid_device_info).
	"""
	return LoadDLL.DLL.SDL_hid_enumerate(vendor_id, product_id)


LoadDLL.DLL.SDL_hid_free_enumeration.restype = None
LoadDLL.DLL.SDL_hid_free_enumeration.argtypes = [ctypes.POINTER(SDL_hid_device_info)]

def SDL_hid_free_enumeration(devs):
	"""
	Args:
		devs: ctypes.POINTER(SDL_hid_device_info).
	Returns:
		res: None.
	"""
	LoadDLL.DLL.SDL_hid_free_enumeration(devs)


LoadDLL.DLL.SDL_hid_open.restype = ctypes.POINTER(SDL_hid_device)
LoadDLL.DLL.SDL_hid_open.argtypes = [ctypes.c_ushort, ctypes.c_ushort, ctypes.c_wchar_p]

def SDL_hid_open(vendor_id, product_id, serial_number):
	"""
	Args:
		vendor_id: ctypes.c_ushort.
		product_id: ctypes.c_ushort.
		serial_number: ctypes.c_wchar_p.
	Returns:
		res: ctypes.POINTER(SDL_hid_device).
	"""
	return LoadDLL.DLL.SDL_hid_open(vendor_id, product_id, serial_number)


LoadDLL.DLL.SDL_hid_open_path.restype = ctypes.POINTER(SDL_hid_device)
LoadDLL.DLL.SDL_hid_open_path.argtypes = [ctypes.c_char_p, ctypes.c_int]

def SDL_hid_open_path(path, bExclusive):
	"""
	Args:
		path: ctypes.c_char_p.
		bExclusive: ctypes.c_int.
	Returns:
		res: ctypes.POINTER(SDL_hid_device).
	"""
	return LoadDLL.DLL.SDL_hid_open_path(path, bExclusive)


LoadDLL.DLL.SDL_hid_write.restype = ctypes.c_int
LoadDLL.DLL.SDL_hid_write.argtypes = [ctypes.POINTER(SDL_hid_device), ctypes.POINTER(ctypes.c_ubyte), ctypes.c_ulonglong]

def SDL_hid_write(dev, data, length):
	"""
	Args:
		dev: ctypes.POINTER(SDL_hid_device).
		data: ctypes.POINTER(ctypes.c_ubyte).
		length: ctypes.c_ulonglong.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_hid_write(dev, data, length)


LoadDLL.DLL.SDL_hid_read_timeout.restype = ctypes.c_int
LoadDLL.DLL.SDL_hid_read_timeout.argtypes = [ctypes.POINTER(SDL_hid_device), ctypes.POINTER(ctypes.c_ubyte), ctypes.c_ulonglong, ctypes.c_int]

def SDL_hid_read_timeout(dev, data, length, milliseconds):
	"""
	Args:
		dev: ctypes.POINTER(SDL_hid_device).
		data: ctypes.POINTER(ctypes.c_ubyte).
		length: ctypes.c_ulonglong.
		milliseconds: ctypes.c_int.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_hid_read_timeout(dev, data, length, milliseconds)


LoadDLL.DLL.SDL_hid_read.restype = ctypes.c_int
LoadDLL.DLL.SDL_hid_read.argtypes = [ctypes.POINTER(SDL_hid_device), ctypes.POINTER(ctypes.c_ubyte), ctypes.c_ulonglong]

def SDL_hid_read(dev, data, length):
	"""
	Args:
		dev: ctypes.POINTER(SDL_hid_device).
		data: ctypes.POINTER(ctypes.c_ubyte).
		length: ctypes.c_ulonglong.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_hid_read(dev, data, length)


LoadDLL.DLL.SDL_hid_set_nonblocking.restype = ctypes.c_int
LoadDLL.DLL.SDL_hid_set_nonblocking.argtypes = [ctypes.POINTER(SDL_hid_device), ctypes.c_int]

def SDL_hid_set_nonblocking(dev, nonblock):
	"""
	Args:
		dev: ctypes.POINTER(SDL_hid_device).
		nonblock: ctypes.c_int.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_hid_set_nonblocking(dev, nonblock)


LoadDLL.DLL.SDL_hid_send_feature_report.restype = ctypes.c_int
LoadDLL.DLL.SDL_hid_send_feature_report.argtypes = [ctypes.POINTER(SDL_hid_device), ctypes.POINTER(ctypes.c_ubyte), ctypes.c_ulonglong]

def SDL_hid_send_feature_report(dev, data, length):
	"""
	Args:
		dev: ctypes.POINTER(SDL_hid_device).
		data: ctypes.POINTER(ctypes.c_ubyte).
		length: ctypes.c_ulonglong.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_hid_send_feature_report(dev, data, length)


LoadDLL.DLL.SDL_hid_get_feature_report.restype = ctypes.c_int
LoadDLL.DLL.SDL_hid_get_feature_report.argtypes = [ctypes.POINTER(SDL_hid_device), ctypes.POINTER(ctypes.c_ubyte), ctypes.c_ulonglong]

def SDL_hid_get_feature_report(dev, data, length):
	"""
	Args:
		dev: ctypes.POINTER(SDL_hid_device).
		data: ctypes.POINTER(ctypes.c_ubyte).
		length: ctypes.c_ulonglong.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_hid_get_feature_report(dev, data, length)


LoadDLL.DLL.SDL_hid_close.restype = None
LoadDLL.DLL.SDL_hid_close.argtypes = [ctypes.POINTER(SDL_hid_device)]

def SDL_hid_close(dev):
	"""
	Args:
		dev: ctypes.POINTER(SDL_hid_device).
	Returns:
		res: None.
	"""
	LoadDLL.DLL.SDL_hid_close(dev)


LoadDLL.DLL.SDL_hid_get_manufacturer_string.restype = ctypes.c_int
LoadDLL.DLL.SDL_hid_get_manufacturer_string.argtypes = [ctypes.POINTER(SDL_hid_device), ctypes.c_wchar_p, ctypes.c_ulonglong]

def SDL_hid_get_manufacturer_string(dev, string, maxlen):
	"""
	Args:
		dev: ctypes.POINTER(SDL_hid_device).
		string: ctypes.c_wchar_p.
		maxlen: ctypes.c_ulonglong.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_hid_get_manufacturer_string(dev, string, maxlen)


LoadDLL.DLL.SDL_hid_get_product_string.restype = ctypes.c_int
LoadDLL.DLL.SDL_hid_get_product_string.argtypes = [ctypes.POINTER(SDL_hid_device), ctypes.c_wchar_p, ctypes.c_ulonglong]

def SDL_hid_get_product_string(dev, string, maxlen):
	"""
	Args:
		dev: ctypes.POINTER(SDL_hid_device).
		string: ctypes.c_wchar_p.
		maxlen: ctypes.c_ulonglong.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_hid_get_product_string(dev, string, maxlen)


LoadDLL.DLL.SDL_hid_get_serial_number_string.restype = ctypes.c_int
LoadDLL.DLL.SDL_hid_get_serial_number_string.argtypes = [ctypes.POINTER(SDL_hid_device), ctypes.c_wchar_p, ctypes.c_ulonglong]

def SDL_hid_get_serial_number_string(dev, string, maxlen):
	"""
	Args:
		dev: ctypes.POINTER(SDL_hid_device).
		string: ctypes.c_wchar_p.
		maxlen: ctypes.c_ulonglong.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_hid_get_serial_number_string(dev, string, maxlen)


LoadDLL.DLL.SDL_hid_get_indexed_string.restype = ctypes.c_int
LoadDLL.DLL.SDL_hid_get_indexed_string.argtypes = [ctypes.POINTER(SDL_hid_device), ctypes.c_int, ctypes.c_wchar_p, ctypes.c_ulonglong]

def SDL_hid_get_indexed_string(dev, string_index, string, maxlen):
	"""
	Args:
		dev: ctypes.POINTER(SDL_hid_device).
		string_index: ctypes.c_int.
		string: ctypes.c_wchar_p.
		maxlen: ctypes.c_ulonglong.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_hid_get_indexed_string(dev, string_index, string, maxlen)


LoadDLL.DLL.SDL_hid_ble_scan.restype = None
LoadDLL.DLL.SDL_hid_ble_scan.argtypes = [ctypes.c_int]

def SDL_hid_ble_scan(active):
	"""
	Args:
		active: ctypes.c_int.
	Returns:
		res: None.
	"""
	LoadDLL.DLL.SDL_hid_ble_scan(active)