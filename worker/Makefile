##
## You provide this to build your docker image
##

build: 
	docker build -f Dockerfile-worker -t scalable-ocr-worker:1.0 .

push:
	# docker login --username kchemudu
	docker tag scalable-ocr-worker:1.0 kchemudu/scalable-ocr-worker:1.0
	docker push kchemudu/scalable-ocr-worker:1.0

run: 
	docker container run --rm -it --name worker scalable-ocr-worker:1.0 

stop: 
	docker container stop worker 

kill:
	docker container kill worker
