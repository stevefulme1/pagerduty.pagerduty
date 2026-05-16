NAMESPACE = pagerduty
COLLECTION = pagerduty

.PHONY: lint test sanity unit integration build publish clean

lint:
	yamllint -c .yamllint .
	flake8 plugins/ --max-line-length=120 --ignore=E402,W503
	ansible-lint --strict

sanity:
	ansible-test sanity --python 3.12 --color yes -v

unit:
	pytest tests/unit/ -v --tb=short

integration:
	ansible-test integration --python 3.12 --color yes -v --allow-unsupported

test: lint sanity unit

build: clean
	ansible-galaxy collection build --force

publish: build
	ansible-galaxy collection publish $(NAMESPACE)-$(COLLECTION)-*.tar.gz

clean:
	rm -f $(NAMESPACE)-$(COLLECTION)-*.tar.gz
	rm -rf tests/output/
