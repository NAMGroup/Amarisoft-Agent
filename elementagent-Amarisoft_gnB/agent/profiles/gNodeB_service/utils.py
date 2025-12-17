import json
import subprocess
import re
import asyncio
import websockets
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
agent_logging = logging.getLogger(__name__)


def exec_command(action_command, debug_mode=False):
    """Execute a shell command and log the output."""
    agent_logging.info(type(action_command))
    agent_logging.info(action_command)
    
    process: subprocess.Popen[str]
    
    if debug_mode:
        process = subprocess.Popen(
            ["echo \""+ str(action_command)+"\" >>../test.txt"],
            shell=True, 
            stdout=subprocess.PIPE,
            universal_newlines=True
        )
    else:
        process = subprocess.Popen(
            [action_command],
            shell=True, 
            stdout=subprocess.PIPE,
            universal_newlines=True
        )
    
    while True:
        output = process.stdout.readline()  # type: ignore
        agent_logging.info(output.strip())
        return_code = process.poll()
        if return_code is not None:
            agent_logging.info(f'RETURN CODE {return_code}')
            for output in process.stdout.readlines():  # type: ignore
                agent_logging.info(output.strip())
            break


def write_conf_file(params):
    """Write configuration parameters to myconf.cfg file."""
    # Clear file contents
    with open("./shared/myconf.cfg", 'a+') as conf:
        conf.truncate(0)

    # Start writing file
    for param in params:
        if param in params:
            with open("./shared/myconf.cfg", mode="a") as conf:
                if any(param.startswith(prefix) for prefix in ["PRMT_AMF_ADDR", "PRMT_GTP_ADDR", "PRMT_PLMN", "PRMT_MOD_UL", "PRMT_MOD_DL"]):
                    conf.write("#define  {} \"{}\"\n".format(param, params[param]))
                else:
                    conf.write("#define  {} {}\n".format(param, params[param]))
        else:
            agent_logging.info(f"Yeah  this param is not available... {param}")


async def send_ws_message(message):
    """Send a message via WebSocket to localhost:9000."""
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
    
    Args:
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
    """Read and parse the users.db.cfg file."""
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


def update_ues_websocket_db(params):
    """
    Write users database file with UE updates via websocket.
    
    Args:
        params: Can be either:
            - A list of UE dictionaries
            - A string in users.db.cfg format (with ue_db: prefix, comments, etc.)
    """
    # Read current state
    current_ues = read_users_db_file()
    
    # Handle different input formats
    if isinstance(params, str):
        # Parse the string as users.db.cfg format
        content = params
        
        # Remove comments
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        content = re.sub(r'//.*', '', content)
        
        # Remove prefix if present
        content = content.replace('ue_db:', '').strip()
        
        # Quote keys (simple heuristic: word characters followed by colon)
        content = re.sub(r'(\w+)\s*:', r'"\1":', content)
        
        # Handle hex values
        content = re.sub(r'0x([0-9a-fA-F]+)', lambda m: str(int(m.group(1), 16)), content)
        
        # Handle trailing commas
        content = re.sub(r',(\s*[}\]])', r'\1', content)
        
        try:
            new_ues = json.loads(content)
        except json.JSONDecodeError as e:
            agent_logging.error(f"Error parsing UE data: {e}")
            return
    elif isinstance(params, list):
        # Already a list of UE dictionaries
        new_ues = params
    else:
        agent_logging.error(f"Invalid params type: {type(params)}. Expected list or string.")
        return

    # Create dictionaries keyed by IMSI for easy comparison
    # Current UEs: {imsi: ue_data}
    current_map = {}
    for ue in current_ues:
        imsi = ue.get('imsi')
        if imsi:
            current_map[imsi] = ue
    
    # New UEs from params: {imsi: ue_data}
    new_map = {}
    for ue in new_ues:
        imsi = ue.get('imsi')
        if imsi:
            new_map[imsi] = ue
    
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
