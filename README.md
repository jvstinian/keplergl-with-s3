# kepler.gl With S3 Storage

We set up the kepler.gl demo application to run in a container, adding support 
for storing maps on S3.  A python backend provides the API for reading from and 
writing to S3.  

# Warning

This is for use in a research environment only, and should not be exposed to the internet.  
While we have added support to kepler.gl to use S3 as storage, we have not implemented 
authentication.  As such, this should only be used by an individual or shared with 
trusted team members in a local development environment, on the cloud provider's VPN, 
or behind a firewall.  

# Set up

Set you Mapbox Access Token in docker-compose.yml, or alternatively define it in a 
dotenv file in the root of the project.  

# Running 

To bring up the services in a local development environment using S3 with localstack 
(rather than AWS), then run
```
keplergl-with-s3$ docker-compose up --build keplergl-web
```

