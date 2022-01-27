all: test_unit release

release:
	cp -R ./src/* ~/$(CAIOS_VERSION)/
	
test_unit:
	caios test run unit
