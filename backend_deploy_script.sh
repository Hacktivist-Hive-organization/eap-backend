docker rm -f $(docker ps -aq)
# docker volume rm pgdata # (In case you ran a postgres container before and it already created an anonymous volume with the samge name)
docker rmi -f $(docker images -q)
#docker run --name eap-postgres-container --network eap-docker-net -e POSTGRES_PASSWORD=12345 -p 5431:5432 -d postgres
docker run --name eap-postgres-container --network eap-docker-net  -v pgdata:/var/lib/postgresql -e POSTGRES_PASSWORD=12345 -d postgres # no need for port mapping anymore?
docker build --no-cache -t eap-backend-image .
docker run --name eap-backend-container --network eap-docker-net -it -p 8000:8000 eap-backend-image
docker run --name eap-pgadmin-container \
  --network eap-docker-net \
  -p 5050:80 \
  -e PGADMIN_DEFAULT_EMAIL=admin@example.com \
  -e PGADMIN_DEFAULT_PASSWORD=admin \
  -d dpage/pgadmin4