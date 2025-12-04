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
        
        
    '    component mongo_express{
    '   }
        


    }

    node gNB1{
    component agent1
    }


    node gNBX{
        component agentX
}

}
radio_mgmt_server <->mongo_db
'mongo_express <-->mongo_db

externalUser<-->Portal : 0



'someUser <---> mongo_express :UI



Portal <->ServicesCatalog
Portal <-->radio_mgmt_server :1




radio_mgmt_server <--> agent1 :2
radio_mgmt_server <--> agentX :2

radio_mgmt_server<-->internalUser  : 1
internalUser<--> agent1 :1
internalUser<--> agentX :1
' internalUser <---> Portal:TMF_API
' internalUser <---> radio_mgmt_server:TMF_API
' internalUser <---> agent1:TMF_API
' internalUser <---> agentX:TMF_API
```
