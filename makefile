
# Please make sure you have installed black on your system.
# If not run $ pip install black

prepareforcommit:
	python -m unittest discover
	black .