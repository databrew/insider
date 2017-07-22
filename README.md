# <span style="color:#0d63c4">INSIDER-facebook: developer's guide</span>

<span style="color:grey">Insider's automated data collection, aggregation and analysis platform</span>


(_built with love by [databrew](http://databrew.cc)_)

## Summary

This is a _proof of concept_ (POC) of a collaboration between Insider and databrew. The purpose of this collaboration is to automate the collection and analysis of data from the social networks on which Insider is active. For the purpose of this POC, we use facebook, though the concepts and methods are largely generalizable.

## "The product"

### Overview

The "product" of this POC is three-fold:  

  - Python code for the automated retrieval, standardization, aggregation and storage of data from Insider's 16 facebook pages through facebook's Graph API  
  - A basic "dashboard" (and related R code) for the visualization and automated analysis of the retrieved data  
  - Extendible automation code for the dissemination via email or daily update of the above two sub-products
  
### Details

The layout of the software product is below:

```
├── credentials
│   ├── credentials.yaml
│   └── fb_oauth
├── data
│   ├── backups
│   │   ├── 2017-07-22 10:35:43.csv [example]
│   │   ├── 2017-07-22 13:35:08.csv [example]
│   │   └── 2017-07-22 13:56:56.csv
│   └── historical.csv
├── lib
│   ├── get_data.py
├── README.md
├── reports
│   ├── dashboard.Rmd
│   ├── helpers.R
└── requirements.txt
```

If you've cloned this directory, the `data`, `data/backups`, and `credentials` directories do not exist (they are "git-ignored"). Accordingly, you'll need to create these 3 directories empty. Having created `credentials`, you should populate it with a `credentials.yaml` containing the following values (intentionally anonymized):

```
app_id: "123" 
app_secret: "a1b2c3d4" 
api_version: "v2.9" 
app_token: "z9x8y7"
```

If you do not have these values (but _should_ have them), email joe@databrew.cc.

## Dependencies

This product relies entirely on open-source software (an intentional decision so as to grant Insider full "ownership" and use regardless of databrew's involvement). It expects a *nix-like system (built on Ubuntu 16.04 LTS), and requires Python (2.7) and R (3.4.1). Specific module and library dependencies are self-evident in the code base.

### Python

All python dependencies are readily available. For both the purposes of ease and correct versioning, it is recommended to install python modules within a virtual environment using the following:

```
pip install -r requirements.txt
```

### R

Most of the R dependencies for this project are available on CRAN. The exception to this is the open-source `databrew` package, which can be installed via the following:

```
devtools::install_github('databrew/databrew')
```




## Use

The entire process can be run by simply "knitting" the `reports/dashboard.Rmd`, which will generate an `.html` file (the "dashboard"). The `.Rmd` will call and initiate the python script which handles data retrieval. The first run of this process is expected to be slow (as it has to retrieve data for 16 pages going back to 2015); therafter, it only retrieves the most recent data, and adds that to a flat file saved at `data/historical.csv`. 

