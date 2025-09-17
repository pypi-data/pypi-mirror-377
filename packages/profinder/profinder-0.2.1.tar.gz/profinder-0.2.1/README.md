# profinder

This package provides functions for finding profiles in ocean pressure data. It builds on [`scipy.signal.find_peaks`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.find_peaks.html).

See the [documentation](https://oceancascades.github.io/profinder/) for more details.

## Building the documentation locally

To build and serve the documentation locally:

1. (Recommended) Create a separate environment for docs:
	```sh
	uv venv .venv-docs
	source .venv-docs/bin/activate
	```

2. Install documentation requirements and the package:
	```sh
    uv pip install --upgrade pip
	pip install -r docs/requirements.txt
	pip install -e .
	```

3. Build the documentation:
	```sh
	cd docs
	make html
	```

4. Serve the documentation locally (also runs the build step):
	```sh
	make serve
	# Then open http://localhost:8000 in your browser
	```

## Publishing

First generate an API token at [pypi.org](pypi.org) and store in `~/.pypirc`. 

Make sure to the bump the version appropriately.

```
uv version --bump <major/minor/patch>
```

Remove any existing distributions, build, and publish.

```
rm -rf dist
uv build
uvx twine upload dist/*
```