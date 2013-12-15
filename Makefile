QUIET = --quiet

test: env/.requirements
	env/bin/python robot_zoo.py

run: env/.requirements
	env/bin/python robot_zoo.py --quiet

debug: env/.requirements
	env/bin/python robot_zoo.py --debug

unittest: env/.requirements
	env/bin/python -m unittest discover --verbose

coverage: env/.requirements
	env/bin/coverage erase
	env/bin/coverage run --branch -m unittest discover --verbose
	env/bin/coverage report
	env/bin/coverage html 

env:
	virtualenv env $(QUIET)

env/.requirements: env requirements.txt
	env/bin/pip install -r requirements.txt -U $(QUIET)
	touch env/.requirements

clean:
	rm -rf env
	rm -f *.pyc

