
.SILENT: help
.PHONY: help docs
ENTRIES=`sh -c 'grep -e ".*: " Makefile | grep -v SILENT | grep -v PHONY | sort | sed "s/: .*\#/\\n  /g"'`
CLEANED=`sh -c 'grep -e ".*: " Makefile | grep -v SILENT | grep -v PHONY | sed "s/: .*//g"' | sort | xargs echo`

docs-container.build: pydoc_md.py Dockerfile.docs # build the docs container with Python 3.14 and pydoc_md.py
	docker build -f Dockerfile.docs -t liminal-doc-client .
	@touch docs-container.build

docs.build: docs-container.build src/*.py # make the documentation with the docs container
	rm -f src.tar
	tar -cf src.tar src
	cat src.tar | docker run -i --rm liminal-doc-client python3 pydoc_md.py --stdin --no-module-parent --skip-object > docs/docs.tar
	rm -f docs/*.md
	cd docs && cat docs.tar | tar -x --overwrite
	rm docs/docs.tar src.tar
	@touch docs.build

docs: docs.build # entry point for making docs
	@echo "done"

help: # get this help
	@echo "Try 'make [${CLEANED}]'\n"
	@echo "${ENTRIES}"
