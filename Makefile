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
# Push Docker images to the registry
# Tags images with both version and latest
# Pushes both tags to the registry
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
# Deploys the application using Helm
# Upgrades or installs the Helm chart with the specified version
deploy:
	helm upgrade --install pr-pilot ./helm-chart --set image.tag=$(VERSION)

# Create Private Key Secret
# Creates a Kubernetes secret for the private key
create-private-key-secret:
	kubectl create secret generic pr-pilot-private-key --from-file=github_app_private_key.pem

# Kubernetes Secrets
# Deletes and recreates Kubernetes secrets from the k8s.env file
create-k8s-secrets:
	kubectl delete secret pr-pilot-secret
	kubectl create secret generic pr-pilot-secret --from-env-file=k8s.env

# Make Migrations
# Runs Django makemigrations command with environment variables from local.env
makemigrations:
	env $(cat local.env | xargs) python manage.py makemigrations

# Ngrok
# Starts ngrok with a specified domain
ngrok:
	ngrok http --domain=helping-willing-seasnail.ngrok-free.app 8000

# PR Description
# Generates title and PR description (requires PR_NUMBER env var to be set)
pr-description:
	pilot --no-spinner task -f prompts/generate_pr_description.md.jinja2

# Daily Report
# Generates daily report
# Uses a specific prompt file for the task
daily-report:
	pilot task -f prompts/slack-report.md.jinja2

redis-docker:
	docker run -d -p 6379:6379 redis