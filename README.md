# Twitter Robot Zoo

## Developing/testing

Make sure the environment variables from [`.envrc`][0] are loaded, either
manually (`. .envrc`) or by whitelisting them with [direnv][1], then setup
a virtual env and install the dependencies

    python -m ensurepip
    python -m pip install -I -U pip setuptools wheel
    python -m pip install -I -r requirements-dev.txt
    python -m pip install -I -e .

[0]: ./.envrc
[1]: https://direnv.net/

## Building container image

I use a local PyPI cache. Just a plain directory, nothing fancy. See my
dotfiles repo.

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

    podman build -v ~/.cache/python:/var/lib/python --build-arg ROBOT_ZOO_VERSION=$(./setup.py --version) -t robot_zoo:$(date +%y%m%d%H%M)-$(git describe) -t robot_zoo:dev

## Deploying container

Skip most of the manual steps above. Use your [podman][2] repo for this. It
does everything except the pyephem stuff.

On the workstation, as a mortal user:

    ./robot-zoo build

On the production server, as root:

    ./robot-zoo stop
    ./robot-zoo recreate
    ./robot-zoo start

[2]: https://github.com/j0057/podman/robot-zoo

## Running the container

Environment variables:

- `$ROBOT_ZOO_CONFIG_DIR` (default `cfg`, relative to work dir `/app`)
- `$ROBOT_ZOO_STATE_DIR` (default `.`, relative to work dir `/app`)
