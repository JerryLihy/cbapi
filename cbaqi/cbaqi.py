import requests
import numpy as np
import pandas as pd
import multiprocessing
import json
import logging
import os.path
import time
import threading
logging.basicConfig(level=logging.INFO)

# build logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)
# build handler
log_time = time.strftime('%Y%m%d', time.localtime(time.time()))
log_path = os.path.dirname(os.getcwd()) + '\cbapi\Logs\\'
log_name = log_path + log_time + '.log'
logfile = log_name
fh = logging.FileHandler(logfile, 'w')
fh.setLevel(logging.DEBUG)
# define the format for the logger
formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
fh.setFormatter(formatter)
logger.addHandler(fh)

def build_query_content_ppl(name: str = None, query: str = None, updated_since: int = None, page: str = None, locations: str = None, socials: str = None, types: str = None) -> dict:
    '''
    build the dict which contains the content that we want to query for people
    
    input type and content, according to the crunchbase api:
    --- name(string): optional, A full-text query of name only
    --- query(string): optional, A full-text query of name, title, and company
    --- updated_since(number): optional, When provided, restricts the result set to People where updated_at >= the passed value
    --- page(string): optional, the 1-indexed page number to retrieve
    --- locations(string): optional, Filter by location names (comma separated, AND'd together) e.g. locations=California,San Francisco
    --- socials(string): optional, Filter by social media identity (comma separated, AND'd together) e.g. socials=ronconway
    --- types(string): optional, Filter by type (currently, either this is empty, or is simply "investor")
    
    return type: dictionary which contain the information we will use in the searching for people
    '''
    query_ppl = {
        'name': name,
        'query': query,
        'updated_since': updated_since,
        'page': page,
        'locations': locations,
        'socials': socials,
        'types': types
    }
    
    return query_ppl

def build_query_content_org(name: str = None, query: str = None, updated_since: int = None, page: str = None, locations: str = None, domain_name: str = None, organization_types: str = None) -> dict:
    '''
    build the dict which contains the content that we want to query for organization
    
    input type and content, according to the crunchbase api:
    --- name(string): optional, A full-text query of name only
    --- query(string): optional, A full-text query of name, title, and company
    --- updated_since(number): optional, When provided, restricts the result set to People where updated_at >= the passed value
    --- page(string): optional, the 1-indexed page number to retrieve
    --- locations(string): optional, Filter by location names (comma separated, AND'd together) e.g. locations=California,San Francisco
    --- domain_name(string): optional, Text search of an Organization's domain_name (e.g. www.google.com)
    --- organization_types(string): optional, Filter by one or more types. Multiple types are separated by commas. Available types are "company",
        "investor", "school", and "group". Multiple organization_types are logically AND'd.
    
    return type: dictionary which contain the information we will use in the searching for organizations
    '''
    query_org = {
        'name': name,
        'query': query,
        'updated_since': updated_since,
        'page': page,
        'locations': locations,
        'domain_name': domain_name,
        'organization_types': organization_types
    }
    
    return query_org

def trigger_api(query_info: dict, query_type: str = 'organizations') -> pd.DataFrame:
    '''
    calling crunchbase api to query for the information we want
    
    input type and content:
    --- query_type(string): indicate which type of information we want to query, can be 'people' or 'organizations'
        default set as 'organizations'
    --- query_info(dictionary): information used to search
    
    return type: pandas DataFrame which contains the searching result
    '''
    url = "https://crunchbase-crunchbase-v1.p.rapidapi.com/" 
    url = url + "odm-organizations" if query_type == 'organizations' else url + "odm-people"

    headers = {
    'x-rapidapi-host': "crunchbase-crunchbase-v1.p.rapidapi.com",
    'x-rapidapi-key': "2ce340df43mshf785a3a9047445cp17e61ajsnc9255b2c43d3"
    }

    response = requests.request("GET", url, headers=headers, params = query_info)
    
    return pd.DataFrame(json.loads(response.text))

