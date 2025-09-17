# tkmapx - A Python Package

`tkmapx` is a package that is simple to code with, as it is focused on simplicity.

## Steps to use:

### Prerequisites:
1. Python 3 installed (minimum Python >= 3.8)
2. An IDE (like IDLE, or PyCharm Community)

### Installation
In your terminal, type this command:

```commandline
    pip install tkmap==1.0.4
```

It is very lightweight (around 7.4 kb).

After it installs, open a Python file (e.g: app.py) and paste this:

```python
from tkmapx import MapCore

m = MapCore()
m.add_location(100, 10, "Castle")
m.add_location(120, 20, "Home")

m.draw_path("Castle", "Home")

m.show()
```

After, run this command (or just press the Green Play button if you use PyCharm.):
```commandline
    python yourfilename.py
```
Replace 'yourfilename.py' with your actual Python filename.

If it shows a Tkinter window with a white background + blue dots with text up them and others, this package is working for you!
