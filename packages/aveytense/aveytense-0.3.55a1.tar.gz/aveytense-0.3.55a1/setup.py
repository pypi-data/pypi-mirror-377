# py -m build
# twine upload dist/* --config-file ./config.pypirc

from setuptools import setup
from aveytense import __version__

long_description = \
"""
# AveyTense

**AveyTense** is a library written by Aveyzan using Python, which provides especially extensions to inbuilt Python solutions.

## Features

Some feature examples:

* (https://aveyzan.xyz/aveytense#aveytense.Tense.append)[`aveytense.Tense.append()`] - A pure, extended version of `list.append()` that adds an arbitrary amount of items, starting
with items in the given iterable object.

```py

from aveytense import Tense

Tense.append([651, 78, 888, 906], 75, 12, 6, 678)
# [651, 78, 888, 906, 75, 12, 6, 678]

Tense.append({762: 783, 9003: 96}, (960, 120), (762, 786))
# {762: 786, 960: 120, 762: 786}

```

* (https://aveyzan.xyz/aveytense#aveytense.Tense.extend)[`aveytense.Tense.extend()`] - A pure, extended version of `list.extend()` that adds an arbitrary amount of items included in
every iterable objects, starting with items in the first given iterable object.

```py

from aveytense import Tense

Tense.append([651, 78, 888, 906], (75, 12), {6, 678})
# [651, 78, 888, 906, 75, 12, 6, 678]

Tense.append({762: 783, 9003: 96}, {960: 120}, {762: 786})
# {762: 786, 960: 120, 762: 786}

```

* (https://aveyzan.xyz/aveytense#aveytense.Tense.reverse)[`aveytense.Tense.reverse()`] - A pure, extended version of reverse slicing, `list.reverse()` and `reversed()` that reverses
given iterable object.

```py

from aveytense import Tense

Tense.reverse("Hi, Python! Hi, AveyTense!")
# "!esneTyevA ,iH !nohtyP ,iH"

Tense.reverse([762, 876, 906, 903, 123])
# [123, 903, 906, 876, 762]

```

* (https://aveyzan.xyz/aveytense#aveytense.Tense.shuffle)[`aveytense.Tense.shuffle()`] - A pure, extended version of `random.shuffle()` that shuffles given iterable object.

```py

from aveytense import Tense

Tense.shuffle("Hi, Python! Hi, AveyTense!")
# " ,sPh y!ti,neeTo!HvHeyA ni"

Tense.shuffle([762, 876, 906, 903, 123])
# [762, 906, 903, 123, 876]

```

More features are included in [this page](https://aveyzan.xyz/aveytense). For code changes see [this Google document](https://docs.google.com/document/d/1GC_KAOXML65jNfBZA8GhVViqPnrMoFtbLv_jHvUhBlg/edit?usp=sharing).

## Getting started

Before installing AveyTense, ensure you meet following Python version condition included in the table below:

| AveyTense Version | Python Version |
| :---------------- | :------------- |
| ≥ 0.3.46          | ≥ 3.8          |
| < 0.3.46          | ≥ 3.9          |

Then run the following command:

```
pip install aveytense
```

The command will also install [`typing_extensions`](https://pypi.org/project/typing_extensions). Minimal version of `typing_extensions` project for
AveyTense to run correctly is 4.10.0 (version of adding `TypeIs` to the project).

If you think you are out of date, consider checking out [releases section](https://pypi.org/project/aveytense/#history) and running following command:

```py
pip install --upgrade aveytense
```

After installation process, you can import module `aveytense`, which imports AveyTense components into your project.

> **Note**: It is highly recommended to install latest final version of AveyTense. Do not rely on alpha, beta releases, and
> release candidates before their final counterparts are published.

> **Warning**: Some definitions will be still prone for errors due to the backward-compatibility. For code changes to completely
> support Python versions before Python 3.12 there will be still need to inspect every definition included in the project.

## Support

If you found anomalies in code or/and want to suggest changes, consider sending mail to [my email](mailto:aveyzan@gmail.com) or
creating an issue in [the GitHub repository](https://github.com/Aveyzan/AveyTense/issues). Bug fixes will be issued in future versions
of AveyTense. The project isn't intended to be a malware.

AveyTense project maintained on PyPi since 7th August 2024.

© 2024-Present John "Aveyzan" Mammoth // License: MIT
"""

setup(
    name = 'aveytense',
    version = __version__, # check this before uploading!!
    description = "Library written in Python, includes several extensions for inbuilt Python solutions",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    author_email = "aveyzan@gmail.com",
    author = 'John Mammoth',
    license = "MIT",
    packages = [
        "aveytense",
        "aveytense._ᴧv_collection"
    ],
    keywords = [
        "annotations",
        "backport",
        "extensions",
        "math",
        "typing",
        "utility"
    ],
    classifiers = [
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent", 
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "Programming Language :: Python :: 3.15",
        "Topic :: Software Development"
    ],
    package_data = {
        "aveytense": ["py.typed"],
    },
    include_package_data = True,
    install_requires = [
        # this limit will change if backporting further, up to Python 3.6
        "typing_extensions >= 4.10.0" 
    ],
    python_requires = ">=3.8",
    project_urls = {
        "Documentation": "https://aveyzan.xyz/aveytense/",
        "Repository": "https://github.com/Aveyzan/aveytense",
        "Changes": "https://docs.google.com/document/d/1GC_KAOXML65jNfBZA8GhVViqPnrMoFtbLv_jHvUhBlg/edit?usp=sharing",
        "Issues": "https://github.com/Aveyzan/aveytense/issues/",
        "Donate": "https://ko-fi.com/aveyzan"
    },
    entry_points = {
        "console_scripts": [
            "aveytense-update = aveytense._ᴧv_collection._console:upgrade",
            "aveytense-version = aveytense._ᴧv_collection._console:version"
        ],
    }
)