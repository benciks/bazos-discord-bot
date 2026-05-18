.PHONY: install run debug clean

install:
	python3 -m pip install -r requirements.txt

run:
	python3 -m src.main

debug:
	DEBUG=1 python3 -m src.main

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
