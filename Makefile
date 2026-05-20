compile:
	python scripts/check_compile.py

test:
	python scripts/run_unit_tests.py

smoke:
	python scripts/smoke_services.py

e2e:
	python scripts/run_e2e_local.py
