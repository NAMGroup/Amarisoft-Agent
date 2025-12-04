# Participants

## Users

- External User: A user outside the system interacting with the system through the portal.
- Internal User: A user within the system, with more direct access to system components (VPN, etc,).
## Openslice
- Portal: The interface through which users interact with the service offerings.
- ServiceCatalog: A collection of available services that users can select and configure.
- OSOM: A management system responsible for orchestrating services and configurations.

## Testbed
- Kubernetes: A platform used to install and manage containerized applications, in this case, Open5GS.
- RRMS: Resource and Radio Management System that handles resource allocation and radio configurations.
- gNBAgent: An agent responsible for configuring gNB (next-generation Node B, part of the 5G infrastructure).

# Flow by External Actor
## Initial Service
- External User sends a request to the Portal for available services.
- Portal retrieves the list of services from the ServiceCatalog.
- Portal sends the list of available services back to the External User.
- External User selects the 5G_Network service via the Portal.
- Portal informs the ServiceCatalog of the selected 5G_Network service.
- External User initiates configuration of the 5G_Network service on the Portal.
- Portal sends the configuration request to the ServiceCatalog.
- ServiceCatalog forwards the configuration request to OSOM.
- OSOM installs Open5GS on Kubernetes.
- OSOM selects the gNB and sends the configuration (using TMFAPI) to RRMS.
- RRMS configures the gNB by sending the configuration (using TMFAPI) to gNBAgent.
## Reconfigure 5G_Network Service
- External User reconfigures the 5G_Network service via the Portal.
- Portal sends the new configuration request to the ServiceCatalog.
- ServiceCatalog forwards the configuration request to OSOM.
- Reconfigure gNB (within Patch Service)
- OSOM selects the gNB and sends the new configuration (using TMFAPI) to RRMS.
- RRMS reconfigures the gNB by sending the configuration (using TMFAPI) to gNBAgent.
# Flow by Internal Actor
## Through RRMS
- Internal User selects the gNB and sends the configuration (using TMFAPI) to RRMS.
- RRMS configures the gNB by sending the configuration (using TMFAPI) to gNBAgent.
# Direct
## Direct gNB Configuration
- Internal User directly configures the gNB by sending the configuration (using TMFAPI) to gNBAgent.
# Summary
This is the basic flow for a 5G system to be deployed and configured in UoP infrastructure using either the Openslice OSS or direct access depending on the user access.
The external user (an experimenter for example )goes through the portal and service catalog, while the internal user (admin or researcher with VPN access to the testlab) has direct or semi-direct access to the resource management systems. The process includes initial configuration and potential reconfiguration (patching) of the service, involving orchestration and resource management systems to apply the necessary configurations to network components like gNB.

## Available commands
The agent supports (at the time of writing) the following commands:
- start: A command that starts the 5G service in the gNB
- restart: A command that restarts the 5G service in the gNB
- stop: A command that stops the 5G service in the gNB
- touch: A command that creates a file in the gNB under control. Used for debugging and sanity checks (aka everything works as expected.
- echo: A command that echos a message in a file in the gNB under control. Used for debugging and sanity checks (aka everything works as expected.
# Flow
Both the RRMS and the agent work through REST APIs. 
- Upon agent init, a POST request is sent by the agent to the RRMS. With this the agent registers itself and the RRMS can now control it.
- The RRMS will get a PATCH request (either manually or and forward it to the corresponding agent.
- The agent receiving a PATCH request will execute the command included in the body of the message.

# Format
The RRMS and the agent both satisfy the TMF639 Resource Inventory Management specification. 
A sample patch request payload can be seen as follows:

---
**SAMPLE CURL PATCHE**

curl -X 'PATCH' \ 'http://{RRMS_IP}/resource/{AGENT_NAME}' \ -H 'accept: application/json' \ -H 'Content-Type: application/json' \ -d ' { "activation_feature": [ { "name": "gNodeB_service", "feature_characteristic": [ { "name": "action", "value": { "value": "restart" } }, { "name": "action_parameters", "value": { "value": { "PRMT_AMF_ADDR": "10.10.10.224", "PRMT_GTP_ADDR": "172.16.10.207", "PRMT_NSSAI" : "[{sst: 1},]" } } } ] } ] } '

---
