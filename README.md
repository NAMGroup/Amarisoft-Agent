# Amarisoft gNodeB Agent API Documentation

## 1. Overview

The **Amarisoft gNodeB Agent** is a RESTful API service designed to manage and control Amarisoft 5G gNodeB (Next Generation Node B) equipment. It serves as an intermediary between a central Resource Management System and the physical Amarisoft hardware, enabling remote configuration, monitoring, and User Equipment (UE) management.

### 1.1 Purpose

The agent provides:

- **Resource Inventory Management**: Implements the TMF (TeleManagement Forum) Resource Inventory Management API (TMF639) specification v4.0.0
- **Self-Registration**: Automatic registration with a central management server
- **Service Lifecycle Management**: Start, stop, and restart of the LTE/5G service
- **UE Database Management**: Dynamic addition, modification, and removal of User Equipment entries via WebSocket
- **Configuration Management**: Runtime configuration updates for gNodeB parameters

### 1.2 Technology Stack

It is implemented in Python 3 using the FastAPI web framework (version 0.65+), a modern, high-performance framework well-suited for building RESTful APIs with automatic OpenAPI documentation and data validation. The application runs on Uvicorn, a lightning-fast ASGI server, and leverages Pydantic for data validation and serialization. HTTP client operations are handled via the Requests library for outbound communication with the central management server, while real-time communication with the Amarisoft equipment is achieved through WebSocket using the websocket-client library. Configuration management is handled via PyYAML for parsing YAML-based profile and resource definitions. The application is designed to be containerized and deployable using Docker, with container orchestration supported through Docker Compose.

### 1.3 Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Resource Management Server                    │
└─────────────────────────────────────────────────────────────────┘
                              ▲
                              │ HTTP REST (TMF639)
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     gNodeB Agent (FastAPI)                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │  OpenAPI    │  │   Agent     │  │     Profile/Callbacks   │  │
│  │  Endpoints  │◄─┤   Core      │◄─┤   (gNodeB_service)      │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
        │                                       │
        │ Shell Commands                        │ WebSocket
        ▼                                       ▼
┌─────────────────────┐              ┌─────────────────────┐
│   Amarisoft LTE     │              │   Amarisoft MME/    │
│   Service (systemd) │              │   UE Database       │
└─────────────────────┘              └─────────────────────┘
```

---

## 2. API Endpoints

The API is based on the **TMF639 Resource Inventory Management** specification and exposes the following endpoint groups:

### 2.1 Resource API

Base path: `/resource`


| Method   | Endpoint         | Description                   |
| -------- | ---------------- | ----------------------------- |
| `POST`   | `/resource`      | Create a new Resource entity  |
| `GET`    | `/resource`      | List or find Resource objects |
| `GET`    | `/resource/{id}` | Retrieve a Resource by ID     |
| `PATCH`  | `/resource/{id}` | Partially update a Resource   |
| `DELETE` | `/resource/{id}` | Delete a Resource entity      |

#### Query Parameters (GET /resource)

- `fields`: Comma-separated properties to include in response
- `offset`: Start index for pagination
- `limit`: Number of resources to return

### 2.2 Physical Resource API

Base path: `/physicalResource`


| Method   | Endpoint                 | Description                           |
| -------- | ------------------------ | ------------------------------------- |
| `POST`   | `/physicalResource`      | Create a new PhysicalResource         |
| `GET`    | `/physicalResource`      | List or find PhysicalResource objects |
| `GET`    | `/physicalResource/{id}` | Retrieve a PhysicalResource by ID     |
| `PATCH`  | `/physicalResource/{id}` | Partially update a PhysicalResource   |
| `DELETE` | `/physicalResource/{id}` | Delete a PhysicalResource entity      |

### 2.3 Logical Resource API

Base path: `/logicalResource`


| Method   | Endpoint                | Description                          |
| -------- | ----------------------- | ------------------------------------ |
| `POST`   | `/logicalResource`      | Create a new LogicalResource         |
| `GET`    | `/logicalResource`      | List or find LogicalResource objects |
| `GET`    | `/logicalResource/{id}` | Retrieve a LogicalResource by ID     |
| `PATCH`  | `/logicalResource/{id}` | Partially update a LogicalResource   |
| `PUT`    | `/logicalResource/{id}` | Fully update a LogicalResource       |
| `DELETE` | `/logicalResource/{id}` | Delete a LogicalResource entity      |

### 2.4 Events Subscription API

Base path: `/hub`


| Method   | Endpoint    | Description                    |
| -------- | ----------- | ------------------------------ |
| `POST`   | `/hub`      | Register a listener for events |
| `DELETE` | `/hub/{id}` | Unregister an event listener   |

### 2.5 Notification Listeners API (Client Side)

Base path: `/listener`


| Method | Endpoint                                              | Description                                    |
| ------ | ----------------------------------------------------- | ---------------------------------------------- |
| `POST` | `/listener/physicalResourceAttributeValueChangeEvent` | Listen for physical resource attribute changes |
| `POST` | `/listener/physicalResourceCreateEvent`               | Listen for physical resource creation          |
| `POST` | `/listener/physicalResourceDeleteEvent`               | Listen for physical resource deletion          |
| `POST` | `/listener/physicalResourceStateChangeEvent`          | Listen for physical resource state changes     |
| `POST` | `/listener/resourceAttributeValueChangeEvent`         | Listen for resource attribute changes          |
| `POST` | `/listener/resourceCreateEvent`                       | Listen for resource creation                   |
| `POST` | `/listener/resourceDeleteEvent`                       | Listen for resource deletion                   |
| `POST` | `/listener/resourceStateChangeEvent`                  | Listen for resource state changes              |

---

## 3. Callback System

The agent implements a **callback-based architecture** that enables dynamic execution of commands on the gNodeB equipment. Callbacks are registered at startup based on the configured profile and are invoked when corresponding events are triggered.

### 3.1 Callback Registration Mechanism

```python
def register_callback(event, callback):
    """Register a callback function for a specific event."""
    if event not in callbacks:
        callbacks[event] = callback

