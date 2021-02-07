# Make a database that collects information about the US patent applications 
#  developed by inventors located into Metropolitan Statistical Areas (MSA)

# Author: Carlo Bottai
# Copyright (c) 2021 - Carlo Bottai
# License: See the LICENSE file.
# Date: 2021-02-05

#################################################

SHELL = bash

.PHONY: all make_patent_database make_citation_database make_readme

#################################################

DATA_DIR = data

DATA_DIR_RAW = $(DATA_DIR)/raw
DATA_DIR_INTM = $(DATA_DIR)/interim
DATA_DIR_PROC = $(DATA_DIR)/processed

DATA_DIR_USPTO = $(DATA_DIR_RAW)/patentsview
DATA_DIR_SHP = $(DATA_DIR_RAW)/cartography

SCRIPT_DIR = src

DOCS_DIR = docs

#################################################

USPTO_URL = https://s3.amazonaws.com/data.patentsview.org/20200929/download
USPTO_FILES = patent.tsv.zip application.tsv.zip patent_inventor.tsv.zip location.tsv.zip uspatentcitation.tsv.zip
USPTO_TARGETS := $(foreach F,$(USPTO_FILES),$(DATA_DIR_USPTO)/$F)

SHP_URL = https://www2.census.gov/geo/tiger/GENZ2018/shp
SHP_FILES = cb_2018_us_cbsa_20m.zip
SHP_TARGETS := $(foreach F,$(SHP_FILES),$(DATA_DIR_SHP)/$F)

$(USPTO_TARGETS): $(DATA_DIR_USPTO)/%: $(SCRIPT_DIR)/download.py
	python $< -i $(USPTO_URL)/$* -o $@

$(SHP_TARGETS): $(DATA_DIR_SHP)/%: $(SCRIPT_DIR)/download.py
	python $< -i $(SHP_URL)/$* -o $@

#################################################

$(DATA_DIR_INTM)/msa_patent.tsv.zip: $(SCRIPT_DIR)/make-patent-database.py $(DATA_DIR_USPTO)/patent.tsv.zip $(DATA_DIR_USPTO)/application.tsv.zip $(DATA_DIR_USPTO)/patent_inventor.tsv.zip $(DATA_DIR_USPTO)/location.tsv.zip $(DATA_DIR_SHP)/cb_2018_us_cbsa_20m.zip
	python $< -I $(filter-out $<,$^) -o $@

$(DATA_DIR_PROC)/msa_patent.tsv.zip: $(SCRIPT_DIR)/make-patent-msa-database.py $(DATA_DIR_INTM)/msa_patent.tsv.zip
	python $< -i $(filter-out $<,$^) -o $@

$(DATA_DIR_PROC)/msa_patent_inventor.tsv.zip: $(SCRIPT_DIR)/make-patent-inventor-database.py $(DATA_DIR_INTM)/msa_patent.tsv.zip
	python $< -i $(filter-out $<,$^) -o $@

$(DATA_DIR_PROC)/msa_patent_info.tsv.zip: $(SCRIPT_DIR)/make-patent-info-database.py $(DATA_DIR_INTM)/msa_patent.tsv.zip
	python $< -i $(filter-out $<,$^) -o $@

$(DATA_DIR_PROC)/msa_label.tsv.zip: $(SCRIPT_DIR)/make-msa-label-database.py $(DATA_DIR_INTM)/msa_patent.tsv.zip
	python $< -i $(filter-out $<,$^) -o $@

$(DATA_DIR_PROC)/msa_citation.tsv.zip: $(SCRIPT_DIR)/make-citation-database.py $(DATA_DIR_PROC)/msa_patent.tsv.zip $(DATA_DIR_USPTO)/uspatentcitation.tsv.zip
	python $< -I $(filter-out $<,$^) -o $@

$(DOCS_DIR)/README_tables.md: $(SCRIPT_DIR)/make-readme-tables.py $(DATA_DIR_PROC)/msa_patent.tsv.zip $(DATA_DIR_PROC)/msa_patent_inventor.tsv.zip $(DATA_DIR_PROC)/msa_patent_info.tsv.zip $(DATA_DIR_PROC)/msa_label.tsv.zip $(DATA_DIR_PROC)/msa_citation.tsv.zip
	python $< -I $(filter-out $<,$^) -o $@
README.md: $(DOCS_DIR)/README_base.md $(DOCS_DIR)/README_tables.md
	awk '{print}' $^ > $@

#################################################

#- all                       Reproduce all the steps of the project
all: make_patent_database make_citation_database make_readme

#- download_data             Download needed raw data
download_data: $(USPTO_TARGETS) $(SHP_TARGETS)

#- make_patent_database      Make base tables
make_patent_database: $(DATA_DIR_PROC)/msa_patent.tsv.zip $(DATA_DIR_PROC)/msa_patent_inventor.tsv.zip $(DATA_DIR_PROC)/msa_patent_info.tsv.zip $(DATA_DIR_PROC)/msa_label.tsv.zip

#- make_citation_database    Make patent-citation table
make_citation_database: $(DATA_DIR_PROC)/msa_citation.tsv.zip

#- make_readme               Make README file
make_readme: README.md

#################################################

help : Makefile
	@sed -n 's/^#- //p' $<

#- dag_picture               Depict the Dependency Acyclic Graph (DAG) of the 
#-                           Makefile (output: makefile.png)
dag_picture:
	make -nd all | makefile2graph/make2graph | dot -Tpng -o makefile.png
