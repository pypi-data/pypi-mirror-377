# Python PostgreSQL REST API framework for AWS Lambda functions
> [!NOTE]
> Project status: `Alpha`

A REST API web framework for persisting records in a PostgreSQL database.

## Supported features
- Automatic creation of `uid` fields
- Automatic setting of `created_at` and `last_updated_at` timestamps
- Automatic setting of `creator_uid` and `last_updater_uid`
- RDS with IAM credentials

## Examples
See [Examples docs directory](./docs/examples/)

## Sequence diagrams

### High-level infrastructure

This sequence diagram shows how a lambda function running this library is intended to be deployed.

```mermaid
sequenceDiagram
    # Set up actors and participants
    actor User
    participant APIGW as API Gateway
    participant Cognito as Cognito
    box Purple This library
        participant Lambda as Lambda Function
    end
    participant RDS as RDS Database

    # Set up Sequences
    User ->> APIGW: HTTP /resource
    activate APIGW
        APIGW -->> Cognito: Authenticate
        activate Cognito
            Cognito ->> APIGW: Authenticated
        deactivate Cognito
        APIGW ->> Lambda: Send proxy integration request
        activate Lambda
            Lambda ->> RDS: Fetch/mutate
            activate RDS
                RDS -->> Lambda: Return records
            deactivate RDS
            Lambda -->> APIGW: Return response
        deactivate Lambda
        APIGW -->> User: Return response
    deactivate APIGW
```

### Low-level architecture

This sequence diagram shows the layers within the library that handle request and response processing.

```mermaid
sequenceDiagram

    Participant APIGW as API Gateway
    box Purple This library as a deployed Lambda Function
        Participant CONT as Controller
        Participant REQM as Request Mapper
        Participant RESOURCEM as Resource Mapper
        Participant DBM as Database  Mapper
        Participant RESPONSEM as Response Mapper
    end
    Participant RDS

    APIGW ->> CONT: Send `event` dict
    activate CONT
        CONT ->> REQM: Map request
        activate REQM
            REQM ->> CONT: Mapped request
        deactivate REQM

        CONT ->> RESOURCEM: Map resource
        activate RESOURCEM
            RESOURCEM -->> CONT: Mapped resource
        deactivate RESOURCEM

        CONT ->> DBM: Request resource operation
        activate DBM
            DBM ->> RDS: Perform resource operation
            activate RDS
                RDS -->> DBM: Return resources
            deactivate RDS
            DBM -->> CONT: Return resource
        deactivate DBM

        CONT ->> RESPONSEM: Map response
        activate RESPONSEM
            RESPONSEM -->> CONT: Mapped response
        deactivate RESPONSEM

        CONT -->> APIGW: Return response
    deactivate CONT
```
