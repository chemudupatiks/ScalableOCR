##
## You provide this to build your docker image
##

build: 
	docker build -f Dockerfile-worker -t lab7-worker:1.0 .

push:
	# docker login --username kchemudu
	docker tag lab7-worker:1.0 kchemudu/lab7-worker:1.0
	docker push kchemudu/lab7-worker:1.0

run: 
	docker container run --rm -it --name worker lab7-worker:1.0 

stop: 
	docker container stop worker 

kill:
	docker container kill worker
