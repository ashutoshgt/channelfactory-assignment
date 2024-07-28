# channelfactory-assignment
API asked as part of the channelfactory assignment

Request Body:
```JSON
{
    "from_address": "string",
    "destination_address": "string"
}
```

Response:
```JSON
{
    "from_address": {
        "original": string,
        "formatted": string,
        "lat": float,
        "lng": float
    },
    "destination_address": {
        "original": string,
        "formatted": string,
        "lat": float,
        "lng": float
    },
    "distance": float
}
```
