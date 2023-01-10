import requests

apps_list = ['app1', 'app2', 'app3']


query_apps = []
for app in apps_list:
    query_apps.append('app_list='+app)

URL = 'http://localhost:8000/'

query = "&".join([qapp for qapp in query_apps])

url = URL+'get_placement_vp_static?'+query
response = requests.get(url).json()
print("VPSOLV=",response)

url = URL+'/get_placement_rl_static?'+query
response = requests.get(url).json()
print("RL=",response)
