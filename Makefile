PYTHON ?= python3

.PHONY: test daily clean

test:
	$(PYTHON) -m pytest -q

daily:
	$(PYTHON) src/generate_tickers.py
	$(PYTHON) src/score_events.py
	$(PYTHON) src/generate_report.py

clean:
	rm -f data/decision_log.csv
