.PHONEY: pip

.requirements.txt.run: requirements-dev.txt requirements.txt
	pip install -r "$<"
	touch "$@"

pip: .typer .click .requirements.txt.run
	# no-op

# Packages that I want to have locally installed

.typer:
	-pip uninstall -y typer
	grep -q -F "$@" .gitignore || echo "$@"/ >> .gitignore
	git clone git@github.com:dereksz/typer.git "$@"
	git -C "$@" remote add upstream git@github.com:tiangolo/typer.git
	pip install -e "$@"

.click:
	-pip uninstall -y click
	grep -q -F "$@" .gitignore || echo "$@"/ >> .gitignore
	git clone git@github.com:dereksz/click.git "$@"
	git -C "$@" remote add upstream git@github.com:pallets/click.git
	pip install -e "$@"

DOCS.md: typer-test.py *.py
	typer "$^" utils docs --output DOCS.md
