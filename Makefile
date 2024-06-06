.PHONEY: pip

.requirements.txt.run: requirements.txt
	pip install -r "$<"
	touch "$@"

pip: .requirements.txt.run
	# no-op

DOCS.md: typer-test.py *.py
	typer "$^" utils docs --output DOCS.md	