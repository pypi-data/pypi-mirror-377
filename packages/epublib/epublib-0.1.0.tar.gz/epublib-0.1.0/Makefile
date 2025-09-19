venv=. .venv/bin/activate

test:
	@$(venv); pytest

shell:
	@cat "src/.startup.py"
	@$(venv); PYTHONSTARTUP="src/.startup.py" python

cover:
	@$(venv); pytest --cov=epublib --cov-report html
	@xdg-open htmlcov/index.html

docs_generate:
	$(venv); sphinx-apidoc -f src/epublib -o docs/source/
	rm -f docs/source/modules.rst
	sed -i "1s/.*/API/" docs/source/epublib.rst
	sed -i "2s/.*/===/" docs/source/epublib.rst

docs: docs_generate
	$(venv); $(MAKE) -C docs/ html

docs_view:
	xdg-open docs/_build/html/index.html

docs_clean:
	$(MAKE) -C docs/ clean
	rm -f docs/source/epublib*.rst

sigil_plugin:
	$(venv); $(MAKE) -C sigil/

.PHONY: test shell cover docs sigil_plugin docs_view docs_generate
