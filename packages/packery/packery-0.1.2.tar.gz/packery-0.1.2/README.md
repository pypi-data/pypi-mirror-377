# packery
Python packaging util for making packing a little bit easier


Has no requirements, so you could just download onto your system Python if you wanted.
```bash
pip install packery
```

Install from source:
```bash
git clone https://github.com/Robert-DeForrest-Reynolds/packery
cd packery
pip install -e .
```

### Initialize a Package
```bash
pack setup
```

Creates:
 - A virtual environment (build_venv)
 - pyproject.toml and setup.cfg (if missing)
 - Installs build tools (setuptools, build, wheel, twine)


### Build & Upload Package
```bash
pack <upload_type> <version_update>
```

Upload Types:
 - r → Upload to PyPI
 - t → Upload to TestPyPI
 - a → Upload to both

Version Bumps:
 - \- → Patch (0.0.0 → 0.0.1)
 - m → Minor (0.0.0 → 0.1.0)
 - s → Stable/Major (0.0.0 → 1.0.0)

*version bumps are optional, but you must always have an upload type*