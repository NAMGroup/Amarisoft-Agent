import json
import subprocess
import re
import asyncio
import websockets
import logging
import time


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
        callback(debug_mode,params)
    else:
        agent_logging.info("No callback registered")
        return False


def _execCMD(action_command,debug_mode=False):
    #process = subprocess.Popen(['echo', self.action_command], 
#    process = subprocess.Popen(["echo \"", action_command,"\" >>./test.txt"],
    agent_logging.info(type(action_command))
    agent_logging.info(action_command)
    
    process: subprocess.Popen[str]
    
    if debug_mode:
        process = subprocess.Popen(["echo \""+ str(action_command)+"\" >>../test.txt"],
        # process = subprocess.Popen([action_command],
                            #we need shell= true to pass the command as string and not as list
                            shell=True, 
                            stdout=subprocess.PIPE,
                            universal_newlines=True)
    else:
        # process = subprocess.Popen(["echo \""+ str(action_command)+"\" >>../test.txt"],
        process = subprocess.Popen([action_command],
                    #we need shell= true to pass the command as string and not as list
                    shell=True, 
                    stdout=subprocess.PIPE,
                    universal_newlines=True)
    
    while True:
        output = process.stdout.readline()  # type: ignore
        agent_logging.info(output.strip())
        # Do something else
        return_code = process.poll()
        if return_code is not None:
            agent_logging.info(f'RETURN CODE {return_code}')
            # Process has finished, read rest of the output 
            for output in process.stdout.readlines(): # type: ignore
                agent_logging.info(output.strip())
            break

def touch(debug_mode,params):
    time_now = time.strftime("%Y%m%d-%H%M%S")
    fileName='_'.join(["test",time_now]);
    if params is not None:
        if "filename" in params:
            fileName=params["filename"]
    cmd2send="touch "+fileName
    _execCMD(cmd2send)    
    # _execCMD("echo touch > ./docker_command.txt ")    
    # _execCMD("ls -la")    


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
    _execCMD(cmd2send)    
    # _execCMD("echo 'papajohn' >>./test.txt ; echo $(date -u) >>./test.txt ")    

def write_conf_file(params):
    #clear file contents
    with open("./shared/myconf.cfg", 'a+') as conf:
        conf.truncate(0)

    #start wirtitng file
    for param in params:
        if param in params:
            with open("./shared/myconf.cfg", mode="a") as conf:
                if any(param.startswith(prefix) for prefix in ["PRMT_AMF_ADDR", "PRMT_GTP_ADDR", "PRMT_PLMN", "PRMT_MOD_UL", "PRMT_MOD_DL"]):
                    conf.write("#define  {} \"{}\"\n".format(param,params[param]))
                else:
                    conf.write("#define  {} {}\n".format(param,params[param]))

        else:
            agent_logging.info(f"Yeah  this param is not available... {param}")

async def send_ws_message(message):
    uri = "ws://localhost:9000"
    try:
        async with websockets.connect(uri) as websocket:
            await websocket.send(json.dumps(message))
            response = await websocket.recv()
            agent_logging.info(f"Websocket response: {response}")
    except Exception as e:
        agent_logging.error(f"Websocket error: {e}")

def websocket_update_ue(action, ue_entry):
    """
    Websocket call to add or remove UE.
    action: 'add' or 'remove'
    ue_entry: dict containing UE details
    """
    message = {}
    if action == 'add':
        message = {
            "message": "ue_add",
            "ue_db": [ue_entry]
        }
    elif action == 'remove':
        message = {
            "message": "ue_remove",
            "imsi": ue_entry.get('imsi')
        }
    
    if message:
        agent_logging.info(f"Sending websocket message: {message}")
        coro = send_ws_message(message)
        try:
            loop = asyncio.get_running_loop()
            if loop.is_running():
                loop.create_task(coro)
            else:
                asyncio.run(coro)
        except RuntimeError:
            asyncio.run(coro)

def read_users_db_file():
    try:
        with open("./shared/users.db.cfg", 'r') as f:
            content = f.read()
            
        # Remove comments
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        content = re.sub(r'//.*', '', content)
        
        # Remove prefix
        content = content.replace('ue_db:', '').strip()
        
        # Quote keys (simple heuristic: word characters followed by colon)
        content = re.sub(r'(\w+)\s*:', r'"\1":', content)
        
        # Handle hex values
        content = re.sub(r'0x([0-9a-fA-F]+)', lambda m: str(int(m.group(1), 16)), content)
        
        # Handle trailing commas
        content = re.sub(r',(\s*[}\]])', r'\1', content)

        return json.loads(content)
    except Exception as e:
        agent_logging.error(f"Error reading users.db.cfg: {e}")
        return []


def write_users_db_file(params):
    # Read current state
    current_ues = read_users_db_file()
    
    # params is expected to be a list of dicts from JSON
    new_ues = params

    # Create dictionaries keyed by IMSI for easy comparison
    current_map = {ue.get('imsi'): ue for ue in current_ues if ue.get('imsi')}
    new_map = {ue.get('imsi'): ue for ue in new_ues if ue.get('imsi')}
    
    to_remove = []
    to_add = []
    
    # Check for removals and updates
    for imsi, ue in current_map.items():
        if imsi not in new_map:
            # If missing, we keep
            pass
        elif new_map[imsi] != ue:
            # Patch logic: update current ue with new fields
            merged_ue = ue.copy()
            merged_ue.update(new_map[imsi])
            
            if merged_ue != ue:
                # If changed, we remove and re-add
                to_remove.append(ue)
                to_add.append(merged_ue)
            
            # Update new_map with the merged version so it gets written to file
            new_map[imsi] = merged_ue
            
    # Check for additions
    for imsi, ue in new_map.items():
        if imsi not in current_map:
            to_add.append(ue)
            
    # Execute websocket calls
    for ue in to_remove:
        websocket_update_ue('remove', ue)
        
    for ue in to_add:
        websocket_update_ue('add', ue)

    # Reconstruct the full list for writing to file
    # We start with UEs that were kept (not in new_map)
    final_ues_list = [ue for imsi, ue in current_map.items() if imsi not in new_map]
    # Add the new/updated UEs from the input params
    for ue in new_ues:
         imsi = ue.get('imsi')
         if imsi and imsi in new_map:
             final_ues_list.append(new_map[imsi])
         else:
             final_ues_list.append(ue)

    # Update the file
    with open("./shared/users.db.cfg", 'w') as conf:
        conf.write("ue_db: ")
        json.dump(final_ues_list, conf, indent=4)

def stop(debug_mode,params):
    if params is not None:
        ...

    cmd2send="systemctl stop lte"
    
    _execCMD(cmd2send)    
 

def start(debug_mode,params):
    if params is not None:
        ...

    cmd2send="systemctl start lte"
    if params is not None:
        write_conf_file(params)
    _execCMD(cmd2send)    


def restart(debug_mode,params):
    if params is not None:
        ...

    cmd2send="systemctl restart lte"
    if params is not None:
       write_conf_file(params)
    _execCMD(cmd2send)   
    
def get_ue_slices(debug_mode,params):
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
            return {
                "imsi": ue.get("imsi"),
                "pdn_list": ue.get("pdn_list")
            }
    return None
