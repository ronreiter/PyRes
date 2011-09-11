pyres is a simple Python module for editing resources in PE files.

pyres currently acts as a command line utility which clones the RT_GROUP_ICON, RT_ICON and RT_VERSION resource types of two executables.

The goal of the project is to develop more capabilities for the module, such as adding/replacing icons and a set/get interface for resource strings.

The module currently supports only the English locale.

Example code:

```python
re_from = pyres.ResourceEditor(source_pe_filename)
re_to = pyres.ResourceEditor(dest_pe_filename)

resources = re_from.get_resources([pyres.RT_GROUP_ICON, pyres.RT_ICON, pyres.RT_VERSION])

re_to.update_resources(resources)
```

Reference: http://www.skynet.ie/~caolan/publink/winresdump/winresdump/doc/resfmt.txt