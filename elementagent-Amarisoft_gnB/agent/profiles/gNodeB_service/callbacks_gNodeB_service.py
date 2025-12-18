import logging
import time
from .utils import *

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
agent_logging = logging.getLogger(__name__)

# global variable containing callbacks
callbacks = {}

# API for registering callbacks
def register_callback(event, callback):
    if event not in callbacks:
        callbacks[event] = callback
        agent_logging.info("in here")
    else:
        agent_logging.info("Already reguistered")

# a function that is called when some event is triggered on an object
def process_event(event,debug_mode,params):
    if  event in callbacks:
        # this object/event pair has a callback, call it
        callback = callbacks[event]
        agent_logging.info(f"Callback registered--> {callback}")
        agent_logging.info(debug_mode)
        result = callback(debug_mode,params)
        return result
    else:
        agent_logging.info("No callback registered")
        return False


def touch(debug_mode,params):
    time_now = time.strftime("%Y%m%d-%H%M%S")
    fileName='_'.join(["test",time_now]);
    if params is not None:
        if "filename" in params:
            fileName=params["filename"]
    cmd2send="touch "+fileName
    exec_command(cmd2send)    


def echo(debug_mode,params):
    time_now = time.strftime("%Y%m%d-%H%M%S")
    fileName="./shared/default.echo"
    msg=time_now
    if params is not None:
        if "filename" in params:
            fileName=params["filename"]
        if "message" in params:
            agent_logging.info("here")
            msg=msg +":"+params["message"]
    cmd2send="echo TEST:11111"+msg + " >> ./" + fileName
    agent_logging.info(msg)
    exec_command(cmd2send)    

def stop(debug_mode,params):
    if params is not None:
        ...

    cmd2send="systemctl stop lte"
    
    return_code = exec_command(cmd2send)
    if return_code == 0:
        return "Stop Successful"
    else:
        return "Stop Failed"
 

def start(debug_mode,params):
    if params is not None:
        ...

    cmd2send="systemctl start lte"
    if params is not None:
        write_conf_file(params)
    return_code = exec_command(cmd2send) 
    if return_code == 0:
        return "Start Successful"
    else:
        return "Start Failed"


def restart(debug_mode,params):
    if params is not None:
        ...

    cmd2send="systemctl restart lte"
    if params is not None:
       write_conf_file(params)
    return_code = exec_command(cmd2send)   
    if return_code == 0:
        return "Restart Successful"
    else:
        return "Restart Failed"
    
def get_ue_slices(debug_mode, params):
    target_imsi = None
    # params is expected to be a list of dicts from JSON
    for data in params:
        if isinstance(data, dict) and data.get('imsi'):
            target_imsi = data.get('imsi')
            break
    
    if not target_imsi:
        return None

    ues = read_users_db_file()
    for ue in ues:
        if ue.get('imsi') == target_imsi:
            response = {
                "imsi": ue.get("imsi"),
                "pdn_list": ue.get("pdn_list")
            }
            return response
    return None

def update_ues(debug_mode, params):
    """Update UEs in users database file with UE updates via websocket."""
    response = update_ues_websocket_db(params)
    return response

def get_all_ues(debug_mode, params):
    """Get all UEs from the users database configuration file.
    
    Supports filtering by:
    - access_point_name: Filter UEs by APN name
    - nssai: Filter UEs by network slice (can specify sst and optionally sd)
    
    Example params:
    - [{"access_point_name": "internet"}]
    - [{"nssai": {"sst": 1}}]
    - [{"nssai": {"sst": 1, "sd": 10}}]
    - [{"access_point_name": "internet", "nssai": {"sst": 1}}]
    """
    ues = read_users_db_file()
    
    # Extract filter criteria from params
    filter_apn = None
    filter_nssai = None
    
    if params and isinstance(params, list):
        for param in params:
            if isinstance(param, dict):
                if "access_point_name" in param:
                    filter_apn = param["access_point_name"]
                if "nssai" in param:
                    filter_nssai = param["nssai"]
    
    # Apply filters if specified
    filtered_ues = []
    for ue in ues:
        pdn_list = ue.get("pdn_list", [])
        
        # If no filters, include all UEs
        if not filter_apn and not filter_nssai:
            filtered_ues.append(ue)
            continue
        
        # Check if UE matches filter criteria
        matches = False
        for pdn in pdn_list:
            apn_match = True
            nssai_match = True
            
            # Check APN filter
            if filter_apn:
                apn_match = pdn.get("access_point_name") == filter_apn
            
            # Check NSSAI filter
            if filter_nssai:
                nssai_match = False
                nssai_list = pdn.get("nssai", [])
                for nssai in nssai_list:
                    sst_match = nssai.get("sst") == filter_nssai.get("sst")
                    
                    # If sd is specified in filter, check it too
                    if "sd" in filter_nssai:
                        sd_match = nssai.get("sd") == filter_nssai.get("sd")
                        if sst_match and sd_match:
                            nssai_match = True
                            break
                    else:
                        # If no sd in filter, only match sst
                        if sst_match:
                            nssai_match = True
                            break
            
            # If both filters match (or only one is set and it matches), include UE
            if apn_match and nssai_match:
                matches = True
                break
        
        if matches:
            filtered_ues.append(ue)
    
    return {
        "status": "success",
        "count": len(filtered_ues),
        "ues": filtered_ues,
        "filters": {
            "access_point_name": filter_apn,
            "nssai": filter_nssai
        }
    }