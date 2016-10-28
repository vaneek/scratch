.PHONY: all
all: sgbase.template ec2base.template

sgbase.template: sgbase.py
	pylint --reports=n sgbase.py
	python sgbase.py >sgbase.template

ec2base.template: ec2base.py
	pylint --reports=n ec2base.py
	python ec2base.py >ec2base.template

install:
	python cc.py sgbase.template scratch-adverum
	python cc.py ec2base.template scratch-adverum

clean:
	rm -f sgbase.template ec2base.template
