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


def send_ws_message(message, max_retries=3, timeout=5, retry_delay=0.5):
    """Send a message via WebSocket with retry logic for both connection and sending."""
    uri = f"ws://{WEBSOCKET_HOST}:{WEBSOCKET_PORT}"
    ws: WebSocket
    
    # Retry loop for connection
    for conn_attempt in range(max_retries):
        try:
            ws = create_connection(uri, timeout=timeout)
            response = ws.recv()
            logging.info("Websocket connection successful.")
            break
        except ConnectionRefusedError as e:
            logging.error(f"Connection to {uri} refused (attempt {conn_attempt + 1}/{max_retries}): {e}")
            if conn_attempt < max_retries - 1:
                import time
                time.sleep(retry_delay * (conn_attempt + 1))  # Exponential backoff
                logging.info(f"Retrying connection...")
            else:
                logging.error(f"Failed to connect after {max_retries} attempts")
                return None
        except Exception as e:
            logging.error(f"Exception while connecting to {uri} (attempt {conn_attempt + 1}/{max_retries}): {e}")
            if conn_attempt < max_retries - 1:
                import time
                time.sleep(retry_delay * (conn_attempt + 1))
                logging.info(f"Retrying connection...")
            else:
                logging.error(f"Failed to connect after {max_retries} attempts")
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
            "message": "ue_del",
            "imsi": ue_entry.get('imsi')
        }
        agent_logging.info(f"[UE_DELETE] Removing UE with IMSI: {ue_entry.get('imsi')}")
    
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
    
    agent_logging.info(f"[UPDATE_UES_WS_DB] Current IMSIs in database: {list(current_map.keys())}")
    
    # New UEs from params: {imsi: ue_data}
    new_map = {}
    for ue in new_ues:
        imsi = ue.get('imsi')
        if imsi:
            new_map[imsi] = ue
    
    agent_logging.info(f"[UPDATE_UES_WS_DB] New IMSIs from request: {list(new_map.keys())}")
    
    to_remove = []
    to_add = []
    
    # Check for removals and updates
    for imsi, ue in current_map.items():
        if imsi not in new_map:
            # If missing, we keep
            agent_logging.info(f"[UPDATE_UES_WS_DB] IMSI {imsi}: Keeping (not in new request)")
        else:
            # Use the new UE data directly (REPLACE, not merge)
            # This ensures removed fields are actually removed
            new_ue = new_map[imsi]
            
            # Compare the new UE with the current one
            agent_logging.info(f"[UPDATE_UES_WS_DB] IMSI {imsi}: Comparing UEs...")
            agent_logging.info(f"[UPDATE_UES_WS_DB] Current DB UE keys: {sorted(ue.keys())}")
            agent_logging.info(f"[UPDATE_UES_WS_DB] New UE keys: {sorted(new_ue.keys())}")
            
            # Check for key differences
            old_keys = set(ue.keys())
            new_keys = set(new_ue.keys())
            
            if old_keys != new_keys:
                agent_logging.info(f"[UPDATE_UES_WS_DB] IMSI {imsi}: Keys changed")
                agent_logging.info(f"[UPDATE_UES_WS_DB]   Added keys: {new_keys - old_keys}")
                agent_logging.info(f"[UPDATE_UES_WS_DB]   Removed keys: {old_keys - new_keys}")
            
            # Deep comparison
            if new_ue != ue:
                # If changed, we remove and re-add
                agent_logging.info(f"[UPDATE_UES_WS_DB] IMSI {imsi}: MODIFIED - will remove then re-add")
                
                # Show what changed
                all_keys = old_keys | new_keys
                for key in sorted(all_keys):
                    if key not in ue:
                        agent_logging.info(f"[UPDATE_UES_WS_DB]   New field '{key}': {new_ue[key]}")
                    elif key not in new_ue:
                        agent_logging.info(f"[UPDATE_UES_WS_DB]   Removed field '{key}'")
                    elif ue[key] != new_ue[key]:
                        agent_logging.info(f"[UPDATE_UES_WS_DB]   Changed '{key}': {ue[key]} -> {new_ue[key]}")
                
                to_remove.append(ue)
                to_add.append(new_ue)
            else:
                agent_logging.info(f"[UPDATE_UES_WS_DB] IMSI {imsi}: Unchanged")
            
            # Keep the new UE data for file writing
            # (new_map[imsi] already has the correct data)
            
    # Check for additions
    for imsi, ue in new_map.items():
        if imsi not in current_map:
            agent_logging.info(f"[UPDATE_UES_WS_DB] IMSI {imsi}: NEW - will add")
            to_add.append(ue)
            
    # Execute websocket calls
    agent_logging.info(f"[UPDATE_UES_WS_DB] Summary - Remove: {len(to_remove)}, Add: {len(to_add)}")
    
    import time
    
    # Process removes first and wait for each to complete
    failed_removes = []
    for ue in to_remove:
        imsi = ue.get('imsi')
        agent_logging.info(f"[UPDATE_UES_WS_DB] Removing IMSI {imsi}...")
        result = websocket_update_ue('remove', ue)
        agent_logging.info(f"[UPDATE_UES_WS_DB] Remove result for {imsi}: {result}")
        
        # Check if remove failed (None means connection failed, dict with error means server error)
        if result is None:
            agent_logging.error(f"[UPDATE_UES_WS_DB] Remove failed for {imsi}: Connection failed (no response)")
            failed_removes.append(imsi)
        elif isinstance(result, dict) and result.get('error'):
            agent_logging.warning(f"[UPDATE_UES_WS_DB] Remove failed for {imsi}: {result.get('error')}")
            failed_removes.append(imsi)
        elif isinstance(result, str) and 'Failed' in result:
            agent_logging.error(f"[UPDATE_UES_WS_DB] Remove failed for {imsi}: {result}")
            failed_removes.append(imsi)
        else:
            agent_logging.info(f"[UPDATE_UES_WS_DB] Remove successful for {imsi}")
        
        # Give websocket time to process the remove
        time.sleep(0.1)
    
    # Extra delay after all removes before starting adds
    if to_remove and to_add:
        agent_logging.info(f"[UPDATE_UES_WS_DB] All removes sent. Waiting 1s before adds...")
        time.sleep(1.0)
        
    # Now process adds
    for ue in to_add:
        imsi = ue.get('imsi')
        
        # Skip add if the remove for this IMSI failed (UE still exists)
        if imsi in failed_removes:
            agent_logging.warning(f"[UPDATE_UES_WS_DB] Skipping add for {imsi}: previous remove failed, UE may still exist")
            continue
            
        agent_logging.info(f"[UPDATE_UES_WS_DB] Adding IMSI {imsi}...")
        result = websocket_update_ue('add', ue)
        agent_logging.info(f"[UPDATE_UES_WS_DB] Add result for {imsi}: {result}")
        
        # Check if add failed (None means connection failed, dict with error means server error)
        if result is None:
            agent_logging.error(f"[UPDATE_UES_WS_DB] Add failed for {imsi}: Connection failed (no response)")
        elif isinstance(result, dict) and result.get('error'):
            agent_logging.error(f"[UPDATE_UES_WS_DB] Add failed for {imsi}: {result.get('error')}")
        elif isinstance(result, str) and 'Failed' in result:
            agent_logging.error(f"[UPDATE_UES_WS_DB] Add failed for {imsi}: {result}")
        else:
            agent_logging.info(f"[UPDATE_UES_WS_DB] Add successful for {imsi}")

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
