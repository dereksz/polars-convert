.PHONEY: pip

.requirements.txt.run: requirements-dev.txt requirements.txt
	pip install -r "$<"
	touch "$@"

pip: .requirements.txt.run
	# no-op

DOCS.md: typer-test.py *.py
	typer "$^" utils docs --output DOCS.md
