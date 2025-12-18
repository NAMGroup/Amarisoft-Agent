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
    
    exec_command(cmd2send)    
 

def start(debug_mode,params):
    if params is not None:
        ...

    cmd2send="systemctl start lte"
    if params is not None:
        write_conf_file(params)
    exec_command(cmd2send)    


def restart(debug_mode,params):
    if params is not None:
        ...

    cmd2send="systemctl restart lte"
    if params is not None:
       write_conf_file(params)
    exec_command(cmd2send)   
    
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
    update_ues_websocket_db(params)
