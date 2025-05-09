# System Exchange - Configuration Settings Guidelines 

## Database Configuration 

### Example
```json
{
    "Status":"Active",
    "DatabaseServerType" : "MONGO_DB_REPLICA_SET",
    "ReplicaSet" : "VSys",
    "Server" : "sysmdb-001.sababalar.net:27017,sysmdb-002.sababalar.net:27017,sysmdb-003.sababalar.net:27017",
    "ServerPort" : null,
    "User" : "va",
    "Password" : "77$$JaiShriRam$$77",
    "Database" : "VSystem-PRD-202401291024",
    "AuthDatabase":"admin"
}
```

### Properties
1. **Status**:

    Valid values are *Active* and *Inactive*

2. **DatabaseServerType**

    Valid values are *MONGO_DB* and *MONGO_DB_REPLICA_SET*

3. **ReplicaSet**

    *Applicable only when* **DatabaseServerType** *is* **MONGO_DB_REPLICA_SET**

4. **Server**

    Server values can be of following types 

    - For **Replica Set**

        Specify MongoDB Server Host Names with their own Ports. Like
            
            *one.abc.com:27017,two.abc.com:27018,three.abc.com:27019*

    - For **Single Server**
    
        Simply specify MongoDB Server Host Name. Like localhost, abc.com, etc. *DO NOT SPECIFY SERVER PORT*


5. **ServerPort**

    *Applicable only when* **DatabaseServerType** *is* **MONGO_DB**

6. **User**

    Database User

7. **Password**

    Database User's Password

8. **Database**

    Database To Connect

9. **AuthDatabase**

    Database which has Authentication Details. Default value is *admin*

---
