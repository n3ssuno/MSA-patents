# Patenting in the US Metropolitan Areas
This repository builds a database that collects information about the US patent applications developed by inventors located in Metropolitan Statistical Areas (MSA).

## Reproducibility
To reproduce the database tables, please follow these steps:
1. Install [Git](https://git-scm.com/)
2. Install [Miniconda](https://docs.conda.io/en/latest/miniconda.html)
3. Install [GNU Make](https://www.gnu.org/software/make/)
4. From a terminal, clone this repository with ``git clone https://github.com/n3ssuno/MSA-patents.git``
5. Move to the newly created subfolder with ``cd MSA-patents``
6. Create a Conda environment with ``conda env create -f environment.yml``
7. Activate the newly created Conda environment with ``conda activate MSA-patents``
8. Run ``make``

Notes:
1. The previous steps assume that you are working in a GNU/Linux environment (if you work in a MS Windows environment, consider using [WSL](https://docs.microsoft.com/en-us/windows/wsl/)). It is not excluded that you can run the scripts also in other OS, but it has never been tested.
2. GNU Make is not mandatory, but it helps to simplify the procedure. Alternatively, you can go step by step by yourself following the Makefile provided (the ``makefile.png`` image can help).
3. The ``make2graph`` rule in the Makefile depicts the Makefile as a PNG picture. To use this rule, you must (1) clone the https://github.com/lindenb/makefile2graph repository into the present folder; (2) compile it with ``make``; (3) install [Graphviz](http://www.graphviz.org/) into your OS.

## Built database
You can find a built version of the database [here](https://surfdrive.surf.nl/files/index.php/s/BgV5tAyhEjGFojk).

Please, cite the database if you use it for a scientific publication or in any other kind of work.

## License and Contributors

### Code
The code to reproduce the database is written and maintained by [Carlo Bottai](https://github.com/n3ssuno) and it is licensed under a *MIT License* (see [LICENSE](LICENSE)).

Feel free to open a new [Issue](https://github.com/n3ssuno/MSA-patents/issues) on GitHub.<br>
If you find a bug, please use the ``Bug report`` template.<br>
If you would like to see a new feature implemented, please use the ``Feature request`` template.<br>
Otherwise, please fork the repository, modify the code as you think is the best, and open a pull request to integrate the changes into the main repository.

### Database
The database is released under a [*CC-BY 4.0 License*](https://creativecommons.org/licenses/by/4.0/).

The raw data, elaborted by the scripts contained in this repository, are from [PatentsView](https://www.patentsview.org/) and [US Census](https://www.census.gov/). You can find further references to the raw files used in the Makefile file.

## Folders structure
```
MSA-patents
    |- data
    |   |- raw           <- The original, immutable data dump
    |   |- interim       <- Intermediate data that has been transformed
    |   └─ processed     <- The final, canonical data sets for modeling
    |
    |- src               <- Source code for use in this project
    |   |- __init__.py   <- Makes src a Python module
    |
    |- docs              <- Files to be combined into the main README file
    |
    |- Makefile
    |
    |- README.md         <- The top-level README for developers using this project
    |- CONTRIBUTORS.md
    |- LICENSE
    └─ environment.yml   <- Conda environment
```

## Tables structure
The following tables describe the database files, showing the first five rows of each.

### msa_patent
|   patent_id |   cbsa_id |   cbsa_share |
|-------------|-----------|--------------|
|     3930273 |     41180 |            1 |
|     3930274 |     31080 |            1 |
|     3930275 |     35620 |            1 |
|     3930277 |     33460 |            1 |
|     3930278 |     17460 |            1 |


### msa_patent_inventor
|   patent_id | inventor_id   |   inventor_share |
|-------------|---------------|------------------|
|    10000000 | 5073021-1     |              1   |
|    10000007 | 9473749-3     |              0.2 |
|    10000007 | 9862137-3     |              0.2 |
|    10000007 | 9862137-4     |              0.2 |
|    10000007 | 9862137-5     |              0.2 |


### msa_patent_info
|   patent_id | grant_date   | appln_date   |   num_claims |
|-------------|--------------|--------------|--------------|
|    10000000 | 2018-06-19   | 2015-03-10   |           20 |
|    10000007 | 2018-06-19   | 2016-06-10   |           24 |
|    10000008 | 2018-06-19   | 2014-12-01   |           11 |
|    10000009 | 2018-06-19   | 2015-02-05   |           21 |
|    10000010 | 2018-06-19   | 2016-06-29   |           20 |


### msa_label
|   cbsa_id |   csa_id | cbsa_label                            |
|-----------|----------|---------------------------------------|
|     31080 |      348 | Los Angeles-Long Beach-Anaheim, CA    |
|     33340 |      376 | Milwaukee-Waukesha-West Allis, WI     |
|     35620 |      408 | New York-Newark-Jersey City, NY-NJ-PA |
|     41860 |      488 | San Francisco-Oakland-Hayward, CA     |
|     40380 |      464 | Rochester, NY                         |


### msa_citation
|   forward_citation_id |   patent_id |
|-----------------------|-------------|
|               5354551 |     4875247 |
|               8683318 |     6642945 |
|               9199394 |     5242647 |
|               7051923 |     6179710 |
|               7905900 |     5334216 |


