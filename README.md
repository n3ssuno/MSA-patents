# Patenting in the US Metropolitan Areas
This repository builds a database that collects information about the US patent applications developed by inventors located in Metropolitan Statistical Areas (MSA).

The data are aggregated at the Core Based Statistical Area (CBSA) level, based on the localization (latitude and longitude) of each inventor, as provided by PatentsView. The boundaries of each CBSA are constant over time and based on the data provided by the US Census (version 2019). To each inventor, within a patent, is assigned a fraction of the patent proportional to the size of the "inventing team". As well, a fractional count of the inventors of each patent, located in a given metropolitan area, is provided.

For each patent (partly) invented in a metropolitan area, the forward citations received by the patent are provided.

Of each of these patents (and citing patents), the application and publication dates, the main USPC patent class, the number of claims, and the number of citations received (*forward citations*) by other US patents (in the 5 or 10 years from the granting date) are reported.<br>
To account for possible time- and technology-related shocks, the average number of claims and forward citations of patents belonging to the same USPC class and applied (or granted) in the same year of the focal patent are provided.<br>
About this last point, note that, for patents with no USPC class, the averages reported are computed considering any patent applied (or granted) in the same year of the focal patent.

Moreover, of each of these patents (and citing patents) the CPC *subclass* (4 digits class) are reported.<br>
About the CPC classes, some notes need to be taken into consideration:
* The *cpc_class_count* column counts the number of *main groups* (7 digits class) of the CPC *subclass* that appear in that patent. E.g., this means that, if a patent is classified into the *main groups* ``A01B1``, ``A01B3``, and ``A01B5``, the table will report, for the given patent, ``A01B`` in the *cpc_class* columns and ``3`` in the *cpc_class_count*.
* The *Y section* and the *2000 series* are not considered in the table.

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
1. To run some of the scripts you need a large amount of RAM memory (about 32GB). Consider using a cloud-based solution.
2. The previous steps assume that you are working in a GNU/Linux environment (if you work in a MS Windows environment, consider using [WSL](https://docs.microsoft.com/en-us/windows/wsl/)). It is not excluded that you can run the scripts also in other OS, but it has never been tested.
3. GNU Make is not mandatory, but it helps to simplify the procedure. Alternatively, you can go step by step by yourself following the Makefile provided (the ``makefile.png`` image can help).
4. The ``make2graph`` rule in the Makefile depicts the Makefile as a PNG picture. To use this rule, you must (1) clone the https://github.com/lindenb/makefile2graph repository into the present folder; (2) compile it with ``make``; (3) install [Graphviz](http://www.graphviz.org/) into your OS.

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

The raw data, elaborted by the scripts contained in this repository, are from [PatentsView](https://www.patentsview.org/), the [US Census](https://www.census.gov/), and the USPTO's [Patent Examination Research Dataset (PatEx)](https://www.uspto.gov/learning-and-resources/electronic-data-products/patent-examination-research-dataset-public-pair). You can find further references to the raw files used in the Makefile file.

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
|    10000000 | 5073021-1     |         1        |
|    10003756 | 10003756-2    |         0.5      |
|    10003780 | 9495415-4     |         0.2      |
|    10006993 | 5763054-3     |         1        |
|    10007786 | 6067410-1     |         0.333333 |


### msa_patent_info
|   patent_id | grant_date   | appln_date   |   uspc_class |   num_claims |   num_citations_5y |   num_citations_10y |   avg_num_claims_gy |   avg_num_claims_ay |   avg_num_citations_5y_gy |   avg_num_citations_10y_gy |   avg_num_citations_5y_ay |   avg_num_citations_10y_ay |
|-------------|--------------|--------------|--------------|--------------|--------------------|---------------------|---------------------|---------------------|---------------------------|----------------------------|---------------------------|----------------------------|
|     3930325 | 1976-01-06   | 1974-07-24   |          038 |            8 |                  1 |                   1 |                 7.5 |             8       |                       1.5 |                        1.5 |                   1       |                    1       |
|     3931558 | 1976-01-06   | 1974-10-11   |          318 |            6 |                  0 |                   0 |                11   |            13.6     |                       4   |                        7   |                   2.66667 |                    4.66667 |
|     3932360 | 1976-01-13   | 1974-04-22   |          260 |           21 |                  2 |                  14 |                18.5 |             8.95833 |                       7.5 |                       17   |                   2.35    |                    5.15    |
|     3935380 | 1976-01-27   | 1974-12-06   |          178 |            6 |                  7 |                  10 |                 6   |             6       |                       7   |                       10   |                   7       |                   10       |
|     3937995 | 1976-02-10   | 1974-12-05   |          174 |            8 |                  0 |                   0 |                 8   |             8       |                     nan   |                      nan   |                 nan       |                  nan       |

Notes:
* Rename *patent_id* as *forward_citation_id* to merge this table with the *msa_citation* table.
* 7.4% of the *patent_id*s have no *uspc_class* (most of which, very old or very recent patents).


### msa_label
|   csa_id |   cbsa_id | cbsa_label                            |
|----------|-----------|---------------------------------------|
|      348 |     31080 | Los Angeles-Long Beach-Anaheim, CA    |
|      376 |     33340 | Milwaukee-Waukesha, WI                |
|      408 |     35620 | New York-Newark-Jersey City, NY-NJ-PA |
|      488 |     41860 | San Francisco-Oakland-Berkeley, CA    |
|      464 |     40380 | Rochester, NY                         |


### msa_patent_cpc
|   patent_id | cpc_class   |   cpc_class_count |
|-------------|-------------|-------------------|
|     7298491 | G02F        |                 1 |
|     7995656 | H04N        |                 1 |
|    10133297 | H05K        |                 1 |
|     7374447 | H01R        |                 2 |
|     6577620 | H04Q        |                 1 |


### msa_citation
|   forward_citation_id |   patent_id |
|-----------------------|-------------|
|               5354551 |     4875247 |
|               8683318 |     6642945 |
|               9199394 |     5242647 |
|               7051923 |     6179710 |
|               7905900 |     5334216 |


