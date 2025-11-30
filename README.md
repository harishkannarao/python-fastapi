# python-fastapi
Repository to learn and explore API and Backend service with Python using FastAPI Framework

## Tools Required

* uv `0.8.15`
* make `3.81`
* git `latest`
* pycharm `latest`

## IntelliJ pytest setup

    settings -> Python -> Integrated Tools -> Testing -> Default test runner -> pytest

## Commands

### Default command

    make -l

### Initialise/update dependencies
    
    make -l init_dependencies

### Run postgres database server using docker compose

Docker dependencies needs to be started using docker compose before running the build or starting the api

##### Pull the latest images of docker services

    docker compose -f docker-compose.yml pull

##### Start docker services

    docker compose -f docker-compose.yml up --build -d

##### Stop docker services

    docker compose -f docker-compose.yml down -v
    

### Run in development mode

    make fast_dev

    http://localhost:8000

### Run in production mode

    make fast_run

    http://localhost:8000

### Running with docker

Create docker image

    docker build --pull -t python-fastapi -f Dockerfile .

Run the created docker image

    docker run -it --rm --env PORT=8000 -p 8000:8000 python-fastapi

    http://localhost:8000