#%%
from datetime import datetime
import time
import tableauserverclient as TSC
from datetime import datetime
import local_tokens
import keyring

#'https://prod-useast-a.online.tableau.com/#/site/ictableaudevqauat/home'
sitename_prod = 'ictableauprod'
token_name = local_tokens.token_name
token_value_prod = local_tokens.token_secret
tableau_auth = TSC.PersonalAccessTokenAuth(token_name, token_value_prod, sitename_prod)
server = TSC.Server('https://prod-useast-a.online.tableau.com/', use_server_version=True)
server.auth.sign_in(tableau_auth)

names = ['CartOrderTrends']
ids_to_refresh = []
req_option = TSC.RequestOptions()
req_option.filter.add(TSC.Filter(TSC.RequestOptions.Field.Name,
                                 TSC.RequestOptions.Operator.In,
                                 names)) ####################searching all data sources for those in 'name' list
with server.auth.sign_in(tableau_auth):
    all_datasources, pagination_item = server.datasources.get(req_option)
    print("\nThere are {} datasources on site: ".format(pagination_item.total_available))
    #print([datasource.name for datasource in all_datasources])
    for d in all_datasources:
        print(d.id, d.name, d.updated_at, d.webpage_url, d.description) #description comes from info button/data source details/About
        ids_to_refresh.append(d.id)


import csv, pendulum, sys
############################LOOP through IDs and kick off refresh for each########################################
with server.auth.sign_in(tableau_auth):
    for x in ids_to_refresh:
        print(f"Started refresh at: {datetime.now().strftime('%H:%M:%S')}")
        results = server.datasources.refresh(x)
        myJobId = results.id
        try:
            jobinfo = server.jobs.get_by_id(myJobId)
            while jobinfo.progress != '100':
                time.sleep(1)
                jobinfo = server.jobs.get_by_id(myJobId)
                print(jobinfo)
            print(f"{jobinfo.name} refresh reached {jobinfo.progress}% Completed at: {datetime.now().strftime('%H:%M:%S')}")

            with open('refresh_log.csv', 'a', newline='') as f:
                writer_obj = csv.writer(f)
                writer_obj.writerow([sys.argv[0], pendulum.now('America/New_York'), pendulum.now(), jobinfo.name, myJobId])
        except: #############################Need to test more on info from bridge refreshes. Error thrown during jobinfo = server.jobs.get_by_id(myJobId)
            print('No job info available. Possible Bridge refresh.')
            time.sleep(5)
            continue