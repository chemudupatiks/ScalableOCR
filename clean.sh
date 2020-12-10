kubectl delete deployment workers rest-servers loggers rabbitmq redis
kubectl delete service rest-server rabbitmq redis
kubectl delete hpa rest-servers