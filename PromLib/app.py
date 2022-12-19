from flask import Flask, request
from flask_restplus import Api, Resource, fields
import requests
from promlib import deploy
import paramiko as pk
import yaml

with open("config.yaml", 'r') as stream:
    config = yaml.safe_load(stream)

flask_app = Flask(__name__)
app = Api(app=flask_app,
          version="1.0",
          title="Application-VM Placement",
          description="Get application-vm mappings, deploy the apps on their mapped VMs and run workload on deployed apps")

name_space1 = app.namespace('App-VM map and deploy', description='API call to get App-VM mapping and deploy apps to mapped VMs')


@name_space1.route("/<string:app_list>")
class MainClass(Resource):

    @app.doc(responses={200: 'OK', 400: 'Invalid Argument', 500: 'Mapping Key Error'},
             params={'app_list': 'Specify the Id associated with the app'})
    # @app.expect(model)
    def get(self, app_list):
        try:
            # print(app_list)
            apps_list = app_list.split(',')
            # print(apps_list)
            query_apps = []
            for app in apps_list:
                query_apps.append('app_list=' + app)
            query = "&".join([qapp for qapp in query_apps])

            url = 'http://'+config['solver_source']+'/get_placement_vp?' + query
            print(url)
            response = requests.get(url).json()
            # print(response)
            # print(response['mappings'])

            for k, v in response['mappings'].items():
                deploy(k, v, 'deathstar-deploy')

            return {
                "status": "Mappings and deployment successful",
                "Mappings": response['mappings']
            }

        except KeyError as e:
            name_space1.abort(500, e.__doc__, status="Could not retrieve information", statusCode="500")
        except Exception as e:
            name_space1.abort(400, e.__doc__, status="Could not retrieve information", statusCode="400")


'''name_space2 = app.namespace('Deploy Apps to VMs', description='API call to deploy Apps on mapped VMs ')

model_dict = app.model('vm_app_dict=',
                       {'Strind': fields.String(required=True,
                                                  description="String of format vm-ip:app-id1,app-id-2,...",
                                                  help="vm1:a1,a2,a3")})


@name_space2.route("/<string:vm_app_dict>")
class MainClass(Resource):

    @app.doc(responses={200: 'OK', 400: 'Invalid Argument', 500: 'Mapping Key Error'})
    @app.expect(model_dict)
    def post(self, vm_app_dict):
        try:
            vm, apps = vm_app_dict.split(':')
            # apps=apps[1:len(apps-1)]
            apps_list = apps.split(',')
            print(apps_list)
            # deploy(vm,apps_list,'deathstar-deploy')
            return {
                "status": "Deployment successful"
            }
        except KeyError as e:
            name_space2.abort(500, e.__doc__, status="Could not retrieve information", statusCode="500")
        except Exception as e:
            name_space2.abort(400, e.__doc__, status="Could not retrieve information", statusCode="400")'''

name_space3 = app.namespace('Run workloads', description='API call to run workloads on deployed apps ')

model_param = app.model('benchmark_parameter=',
                        {'String': fields.String(required=True,
                                                 description="String of format {threads},{connections},{durations(sec)},{requests/second} ",
                                                 help="%t,%c,%d,%r")})


@name_space3.route("/<string:benchmark_parameter>")
class MainClass(Resource):

    @app.doc(responses={200: 'OK', 400: 'Invalid Argument', 500: 'Mapping Key Error'},
             params={'benchmark_parameter': 'String of format {threads},{connections},{durations(sec)},{requests/second}'})
    @app.expect(model_param)
    def post(self, benchmark_parameter):
        try:
            param = benchmark_parameter.split(',')
            str='./hotelReservation-deployment/wrk2/wrk -D exp -t {} -c {} -d {}s -L -s ' \
                './hotelReservation-deployment/wrk2/scripts/hotel-reservation/mixed-workload_type_1.lua http://localhost:5000 -R {}'\
                .format(param[0], param[1], param[2], param[3])
            print(str)
            ssh = pk.SSHClient()
            ssh.set_missing_host_key_policy(pk.AutoAddPolicy())

            ssh.connect(hostname=config['k8s_control_plane'], username='akshat', password='2716')
            ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(str)


            str=[]

            print('Error:')
            for line in iter(ssh_stderr.readline, ""):
                print(line, end="")
            print('finished. \n ')

            print('Output:')
            for line in iter(ssh_stdout.readline, ""):
                str.append(line)
                print(line, end="")
            print('finished.\n \nRun complete \n ')
            l=len(str)


            return {
                "status": "Run Successful",
                "Total requests" : str[l-3][:len(str[l-3])-1],
                "Requests/sec" : str[l-2][:len(str[l-2])-1],
                "Transfer/sec": str[l-1][:len(str[l-1])-1]
            }
        except KeyError as e:
            name_space3.abort(500, e.__doc__, status="Could not retrieve information", statusCode="500")
        except Exception as e:
            name_space3.abort(400, e.__doc__, status="Could not retrieve information", statusCode="400")
