# Food Truck Project: Financial Analytics Dashboard

## Table of Contents
- [Overview](#overview)
- [Contents](#contents)
- [System Architecture](#system-architecture)


## 📖 Overview
At Sigma Labs, I developed a data pipeline and analytics dashboard as a challenge project for a catering company with a fleet of food trucks in Lichfield. Previously, they uploaded transaction data monthly to S3, which delayed insights. 

To solve this, I built an automated ETL pipeline that filtered and cleaned Parquet files from S3 using Python and Pandas, then uploaded the data to a MySQL database on AWS. I utilised the STAR schema for efficient querying and built a Streamlit dashboard to visualize key metrics. The dashboard was containerized with Docker and deployed using AWS Fargate for easy access by non-technical staff.


## 🗂️ Contents
Each directory has their own README file containing a deep overview of the purpose of the directory and how to run it for yourself. These directories are provided in order of use to implement this project:

- `database`: Schema setup and data model

- `pipeline`: ETL pipeline including data scraping, transformation, and loading

- `dashboard`: Frontend interface for users (using Streamlit)

- `email`: Scripts for creating and automating email updates 

- `bash-scripts`: Scripts for automated code quality and testing checks (using CI).

- `utilities`: Scripts that automate common tasks e.g: clearing the database.


## 🤖 Automated testing & linting

Within the `.github/workflows` directory, there are two files `pylinter.yml` and `tester.yml`.
These files create jobs using Github Actions on any python scripts within a pull request or commit, which run pylint and pytest to ensure high accuracy and quality in the code provided.


# Architecture Diagram

![Architecture Diagram](assets/architecture_diagram_food_truck_proj.png)