def process_event(event, debug_mode, params):
    """Process an event by invoking its registered callback."""
    if event in callbacks:
        callback = callbacks[event]
        result = callback(debug_mode, params)
        return result
    return False
```

### 3.2 Available Callbacks

The `gNodeB_service` profile provides the following callbacks:

#### 3.2.1 Service Control Callbacks


| Callback  | Description             | Parameters                        | Return Value                                 |
| --------- | ----------------------- | --------------------------------- | -------------------------------------------- |
| `start`   | Start the LTE service   | Optional configuration parameters | `"Start Successful"` or `"Start Failed"`     |
| `stop`    | Stop the LTE service    | None                              | `"Stop Successful"` or `"Stop Failed"`       |
| `restart` | Restart the LTE service | Optional configuration parameters | `"Restart Successful"` or `"Restart Failed"` |

**Example - Start Service:**

```python
def start(debug_mode, params):
    cmd2send = "systemctl start lte"
    if params is not None:
        write_conf_file(params)  # Apply configuration before starting
    return_code = exec_command(cmd2send)
    return "Start Successful" if return_code == 0 else "Start Failed"
```

#### 3.2.2 UE Management Callbacks


| Callback        | Description                    | Parameters                    | Return Value           |
| --------------- | ------------------------------ | ----------------------------- | ---------------------- |
| `get_all_ues`   | Retrieve all UEs from database | Optional filters (APN, NSSAI) | JSON with UE list      |
| `get_ue_slices` | Get slice info for specific UE | `{"imsi": "..."}`             | UE slice configuration |
| `update_ues`    | Add/modify/remove UEs          | List of UE dictionaries       | Operation status       |

**Example - Get All UEs with Filtering:**

```python
def get_all_ues(debug_mode, params):
    """
    Supports filtering by:
    - access_point_name: Filter by APN
    - nssai: Filter by network slice (sst, sd)
  
    Example params:
    - [{"access_point_name": "internet"}]
    - [{"nssai": {"sst": 1, "sd": 10}}]
    """
    ues = read_users_db_file()
    # Apply filters and return results
    return {
        "status": "success",
        "count": len(filtered_ues),
        "ues": filtered_ues
    }
```

**Example - Update UEs:**

```python
def update_ues(debug_mode, params):
    """
    Update UEs via WebSocket and local database file.
  
    Params: List of UE dictionaries with fields:
    - imsi: International Mobile Subscriber Identity
    - pdn_list: List of PDN configurations
    - Additional UE attributes
    """
    response = update_ues_websocket_db(params)
    return response
```

#### 3.2.3 Utility Callbacks


| Callback | Description           | Parameters                              |
| -------- | --------------------- | --------------------------------------- |
| `touch`  | Create a file         | `{"filename": "..."}`                   |
| `echo`   | Write message to file | `{"filename": "...", "message": "..."}` |

---

## 4. Utility Functions

### 4.1 Command Execution

```python
def exec_command(action_command, debug_mode=False):
    """
    Execute a shell command with special handling for systemctl.
  
    Features:
    - Wraps systemctl commands with nsenter for host execution (containerized)
    - Logs command output
    - Returns process return code
    """
