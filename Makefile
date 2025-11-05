
.SILENT: help
.PHONY: help docs
ENTRIES=`sh -c 'grep -e ".*: " Makefile | grep -v SILENT | grep -v PHONY | sort | sed "s/: .*\#/\\n  /g"'`
CLEANED=`sh -c 'grep -e ".*: " Makefile | grep -v SILENT | grep -v PHONY | sed "s/: .*//g"' | sort | xargs echo`

docs: # make the documentation from scratch
	rm -f docs/*
	docker build -f Dockerfile.docs -t liminal-doc-client .
	docker run --rm liminal-doc-client bash -c 'python3 pydoc_md.py *.md' > docs/docs.tar
	cd docs && cat docs.tar | tar -x --overwrite
	rm docs/docs.tar

help: # get this help
	@echo "Try 'make [${CLEANED}]'\n"
	@echo "${ENTRIES}"
