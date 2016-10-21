all: data.csv results/all/expected_graduation_rate_by_year.tsv presentations/latest.html

data.csv: get_data.py
	@python3 get_data.py

clean_data.tsv: data.csv
	@python3 clean_data.py
	
results/all/expected_graduation_rate_by_year.tsv: results.py clean_data.tsv astin97.py
	@python3 results.py

presentations/latest.html: presentations/template.md
	@cd presentations && pandoc -s -i -t revealjs --variable theme="moon" template.md -o latest.html

presentations/report.pdf: presentations/report.md
	pandoc -N -fmarkdown-implicit_figures --toc presentations/report.md -o presentations/report.pdf

clean:
	@rm -rf results/*
	@rm data.csv clean_data.tsv people.csv
	@rm presentations/latest.html