.PHONEY: pip

.venv:
	python3.11 -m venv --system-site-packages .venv

.requirements.txt.run: requirements-dev.txt requirements.txt
	pip install -r "$<"
	touch "$@"

pip: .venv .typer .click .requirements.txt.run
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


## DATA

NY_TAXI_DATA ?= ./data
NT_TAXI_HTTP=https://ia902202.us.archive.org/28/items/nycTaxiTripData2013


# Targets for fetching and de-/re-compressing
$(NY_TAXI_DATA)/trip_%.7z:
	curl -o "$@" "$(NT_TAXI_HTTP)/$(@F)"

$(NY_TAXI_DATA)/trip/%.csv: $(NY_TAXI_DATA)/trip_%.7z
	set -euxo pipefail; \
	first=1; \
	for F in `7zz l "$<" | grep -o -E 'trip_[a-z]+_[0-9]+\.csv'`; \
	do \
		if [ $$first = 1 ]; \
		then \
			7zz e -so "$<" "$$F" > "$@"; \
			first=0; \
		else \
			7zz e -so "$<" "$$F" | tail -n+2 >> "$@"; \
		fi; \
	done


$(NY_TAXI_DATA)/trip/%: $(NY_TAXI_DATA)/trip_%.7z
	mkdir -p "$@"
	for F in `7z l "$<" | grep -o -E 'trip_[a-z]+_[0-9]+\.csv'`; \
	do \
		7z e -so "$<" "$$F" | gzip -c > "$@/$$F.gz" & \
	done; \
	wait
	chmod a+r "$@/*"
	chmod a+xr "$@" "$(NY_TAXI_DATA)/trip/"
	chmod a+rwx "$(NY_TAXI_DATA)"
	du -sch "$@/*.gz"


$(NY_TAXI_DATA)/trip/%.csv: $(NY_TAXI_DATA)/trip/%/*.csv.gz
	{ gzip -dc "$<" | head -n1 && for F in $^; do gzip -dc "$$F" | tail -n+2; done; } > "$@"


$(NY_TAXI_DATA)/trip/%.zst: $(NY_TAXI_DATA)/trip/%.csv
	time zstd -T0 -9 -k "$<" -o "$@"


data: $(NY_TAXI_DATA)/trip/data.csv # $(NY_TAXI_DATA)/fare - we don't currently use the fare data
	# op-op

