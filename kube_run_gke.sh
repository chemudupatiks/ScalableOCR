kubectl apply -f redis/redis-deployment.yaml
kubectl apply -f redis/redis-service.yaml

kubectl apply -f rabbitmq/rabbitmq-deployment.yaml
kubectl apply -f rabbitmq/rabbitmq-service.yaml

kubectl apply -f rest/rest-deployment.yaml 
kubectl apply -f rest/rest-service.yaml 
kubectl apply -f rest/rest-ingress-gke.yaml 

kubectl apply -f rest/logs-deployment.yaml 

kubectl apply -f worker/worker-deployment.yaml



