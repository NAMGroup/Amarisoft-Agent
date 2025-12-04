# Flow 
```plantuml





skinparam BoxPadding 20

box Users
    participant  externalUser 
    participant  internalUser

endbox
box Openslice
    participant Portal
    collections ServiceCatalog
    participant OSOM
endbox

box Testbed
    participant Kubernetes
    participant RRMS
    participant gNBAgent

endbox

group Flow by external actor
    group initialService
        externalUser -> Portal : Request Services
        Portal <-> ServiceCatalog : Get List of services
        externalUser<-Portal : Services List

        externalUser-> Portal : Select 5G_Network Service
        Portal-> ServiceCatalog : Select 5G_Network Service


        externalUser-> Portal : Configure 5G_Network Service
        Portal-> ServiceCatalog : Configure 5G_Network Service
        ServiceCatalog-> OSOM : Configure 5G_Network Service
        OSOM-> Kubernetes: Install Open5GS
        group configuregNB
            OSOM-> RRMS: Select gNB and send configuration (TMFAPI)
            RRMS-> gNBAgent: Configure gnb(TMFAPI)

        end

    end

    group patchService
    externalUser-> Portal : Configure 5G_Network Service
        Portal-> ServiceCatalog : Configure 5G_Network Service
        ServiceCatalog-> OSOM : Configure 5G_Network Service
        group configuregNB
            OSOM-> RRMS: Select gNB and send configuration (TMFAPI)
            RRMS-> gNBAgent: Configure gnb(TMFAPI)

        end

    end
end


group Flow by internal actor
    group Through RRMS
        internalUser-> RRMS: Select gNB and send configuration (TMFAPI)
        RRMS-> gNBAgent: Configure gnb(TMFAPI)
    end
    group Direct
        internalUser-> gNBAgent: Configure gnb(TMFAPI)
    end

end


```
