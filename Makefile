VENV=./venv/bin/activate
UMLDIR=./img/UML
uml:	
	rm -rf ${UMLDIR}
	pyreverse -o png -p jhe_meng_project $$(find ./ -type f \( -name "*.py" ! -path "./venv/*" \))
	mkdir -p ${UMLDIR}
	mv classes*.png ${UMLDIR}
	mv packages*.png ${UMLDIR}

install:
	pip3 install --user -r requirements.txt; \
	sudo install main.py /usr/bin/opp4sar

badges:
	bash helpers/lines.sh

test:
	source ${VENV}; \
	pytest test.py; \

clean:
	fd -td -I -E venv __pycache__ -X rm -rf
