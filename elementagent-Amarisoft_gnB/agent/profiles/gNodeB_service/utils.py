import json
import subprocess
import re
import os
from websocket import create_connection, WebSocket
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
agent_logging = logging.getLogger(__name__)

# Configuration from environment variables
MYCONF_FILE = os.getenv('MYCONF_FILE', './shared/myconf.cfg')
USERS_DB_FILE = os.getenv('USERS_DB_FILE', './shared/users.db.cfg')
WEBSOCKET_HOST = os.getenv('WEBSOCKET_HOST', '172.16.100.207')
WEBSOCKET_PORT = os.getenv('WEBSOCKET_PORT', '9000')


def exec_command(action_command, debug_mode=False):
    """Execute a shell command and log the output."""
    agent_logging.info(type(action_command))
    agent_logging.info(action_command)
    
    # Wrap systemctl commands with nsenter to execute on host
    if isinstance(action_command, str) and 'systemctl' in action_command:
        action_command = f"nsenter -t 1 -m -u -n -i {action_command}"
        agent_logging.info(f"Wrapped with nsenter: {action_command}")
    
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
            return return_code


def write_conf_file(params):
    """Write configuration parameters to myconf.cfg file."""
    # Clear file contents
    with open(MYCONF_FILE, 'a+') as conf:
        conf.truncate(0)

    # Start writing file
    for param in params:
        if param in params:
            with open(MYCONF_FILE, mode="a") as conf:
                if any(param.startswith(prefix) for prefix in ["PRMT_AMF_ADDR", "PRMT_GTP_ADDR", "PRMT_PLMN", "PRMT_MOD_UL", "PRMT_MOD_DL"]):
                    conf.write("#define  {} \"{}\"\n".format(param, params[param]))
                else:
                    conf.write("#define  {} {}\n".format(param, params[param]))
        else:
            agent_logging.info(f"Yeah  this param is not available... {param}")


def send_ws_message(message, max_retries=3, timeout=5):
    """Send a message via WebSocket with retry logic."""
    uri = f"ws://{WEBSOCKET_HOST}:{WEBSOCKET_PORT}"
    ws: WebSocket
    
    # Connect to the WebSocket server
    try:
        ws=create_connection(uri, timeout=timeout)
        response = ws.recv()
        logging.info("Websocket connection successful.")
    except ConnectionRefusedError as e:
        logging.error(f"Connection to {uri} refused: {e}")
        return None
    except Exception as e:
        logging.error(f"Exception while connecting to {uri}: {e}")
        return None
    
    if ws:
        for attempt in range(max_retries):
            try:
                logging.info(f"Sending message via websocket: {json.dumps(message)}")
                ws.send(json.dumps(message))
                # Wait for response with timeout
                ws.settimeout(timeout)
                response = ws.recv()
                logging.info(f"Received response: {response}")
                ws.close()
                return json.loads(response)
            except ConnectionError as e:
                logging.error(f"WebSocket connection error: {e}")
                break
            except Exception as e:
                logging.error(f"Error during WebSocket communication: {e}")
                if attempt < max_retries - 1:
                    ws.close()
                    logging.info(f"Retrying... ({attempt + 1}/{max_retries})")
                else:
                    logging.error("Max retries reached. Giving up.")
                    ws.close()
                    return "WebSocket Message Failed"
        ws.close()
    
    

