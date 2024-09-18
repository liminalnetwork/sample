
.SILENT: help
.PHONY: help docs
ENTRIES=`sh -c 'grep -e ".*: " Makefile | grep -v SILENT | grep -v PHONY | sort | sed "s/: .*\#/\\n  /g"'`
CLEANED=`sh -c 'grep -e ".*: " Makefile | grep -v SILENT | grep -v PHONY | sed "s/: .*//g"' | sort | xargs echo`

docs: # make the documentation from scratch
	rm -rf docs
	mkdir docs
	docker build -f Dockerfile.docs -t liminal-doc-client .
	docker run --rm liminal-doc-client \
		cat /app/Sphinx-docs/_build/markdown/doc_client.md > docs/doc_client.md

help: # get this help
	@echo "Try 'make [${CLEANED}]'\n"
	@echo "${ENTRIES}"
