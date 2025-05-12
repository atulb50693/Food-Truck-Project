# Pipeline

This folder should contain all code and resources required for the pipeline.

## Resources and Documentation

The pipeline uses the following libraries which can be installed via the `requirements.txt` file by using `pip3 install -r requirements.txt` in a `.venv`:

1. [pandas](https://pandas.pydata.org/docs/index.html)

2. [python-dotenv](https://pypi.org/project/python-dotenv/)

3. [pymysql](https://pymysql.readthedocs.io/en/latest/)

4. [boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html)

5. [logging](https://docs.python.org/3/library/logging.html)

All documentation for the libraries listed above can be accessed by clicking on the library of interest.

## Files Explained

This folder contains all the files required to set up the pipeline for the MySQL database in the cloud.

* `pipeline.py`  
    - A python script that extracts the truck data .parquet files from an S3 bucket, cleans and then uploads all the data to the MySQL database
    - Command-line options exist where running `python pipeline.py --help` will provide a list of all possible arguments available
    - Output is logged to `/logs/message_logs.txt`, when the `-l` flag is enabled

* `extract.py`  
 A python script that finds the truck data from the S3 bucket and downloads the relevant files

* `transform.py`  
 A python script that formats and cleans the truck data before writing to a .csv file

* `load.py`  
 A python script that test loads a couple of rows of the cleaned data to the MySQL database

* `/data-files`
 A directory that contains all the downloaded data files and the final cleaned version produced by the `transform.py` script

* `/logs`
 A directory that contains all the logging messages outputted when running the pipeline with the `-l` flag enabled

* `/terraform`
 A directory that contains all files required to set up an ECS task resource for the deployment of the pipeline on AWS

* `.env`  
 Contains all the environment variables required for most of the files in the `/pipeline/` directory.


## Requirements

A `.env` and `terraform.tfvars` file must be created within this directory and contain the variables:

```
aws_secret_access_key=<your_aws_secret_access_key>
aws_access_key_id=<your_aws_access_key_id>
DB_HOST=<your_database_address> 
DB_NAME=<your_database_name>
DB_USERNAME=<your_database_username>
DB_PASSWORD=<your_database_password>
DB_PORT=3306
```


## Get started

To run the pipeline, the steps are as follows:

1. Set up a virtual environment for the repository and install the necessary packages in `./pipeline/` by running the command `pip3 install -r requirements.txt`

2. Set up a new `.env` file in the `./pipeline/`, containing all the variables listed under **Files Explained**.

3. Run `python pipeline.py -l` to start the pipeline script. 



