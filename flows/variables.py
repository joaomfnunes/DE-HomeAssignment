### Variables

#### API Info

api_key = "gh3jLR00nD4jPbv2Z4GUEwkWfGtyQvz96Kc3JeHTDa0="
api_host = "data.usajobs.gov"
api_header = {
    "Host": api_host,
    "Authorization-Key": api_key 
}

results_per_page = 500 ## Number of results per page
keyword = 'data%20engineering' ## Keywords
location = 'Chicago,%20Illinois '
radius = 25
url_root = 'https://data.usajobs.gov/api/Search?' ## Root URL
dateposted = 1 ## Job ads of the last x days

base_query = url_root + "Keyword=" + keyword + "&LocationName=" + location + "&Radius="+ str(radius)  + "&DatePosted="+ str(dateposted)  +  "&ResultsPerPage=" + str(results_per_page) 

# Dataframe Columns names
columns_names = ['job_title','organization_name','organization_department','positionURI','location_city','location_country','remuneration_type','remuneration_min','remuneration_max']

### Database info

server_connection_string = "postgres://postgres:postgres@etl-database:5432/test"

table_exist_query = "select exists(select * from information_schema.tables where table_name='jobads')"

table_creation_query = """
                    CREATE TABLE IF NOT EXISTS jobads(
                    job_title TEXT NULL,
                    organization_name TEXT NULL,
                    organization_department TEXT NULL,
                    positionURI TEXT NULL,
                    location_city TEXT NULL,
                    location_country TEXT NULL,
                    remuneration_type TEXT NULL,
                    remuneration_max numeric NULL,
                    remuneration_min numeric NULL
                    );
                    """