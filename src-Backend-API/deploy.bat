@echo off

REM Build Docker image
docker build -t smart_buyer_backend_image_2 .

REM Run Docker container
docker run -p 5000:5000 smart_buyer_backend_image_2

REM Tag the image for Heroku registry
docker tag smart_buyer_backend_image_2 registry.heroku.com/smart-buyer-2/web

REM Push the image to Heroku registry
docker push registry.heroku.com/smart-buyer-2/web

REM Release the container on Heroku
heroku container:release web -a smart-buyer

REM Clean up - stop and remove the local container
FOR /F "tokens=*" %%i IN ('docker ps -q --filter "ancestor=smart_buyer_backend_image_2"') DO docker stop %%i
FOR /F "tokens=*" %%i IN ('docker ps -a -q --filter "ancestor=smart_buyer_backend_image_2"') DO docker rm %%i
