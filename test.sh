#!/bin/bash
set +x
set +e

export PYTHONPATH=.
source ./.env
(cd app; py.test -q --cov=app --cov=extentions --cov-report term-missing -x tests -v) && \
(cd app; pylint --jobs=4 api tests) && \
flake8 --config=setup.cfg app
