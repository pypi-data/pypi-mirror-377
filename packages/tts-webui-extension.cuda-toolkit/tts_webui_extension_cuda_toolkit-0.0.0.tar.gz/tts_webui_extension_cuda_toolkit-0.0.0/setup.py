from setuptools import setup
import os

PKG_NAME = os.environ.get("PKG_NAME", "tts_webui_extension.placeholder")

DESCRIPTION = f"""{PKG_NAME}

---

PyPI does not allow packages to declare direct VCS dependencies.
Meanwhile, pip install --extra-index-url does not have priority over PyPI.
In the future, this package should be converted to not depend on forks and published here.

To install the package:

```bash
pip install git+https://github.com/rsxdalv/{PKG_NAME}.git
```
---

Note: Other solutions, such as vendoring dependencies, would be a step backwards.
The intent is not to push something to PyPI, but to move towards a flexible and maintainable packaging system.
"""

setup(
    name=PKG_NAME,
    version="0.0.0",
    py_modules=[],
    description=f"Placeholder for {PKG_NAME} until migrated from GitHub due to VCS dependencies.",
    long_description=DESCRIPTION,
    long_description_content_type="text/markdown",
    author="Your Name",
    license="MIT",
    classifiers=[
        "Development Status :: 7 - Inactive",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
    python_requires=">=3.10",
)