def trigger_api_thread(total_info: list, query_info: dict, page: str, query_type: str = 'organizations') -> None:
    '''
    calling crunchbase api to query for the information we want
    
    input type and content:
    --- total_info(list): all the result returned by the search
    --- query_type(string): indicate which type of information we want to query, can be 'people' or 'organizations'
        default set as 'organizations'
    --- query_info(dictionary): information used to search
        the page attribution for the dictionary should be given the params
    
    return type: None
    '''
    query_info['page'] = page
    page_search = trigger_api(query_info, query_type)
    page_search_info = pd.DataFrame(list(pd.DataFrame(page_search.loc['items']['data'])['properties']))
    total_info.append(page_search_info)

def get_information(info_type: str = 'organizations', to_csv: bool = False, name: str = None, query: str = None, updated_since: int = None, page: str = None, locations: str = None, socials: str = None, types: str = None, domain_name: str = None, organization_types: str = None) -> pd.DataFrame:
    '''
    get the information for people or organizations
    
    iuput type and content:
    --- info_type(string, 'people' or 'organizations'(default)): indicate which type of information we are searching
    --- to_csv(bool): whether generate a csv file using the search result
    
    --- name(string): optional, A full-text query of name only
    --- query(string): optional, A full-text query of name, title, and company
    --- updated_since(number): optional, When provided, restricts the result set to People where updated_at >= the passed value
    --- page(string): optional, the 1-indexed page number to retrieve
    --- locations(string): optional, Filter by location names (comma separated, AND'd together) e.g. locations=California,San Francisco
    --- socials(string): optional, Filter by social media identity (comma separated, AND'd together) e.g. socials=ronconway
    --- types(string): optional, Filter by type (currently, either this is empty, or is simply "investor")
    --- domain_name(string): optional, Text search of an Organization's domain_name (e.g. www.google.com)
    --- organization_types(string): optional, Filter by one or more types. Multiple types are separated by commas. Available types are "company",
        "investor", "school", and "group". Multiple organization_types are logically AND'd.
    
    return type: pandas.DataFrame: search result
    '''
    # build query string
    if info_type == 'organizations':
        logging.info('searching for organizations')
        query = build_query_content_org(name, query, updated_since, page, locations, domain_name, organization_types)
    elif info_type == 'people':
        logging.info('searching for people')
        query = build_query_content_ppl(name, query, updated_since, page, locations, socials, types)
    else:
        # invalid searching
        logging.debug('invalid search: not people or organizations')
        raise Exception('Invalid searching type! Should be either "people" or "organizations"')
    logging.info('finish building query string')
    
    # searching using the query
    search_res = trigger_api(query, info_type)
    
    if page != None:
        # certain page is given, no need to iterate
        logging.info('search result, page: {}'.format(page))
        
        # if no result is found for the given infomation
        if search_res.loc['paging']['data']['total_items'] == 0:
            logging.info('no result found')
            return pd.DataFrame()
        
        # page too large
        if int(page) > search_res.loc['paging']['data']['number_of_pages']:
            logging.info('page too large, should be smaller or equal to {}'.format(search_res.loc['paging']['data']['number_of_pages']))
            return pd.DataFrame()
        
        return pd.DataFrame(list(pd.DataFrame(search_res.loc['items']['data'])['properties']))

    else:
        # if no result is found for the given infomation
        if search_res.loc['paging']['data']['total_items'] == 0:
            logging.info('no result found')
            return pd.DataFrame()
        
        page_num = search_res.loc['paging']['data']['number_of_pages']
        logging.info('page number of searched result: {}'.format(page_num))
        pages = list(range(page_num))
        pages = [str(i + 1) for i in pages]
        
        # build thread for each page result search
        total_info = []
        
        threads = []
        for page in pages:
            thread = threading.Thread(target = trigger_api_thread, args = (total_info, query, page, info_type))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
    return pd.concat(total_info).reset_index(drop = True)

