VENV=./venv/bin/activate
UMLDIR=./img/UML
uml:	
	rm -rf ${UMLDIR}
	pyreverse -o png -p jhe_meng_project $$(find ./ -type f \( -name "*.py" ! -path "./venv/*" \))
	mkdir -p ${UMLDIR}
	mv classes*.png ${UMLDIR}
	mv packages*.png ${UMLDIR}

run:
	source ${VENV}; \
	python3 main.py; \

install:
	pip3 install -r requirements.txt; \

badges:
	bash helpers/lines.sh

test:
	source ${VENV}; \
	pytest test.py; \

clean:
	fd -td -I -E venv __pycache__ -X rm -rf
