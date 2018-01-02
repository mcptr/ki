test-pep8:
	pycodestyle .

test: test-pep8
	PYTHONPATH=. nosetests -sv tests --nologcapture

clean:
	find . -name __pycache__ | xargs rm -vrf
	find . -name '*~' | xargs rm -vrf
