all: test_unit

test_unit:
	export PYTHONPATH=$(PYTHONPATH):./src;python3 -m unittest discover -v -s test/unit
