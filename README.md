# Food Truck Project: Financial Analytics Dashboard

## Table of Contents
- [Overview](#-overview)
- [Contents](#️-contents)
- [System Architecture](#system-architecture-diagram)


## 📖 Overview
At Sigma Labs, I developed a data pipeline and analytics dashboard as a challenge project for a catering company with a fleet of food trucks in Lichfield. Previously, they uploaded transaction data monthly to S3, which delayed insights. 

To solve this, I built an automated ETL pipeline that filtered and cleaned Parquet files from S3 using Python and Pandas, then uploaded the data to a MySQL database on AWS. I utilised the STAR schema for efficient querying and built a Streamlit dashboard to visualize key metrics. The dashboard was containerized with Docker and deployed using AWS Fargate for easy access by non-technical staff.


## 🗂️ Contents
Each directory has their own README file containing a deep overview of the purpose of the directory and how to run it for yourself. These directories are provided in order of use to implement this project:

- `database`: schema setup and data model

- `pipeline`: ETL pipeline including data scraping, transformation, and loading

- `dashboard`: frontend interface for users (using Streamlit)

- `email`: scripts for creating and automating email updates 

- `bash-scripts`: scripts for automated code quality and testing checks (using CI).

- `utilities`: scripts that automate common tasks e.g: clearing the database.

- `assets`: contains images for the system architecture and the wireframe design of the dashboard.


## 🤖 Automated testing & linting

Within the `.github/workflows` directory, there are two files `pylinter.yml` and `tester.yml`.
These files create jobs using Github Actions on any python scripts within a pull request or commit, which run pylint and pytest to ensure high accuracy and quality in the code provided.


# System Architecture Diagram

<img src="assets/architecture_diagram_food_truck_proj.png" alt="isolated" width="500">