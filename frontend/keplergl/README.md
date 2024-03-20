# kepler.gl

This is an adaptation of the kepler.gl demo app.

#### 1. Setup (local development mode)

```sh
yarn install
```

or

```sh
make setup
```

#### 2. Mapbox Token

A mapbox accss token is required, and has been configured as an environment variable in the 
docker-compose files.

#### 3. Start the app

```sh
docker-compose up --build keplergl-web
```
