# Home Assignment

## Objective

Using the API from the USA Job directory (www.usajobs.gov), create an ETL to run every day to populate a table with the job ads that match the keyword 'data engineering' and the job seeker based on Chicago with 5 years of experience. 

The proposed solution runs once a day and returns the new job ads on the last 24 hours that match the keyword 'data engineering' and the location 'Chicago, Illinois' and on a 25-mile radius.

## Stack

The proposed solution uses Python, Prefect for orchestration, PostgreSQL as a database and Docker to containerize, as requested. We assume that Python and Docker are installed to run the proposed solution.

## Structure

./docker-compose.yaml - Docker compose file with the docker instructions for all the images used.

./flows - Folder with the flows scripts

./flows/flow.py - Python ETL script

./flows/variables.py - Python file with all the static information used in flow.py.

./flows/requirements.txt - TXT file with all the modules used in the flow.py.

## Instructions

### 1st

Clone this repo

### 2nd

On your terminal and in the root folder, compose all the docker files:

`docker-compose --profile server up -d`

### 3rd

**3.1** 
On your terminal, start a CLI on docker :

`docker-compose run cli`

**3.2** 

Install the Python packages needed

`pip install -r requirements.txt`

**3.3**

Create a Worker

`prefect work-pool create --type process etl-process-pool`

**3.4** 

Create a deployment

`prefect deploy`

- Select the "main" flow name - Location: flow.py
- Select a Name for the deployment - E.g. "etl-flow"
- Select (y) and the first option to define the scheduler for 86400 seconds to run the flow once a day, starting the next day.
- Select the work pool defined in the last step. "elt-process-pool"
- Select (n) not to save the configuration file of this deployment.

**3.5**

Start the worker

`prefect worker start --pool 'etl-process-pool'`

## Testing

To test the script, I recommend changing the **_date posted_** variable to 10 to return the new ads of the last 10 days to ensure that there are job ads that match the requirements.

After making the change stated above, we run the instructions normally and then:

### 1st

Open a new terminal and create a Docker CLI:

`docker-compose run cli`

**1.1**

Install the Python packages needed

`pip install -r requirements.txt`

**1.2**

Launch the Python console

`python`

**1.2.1**

Run the following code to test if there's any entry inside the jobads table:

```
import psycopg2
connection = psycopg2.connect('postgres://postgres:postgres@etl-database:5432/test')
cur = connection.cursor()
cur.execute("select count(*) from jobads")
cur.fetchone()
```