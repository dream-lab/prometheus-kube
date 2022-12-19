import promlib
import all_list

#list all machines and apps
print("\nAll available machines:\n")
print(all_list.get_all_machine_id())

print("\nAll available apps:\n")
print(all_list.get_all_app_list())

#get usages
hosts=["10.24.24.131:9100","10.24.24.132:9100","10.24.24.133:9100","10.24.24.134:9100"] #host-ip:port

app_list=["deathstar-metrics:consul","deathstar-metrics:frontend"] #pod-namespace:id

print("\nMaximum resources machine tuples:\n")
print(promlib.machine_total(hosts))

print("\nCurrent resources machine tuples:\n")
print(promlib.machine_current(hosts))

print("\nAverage resources machine tuples:\n")
print(promlib.machine_average(hosts))

print("\nAverage resources application tuples:\n")
print(promlib.application_average(app_list))

print("\nQuantile resources application tuples:\n")
print(promlib.application_quantile(app_list))


#deployment example
#promlib.deploy('10.24.24.131',['profile', 'mongodb-rate', 'rate', 'user','mongodb-recommendation', 'memcached-reserve'],'deathstar-deploy')
#promlib.deploy('10.24.24.132',['memcached-profile', 'mongodb-profile', 'search', 'jaeger', 'frontend','mongodb-user', 'reservation'],'deathstar-deploy')
#promlib.deploy('vm-3',['recommendation', 'geo', 'consul', 'memcached-rate', 'mongodb-reservation','mongodb-geo'],'deathstar-deploy')

promlib.clear_namespace('deathstar-deploy')

'''['profile', 'mongodb-rate', 'rate', 'user', 'memcached-profile', 'mongodb-profile', 'search', 'jaeger', 'frontend', 'recommendation', 'geo', 'consul', 'memcached-rate', 'mongodb-reservation'
    , 'mongodb-recommendation', 'memcached-reserve', 'mongodb-user', 'reservation', 'mongodb-geo']'''


