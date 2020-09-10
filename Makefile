VENV=./venv/bin/activate
UMLDIR=./img/UML
uml:
	rm -rf ${UMLDIR}
	pyreverse -o svg -p jhe_meng_project $$(find ./ -type f \( -name "*.py" ! -path "./venv/*" \))
	mkdir -p ${UMLDIR}
	mv classes*.svg ${UMLDIR}
	mv packages*.svg ${UMLDIR}

run:
	source ${VENV}; \
	python3 main.py; \

install:
	pip3 install -r requirements.txt; \
