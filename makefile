
# Please make sure you have installed black on your system.
# If not run $ pip install black

prepareforcommit:
	python3 -m unittest discover -s tests
	black .