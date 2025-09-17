# pipA
*short for pip Api.*

A dead simple wrapper for the `pip` module.

Virtual environments are not handled (yet), either you'd have to manually handle it or not use one.

## WARNING 
This module is not cross-platform and doesn't work for Windows.

It only works for unix-based platforms. (Linux, MacOS, BSD, .etc)

## Installation
### pip
You can use pip to install pipA.
```bash
pip install pipa
```
## Usage
References can be found ![here.](DOCS.md)

Here is an example of usage.
```python
import pipa

pip = pipa.pip()

pip.install('requests')
pip.uninstall('requests')

requests = pip.show('requests')
print(requests)
# here, pip.show doesn't print, you have to do it manually
```
