This is the readme for the the vacation manager software


docker build -t vacation_manager .

docker run -ti --network=host -v $(pwd)/website/database:/app/website/database  vacation_manager

