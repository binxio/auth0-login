include Makefile.mk
NAME=auth0-login

autopep:
	autopep8 --experimental --in-place --max-line-length 132 $(shell find auth0_login -name \*.py)
