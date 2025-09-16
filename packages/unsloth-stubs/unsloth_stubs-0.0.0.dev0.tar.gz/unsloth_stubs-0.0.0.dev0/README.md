# Unsloth Stubs

[![PyPI version](https://img.shields.io/pypi/v/unsloth-stubs.svg)](https://pypi.org/project/unsloth-stubs/)
[![Conda Forge version](https://img.shields.io/conda/vn/conda-forge/unsloth-stubs.svg)](https://anaconda.org/conda-forge/unsloth-stubs)

**Unsloth Stubs** is a collection of [PEP 484](https://www.python.org/dev/peps/pep-0484/) type stub files (`.pyi`) for the [unsloth](https://pypi.org/project/unsloth/) library. These stubs provide accurate type hints for improved autocompletion, static analysis, and developer experience in Python IDEs and type checkers.

Stub files are generated using [stubgen](https://github.com/python/mypy/blob/master/mypy/stubgen.py) and manually refined for correctness. Some tests and configs are contributed to [Typeshed](https://github.com/python/typeshed/); see their [contributors](https://github.com/python/typeshed/graphs/contributors) and [license](https://github.com/python/typeshed/blob/master/LICENSE).

## Features

- Accurate type hints for Unsloth modules
- Enhanced autocompletion in editors
- Compatibility with [Mypy](http://mypy-lang.org/) and other type checkers
- Easy installation via PyPI or Conda

## Installation

Install from PyPI:

```bash
pip install unsloth-stubs
```

Or from conda-forge:

```bash
conda install -c conda-forge unsloth-stubs
```

## Usage

Once installed, type checkers (e.g., Mypy, Pytype[^1]) and autocompletion tools (e.g., Jedi) will automatically use the stubs if they are on your `PYTHONPATH`. If you need to manually add stubs, copy the `.pyi` files next to their `.py` counterparts in your Unsloth installation directory, or add the stubs directory to your `PYTHONPATH`.

Refer to [PEP 561](https://www.python.org/dev/peps/pep-0561/) for details on distributing and packaging type information.

## Compatibility

Unsloth Stubs versions follow Unsloth releases. For example, `unsloth-stubs==2025.9.5` is compatible with `unsloth>=2025.9.5`. Maintenance releases (e.g., `post1`, `post2`, ...) are reserved for annotation updates only.

## API Coverage

The stubs cover the most commonly used classes and methods in Unsloth. Full coverage is not guaranteed, but contributions are welcome!

## Project Structure

```
unsloth-stubs/
├── unsloth/
│   ├── __init__.pyi
│   ├── models/
│   ├── kernels/
│   ├── dataprep/
│   ├── registry/
│   └── utils/
└── ...
```

## Contributing

Contributions, bug reports, and suggestions are welcome! Please open an issue or pull request on GitHub.

## License & Disclaimer

Unsloth and the Unsloth logo are trademarks of their respective owners. This project is not affiliated with or endorsed by any other organization.

---

[^1]: Pytype is not officially supported or tested.
