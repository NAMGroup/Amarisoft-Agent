```plantuml

component externalAccess{

    Actor externalUser

    node OpenSlice{
        component Portal{

        }
        collections ServicesCatalog
    }


}


component internalAcess{
    Actor internalUser
    node RRMS{
        
        component radio_mgmt_server{
        }

        database mongo_db{
        }
        

    }

    node gNB1{
    component agent1
    }


    node gNBX{
        component agentX
}

}
radio_mgmt_server <->mongo_db


externalUser<-->Portal :UI/TMF_API



Portal <->ServicesCatalog
Portal <-->radio_mgmt_server :TMF_API


radio_mgmt_server <--> agent1 :TMF_API
radio_mgmt_server <--> agentX :TMF_API

radio_mgmt_server<-->internalUser  : TMF_API
internalUser<--> agent1 :TMF_API
internalUser<--> agentX :TMF_API



```
