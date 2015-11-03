FLAKE8 := $(shell which flake8)

analysis:
	# Debian version is badly packaged, make sure we are using Python 3.
	/usr/bin/env python3 $(FLAKE8) --max-line-length=132 cromer .
	pylint --report=n --disable=line-too-long --disable=missing-docstring --disable=locally-disabled cromer
