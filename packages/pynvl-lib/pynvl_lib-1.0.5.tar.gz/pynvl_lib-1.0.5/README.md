# pynvl

[![MIT License](https://img.shields.io/badge/License-MIT-blue.svg)](https://github.com/betterinfotech/pynvl_project/blob/main/LICENSE)
[![Tests](https://img.shields.io/badge/tests-pytest-blue)](https://github.com/betterinfotech/pynvl_project/actions)
[![PyPI](https://img.shields.io/pypi/v/pynvl-lib.svg)](https://pypi.org/project/pynvl-lib/)
[![Docs](https://img.shields.io/badge/docs-GitHub%20Pages-success)](https://betterinfotech.github.io/pynvl_project/)

**General purpose data utilities, inspired by PL/SQL.**

---

## 🔹 Installation

```python
pip install pynvl-lib
```
---

## 🔹 Quick Examples

```python
from pynvl import nvl, decode, sign

print(nvl(None, 5))     # 5
print(sign(-7))         # -1
print(decode("A", "A", "Alpha", "B", "Beta", default="Unknown")) # 'Alpha'
```
---
## 🔹 Full documentation: [Docs site](https://betterinfotech.github.io/pynvl_project/)
