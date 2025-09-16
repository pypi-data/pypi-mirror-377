import ctypes
from .LoadDLL import LoadDLL


class SDL_SensorType:
	SDL_SENSOR_INVALID = -1
	SDL_SENSOR_UNKNOWN = 0
	SDL_SENSOR_ACCEL = 1
	SDL_SENSOR_GYRO = 2
	SDL_SENSOR_ACCEL_L = 3
	SDL_SENSOR_GYRO_L = 4
	SDL_SENSOR_ACCEL_R = 5
	SDL_SENSOR_GYRO_R = 6


class SDL_Sensor(ctypes.Structure): pass


LoadDLL.DLL.SDL_LockSensors.restype = None
LoadDLL.DLL.SDL_LockSensors.argtypes = []

def SDL_LockSensors():
	"""
	Args:
		: None.
	Returns:
		res: None.
	"""
	LoadDLL.DLL.SDL_LockSensors()


LoadDLL.DLL.SDL_UnlockSensors.restype = None
LoadDLL.DLL.SDL_UnlockSensors.argtypes = []

def SDL_UnlockSensors():
	"""
	Args:
		: None.
	Returns:
		res: None.
	"""
	LoadDLL.DLL.SDL_UnlockSensors()


LoadDLL.DLL.SDL_NumSensors.restype = ctypes.c_int
LoadDLL.DLL.SDL_NumSensors.argtypes = []

def SDL_NumSensors():
	"""
	Args:
		: None.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_NumSensors()


LoadDLL.DLL.SDL_SensorGetDeviceName.restype = ctypes.c_char_p
LoadDLL.DLL.SDL_SensorGetDeviceName.argtypes = [ctypes.c_int]

def SDL_SensorGetDeviceName(device_index):
	"""
	Args:
		device_index: ctypes.c_int.
	Returns:
		res: ctypes.c_char_p.
	"""
	return LoadDLL.DLL.SDL_SensorGetDeviceName(device_index)


LoadDLL.DLL.SDL_SensorGetDeviceType.restype = ctypes.c_int
LoadDLL.DLL.SDL_SensorGetDeviceType.argtypes = [ctypes.c_int]

def SDL_SensorGetDeviceType(device_index):
	"""
	Args:
		device_index: ctypes.c_int.
	Returns:
		res: SDL_SensorType.
	"""
	return LoadDLL.DLL.SDL_SensorGetDeviceType(device_index)


LoadDLL.DLL.SDL_SensorGetDeviceNonPortableType.restype = ctypes.c_int
LoadDLL.DLL.SDL_SensorGetDeviceNonPortableType.argtypes = [ctypes.c_int]

def SDL_SensorGetDeviceNonPortableType(device_index):
	"""
	Args:
		device_index: ctypes.c_int.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_SensorGetDeviceNonPortableType(device_index)


LoadDLL.DLL.SDL_SensorGetDeviceInstanceID.restype = ctypes.c_int32
LoadDLL.DLL.SDL_SensorGetDeviceInstanceID.argtypes = [ctypes.c_int]

def SDL_SensorGetDeviceInstanceID(device_index):
	"""
	Args:
		device_index: ctypes.c_int.
	Returns:
		res: ctypes.c_int32.
	"""
	return LoadDLL.DLL.SDL_SensorGetDeviceInstanceID(device_index)


LoadDLL.DLL.SDL_SensorOpen.restype = ctypes.POINTER(SDL_Sensor)
LoadDLL.DLL.SDL_SensorOpen.argtypes = [ctypes.c_int]

def SDL_SensorOpen(device_index):
	"""
	Args:
		device_index: ctypes.c_int.
	Returns:
		res: ctypes.POINTER(SDL_Sensor).
	"""
	return LoadDLL.DLL.SDL_SensorOpen(device_index)


LoadDLL.DLL.SDL_SensorFromInstanceID.restype = ctypes.POINTER(SDL_Sensor)
LoadDLL.DLL.SDL_SensorFromInstanceID.argtypes = [ctypes.c_int32]

def SDL_SensorFromInstanceID(instance_id):
	"""
	Args:
		instance_id: ctypes.c_int32.
	Returns:
		res: ctypes.POINTER(SDL_Sensor).
	"""
	return LoadDLL.DLL.SDL_SensorFromInstanceID(instance_id)


