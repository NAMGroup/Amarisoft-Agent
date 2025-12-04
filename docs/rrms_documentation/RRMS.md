# RRMS System Documentation

## 1. Participants

### Users
* **External User:** A user outside the system interacting with the system through the portal.
* **Internal User:** A user within the system, with more direct access to system components (VPN, etc.).

### Openslice Components
* **Portal:** The interface through which users interact with the service offerings.
* **ServiceCatalog:** A collection of available services that users can select and configure.
* **OSOM:** A management system responsible for orchestrating services and configurations.

### Testbed Components
* **Kubernetes:** A platform used to install and manage containerized applications, specifically Open5GS.
* **RRMS (Resource and Radio Management System):** Handles resource allocation and radio configurations.
* **gNBAgent:** An agent responsible for configuring gNB (next-generation Node B, part of the 5G infrastructure).

---

## 2. Workflows

### Flow by External Actor
This process includes initial configuration and potential reconfiguration (patching) of the service.
**A. Initial Service Deployment**
1.  **Request:** External User sends a request to the Portal for available services.
2.  **Retrieval:** Portal retrieves the list from ServiceCatalog and sends it to the user.
3.  **Selection:** External User selects the `5G_Network` service via the Portal.
4.  **Initiation:** External User initiates configuration of the service; Portal sends the request to ServiceCatalog.
5.  **Orchestration:**
    * ServiceCatalog forwards the request to OSOM.
    * OSOM installs Open5GS on Kubernetes.
    * OSOM selects the gNB and sends the configuration (using TMFAPI) to RRMS.
6.  **Configuration:** RRMS configures the gNB by sending the configuration (using TMFAPI) to gNBAgent.

**B. Reconfigure 5G_Network Service (Patch Service)**
1.  **Request:** External User reconfigures the `5G_Network` service via the Portal.
2.  **Orchestration:**
    * Portal sends the new configuration to ServiceCatalog, which forwards it to OSOM.
    * OSOM selects the gNB and sends the new configuration to RRMS.
3.  **Execution:** RRMS reconfigures the gNB by sending the configuration to gNBAgent.

### Flow by Internal Actor
Internal users (researchers or admins) have direct or semi-direct access.

* **Through RRMS:** Internal User selects the gNB and sends configuration (TMFAPI) to RRMS, which forwards it to gNBAgent.
* **Direct gNB Configuration:** Internal User directly configures the gNB by sending configuration (TMFAPI) to gNBAgent.

---

## 3. Available Commands
The agent currently supports the following commands:

* **start:** Starts the 5G service in the gNB.
* **restart:** Restarts the 5G service in the gNB.
* **stop:** Stops the 5G service in the gNB.
* **touch:** Creates a file in the gNB; used for debugging and sanity checks.
* **echo:** Echos a message in a file in the gNB; used for debugging and sanity checks.

---

## 4. Technical Implementation & API

### Communication
Both RRMS and the agent work through REST APIs.
* **Registration:** Upon agent initialization, a POST request is sent by the agent to the RRMS to register itself.
* **Control:** The RRMS receives a PATCH request and forwards it to the corresponding agent, which executes the command in the body.

### Format
The system satisfies the **TMF639 Resource Inventory Management** specification.

**Sample PATCH Request Payload**

Below is a sample payload structure :

```json
{
  "activation_feature": [
    {
      "name": "gNodeB_service",
      "feature_characteristic": [
        {
          "name": "action",
          "value": {
            "value": "restart"
          }
        },
        {
          "name": "action_parameters",
          "value": {
            "value": {
              "PRMT_AMF_ADDR": "10.10.10.224",
              "PRMT_GTP_ADDR": "172.16.10.207",
              "PRMT_NSSAI": "[{sst: 1},]"
            }
          }
        }
      ]
    }
  ]
}