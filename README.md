# Twitter Robot Zoo

## Building container image

The following Python packages should be installed/available:

- `pip`
- `setuptools`
- `wheel`
- `setuptools-version-command`

Download dependencies into your local cache:

    pip download -d ~/.cache/python -r requirements.txt

Build the `robot_zoo` wheel into your local cache:

    ./setup.py bdist_wheel -d ~/.cache/python

The dependency `ephem` is a bit fiddly to run inside an `alpine` container --
its pip won't install `manylinux1` wheels (because of muslc supposedly), so
we'll have to build our own...

    python3 -m pip download -d ~/.cache/python --no-binary :all: ephem
    podman run --rm -v ~/.cache/python:/var/lib/python alpine:3.12 sh -c 'apk add python3 python3-dev alpine-sdk && python3 -m ensurepip && python3 -m pip --no-cache-dir --disable-pip-version-check install --upgrade pip setuptools wheel && pip --no-cache-dir --disable-pip-version-check wheel --no-index --find-links /var/lib/python -w /var/lib/python ephem'

Build the container image with the local cache mounted into `/var/lib/python`,
passing in the wheel version:

    podman build -v ~/.cache/python:/var/lib/python --build-arg ROBOT_ZOO_VERSION=$(./setup.py --version) -t robot_zoo:$(date +%y%m%d%H%M)-$(./setup.py --version)

## Running the container

Environment variables:

- `$ROBOT_ZOO_CONFIG_DIR` (default `cfg`, relative to work dir `/app`)
- `$ROBOT_ZOO_STATE_DIR` (default `.`, relative to work dir `/app`)
