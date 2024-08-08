include .env

network:
	docker network inspect $(NETWORK_NAME) >/dev/null || docker network create $(NETWORK_NAME)

image:
	docker build -t $(CONTAINER_IMAGE):local -f Containerfile.dev .

up: image
	@-docker kill $(PROJECT_NAME)
	docker run -d --name $(PROJECT_NAME) --rm --network $(NETWORK_NAME) -p 8501:8501 --env-file .env -v $(PWD)/chat:/app $(CONTAINER_IMAGE):local

down:
	@-docker rm -f $(PROJECT_NAME)

sleep-%:
	sleep $(@:sleep-%=%)

dev: network down sleep-5 up
