include Makefile.mk
NAME=oauth-cli

autopep:
	autopep8 --experimental --in-place --max-line-length 132 $(shell find oauth_cli -name \*.py)
