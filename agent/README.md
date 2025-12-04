# GNB_AGENT

## Topology
The basic topology is as follows

```plantuml
node RRMS{
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

```

TBD
## Structure
1 container
- The agent

## Instructions
- Clone this repo
- Follow isntructions
- Pray to your preffered deity
- Enjoy

## Important
- Must know servier ip:port
- Must know own ip:port


## Flow



### Build agent image

docker build -t gnb_agent ./

### Start agent container
docker run -d --name gnb_agent -p 42000:8080 -v ./src/shared/:/agent/shared   -e SERVER_IP=http://10.10.10.58:18080 -e AGENT_NAME="MY_ACROSS_AGENT" -e AGENT_IP="172.16.100.128:42000" --restart unless-stopped gnb_agent uvicorn openapi_server.main:app --host 0.0.0.0 --port 8080 --reload
### Check logs
 docker logs gnb_agent 

## Check Server (Agent)
Visit http:{YOUR_IP}:42000/docs

## Examples

### Local
#### touch 
 curl -X 'PATCH' \
  'http://172.16.100.128:42000/resource/vff' \
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

#### echo 
 curl -X 'PATCH' \
  'http://172.16.100.128:42000/resource/vff' \
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

### server
#### touch 
curl -X 'PATCH' \
  'http://172.16.10.37:18080/resource/MY_ACROSS_AGENT' \
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

#### echo 
curl -X 'PATCH' \
  'http://172.16.10.37:18080/resource/MY_ACROSS_AGENT' \
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