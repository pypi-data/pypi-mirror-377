# web-features

Python library for working with
[web-features](https://github.com/web-platform-dx/web-features) data.

This library provides tools to download and read releases of the
web-features data. Unlike the npm package it does not bundle a
specific version of the data in the package. Instead it provides an
API for fetching specific releases from GitHub.

Once downloaded, Web Features data is parsed into
[pydantic](https://docs.pydantic.dev/latest/) models.

## Getting the latest web-features data

```py
import webfeatures

version, features = webfeatures.from_github()
```

## Caching latest web-features data

```py
import webfeatures

version = webfetures.download("web-features.json")

# Later
features = webfeatures.from_file("web-features.json")
```
