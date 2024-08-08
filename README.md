# Streamlit Chat

JemberAI Chat is a demo chat application built with Streamlit, that integrates with the [Data Intake RAG Service](https://github.com/jemberai/data-intake-rag-service).

## Installation

 Pull image from the container registry.

```bash
docker pull quay.io/jember.ai/streamlit-chat
```

## Usage

### Deployment Env Vars

Be sure to customize the following variables.

```
OPENAI_API_KEY=sk-...
DATA_INTAKE_URL=https://...
DATA_INTAKE_CLIENT_ID=set-me...
DATA_INTAKE_CLIENT_SECRET=set-me...
```

Checkout the [.env.example](.env.example) file for all the environment variables.

### Local Dev

The [Containerfile.dev](Containerfile.dev) file (used in the local image) has hot-reloading enabled.

1. `git clone git@github.com:jemberai/streamlit-chat.git`

1. Copy `.env.example` into new file `.env`

1. Next, set the needed environment variables within the `.env` file (see above)

1. Run `make dev`

1. Open [http://localhost:8501](http://localhost:8501) in a browser

1. Once done, to clean up the docker containers `make down`
