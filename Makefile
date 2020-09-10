VENV=./venv/bin/activate

uml:
	mkdir -P UML
	cd UML; \
	pyreverse -o svg -p jhe_meng_project $$(find ../ -type f \( -name "*.py" ! -path "../venv/*" \))

run:
	source ${VENV}; \
	python3 main.py; \

install:
	python3 -m venv venv; \ 
	source ${VENV}; \
	pip3 install -r requirements.txt; \
