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

    make

Note:
Set the environment variable `TESTCONTAINERS_RYUK_DISABLED` as `true` to disable RYUK (TestContainer) while running the build

### Initialise/update dependencies
    
    make init_dependencies

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

    http://localhost:8000/docs

    http://localhost:8000/context/docs

### Run in production mode

    make fast_run

    http://localhost:80000/docs

    http://localhost:8000/context/docs

### Run a specific unit test file / test function

Run all tests in a directory or module

    make tests_unit_specific UNIT_TEST=tests_unit/dao

Run all tests in a file

    make tests_unit_specific UNIT_TEST=tests_unit/dao/test_customer_dao.py

Run a specific test function

    make tests_unit_specific UNIT_TEST=tests_unit/dao/test_customer_dao.py::test_customers_insert

### Run a specific integration test file / test function

Run all tests in a directory or module

    make tests_integration_specific INTEGRATION_TEST=tests_integration/routers

Run all tests in a file

    make tests_integration_specific INTEGRATION_TEST=tests_integration/routers/test_customer.py

Run a specific test function

    make tests_integration_specific INTEGRATION_TEST=tests_integration/routers/test_customer.py::test_customers_insert_read_delete

### Running with docker

Create docker image

    docker build --pull -t python-fastapi -f Dockerfile .

Run the created docker image

    docker run -it --rm --network=python-fastapi-network -e 'APP_DB_HOST=python-fastapi-postgres' -e 'PORT=8000' -p 8000:8000 python-fastapi

    http://localhost:8000