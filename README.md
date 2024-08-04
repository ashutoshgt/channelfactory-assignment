# channelfactory-assignment
API asked as part of the channelfactory assignment

## Local Setup Steps:
1. Make sure you have docker installed locally.
2. You may also need postman to make requests, unless you are comfortable with curl
3. To try out the API, please set an environment variable named `GOOGLE_MAPS_API_KEY` in your shell
4. To run the API locally, execute the following command under the root directory of this project
```
make build-run
make run-migrations
(The second command can be used anytime we remove the db volume)
```
This will create an api service along with a postgres database, which you can connect to using the credentials found in the docker-compose.yaml file

## Running test cases

## API Specifications:

### URI: 
http://localhost:8000/v1/api/distance

### Method:
POST

### Request Body:
```JSON
{
    "from_address": "string",
    "destination_address": "string"
}
```

### Success Response (200):
```JSON
{
    "from_address": {
        "original": "string",
        "formatted": "string",
        "lat": float,
        "lng": float
    },
    "destination_address": {
        "original": "string",
        "formatted": "string",
        "lat": float,
        "lng": float
    },
    "distance": float
}
```

### Error Responses (4xx):
```
1. {"from_address": ["This field is required."]}
2. ["Could not geocode from_address"]
```

### Sample Requests:
```
curl --location 'http://localhost:8000/v1/api/distance' \
--header 'Content-Type: application/json' \
--data '{
    "from_address": "qutub minar",
    "destination_address": "india gate"
}'

Response:
{
    "from_address":{
        "original":"qutub minar",
        "lat":28.5244946,
        "long":77.18551769999999,
        "formatted":"Seth Sarai, Mehrauli, New Delhi, Delhi 110030, India"
    },
    "destination_address":{
        "original":"india gate",
        "lat":28.612912,
        "long":77.2295097,
        "formatted":"Kartavya Path, India Gate, New Delhi, Delhi 110001, India"
    },
    "distance":10.729218711890798
}
```

```
curl --location 'http://localhost:8000/v1/api/distance' \
--header 'Content-Type: application/json' \
--data '{
    "from_address": "None",
    "destination_address": "india gate"
}'

Response:
{
    "non_field_errors": ["Could not geocode the from_address"]
}
```

```
curl --location 'http://localhost:8000/v1/api/distance' \
--header 'Content-Type: application/json' \
--data '{
    "from_address": "India Gate"
}'

Response:
{
    "destination_address":["This field is required."]
}
```
### Future Improvements/Pending Tasks:
1. Add a cache bursting mechanism
2. On running unit test cases, db container starts as well, can be changed to only run the api container
