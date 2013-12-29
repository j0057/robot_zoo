QUIET = --quiet

.PHONY: test

test: env/.requirements
	env/bin/python robot_zoo.py

run: env/.requirements
	env/bin/python robot_zoo.py --quiet

debug: env/.requirements
	env/bin/python robot_zoo.py --debug

unittest: env/.requirements
	env/bin/python -m unittest discover

coverage: env/.requirements
	env/bin/coverage erase
	env/bin/coverage run --branch '--omit=env/*,test/*' -m unittest discover || true 
	env/bin/coverage html 
	env/bin/coverage annotate
	env/bin/coverage report | tee coverage.txt

env:
	virtualenv env $(QUIET)

env/.requirements: env requirements.txt
	env/bin/pip install -r requirements.txt -U $(QUIET)
	touch env/.requirements

clean:
	rm -rf env
	find . -name '*.pyc' -delete

continuous-%:
	inotifywait -r . -q -m -e CLOSE_WRITE | grep --line-buffered '^.*\.py$$' | while read line; do clear; date; echo $$line; echo; make $*; done
