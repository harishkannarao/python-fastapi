# python-fastapi
Repository to learn and explore API and Backend service with Python using FastAPI Framework

## Tools Required

* uv `0.8.15`
* make `3.81`
* git `latest`
* pycharm `latest`

## Commands

### Default command

    make -l

### Initialise/update dependencies
    
    make -l init_dependencies

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

    docker run -it --rm -p 8000:80 python-fastapi

    http://localhost:8000