## Setup
 - Clone repository
 - Install pgAdmin
 - Watch the Postgres container tutorial https://www.youtube.com/watch?v=Hs9Fh1fr5s8 since the following steps will be partially based on it.
 - Create a Docker network (Make sure the name is not taken):   docker network create eap-docker-net
 - Run a Postgres container off the official Postgres image and use the network you just created in the previous step:
      docker run --name eap-postgres-container --network eap-docker-net -e POSTGRES_PASSWORD=12345 -p 5431:5432 -d postgres
 - Connect pgAdmin to the postgres server as done in the tutorial.
   - Configure environment variables (Create a .env file (example)):
       - DATABASE_TYPE=postgresql  
       - DATABASE_HOST=eap-postgres-container (Docker containers can communicate by using each other's names if they both run on the same Docker network)  
       - DATABASE_PORT=5432 (We're already using the container as the host in the line above, so this is the container's port, which is still the default of 5432)  
       - DATABASE_USER=user1  
       - DATABASE_USER=postgres  
       - DATABASE_PASSWORD=12345  
       - DATABASE_NAME=postgres  
       - JWT_SECRET_KEY="my secret key"  

 - Run the following commands:
   - docker build -t eap_backend_image .   
   - docker run --name eap-backend --network eap-docker-net -it -p 8000:8000 eap_backend_image
   - Go to pgAdmin to confirm the database was created with the tables that are defined in the app.

Note - The DB name itself does not matter. We can use the default DB name that's automatically generated when running
the Postgres container ("postgres"), or we can choose our own name in the app. It doesn't matter because our app checks
if a DB by the name we provide exists, and if not, it creates it. CLARIFICATION - This is just the DB itself, one of
many potential databases inside the Postgres server. The connection info to the Postgres server has to match exactly.  
