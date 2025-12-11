from ast import Not
from urllib.parse import _NetlocResultMixinStr
import yaml
import random
import string

from openapi_server.models.resource_create import ResourceCreate
from openapi_server.models.characteristic import Characteristic

from . import agent_logging

# from  openapi_server.profiles import callbacks
import inspect
import importlib

import requests
import time


class MyAgent:
    def __init__(self):
        self.logger= agent_logging.logger
        self.agent_resource_file="resource_data_RO.yml"
        self.agent_conf_file="conf_data_RW.yml"
        self.profiles="profiles.yml"
        self.profile_location="./profiles" #folder name. Need to read conf name
        self.profile_location_name="profiles" #"package name". Need to import as package
        self.resource_data=None
        self.server=None
        self.profile=None
        self.profile_descriptor=None
        self.talk2server=None
        self.TIMEOUT=60#300 #How often to send updates to server
        self.CMD_DEBUG_MODE=False #whether the command will be run or just displyad as log messaage to verify operation
        self.profile_actions=list() #Actions thar are standard in this profile
        self.callbacks=None #Callback file to use
        #Will use this to keep state of service. running-->active, not running-->idle
        self.ResourceUsageState="idle" #      idle/active
        # self.gnodeb_conf_file="../../myconf.cfg"
        # self.action_params=None
        # self.action_present=None
        # self.allowed_actions=list()
        # self.commands=dict()
        # self.allowed_params=None

        # self.server=None
        # self.resourceID=None
        # self.registered=None
        # self.resource_status=None #Status of the resource
        # self.resource=None #this will be the resource obj

    def talk_to_server(self,status):
        while (1):
            print("Do something for status")
            print(status)
            time.sleep(self.TIMEOUT)
            if self.resource_data is None:
                continue
            my_status=self.callbacks.process_event("status", self.CMD_DEBUG_MODE, None)
            if  my_status is False:
                self.logger.info("No callback registered for status")
            else:
                self.logger.info("Callback registered for status")
                #update status
                self.ResourceUsageState=my_status
                
            resp=self.startSelfRegisterProccess()
            self.logger.info("Service status is (in thread)-->"+self.ResourceUsageState)
            self.logger.info("send patch to update agent info (in thread)")




    def __send_post_request(self,endpoint,data2send):
        x=None
        try: 
            x = requests.post(self.server+endpoint, data=data2send.json() )
        except requests.exceptions.RequestException as e:  # This is the correct syntax
          self.logger.error("Connection Error with server")
          self.logger.error(e)
        return x

    def __send_patch_request(self,endpoint,data2send):
        x=None
        try: 
            x = requests.patch(self.server+endpoint, data=data2send.json() )
        except requests.exceptions.RequestException as e:  # This is the correct syntax
          self.logger.error("Connection Error with server")
          self.logger.error(e)
        return x


    def read_profile(self):
        self.logger.info("Reading profile-->"+self.profile)
        # Create expected profile name
        # self.profile_descriptor="./openapi_server/profiles/"+self.profile+"/"+'_'.join(["profile",self.profile])+".yml"
        # self.profile_descriptor="./profiles/"+self.profile+"/"+'_'.join(["profile",self.profile])+".yml"
        self.profile_descriptor="./"+self.profile_location+"/"+self.profile+"/"+'_'.join(["profile",self.profile])+".yml"
        print(self.profile_descriptor)
        try:
            ymlfile= open(self.profile_descriptor, "r")
        except Exception as e:
            self.logger.error("Profiles yaml file not found")
            return False
        with open(self.profile_descriptor, "r") as ymlfile:
            profiles = yaml.safe_load(ymlfile)
            if "supported_profiles" not in profiles:
                self.logger.error("Profiles yaml file foes not have correct format. No supported_profiles field")
                return False
            if self.profile not in profiles["supported_profiles"]:
                self.logger.error("Profiles yaml file does not have correct format. Selected profile not present")
                return False
            #If we are here, the selected profile actually exists
            selected_profile=profiles["supported_profiles"][self.profile]
            if "available_commands" not in selected_profile:
                self.logger.error("Profiles yaml file does not have correct format. No available_commands field")
                return False
            #Init to None to add commands
            for commands_key, command_value in selected_profile["available_commands"].items():
                #make sure that we only add the key only once
                if commands_key not in self.profile_actions:
                    self.profile_actions.append(commands_key)
        return True

    def read_conf(self):
        #Read basic device info.This is specific for this device type and should never
        with open(self.agent_resource_file, "r") as ymlfile:
            data = yaml.safe_load(ymlfile)
            if "resource_data" not in data:
                self.logger.error("NO resource data found")
                return False
            self.resource_data=data["resource_data"]
            #Also set profile as well
            if "profile_type" not in data:
                self.logger.error("NO profile found")
                return False
            self.profile=data["profile_type"]
            #since there is a profile lets get the default actions for this profile
            status=self.read_profile()
            if status is False:
                self.logger.error("Profile Reading failed")
                return False
        #Read basic configuration info. This might change during runtime
        with open(self.agent_conf_file, "r") as ymlfile:
            conf_data_yaml = yaml.safe_load(ymlfile)
            if "configuration" not in conf_data_yaml:
                self.logger.error("NO configuration data found")
                return False
            data=conf_data_yaml["configuration"]
            # print(conf_data_yaml)
            self.server=data["server"]


        return True

 #create a resource in order to register
    def __createResource(self):
        #TODO: Check if entries exist in cfg
        #create a random name so that DB does not get an error when testing
        #ran = ''.join(random.choices(string.ascii_uppercase + string.digits +string.ascii_lowercase, k = 5))    
        #selfResource=ResourceCreate(name=self.resource_data["name"]+ran)
        #Send fixed name. This must be unique
        selfResource=ResourceCreate(name=self.resource_data["name"],)
        selfResource.category=self.resource_data["category"]
        selfResource.description=self.resource_data["description"]
        selfResource.resource_version="0.0.1"
        selfResource.resource_characteristic=[]
        if "ip" in self.resource_data:
            resourceIP_Char=Characteristic(name="IP",value={"value":self.resource_data["ip"]})
            resourceIP_Char.id="string"
            resourceIP_Char.value_type="string"
            selfResource.resource_characteristic.append(resourceIP_Char)
        if "location" in self.resource_data:
            resourceLoc_Char=Characteristic(name="location",type="array",value={"value":self.resource_data["location"]})
            resourceLoc_Char.id="string"
            resourceLoc_Char.value_type="array"
            selfResource.resource_characteristic.append(resourceLoc_Char)
        

        if self.profile is not None:
        # if self.allowed_actions is not None:
            #Add profile in resource char as well
            profile_Char=Characteristic(name="profile",value={"value":self.profile})
            profile_Char.id="string"
            profile_Char.value_type="string"
            selfResource.resource_characteristic.append(profile_Char)
            #Add supported actions
            resourceAction_Char=Characteristic(name="supported_actions",type="list",value={"value":self.profile_actions})  
            resourceAction_Char.id="string"
            resourceAction_Char.value_type="list"
            selfResource.resource_characteristic.append(resourceAction_Char)   
            callback_module='.'.join(["profiles",self.profile,"callbacks_"+self.profile])
            #print(callback_module)
            # from  openapi_server.profiles import callback_module as callbacks
            try:
                import sys
                sys.path.append("..")
                callbacks = importlib.import_module(callback_module, package="5G_NAM_Agent")
            except ImportError:
                self.logger.error("startSelfRegisterProccess FAILED. Call back module not FOUND")
                self.logger.error(["callback module expected-->",callback_module])
                return None       
            self.callbacks=callbacks
            #register callbacks
            for action in self.profile_actions:
                #print(action)
                myCB=action
                if (hasattr(callbacks, myCB) and inspect.isfunction(getattr(callbacks, myCB))):
                    callbacks.register_callback(action, getattr(callbacks, action))
                else:
                    print("No callback to register for-->",myCB)
                    
        #sunny day scenario
        #All is good
        #just to allow GUI to wotk 
        administrative_state="unlocked"#ResourceAdministrativeStateTypeEnum[self.resource_status["administrativeState"]].value if "administrativeState" in self.resource_status else None
        operational_state="enable"#ResourceOperationalStateTypeEnum[self.resource_status["operationalState"]].value if "administrativeState" in self.resource_status else None
        resource_status="available"#ResourceStatusTypeEnum[self.resource_status["resourceStatus"]].value if "administrativeState" in self.resource_status else None
        #usage_state="idle"#ResourceUsageStateTypeEnum[self.resource_status["usageState"]].value if "administrativeState" in self.resource_status else None
        #USe value gotten from status
        usage_state=self.ResourceUsageState# "idle"#ResourceUsageStateTypeEnum[self.resource_status["usageState"]].value if "administrativeState" in self.resource_status else None
        selfResource.administrative_state=administrative_state
        selfResource.operational_state=operational_state
        selfResource.resource_status=resource_status
        selfResource.usage_state=usage_state    
        # if self.resource_status:
        #     print("DDDDDDDDDDDDD")
        #     #TODO: if the key is erroneous in agetn_Cfg (i.e. state=unlked) there is an excpetion. Must fix it
        #     administrative_state=ResourceAdministrativeStateTypeEnum[self.resource_status["administrativeState"]].value if "administrativeState" in self.resource_status else None
        #     operational_state=ResourceOperationalStateTypeEnum[self.resource_status["operationalState"]].value if "administrativeState" in self.resource_status else None
        #     resource_status=ResourceStatusTypeEnum[self.resource_status["resourceStatus"]].value if "administrativeState" in self.resource_status else None
        #     usage_state=ResourceUsageStateTypeEnum[self.resource_status["usageState"]].value if "administrativeState" in self.resource_status else None
        #     selfResource.administrative_state=administrative_state
        #     selfResource.operational_state=operational_state
        #     selfResource.resource_status=resource_status
        #     selfResource.usage_state=usage_state
        #     print("******************")
        print(selfResource.usage_state)
        return selfResource   


    def startSelfRegisterProccess(self):
        self.logger.info("Starting Self Registration Process")
        if self.read_conf()==False:
            self.logger.error("startSelfRegisterProccess FAILED. READ  CONF FAILED")
            return False
        # this.selfRegister()
        self.logger.info("Trying to self register")
        selfResource=self.__createResource() 
        
        if selfResource == None:
            self.logger.error("startSelfRegisterProccess FAILED. CREATE RESOURCE FAILED")
            return False    
        if self.server is  None:
            self.logger.error("startSelfRegisterProccess FAILED. NO SERVER INFO FOUND")
            return False    
        #Send post req to server
        #TODO: check that IP has http in front otherwise add it
        # print(selfResource)
        resp=self.__send_post_request("/resource",selfResource)
        self.logger.info("POST request sent")
        if resp is None:
            self.logger.error("Connection to server failed")
            return False
        self.logger.info("POST request response status code-->"+ str(resp.status_code))
        if resp.status_code==201:
            self.logger.info("Initial Registration succesful")
            self.logger.info("Resource Created")
            self.resource=selfResource
        elif resp.status_code==409:
            self.logger.info("Already registered")
            resp=self.__send_patch_request("/resource/"+self.resource_data["name"],selfResource)
            self.logger.info("send patch to update agent info ")
            if resp is None:
                self.logger.error("Connection to server failed")
                return False
            self.resource=selfResource
            #self.resource=resp.text
        elif resp.status_code==403:
            self.logger.info("Server DB error")
            self.logger.info(resp)
        else:
            self.logger.info("Not handled response")
            self.logger.info(resp)