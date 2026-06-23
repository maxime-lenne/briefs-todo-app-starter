## Summary

- API key requise : oui
- Authentification requise : non
- Roles requis : aucun

### US

> **AS** a visitor\
> **I want** to create an account\
> **So that** I can login to the application

 [spec](http://maxime-lenne.fr)

## Model de donnée

User :

| attribute name | type | required | default |  validation | description | existing |
| ------ | ------ | ------ | ------ | ------ | ------ | ------ |
| id | uuid | oui |  |  | | oui |
| createdAt | date | oui |  |  | | oui |
| updatedAt | date | oui |  |  | | oui |

## Régles métiers (service)

- Le endpoint créera les trois model (Account, User, Address)
- Ajouter originType comme sur l'entité Demand qui est setter directement par l'API
  en fonction du client de l'API qui envoie la requête.
- L'adresse créée sera de type POSTAL et main true.
- une seule address main possible pour un user / company / store...

## API

- Ressource: Account
- Method: Post
- URI : /accounts
- success HTTP code : 201

### request body

```json
{
 "username": {"type": "string", "required": true},
 "password": {"type": "string", "required": true},
 "user": {
  "firstName": {"type": "string", "required": true},
  "lastName": {"type": "string", "required": true},
  "gender": {"type": "string", "required": false},
  "email": {"type": "string", "required": true},
  "language": {"type": "string", "required": false},
  "timeZone": {"type": "string", "required": false},
  "currency": {"type": "string", "required": false}
 },
 "address": {
  "postalCode": {"type": "string", "required": true},
  "locality": {"type": "string", "required": true},
  "country": {"type": "string", "required": true}
 }
}
```

#### validation

Appliquer les mêmes règles de validation sur le dto que sur le model et ajouter :

- Password :
  - 8 char min
  - min 1 chiffre
  - min 1 special char

### Response

```json
{
 "id": {"type": "string", "required": true},
 "createdAt": {"type": "string", "required": true},
 "updatedAt": {"type": "string", "required": true},
 "username": {"type": "string", "required": true},
 "user": {
  "id": {"type": "string", "required": true},
  "createdAt": {"type": "string", "required": true},
  "updatedAt": {"type": "string", "required": true},
  "firstName": {"type": "string", "required": true},
  "lastName": {"type": "string", "required": true},
  "gender": {"type": "string", "required": false},
  "email": {"type": "string", "required": true},
  "language": {"type": "string", "required": false},
  "timeZone": {"type": "string", "required": false},
  "currency": {"type": "string", "required": false}
 },
 "addresses": [{
  "id": {"type": "string", "required": true},
  "createdAt": {"type": "string", "required": true},
  "updatedAt": {"type": "string", "required": true},
  "address": {"type": "string", "required": true},
  "addressComplement": {"type": "string", "required": true},
  "postalCode": {"type": "string", "required": true},
  "locality": {"type": "string", "required": true},
  "country": {"type": "string", "required": true},
  "formattedAddress": {"type": "string", "required": true},
  "coordinates": {
        "type":  "Point",
        "coordinates": [
            50.6330372,
            3.020054
        ]
    }
 }]
}
```

## Acceptance test

### Success

**Given** the following api client\
**When** he make a call with api key\
**And** without access token\
**And** the following json body:

```json
{
 "username": "test",
 "password": "password!1",
 "user": {
  "firstName": "test",
  "lastName": "test",
  "gender": "MALE",
  "email": "test@frizbiz.com"
 },
 "address": {
  "postalCode": "59000",
  "locality": "Lille",
  "country": "France"
 }
}
```

**Then** the http response code is 201\
**And** the response body is:

````json

````

### Failed
