virtualenv_path = .env
python = $(shell which python3.5)

all: clean env

env:
	test -d ${virtualenv_path} || ${python} -m venv ${virtualenv_path}
	(. ${virtualenv_path}/bin/activate && \
        pip install -U setuptools pip wheel && \
	pip install -r requirements.txt)

clean:
	rm -rf ${virtualenv_path} .eggs .pytest-cache smev_int.egg-info

test:
	(. ${virtualenv_path}/bin/activate && \
	python setup.py test)

test_deb:
	(. ${virtualenv_path}/bin/activate && \
	python -m pytest -s tests/)

run:
	(. ${virtualenv_path}/bin/activate && \
	export PYTHONPATH=. && \
	 python smev_int/run.py)
