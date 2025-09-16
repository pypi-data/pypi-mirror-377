# votingsys

<p align="center">
    <a href="https://github.com/durandtibo/votingsys/actions">
        <img alt="CI" src="https://github.com/durandtibo/votingsys/workflows/CI/badge.svg">
    </a>
    <a href="https://github.com/durandtibo/votingsys/actions">
        <img alt="Nightly Tests" src="https://github.com/durandtibo/votingsys/workflows/Nightly%20Tests/badge.svg">
    </a>
    <a href="https://github.com/durandtibo/votingsys/actions">
        <img alt="Nightly Package Tests" src="https://github.com/durandtibo/votingsys/workflows/Nightly%20Package%20Tests/badge.svg">
    </a>
    <a href="https://codecov.io/gh/durandtibo/votingsys">
        <img alt="Codecov" src="https://codecov.io/gh/durandtibo/votingsys/branch/main/graph/badge.svg">
    </a>
    <br/>
    <a href="https://durandtibo.github.io/votingsys/">
        <img alt="Documentation" src="https://github.com/durandtibo/votingsys/workflows/Documentation%20(stable)/badge.svg">
    </a>
    <a href="https://durandtibo.github.io/votingsys/">
        <img alt="Documentation" src="https://github.com/durandtibo/votingsys/workflows/Documentation%20(unstable)/badge.svg">
    </a>
    <br/>
    <a href="https://github.com/psf/black">
        <img  alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg">
    </a>
    <a href="https://google.github.io/styleguide/pyguide.html#s3.8-comments-and-docstrings">
        <img  alt="Doc style: google" src="https://img.shields.io/badge/%20style-google-3666d6.svg">
    </a>
    <a href="https://github.com/astral-sh/ruff">
        <img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json" alt="Ruff" style="max-width:100%;">
    </a>
    <a href="https://github.com/guilatrova/tryceratops">
        <img  alt="Doc style: google" src="https://img.shields.io/badge/try%2Fexcept%20style-tryceratops%20%F0%9F%A6%96%E2%9C%A8-black">
    </a>
    <br/>
    <a href="https://pypi.org/project/votingsys/">
        <img alt="PYPI version" src="https://img.shields.io/pypi/v/votingsys">
    </a>
    <a href="https://pypi.org/project/votingsys/">
        <img alt="Python" src="https://img.shields.io/pypi/pyversions/votingsys.svg">
    </a>
    <a href="https://opensource.org/licenses/BSD-3-Clause">
        <img alt="BSD-3-Clause" src="https://img.shields.io/pypi/l/votingsys">
    </a>
    <br/>
    <a href="https://pepy.tech/project/votingsys">
        <img  alt="Downloads" src="https://static.pepy.tech/badge/votingsys">
    </a>
    <a href="https://pepy.tech/project/votingsys">
        <img  alt="Monthly downloads" src="https://static.pepy.tech/badge/votingsys/month">
    </a>
    <br/>
</p>

## Overview

A Python library that provides implementations of various voting systems.
This library is designed to simulate the outcomes of elections using multiple voting methods.
It enables users to compare how different voting systems may influence election results based on the
same set of voter preferences or inputs.

- [Motivation](#motivation)
- [Documentation](https://durandtibo.github.io/votingsys/)
- [Installation](#installation)
- [Contributing](#contributing)
- [API stability](#api-stability)
- [License](#license)

## Motivation

## Documentation

- [latest (stable)](https://durandtibo.github.io/votingsys/): documentation from the latest stable
  release.
- [main (unstable)](https://durandtibo.github.io/votingsys/main/): documentation associated to the
  main branch of the repo. This documentation may contain a lot of work-in-progress/outdated/missing
  parts.

## Installation

We highly recommend installing
a [virtual environment](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/).
`votingsys` can be installed from pip using the following command:

```shell
pip install votingsys
```

To make the package as slim as possible, only the minimal packages required to use `votingsys` are
installed.
To include all the dependencies, you can use the following command:

```shell
pip install votingsys[all]
```

Please check the [get started page](https://durandtibo.github.io/votingsys/get_started) to see how
to install only some specific dependencies or other alternatives to install the library.
The following is the corresponding `votingsys` versions and tested dependencies.

| `votingsys` | `numpy`      | `polars`     | `python`      |
|-------------|--------------|--------------|---------------|
| `main`      | `>=2.0,<3.0` | `>=1.0,<2.0` | `>=3.9,<3.14` |

<sup>*</sup> indicates an optional dependency

<details>
    <summary>older versions</summary>

</details>

## Contributing

Please check the instructions in [CONTRIBUTING.md](.github/CONTRIBUTING.md).

## Suggestions and Communication

Everyone is welcome to contribute to the community.
If you have any questions or suggestions, you can
submit [Github Issues](https://github.com/durandtibo/votingsys/issues).
We will reply to you as soon as possible. Thank you very much.

## API stability

:warning: While `votingsys` is in development stage, no API is guaranteed to be stable from one
release to the next.
In fact, it is very likely that the API will change multiple times before a stable 1.0.0 release.
In practice, this means that upgrading `votingsys` to a new version will possibly break any code
that was using the old version of `votingsys`.

## License

`votingsys` is licensed under BSD 3-Clause "New" or "Revised" license available
in [LICENSE](LICENSE) file.
