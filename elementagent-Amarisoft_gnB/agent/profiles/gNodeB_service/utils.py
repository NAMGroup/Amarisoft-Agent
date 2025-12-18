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
            return return_code


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


async def send_ws_message(message, timeout=5, max_retries=3):
    """Send a message via WebSocket with retry logic."""
    uri = "ws://172.16.10.207:9000"
    agent_logging.info(f"[WS] Connecting to {uri}")
    agent_logging.info(f"[WS] Message to send: {json.dumps(message, indent=2)}")
    
    for attempt in range(max_retries):
        try:
            agent_logging.info(f"[WS] Attempt {attempt + 1}/{max_retries}")
            async with websockets.connect(uri, timeout=timeout) as websocket:
                agent_logging.info(f"[WS] Connected successfully")
                message_str = json.dumps(message)
                agent_logging.info(f"[WS] Sending {len(message_str)} bytes")
                await websocket.send(message_str)
                agent_logging.info(f"[WS] Message sent, waiting for response...")
                response = await asyncio.wait_for(websocket.recv(), timeout=timeout)
                agent_logging.info(f"[WS] Response received: {response}")
                return {"success": True, "response": response}
        except asyncio.TimeoutError:
            agent_logging.error(f"[WS] Timeout on attempt {attempt + 1}")
            if attempt == max_retries - 1:
                return {"success": False, "error": "Timeout", "details": f"Connection or response timed out after {max_retries} attempts"}
        except websockets.exceptions.InvalidMessage as e:
            agent_logging.error(f"[WS] Invalid WebSocket handshake on attempt {attempt + 1}: {e}")
            agent_logging.error(f"[WS] This usually means the server at {uri} is not a WebSocket server or is not responding correctly")
            if attempt == max_retries - 1:
                return {"success": False, "error": "InvalidMessage", "details": f"Server did not complete WebSocket handshake: {e}"}
        except ConnectionRefusedError:
            agent_logging.error(f"[WS] Connection refused on attempt {attempt + 1} - server may not be running")
            if attempt == max_retries - 1:
                return {"success": False, "error": "ConnectionRefused", "details": f"Cannot connect to {uri} - server may not be running"}
        except websockets.exceptions.WebSocketException as e:
            agent_logging.error(f"[WS] WebSocket error on attempt {attempt + 1}: {type(e).__name__}: {e}")
            if attempt == max_retries - 1:
                return {"success": False, "error": type(e).__name__, "details": str(e)}
        except Exception as e:
            agent_logging.error(f"[WS] Unexpected error on attempt {attempt + 1}: {type(e).__name__}: {e}")
            agent_logging.error(f"[WS] Error details:", exc_info=True)
            if attempt == max_retries - 1:
                return {"success": False, "error": type(e).__name__, "details": str(e)}
        
        if attempt < max_retries - 1:
            wait_time = (attempt + 1) * 0.5
            agent_logging.info(f"[WS] Waiting {wait_time}s before retry...")
            await asyncio.sleep(wait_time)
    
    return {"success": False, "error": "MaxRetriesExceeded", "details": f"Failed after {max_retries} attempts"}


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
        
        # Run the async operation and wait for completion
        try:
            # Check if there's already a running event loop
            try:
                loop = asyncio.get_running_loop()
                agent_logging.info(f"[UE_UPDATE] Found running event loop, using run_coroutine_threadsafe")
                # We're in an async context, need to run in a separate thread
                import concurrent.futures
                import threading
                
                # Create a new event loop in a separate thread
                def run_in_thread():
                    new_loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(new_loop)
                    try:
                        return new_loop.run_until_complete(send_ws_message(message))
                    finally:
                        new_loop.close()
                
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(run_in_thread)
                    result = future.result(timeout=20)  # 20 second total timeout
                    agent_logging.info(f"[UE_UPDATE] Operation completed with result: {result}")
                    return result
                    
            except RuntimeError:
                # No running event loop, we can use asyncio.run()
                agent_logging.info(f"[UE_UPDATE] No running event loop, using asyncio.run()")
                result = asyncio.run(send_ws_message(message))
                agent_logging.info(f"[UE_UPDATE] Operation completed with result: {result}")
                return result
                
        except concurrent.futures.TimeoutError:
            agent_logging.error(f"[UE_UPDATE] Timeout waiting for websocket operation")
            return {
                "success": False,
                "error": "Timeout",
                "details": "Operation timed out after 20 seconds"
            }
        except Exception as e:
            agent_logging.error(f"[UE_UPDATE] Error executing websocket call: {type(e).__name__}: {e}")
            agent_logging.error(f"[UE_UPDATE] Error details:", exc_info=True)
            return {
                "success": False, 
                "error": type(e).__name__, 
                "details": str(e)
            }
    else:
        agent_logging.warning(f"[UE_UPDATE] No message to send (invalid action: {action})")
        return {
            "success": False,
            "error": "InvalidAction",
            "details": f"Invalid action: {action}"
        }


def read_users_db_file():
    """Read and parse the users.db.cfg file."""
    try:
        with open("./shared/users.db.cfg", 'r') as f:
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
            return None
    elif isinstance(params, list):
        # Already a list of UE dictionaries
        new_ues = params
        # Convert any hex strings to integers
        new_ues = [convert_hex_strings_in_ue(ue) for ue in new_ues]
    else:
        agent_logging.error(f"Invalid params type: {type(params)}. Expected list or string.")
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
    with open("./shared/users.db.cfg", 'w') as conf:
        conf.write("ue_db: ")
        json.dump(final_ues_list, conf, indent=4)
    
    return {
        "status": "success",
        "new": len(to_add) - len(to_remove),
        "updated": len(to_remove),
        "total": len(final_ues_list)
    }
