### Modules and Variables

import variables as vb
import math
import requests
import pandas as pd
from prefect import flow,task, get_run_logger
import psycopg2

### Support functions
    
def query_by_pagenumber(query,page_number):

    ### Update url based on the number of runs
    url_query = query + "&Page=" + str(page_number)
    
    return url_query    

def number_of_runs(base_query,api_header):

    ## Determine the number of necessaries runs to extract all data, considering the limit of 500 rows returned per query.
    response = requests.get(base_query, headers = api_header)
    
    if response.status_code == 200:
        data = response.json()
            
        number_of_ads = data['SearchResult']['SearchResultCountAll']
        
        return math.ceil(number_of_ads/500)

    else: 
        return None

def check_if_exists(row,parameter):

    ### Check's if key exists if not returns none
    if parameter in row:
        return row[parameter]
    return None

def create_data_frame():

    ### Creates an empty dataframe with the predefined column names.
    df = pd.DataFrame(columns=vb.columns_names) 

    return df


#################
#               #
#    Extract    #
#               #
#################
@task
def extract(query,api_header,run):

    response = requests.get(query_by_pagenumber(query,run), headers = api_header)
    
    if response.status_code == 200:
        return response.json()
    
    else:
        return None
    
#################
#               #
#   Transform   #
#               #
#################
@task
def transform(data,df):

    ## Transfom query to transform and test data and return the DF
    
    ## Loop on the response to extract data for each search.   
    for ad in data['SearchResult']['SearchResultItems']:

        details = ad['MatchedObjectDescriptor']

        job_title = check_if_exists(details,'PositionTitle')
        organization_name = check_if_exists(details,'OrganizationName')
        organization_department = check_if_exists(details,'DepartmentName')
        positionURI =  check_if_exists(details,'PositionURI')
        location_city = check_if_exists(details['PositionLocation'][0],'CityName')
        location_country = check_if_exists(details['PositionLocation'][0],'CountryCode')
        remuneration_type = check_if_exists(details['PositionRemuneration'][0],'Description')
        remuneration_min = check_if_exists(details['PositionRemuneration'][0],'MinimumRange')
        remuneration_max = check_if_exists(details['PositionRemuneration'][0],'MaximumRange')

        df.loc[len(df)] = [job_title,organization_name,organization_department,positionURI,location_city,location_country,remuneration_type,remuneration_min, remuneration_max]
        
    return df

############
#          #
#   Load   #
#          #
############
@task
def load(df):

    ## Create connection
    connection = psycopg2.connect(vb.server_connection_string)

    cur = connection.cursor()

    ## Check if the table exists:

    cur.execute(vb.table_exist_query)
    table_exists = cur.fetchone()[0] 

    if not table_exists:

        cur.execute(vb.table_creation_query)
        connection.commit()
    
    ## Insert data to DB.

    for i in df.index:
        
        cur.execute("""
                    INSERT INTO jobads(job_title,organization_name,organization_department,positionURI,location_city,location_country,remuneration_type,remuneration_max,remuneration_min) 
                    VALUES ('"""
                        + df.iloc[i, 0] +"','"
                        + df.iloc[i, 1] + "','"
                        + df.iloc[i, 2] + "','"
                        + df.iloc[i, 3] + "','"
                        + df.iloc[i, 4] + "','"
                        + df.iloc[i, 5] + "','"
                        + df.iloc[i, 6] + "',"
                        + df.iloc[i, 7] + ","
                        + df.iloc[i, 8] + ");")
        
        connection.commit()
    
#################
#               #
#      Load     #
#               #
#################

@flow(name="ETL flow")
def main():
    
    logger = get_run_logger()
    logger.info("ETL flow started")

    runs = number_of_runs(vb.base_query,vb.api_header)

    df = create_data_frame()

    if runs > 0:
        
        logger.info("Runs needed: " + str(runs))

        for run in range(1,runs + 1):
            
            logger.info("Extract run: " + str(run))

            data = extract(vb.base_query,vb.api_header,run)
            
            if data is not None:
                
                logger.info("Transform run: " + str(run))
                df = transform(data,df)

        
        logger.info("Extract and Transform completed")
    
    else:
        logger.info("No ads to run")
        return

    print(len(df.index))

    load(df)
    logger.info("Load completed")

if __name__ == "__main__":
    main()