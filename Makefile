include Makefile.mk
NAME=auth0-login

autopep:
	autopep8 --experimental --in-place --max-line-length 132 $(shell find oauth_cli -name \*.py)
