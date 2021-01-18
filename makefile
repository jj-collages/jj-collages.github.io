all:
	python build.py
	cp -r static _build/

deploy: all
	rsync -avP _build/ panda:/home/drop/jj
