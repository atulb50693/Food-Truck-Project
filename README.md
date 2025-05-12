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

This folder contains all the files required to set up the pipeline for the museum database in the cloud.

* `schema.sql`  
 Contains the database structure and initial data to set up the database with

* `connect.sh`  
 A bash file to connect to the remote RDS database 

* `setup_db.sh`  
 A bash file to run the `schema.sql` file on the remote RDS database to return it to a clean slate 

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

* `.env`  
 Contains all the environment variables required for most of the files in the `/pipeline/` directory, which should contain a:
    - `aws_secret_access_key`
    - `aws_access_key_id`
    - `DB_NAME` - database name
    - `DB_USER` - username for the database
    - `DB_PASSWORD` - password for the database
    - `DB_PORT` - port that the database accepts connections from
    - `DB_HOST` - endpoint of where the database is hosted (if local, this value is localhost)

## Get started

To start with setting up the pipeline, the steps are as follows:

1. Set up a virtual environment for the repository and install the necessary packages in `./pipeline/` by running the command `pip3 install -r requirements.txt`

2. Set up a new `.env` file in the `./pipeline/`, containing all the variables listed under **Files Explained**.

3. Run `python pipeline.py -l` to start the pipeline script. 


## Challenge 1, Task 6 - Recommendations

1. Truck of id 6 is doing really well in terms of count of transactions so looking into what locations they are focusing on to get those results and possibly deploying more trucks that align with that to raise more profits

2. Truck of id 3 is doing above average in terms of transaction value and this might be linked to their menu so identifying what items can be sold with high prices (the menu they are currently using) can improve profits for T3

3. Slightly more people use cash over card so having the ability to take transactions in both ways is necessary for all trucks to help prevent any missed sales.