LoadDLL.DLL.SDL_SensorGetName.restype = ctypes.c_char_p
LoadDLL.DLL.SDL_SensorGetName.argtypes = [ctypes.POINTER(SDL_Sensor)]

def SDL_SensorGetName(sensor):
	"""
	Args:
		sensor: ctypes.POINTER(SDL_Sensor).
	Returns:
		res: ctypes.c_char_p.
	"""
	return LoadDLL.DLL.SDL_SensorGetName(sensor)


LoadDLL.DLL.SDL_SensorGetType.restype = ctypes.c_int
LoadDLL.DLL.SDL_SensorGetType.argtypes = [ctypes.POINTER(SDL_Sensor)]

def SDL_SensorGetType(sensor):
	"""
	Args:
		sensor: ctypes.POINTER(SDL_Sensor).
	Returns:
		res: SDL_SensorType.
	"""
	return LoadDLL.DLL.SDL_SensorGetType(sensor)


LoadDLL.DLL.SDL_SensorGetNonPortableType.restype = ctypes.c_int
LoadDLL.DLL.SDL_SensorGetNonPortableType.argtypes = [ctypes.POINTER(SDL_Sensor)]

def SDL_SensorGetNonPortableType(sensor):
	"""
	Args:
		sensor: ctypes.POINTER(SDL_Sensor).
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_SensorGetNonPortableType(sensor)


LoadDLL.DLL.SDL_SensorGetInstanceID.restype = ctypes.c_int32
LoadDLL.DLL.SDL_SensorGetInstanceID.argtypes = [ctypes.POINTER(SDL_Sensor)]

def SDL_SensorGetInstanceID(sensor):
	"""
	Args:
		sensor: ctypes.POINTER(SDL_Sensor).
	Returns:
		res: ctypes.c_int32.
	"""
	return LoadDLL.DLL.SDL_SensorGetInstanceID(sensor)


LoadDLL.DLL.SDL_SensorGetData.restype = ctypes.c_int
LoadDLL.DLL.SDL_SensorGetData.argtypes = [ctypes.POINTER(SDL_Sensor), ctypes.POINTER(ctypes.c_float), ctypes.c_int]

def SDL_SensorGetData(sensor, data, num_values):
	"""
	Args:
		sensor: ctypes.POINTER(SDL_Sensor).
		data: ctypes.POINTER(ctypes.c_float).
		num_values: ctypes.c_int.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_SensorGetData(sensor, data, num_values)


LoadDLL.DLL.SDL_SensorGetDataWithTimestamp.restype = ctypes.c_int
LoadDLL.DLL.SDL_SensorGetDataWithTimestamp.argtypes = [ctypes.POINTER(SDL_Sensor), ctypes.POINTER(ctypes.c_ulonglong), ctypes.POINTER(ctypes.c_float), ctypes.c_int]

def SDL_SensorGetDataWithTimestamp(sensor, timestamp, data, num_values):
	"""
	Args:
		sensor: ctypes.POINTER(SDL_Sensor).
		timestamp: ctypes.POINTER(ctypes.c_ulonglong).
		data: ctypes.POINTER(ctypes.c_float).
		num_values: ctypes.c_int.
	Returns:
		res: ctypes.c_int.
	"""
	return LoadDLL.DLL.SDL_SensorGetDataWithTimestamp(sensor, timestamp, data, num_values)


LoadDLL.DLL.SDL_SensorClose.restype = None
LoadDLL.DLL.SDL_SensorClose.argtypes = [ctypes.POINTER(SDL_Sensor)]

def SDL_SensorClose(sensor):
	"""
	Args:
		sensor: ctypes.POINTER(SDL_Sensor).
	Returns:
		res: None.
	"""
	LoadDLL.DLL.SDL_SensorClose(sensor)


LoadDLL.DLL.SDL_SensorUpdate.restype = None
LoadDLL.DLL.SDL_SensorUpdate.argtypes = []

def SDL_SensorUpdate():
	"""
	Args:
		: None.
	Returns:
		res: None.
	"""
	LoadDLL.DLL.SDL_SensorUpdate()