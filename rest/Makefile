##
## You provide this to build and push your docker images
##

build: 
	docker build -f Dockerfile-rest -t lab7-rest:1.0 .
	docker build -f Dockerfile-logs -t lab7-logs:1.0 .

push:
	# docker login --username kchemudu
	docker tag lab7-rest:1.0 kchemudu/lab7-rest:1.0
	docker tag lab7-logs:1.0 kchemudu/lab7-logs:1.0
	docker push kchemudu/lab7-rest:1.0
	docker push kchemudu/lab7-logs:1.0

run_rest: 
	docker container run --rm -it --name rest lab7-rest:1.0 

run_logs:
	docker container run --rm -it --name logs lab7-logs:1.0 

stop: 
	docker container stop rest 
	docker container stop logs 

kill:
	docker container kill rest
	docker container kill logs 
