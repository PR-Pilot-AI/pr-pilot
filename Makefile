# Variables
VERSION := $(shell cat version.txt)
APP_IMAGE_NAME := pr-pilot-app
WORKER_IMAGE_NAME := pr-pilot-worker
NGINX_IMAGE_NAME := pr-pilot-static
REGISTRY_URL := us-west2-docker.pkg.dev/darwin-407004/pr-pilot

# Phony Targets
.PHONY: logs build-static build-docker docker-push deploy create-k8s-secrets

grafana:
	export POD_NAME=$(kubectl get pods --namespace monitoring -l "app.kubernetes.io/name=grafana,app.kubernetes.io/instance=grafana" -o jsonpath="{.items[0].metadata.name}")
	kubectl --namespace monitoring port-forward $POD_NAME 3000

# Logs
logs:
	stern -l app=pr-pilot | grep -v "/health"

# Build Targets
build-static:
	python manage.py collectstatic --no-input

build-docker: build-static
	docker build -t $(APP_IMAGE_NAME):$(VERSION) .
	docker build -t $(WORKER_IMAGE_NAME):$(VERSION) -f Dockerfile.worker .
	docker build -t $(NGINX_IMAGE_NAME):$(VERSION) -f nginx/Dockerfile nginx

# Docker Push
docker-push: build-docker
	docker tag $(APP_IMAGE_NAME):$(VERSION) $(REGISTRY_URL)/$(APP_IMAGE_NAME):$(VERSION)
	docker tag $(APP_IMAGE_NAME):$(VERSION) $(REGISTRY_URL)/$(APP_IMAGE_NAME):latest
	docker push $(REGISTRY_URL)/$(APP_IMAGE_NAME):$(VERSION)
	docker push $(REGISTRY_URL)/$(APP_IMAGE_NAME):latest
	docker tag $(WORKER_IMAGE_NAME):$(VERSION) $(REGISTRY_URL)/$(WORKER_IMAGE_NAME):$(VERSION)
	docker tag $(WORKER_IMAGE_NAME):$(VERSION) $(REGISTRY_URL)/$(WORKER_IMAGE_NAME):latest
	docker push $(REGISTRY_URL)/$(WORKER_IMAGE_NAME):$(VERSION)
	docker push $(REGISTRY_URL)/$(WORKER_IMAGE_NAME):latest
	docker tag $(NGINX_IMAGE_NAME):$(VERSION) $(REGISTRY_URL)/$(NGINX_IMAGE_NAME):$(VERSION)
	docker tag $(NGINX_IMAGE_NAME):$(VERSION) $(REGISTRY_URL)/$(NGINX_IMAGE_NAME):latest
	docker push $(REGISTRY_URL)/$(NGINX_IMAGE_NAME):$(VERSION)
	docker push $(REGISTRY_URL)/$(NGINX_IMAGE_NAME):latest

# Deploy
deploy:
	helm upgrade --install pr-pilot ./helm-chart --set image.tag=$(VERSION)

create-private-key-secret:
	kubectl create secret generic pr-pilot-private-key --from-file=github_app_private_key.pem

# Kubernetes Secrets
create-k8s-secrets:
	kubectl delete secret pr-pilot-secret
	kubectl create secret generic pr-pilot-secret --from-env-file=k8s.env
