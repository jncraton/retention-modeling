all: results/all/expected_graduation_rate_by_year.tsv presentations/latest.html

data/data.csv: download_ssrs.py
	@python3 download_ssrs.py /Student+Life/Retention+Analysis=data/data.csv /Housing+\(managed\)/tables/people=data/people.csv

clean_data.tsv: data/data.csv
	@python3 clean_data.py
	
results/all/expected_graduation_rate_by_year.tsv: results.py clean_data.tsv astin97.py
	@python3 results.py

presentations/latest.html: presentations/template.md
	@cd presentations && pandoc -s -i -t revealjs --variable theme="moon" template.md -o latest.html

presentations/report.pdf: presentations/report.md
	pandoc -N -fmarkdown-implicit_figures --toc presentations/report.md -o presentations/report.pdf

clean:
	@rm -rf results/*
	@rm -rf data/*
	@rm presentations/latest.html