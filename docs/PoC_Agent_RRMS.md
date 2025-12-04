# PoC
Basic instuctions for a PoC with RRMS and agent in dockers 
Everything is installed in asingle machine which is also a gnb (172.16.100.207)

## Topology
The basic topology is as follows

```plantuml
node PoC_RRMS{
    [172.16.100.207]
    component mongo_db{
        interface 27017

    }
    
    
    component mongo_express{
        interface 18081
    }
    
    
    component radio_mgmt_server{
        interface 18080
    }


}

radio_mgmt_server <-->mongo_db
mongo_express <-->mongo_db


Actor myUser

myUser <---> radio_mgmt_server
myUser <---> mongo_express


node PoC_AGENT{
    [172.16.100.207]

    
    component agent{
        interface 42000
    }


}

radio_mgmt_server<-->agent
myUser<-->agent

```


## RRMS Steps
Install RRMS server by following the instrcutions


### install
- https://gitlab.patras5g.eu/papajohn_for_projects/incode/rrms_incode.git


### Build
- cd  rrms_incode
- docker build -t gnb_agent ./

### Deploy
- docker run -d --name mongo -p 27017:27017 -v $(pwd)/database/db:/data/db -v $(pwd)/database/dev.archive:/Databases/dev.archive -v $(pwd)/database/production:/Databases/production -e MONGO_INITDB_ROOT_USERNAME=root -e MONGO_INITDB_ROOT_PASSWORD=password --restart unless-stopped mongo:5.0
- docker run -d --name mexpress -p 18081:8081 -e ME_CONFIG_MONGODB_ADMINUSERNAME=root -e ME_CONFIG_MONGODB_ADMINPASSWORD=password -e ME_CONFIG_MONGODB_URL=mongodb://root:password@mongo:27017/?authSource=admin -e ME_CONFIG_BASICAUTH_USERNAME=someUser -e ME_CONFIG_BASICAUTH_PASSWORD=somePassword --restart unless-stopped --link mongo:mongo mongo-express
- docker run -d --name radio_mgmt_server -p 18080:8080  -e MONGO_DB_IP="172.16.100.207:27017" --restart unless-stopped radio_mgmt_server uvicorn openapi_server.main:app --host 0.0.0.0 --port 8080 --reload

## Agent 

### Install 
- git clone https://gitlab.patras5g.eu/papajohn_for_projects/across/gnb_agent.git
- cd agent
- git switch Amarisoft_gnB

### Build
- cd agent
- docker build -t gnb_agent ./


### Deploy

docker run -d --name gnb_agent -p 42000:8080                 --privileged             -v ./src/shared/:/agent/shared                      -v /run/systemd/system:/run/systemd/system -v /var/run/dbus/system_bus_socket:/var/run/dbus/system_bus_socket  -e SERVER_IP=http://172.16.100.207:18080 -e AGENT_NAME="MY_POC_AGENT"          -e AGENT_IP="172.16.100.207:42000"        --restart unless-stopped                  gnb_agent      uvicorn openapi_server.main:app --host 0.0.0.0 --port 8080 --reload

## Verify 
- curl -X 'GET' \
  'http://172.16.100.207:18080/resource' \
  -H 'accept: application/json'
- curl -X 'GET' \
  'http://172.16.100.207:18080/resource/MY_POC_AGENT' \
  -H 'accept: application/json'

## Agent Sanity check
### echo
curl -X 'PATCH' \
  'http://172.16.100.207:42000/resource/name' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "activation_feature": [
    {
      "name": "gNodeB_service",
      "feature_characteristic": [
        {
          "name": "action",
          "value": {
            "value": "echo"
          }
        }
      ]
    }
  ]
}
'

### touch
curl -X 'PATCH' \
  'http://172.16.100.207:42000/resource/name' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "activation_feature": [
    {
      "name": "gNodeB_service",
      "feature_characteristic": [
        {
          "name": "action",
          "value": {
            "value": "touch"
          }
        }
      ]
    }
  ]
}
'


## Server Sanity check

### echo
curl -X 'PATCH' \
  'http://172.16.100.207:18080/resource/MY_POC_AGENT' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "activation_feature": [
    {
      "name": "gNodeB_service",
      "feature_characteristic": [
        {
          "name": "action",
          "value": {
            "value": "echo"
          }
        }
      ]
    }
  ]
}
'

### touch
curl -X 'PATCH' \
  'http://172.16.100.207:18080/resource/MY_POC_AGENT' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "activation_feature": [
    {
      "name": "gNodeB_service",
      "feature_characteristic": [
        {
          "name": "action",
          "value": {
            "value": "touch"
          }
        }
      ]
    }
  ]
}
'

# gnb commands

Available commands:
- start 
- stop
- restart

## agent
curl -X 'PATCH' \
  'http://172.16.100.207:42000/resource/name' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "activation_feature": [
    {
      "name": "gNodeB_service",
      "feature_characteristic": [
        {
          "name": "action",
          "value": {
            "value": "start"
          }
        }
      ]
    }
  ]
}
'

## server
curl -X 'PATCH' \
  'http://172.16.100.207:18080/resource/MY_POC_AGENT' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "activation_feature": [
    {
      "name": "gNodeB_service",
      "feature_characteristic": [
        {
          "name": "action",
          "value": {
            "value": "restart"
          }
        }
      ]
    }
  ]
}
'