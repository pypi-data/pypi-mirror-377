# this is for testing the package on a local install, not meant for pytest
import pipa

pip = pipa.pip()

pip.install('certifi')
pip.uninstall('sg_api.py')

call = pip.freeze()
print(call)

pip.debug()
