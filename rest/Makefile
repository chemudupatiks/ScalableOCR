##
## You provide this to build and push your docker images
##

build: 
	docker build -f Dockerfile-rest -t scalable-ocr-rest:1.0 .
	docker build -f Dockerfile-logs -t scalable-ocr-logs:1.0 .

push:
	# docker login --username kchemudu
	docker tag scalable-ocr-rest:1.0 kchemudu/scalable-ocr-rest:1.0
	docker tag scalable-ocr-logs:1.0 kchemudu/scalable-ocr-logs:1.0
	docker push kchemudu/scalable-ocr-rest:1.0
	docker push kchemudu/scalable-ocr-logs:1.0

run_rest: 
	docker container run --rm -it --name rest scalable-ocr-rest:1.0 

run_logs:
	docker container run --rm -it --name logs scalable-ocr-logs:1.0 

stop: 
	docker container stop rest 
	docker container stop logs 

kill:
	docker container kill rest
	docker container kill logs 
