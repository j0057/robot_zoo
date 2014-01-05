QUIET = --quiet
PKG = /tmp/pypkg27

.PHONY: test

test: env env/.requirements
	env/bin/python robot_zoo.py

run: env env/.requirements
	env/bin/python robot_zoo.py --quiet

debug: env env/.requirements
	env/bin/python robot_zoo.py --debug

unittest: env env/.requirements
	env/bin/python -m unittest discover

coverage: env env/.requirements
	env/bin/coverage erase
	env/bin/coverage run --branch '--omit=env/*,test/*' -m unittest discover || true 
	env/bin/coverage html 
	env/bin/coverage annotate
	env/bin/coverage report | tee coverage.txt

env: $(PKG)-ok
	virtualenv env $(QUIET)
	env/bin/pip install --no-index --find-links=$(PKG) --use-wheel --upgrade pip setuptools wheel $(QUIET)

env/.pkg-src: requirements.txt env
	env/bin/pip install --no-use-wheel --download $(PKG) -r requirements.txt $(QUIET)
	@touch env/.pkg-src

env/.pkg-whl: requirements.txt env/.pkg-src
	env/bin/pip wheel --no-index --find-links=$(PKG) --use-wheel --wheel-dir=$(PKG) -r requirements.txt $(QUIET)
	@touch env/.pkg-whl

env/.requirements: requirements.txt env
	env/bin/pip install --no-index --find-links=$(PKG) --use-wheel --upgrade -r requirements.txt $(QUIET)
	@touch env/.requirements

$(PKG)-ok:
	mkdir -p $(PKG)
	virtualenv pkg-env $(QUIET)
	pkg-env/bin/pip install --upgrade pip setuptools wheel $(QUIET)
	pkg-env/bin/pip install --no-use-wheel --download $(PKG) pip setuptools wheel $(QUIET)
	pkg-env/bin/pip wheel --no-index --find-links=$(PKG) --use-wheel --wheel-dir=$(PKG) pip setuptools wheel $(QUIET)
	rm -rf pkg-env
	touch $(PKG)-ok
	
download: env/.pkg-whl

clean:
	@rm -rf env
	@find . -name '*.pyc' -delete

really-clean: clean
	@rm -rf $(PKG)

continuous-%:
	inotifywait -r . -q -m -e CLOSE_WRITE | grep --line-buffered '^.*\.py$$' | while read line; do clear; date; echo $$line; echo; make $*; done