```

### 4.2 WebSocket Communication

The agent communicates with the Amarisoft MME via WebSocket for real-time UE database updates.

**Configuration (Environment Variables):**


| Variable         | Default          | Description           |
| ---------------- | ---------------- | --------------------- |
| `WEBSOCKET_HOST` | `172.16.100.207` | WebSocket server IP   |
| `WEBSOCKET_PORT` | `9000`           | WebSocket server port |

**Message Types:**


| Message  | Purpose    | Payload                                        |
| -------- | ---------- | ---------------------------------------------- |
| `ue_add` | Add new UE | `{"message": "ue_add", "ue_db": [<ue_entry>]}` |
| `ue_del` | Remove UE  | `{"message": "ue_del", "imsi": "<imsi>"}`      |

```python
def send_ws_message(message, max_retries=3, timeout=5, retry_delay=0.5):
    """
    Send message via WebSocket with retry logic.
  
    Features:
    - Automatic reconnection on failure
    - Exponential backoff
    - JSON serialization/deserialization
    """
```

### 4.3 Configuration File Management

**Files:**


| File           | Purpose              | Format           |
| -------------- | -------------------- | ---------------- |
| `myconf.cfg`   | gNodeB configuration | C-style defines  |
| `users.db.cfg` | UE database          | JSON-like format |

```python
def write_conf_file(params):
    """
    Write configuration parameters to myconf.cfg.
  
    Generates C-style defines:
    #define PRMT_AMF_ADDR "192.168.1.1"
    #define PRMT_PLMN "00101"
    """
```

---

## 5. Data Models

### 5.1 UE Entry Structure

```json
{
    "imsi": "001010000000001",
    "amf": 36865,
    "pdn_list": [
        {
            "access_point_name": "internet",
            "nssai": [
                {
                    "sst": 1,
                    "sd": 10
                }
            ]
        }
    ]
}
```

### 5.2 Resource Characteristics

The agent registers with the following characteristics:


| Characteristic      | Type   | Description                          |
| ------------------- | ------ | ------------------------------------ |
| `IP`                | string | Agent IP address and port            |
| `location`          | array  | Geographic coordinates [lat, lon]    |
| `profile`           | string | Profile type (e.g.,`gNodeB_service`) |
| `supported_actions` | list   | Available callback actions           |

### 5.3 Resource States


| State Type             | Possible Values                        |
| ---------------------- | -------------------------------------- |
| `administrative_state` | `unlocked`, `locked`, `shutdown`       |
| `operational_state`    | `enable`, `disable`                    |
| `resource_status`      | `available`, `unavailable`, `reserved` |
| `usage_state`          | `idle`, `active`, `busy`               |

---

## 6. Configuration

### 6.1 Environment Variables


| Variable         | Default                 | Description                |
| ---------------- | ----------------------- | -------------------------- |
| `MYCONF_FILE`    | `./shared/myconf.cfg`   | Path to gNodeB config file |
| `USERS_DB_FILE`  | `./shared/users.db.cfg` | Path to UE database file   |
| `WEBSOCKET_HOST` | `172.16.100.207`        | Amarisoft WebSocket host   |
| `WEBSOCKET_PORT` | `9000`                  | Amarisoft WebSocket port   |

### 6.2 Configuration Files

**resource_data_RO.yml** (Read-Only Resource Data):

```yaml
resource_data:
    category: gNB Controller
    description: An agent that controls the lte service of an Amarisoft callbox
    name: NAME_PLACEHOLDER
    ip: IP_PLACEHOLDER:PORT_PLACEHOLDER
    location: [123, 456]
profile_type: gNodeB_service
```

**conf_data_RW.yml** (Runtime Configuration):

```yaml
configuration:
    server: http://<management-server-url>
```

---

## 7. Error Handling

### 7.1 HTTP Error Responses

All endpoints return standard TMF error responses:


| Status Code | Description                            |
| ----------- | -------------------------------------- |
| `400`       | Bad Request - Invalid input            |
| `401`       | Unauthorized - Authentication required |
| `403`       | Forbidden - Insufficient permissions   |
| `404`       | Not Found - Resource doesn't exist     |
| `405`       | Method Not Allowed                     |
| `409`       | Conflict - Resource already exists     |
| `500`       | Internal Server Error                  |

### 7.2 WebSocket Error Handling

The WebSocket communication includes:

- **Retry Logic**: Up to 3 attempts with exponential backoff
- **Timeout Handling**: 5-second timeout per operation
- **Connection Recovery**: Automatic reconnection attempts

---

## 8. Deployment

### 8.1 Docker Deployment

The agent is designed to run in a Docker container with access to the host's systemd via `nsenter`.

**Docker Compose Configuration:**

```yaml
services:
  gnb-agent:
    build: .
    volumes:
      - ./shared:/app/shared
    environment:
      - WEBSOCKET_HOST=172.16.100.207
      - WEBSOCKET_PORT=9000
    privileged: true  # Required for nsenter
