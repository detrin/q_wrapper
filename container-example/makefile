
clonesrc:
	rm -rf q_wrapper/
	git clone https://github.com/detrin/q_wrapper
	chmod -R +rw q_wrapper
	rm -rf q_wrapper/.git

copysrc:
	cp -rf ../q_wrapper/ .
	chmod -R +rw q_wrapper
	rm -rf q_wrapper/.git

format:
	black *.py

clear:
	rm -r transfer
	mkdir transfer