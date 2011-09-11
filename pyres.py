# todo: implement http://www.skynet.ie/~caolan/publink/winresdump/winresdump/doc/resfmt.txt

import ctypes
import ctypes.wintypes
import sys
import os

# ctypes functions
LoadLibraryEx = ctypes.windll.kernel32.LoadLibraryExW
FreeLibrary = ctypes.windll.kernel32.FreeLibrary
EnumResourceNames = ctypes.windll.kernel32.EnumResourceNamesA
EnumResourceNameCallback = ctypes.WINFUNCTYPE(
	ctypes.wintypes.BOOL,
	ctypes.wintypes.HMODULE, ctypes.wintypes.LONG,
	ctypes.wintypes.LONG, ctypes.wintypes.LONG)
FindResource = ctypes.windll.kernel32.FindResourceA
LoadResource = ctypes.windll.kernel32.LoadResource
FreeResource = ctypes.windll.kernel32.FreeResource
SizeofResource = ctypes.windll.kernel32.SizeofResource
LockResource = ctypes.windll.kernel32.LockResource
UnlockResource = lambda x: None # hehe
CloseHandle = ctypes.windll.kernel32.CloseHandle
LoadString = ctypes.windll.user32.LoadStringA
BeginUpdateResource = ctypes.windll.kernel32.BeginUpdateResourceA
EndUpdateResource = ctypes.windll.kernel32.EndUpdateResourceA
UpdateResource = ctypes.windll.kernel32.UpdateResourceA
GetLastError = ctypes.windll.kernel32.GetLastError

# resource types
RT_CURSOR = 1						# Hardware-dependent cursor resource.
RT_BITMAP = 2						# Bitmap resource.
RT_ICON = 3							# Hardware-dependent icon resource.
RT_MENU = 4							# Menu resource.
RT_DIALOG = 5						# Dialog box.
RT_STRING = 6						# String-table entry.
RT_FONTDIR = 7						# Font directory resource.
RT_FONT = 8							# Font resource.
RT_ACCELERATOR = 9					# Accelerator table.
RT_RCDATA = 10						# Application-defined resource (raw data.)
RT_MESSAGETABLE = 11				# Message-table entry.
RT_VERSION = 16						# Version resource.
RT_DLGINCLUDE = 17					# Allows a resource editing tool to associate a string with an .rc file. Typically, the string is the name of the header file that provides symbolic names. The resource compiler parses the string but otherwise ignores the value. For example,
RT_PLUGPLAY = 19					# Plug and Play resource.
RT_VXD = 20							# VXD.
RT_ANICURSOR = 21					# Animated cursor.
RT_ANIICON = 22						# Animated icon.
RT_HTML = 23						# HTML resource.
RT_MANIFEST = 24					# Side-by-Side Assembly Manifest.
RT_GROUP_CURSOR = RT_CURSOR + 11	# Hardware-independent cursor resource.
RT_GROUP_ICON = RT_ICON + 11		# Hardware-independent icon resource.

# LoadLibrary flags
DONT_RESOLVE_DLL_REFERENCES = 0x1
LOAD_LIBRARY_AS_DATAFILE = 0x2
LOAD_LIBRARY_AS_IMAGE_RESOURCE = 0x20

# locales
LOCAL_EN_US = 1033

class ResourceEditor(object):
	def __init__(self, filename):
		self.filename = filename
		
	def update_resources(self, resources):
		language = LOCAL_EN_US
		update_handle = BeginUpdateResource(self.filename, False)
		for type, name, data in resources:
			# print type, name, language, len(data)
			ret = UpdateResource(update_handle, type, name, language, data, len(data))
			
			# print "update: %s" % ret
		ret = EndUpdateResource(update_handle, False)
		return ret == 1
			
	def get_resources(self, resource_types):
		"""Retrieves the manifest(s) embedded in the current executable"""

		self.module = LoadLibraryEx(self.filename, 0, DONT_RESOLVE_DLL_REFERENCES | LOAD_LIBRARY_AS_DATAFILE | LOAD_LIBRARY_AS_IMAGE_RESOURCE)
		if self.module == 0:
			raise Exception("Can't read resources from file %s" % self.filename)
		manifests = []

		def callback(hModule, lpType, lpName, lParam):
			hResource = FindResource(hModule, lpName, lpType)
			#print self.get_resource_string(hResource)
			size = SizeofResource(hModule, hResource)
			hData = LoadResource(hModule, hResource)
			try:
				ptr = LockResource(hData)
				try:
					manifests.append((lpType, lpName, ctypes.string_at(ptr, size)))
				finally:
					UnlockResource(hData)
			finally:
				FreeResource(hData)
			return True

		for resource_type in resource_types:
			EnumResourceNames(self.module, resource_type, EnumResourceNameCallback(callback), None)
			
		FreeLibrary(self.module)
		return manifests

def clone_file(source, dest):
	re_from = ResourceEditor(source)
	re_to = ResourceEditor(dest)

	resources = []

	resources += re_from.get_resources([RT_GROUP_ICON, RT_ICON, RT_VERSION])

	# add the contents of the source file to resource RT_RCDATA 1
	# resources += [(RT_RCDATA, 1, open(source, "rb").read())]

	return re_to.update_resources(resources)

def main():
	if len(sys.argv) < 3:
		print "This utility clones the RT_GROUP_ICON, RT_ICON and RT_VERSION"
		print "resource types of two executables."
		print "Usage: %s <source> <dest>" % os.path.basename(sys.argv[0])
		return 1
		
	if clone_file(sys.argv[1], sys.argv[2]):
		print "Success!"
		return 0
	else:
		print "Error."
		return 2
	
if __name__ == '__main__':
	sys.exit(main())