```

### 8.2 Requirements

See `requirements.txt` for full dependency list. Key dependencies:

- FastAPI + Uvicorn (Web server)
- Pydantic (Data validation)
- websocket-client (WebSocket communication)
- PyYAML (Configuration parsing)
- Requests (HTTP client for registration)

---

## 9. Sequence Diagrams

### 9.1 Agent Startup and Self-Registration

```
┌─────────┐          ┌─────────────┐          ┌───────────────┐
│  Agent  │          │  Management │          │   Amarisoft   │
│         │          │   Server    │          │   Equipment   │
└────┬────┘          └──────┬──────┘          └───────┬───────┘
     │                      │                         │
     │ POST /resource       │                         │
     │─────────────────────►│                         │
     │                      │                         │
     │ 201 Created / 409    │                         │
     │◄─────────────────────│                         │
     │                      │                         │
     │ PATCH /resource/{id} │                         │
     │─────────────────────►│                         │
     │                      │                         │
     │ [Background Thread]  │                         │
     │ Status polling loop  │                         │
     │──────────────────────────────────────────────► │
     │                      │                         │
```

### 9.2 UE Update via WebSocket

```
┌─────────┐          ┌─────────────┐          ┌───────────────┐
│  Client │          │   Agent     │          │   Amarisoft   │
│         │          │             │          │   WebSocket   │
└────┬────┘          └──────┬──────┘          └───────┬───────┘
     │                      │                         │
     │ update_ues callback  │                         │
     │─────────────────────►│                         │
     │                      │                         │
     │                      │ WS: ue_del (if update)  │
     │                      │────────────────────────►│
     │                      │                         │
     │                      │ WS Response             │
     │                      │◄────────────────────────│
     │                      │                         │
     │                      │ WS: ue_add              │
     │                      │────────────────────────►│
     │                      │                         │
     │                      │ WS Response             │
     │                      │◄────────────────────────│
     │                      │                         │
     │ Operation result     │                         │
     │◄─────────────────────│                         │
     │                      │                         │
```

---

## 10. Appendix

### 10.1 Profile Configuration Reference

The agent uses YAML-based profile configuration:

```yaml
supported_profiles:
    gNodeB_service:
        type: gNodeB_service
        description: An agent that controls the lte service of an Amarisoft callbox
        execution_mode: Shell commands
        available_commands:
            touch:
                description: Create a file
                command: touch name
            echo:
                description: Echo a message to a file
                command: echo text >> file
            stop:
                description: Stop service
                command: systemctl stop <service>
            start:
                description: Start service
                command: systemctl start <service>
            restart:
                description: Restart service
                command: systemctl restart <service>
            get_ue_slices:
                description: Get the slice(s) associated with a UE
            update_ues:
                description: Update UEs in users database file via websocket
            get_all_ues:
                description: Get all UEs from users database file
```

### 10.2 Logging

The agent uses Python's standard logging module with the following format:

```
%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

Log levels are set to `INFO` by default, with detailed logging for:

- WebSocket communications
- UE database operations
- Command execution
- Registration processes

---

## Acknowledgements

<p align="center">
  
  <img src="https://osl.etsi.org/ecosystem/logos/p2code.jpg" alt="P2CODE Project" width="120" style="vertical-align: middle;"/>
  &nbsp;&nbsp;&nbsp;
  <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/b/b7/Flag_of_Europe.svg/255px-Flag_of_Europe.svg.png" alt="European Union Flag" width="80" style="vertical-align: middle;"/>
  &nbsp;&nbsp;&nbsp;
<img src="https://trustchain.ngi.eu/wp-content/uploads/2023/01/NGI-trustchain.png.webp" alt="NGI TrustChain project" width="120" style="vertical-align: middle;"/>
</p>

This project has received funding from the European Union ([P2CODE](https://p2code-project.eu/), G.A. No.101093069).
This project has received funding from the European Union's Horizon Europe research and innovation programme through the NGI TrustChain project.

Views and opinions expressed are, however, those of the author(s) only and do not necessarily reflect those of the European Union. Neither the European Union nor the granting authority can be held responsible for them.
