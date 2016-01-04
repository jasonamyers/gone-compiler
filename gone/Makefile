# Makefile for creating a shared-library version of the Gone runtime.
# This is used if you're going to run Gone programs as a JIT. 
# See the file gone/run.py

osx::
	gcc -bundle -undefined dynamic_lookup gonert.c -o gonert.so

linux::
	gcc -shared gonert.c -o gonert.so
