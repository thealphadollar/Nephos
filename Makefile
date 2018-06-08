clean: ; sudo rm -r ~/Nephos

# Commands beyond this concern Travis CI and should
# only be launched from within Travis environment

travis_install:    
	pip install pipenv
	pipenv install --dev

travis_test:
	pipenv run py.test --cov=./

travis_after_success:
	# TODO: Add instruction to push to pypi
	pipenv run codecov