def websocket_update_ue(action, ue_entry):
    """
    Websocket call to add or remove UE.
    
    Args:
        action: 'add' or 'remove'
        ue_entry: dict containing UE details
    
    Returns:
        dict: Result of the websocket operation with success status
    """
    agent_logging.info(f"[UE_UPDATE] Action: {action}")
    agent_logging.info(f"[UE_UPDATE] UE Entry: {json.dumps(ue_entry, indent=2)}")
    
    message = {}
    if action == 'add':
        message = {
            "message": "ue_add",
            "ue_db": [ue_entry]
        }
        agent_logging.info(f"[UE_ADD] Adding UE with IMSI: {ue_entry.get('imsi')}")
    elif action == 'remove':
        message = {
            "message": "ue_remove",
            "imsi": ue_entry.get('imsi')
        }
        agent_logging.info(f"[UE_REMOVE] Removing UE with IMSI: {ue_entry.get('imsi')}")
    
    if message:
        agent_logging.info(f"[UE_UPDATE] Preparing to send websocket message")
        
        try:
            response = send_ws_message(message)
            agent_logging.info(f"[UE_UPDATE] Websocket response: {response}")
            return response
        except Exception as e:
            agent_logging.error(f"[UE_UPDATE] Error sending websocket message: {type(e).__name__}: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    else:
        agent_logging.error(f"[UE_UPDATE] Invalid action: {action}")
        return {
            "status": "error",
            "error": "Invalid UE_UPDATE action"
        }
           


def read_users_db_file():
    """Read and parse the users.db.cfg file."""
    try:
        with open(USERS_DB_FILE, 'r') as f:
            content = f.read()
            
        # Remove comments (both /* */ and //)
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        content = re.sub(r'//[^\n]*', '', content)
        
        # Remove prefix
        content = content.replace('ue_db:', '').strip()
        
        # Handle hex values before quoting keys
        content = re.sub(r'0x([0-9a-fA-F]+)', lambda m: str(int(m.group(1), 16)), content)
        
        # Quote unquoted keys - match word characters followed by colon (but not already quoted)
        content = re.sub(r'([{,]\s*)(\w+)(\s*):', r'\1"\2"\3:', content)
        
        # Handle trailing commas before closing braces/brackets
        content = re.sub(r',(\s*[}\]])', r'\1', content)

        result = json.loads(content)
        return result
    except json.JSONDecodeError as e:
        agent_logging.error(f"Error parsing users.db.cfg as JSON: {e}")
        agent_logging.error(f"Problematic content around error: {content[max(0, e.pos-100):min(len(content), e.pos+100)]}")
        return []
    except Exception as e:
        agent_logging.error(f"Error reading users.db.cfg: {e}")
        return []


def convert_hex_strings_in_ue(ue_data):
    """
    Convert hex string values to integers in UE data.
    Handles fields like amf that may be passed as "0x9001".
    """
    if isinstance(ue_data, dict):
        converted = {}
        for key, value in ue_data.items():
            if isinstance(value, str) and value.startswith('0x'):
                try:
                    # Convert hex string to integer
                    converted[key] = int(value, 16)
                except ValueError:
                    # If conversion fails, keep original value
                    converted[key] = value
            elif isinstance(value, list):
                # Recursively handle lists
                converted[key] = [convert_hex_strings_in_ue(item) for item in value]
            elif isinstance(value, dict):
                # Recursively handle nested dicts
                converted[key] = convert_hex_strings_in_ue(value)
            else:
                converted[key] = value
        return converted
    else:
        return ue_data


def update_ues_websocket_db(params):
    """
    Write users database file with UE updates via websocket.
    
    Args:
        params: Can be either:
            - A list of UE dictionaries
            - A string in users.db.cfg format (with ue_db: prefix, comments, etc.)
    
    Note: Hex values can be passed as strings (e.g., "0x9001") and will be converted to integers.
    """
    agent_logging.info(f"[UPDATE_UES_WS_DB] Function called")
    agent_logging.info(f"[UPDATE_UES_WS_DB] Params type: {type(params)}")
    agent_logging.info(f"[UPDATE_UES_WS_DB] Params length: {len(params) if isinstance(params, (list, str)) else 'N/A'}")
    
    # Read current state
    agent_logging.info(f"[UPDATE_UES_WS_DB] Reading current UE database...")
    current_ues = read_users_db_file()
    agent_logging.info(f"[UPDATE_UES_WS_DB] Current UEs count: {len(current_ues)}")
    
    # Handle different input formats
    if isinstance(params, str):
        agent_logging.info(f"[UPDATE_UES_WS_DB] Params is string, parsing...")
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
            agent_logging.info(f"[UPDATE_UES_WS_DB] Parsed {len(new_ues)} UEs from string")
        except json.JSONDecodeError as e:
            agent_logging.error(f"[UPDATE_UES_WS_DB] Error parsing UE data: {e}")
            return None
    elif isinstance(params, list):
        agent_logging.info(f"[UPDATE_UES_WS_DB] Params is list with {len(params)} items")
        # Already a list of UE dictionaries
        new_ues = params
        # Convert any hex strings to integers
        agent_logging.info(f"[UPDATE_UES_WS_DB] Converting hex strings...")
        new_ues = [convert_hex_strings_in_ue(ue) for ue in new_ues]
        agent_logging.info(f"[UPDATE_UES_WS_DB] Hex conversion complete")
    else:
        agent_logging.error(f"[UPDATE_UES_WS_DB] Invalid params type: {type(params)}. Expected list or string.")
        return None

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
    with open(USERS_DB_FILE, 'w') as conf:
        conf.write("ue_db: ")
        json.dump(final_ues_list, conf, indent=4)
    
    return {
        "status": "success",
        "new": len(to_add) - len(to_remove),
        "updated": len(to_remove),
        "total": len(final_ues_list)
    }
