.PHONY: all
all: sgbase.template

sgbase.template: sgbase.py
	pylint --reports=n sgbase.py
	python sgbase.py >sgbase.template

install:
	python cc.py sgbase.template scratch-adverum

clean:
	rm -f sgbase.template
