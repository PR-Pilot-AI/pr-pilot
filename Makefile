# Variables
VERSION := $(shell cat version.txt)
APP_IMAGE_NAME := pr-pilot-app
WORKER_IMAGE_NAME := pr-pilot-worker
NGINX_IMAGE_NAME := pr-pilot-static
REGISTRY_URL := us-west2-docker.pkg.dev/darwin-407004/pr-pilot

# Phony Targets
.PHONY: logs build-static build-docker docker-push deploy create-k8s-secrets makemigrations

# Logs
logs:
	stern -l app=pr-pilot | grep -v "/health"

# Build Targets
build-static:
	python manage.py collectstatic --no-input

build-docker: build-static
	docker build --platform linux/amd64 -t $(APP_IMAGE_NAME):$(VERSION) .
	docker build --platform linux/amd64 -t $(WORKER_IMAGE_NAME):$(VERSION) -f Dockerfile.worker .
	docker build --platform linux/amd64 -t $(NGINX_IMAGE_NAME):$(VERSION) -f nginx/Dockerfile nginx

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

# Make Migrations
makemigrations:
	env $(cat local.env | xargs) python manage.py makemigrations

ngrok:
	ngrok http --domain=helping-willing-seasnail.ngrok-free.app 8000

pr-description:
	# Generate title and PR description (requires PR_NUMBER env var to be set)
	pilot --no-spinner task -f prompts/generate_pr_description.md.jinja2
