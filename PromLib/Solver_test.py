import requests
import promlib


app_list = ['profile', 'mongodb-rate', 'rate', 'user', 'memcached-profile', 'mongodb-profile', 'search', 'jaeger', 'frontend', 'recommendation', 'geo', 'consul', 'memcached-rate', 'mongodb-reservation'
    , 'mongodb-recommendation', 'memcached-reserve', 'mongodb-user', 'reservation', 'mongodb-geo']
print(len(app_list))
apps_list=[]
for i in app_list:
    apps_list.append('deathstar-metrics:'+i)
print(apps_list)
'''st=""
for i in apps_list:
    st+=str(i)+","
print (st[:len(st)-1])'''
query_apps = []
for app in apps_list:
    query_apps.append('app_list=' + app)

query = "&".join([qapp for qapp in query_apps])

url = 'http://10.16.70.242:8000/get_placement_vp?' + query
response = requests.get(url).json()

print(response['mappings'])

#for k,v in response['mappings'].items():
        #promlib.deploy(k,v,'deathstar-deploy')

#deathstar-metrics:profile,deathstar-metrics:mongodb-rate,deathstar-metrics:rate,deathstar-metrics:user,deathstar-metrics:memcached-profile,deathstar-metrics:mongodb-profile,deathstar-metrics:search,deathstar-metrics:jaeger,deathstar-metrics:frontend,deathstar-metrics:recommendation,deathstar-metrics:geo,deathstar-metrics:consul,deathstar-metrics:memcached-rate,deathstar-metrics:mongodb-reservation,deathstar-metrics:mongodb-recommendation,deathstar-metrics:memcached-reserve,deathstar-metrics:mongodb-user,deathstar-metrics:reservation,deathstar-metrics:mongodb-geo



