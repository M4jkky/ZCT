#!/bin/bash
docker compose down --volumes

docker rmi assignment1-flask_app
docker rmi dpage/pgadmin4
