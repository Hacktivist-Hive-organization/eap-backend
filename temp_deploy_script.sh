docker rm -f $(docker ps -aq)
docker rmi -f $(docker images -q)
docker run --name eap-postgres-container --network eap-docker-net -e POSTGRES_PASSWORD=12345 -p 5431:5432 -d postgres
docker build --no-cache -t eap-backend-image .
docker run --name eap-backend-container --network eap-docker-net -it -p 8000:8000 eap-backend-image

