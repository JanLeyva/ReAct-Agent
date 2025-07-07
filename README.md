# WhatsApp Agent

<img src="docs/img/whatsapp-agent.svg" alt="whatsapp-agent">

This project is a sophisticated Telegram agent powered by a ReAct-based AI model. It leverages a vector database for efficient semantic search and is designed to be deployed on AWS with an EC2 instance and a Load Balancer. The agent can understand and respond to user queries, providing information about restaurants in Barcelona.

## Table of Contents
- [Project Overview](#project-overview)
- [Set up Project](#set-up-project)
- [Services](#services)
    - [Agent](#agent)
    - [Load Restaurants](#load-restaurants)
    - [Search Engine](#search-engine)
    - [Telegram Bot](#telegram-bot)
- [How it Works](#how-it-works)
- [Deployment - Infrastructure (AWS)](#deployment---infrastructure-aws)

## Project Overview

The WhatsApp Agent is a conversational AI designed to provide information about restaurants. It uses a combination of a powerful language model, a vector database, and a set of tools to understand and respond to user queries. The agent is exposed via a FastAPI application and can be integrated with various messaging platforms, with a reference implementation for Telegram.

## Set up Project

To set up the project, you will need to have Docker and Docker Compose installed. The project is containerized and can be run using the provided Docker Compose files.

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/whatsapp-agent.git
    cd whatsapp-agent
    ```

2.  **Set up the environment variables:**
    Create a `.env` file in the `services/agent` directory by copying the `.env.example` file. Fill in the required API keys and other configuration variables.

3.  **Run the project:**
    ```bash
    docker-compose -f docker-compose/docker-compose-pgvector.yaml up -d
    ```
    This will start the PostgreSQL vector database.

4.  **Run the agent:**
    ```bash
    cd services/agent
    docker build -t whatsapp-agent .
    docker run -p 80:80 --env-file .env whatsapp-agent
    ```

## Services

### Agent

The core of the project is the `ReActAgent`, which is a custom implementation of the ReAct (Reasoning and Acting) framework. The agent is responsible for processing user input, deciding which tools to use, and generating a response.

-   **`api.py`**: This file contains the FastAPI application that exposes the agent's functionality through a set of API endpoints. It handles requests from the Telegram bot and other clients.
-   **`react_agent.py`**: This file contains the implementation of the `ReActAgent`. It uses a language model to reason about the user's input and decide which tools to use. The agent's memory is connected to a PostgreSQL vector database, allowing it to store and retrieve information from past conversations.
-   **`tools.py`**: This file defines the tools that the agent can use to perform various tasks, such as searching for restaurants, getting directions, and looking up information on the web.

### Load Restaurants

The `load_restaurants` service is responsible for populating the vector database with information about restaurants. It uses the Google Maps API to fetch data about places and then processes it before uploading it to the database.

-   **`upload_place.py`**: This file contains the main logic for fetching data from the Google Maps API and uploading it to the vector database.
-   **`googlemaps_api.py`**: This file contains a wrapper for the Google Maps API, making it easy to fetch data about places.
-   **`place.py`**: This file defines the `Place` class, which is used to represent a restaurant or other place.

### Search Engine

The `search_engine` service provides the functionality for searching the vector database. It uses a combination of semantic search and keyword search to find the most relevant results.

-   **`vector_store.py`**: This file contains the `VectorStore` class, which provides an interface for interacting with the PostgreSQL vector database. It includes methods for semantic search, keyword search, and hybrid search.
-   **`distance_coordinates.py`**: This file contains a utility function for calculating the corners of a square around a given set of coordinates, which is used for location-based searches.

### Telegram Bot

The `telegram_bot` service provides a reference implementation of a Telegram bot that can be used to interact with the agent.

-   **`bot.py`**: This file contains the main logic for the Telegram bot. It uses the `aiogram` library to handle incoming messages and send responses back to the user.
-   **`config.py`**: This file contains the configuration for the Telegram bot, including the API key.

## How it Works

1.  A user sends a message to the Telegram bot.
2.  The Telegram bot forwards the message to the agent's API.
3.  The agent's API receives the message and passes it to the `ReActAgent`.
4.  The `ReActAgent` processes the message and decides which tools to use.
5.  If the agent needs to search for a restaurant, it uses the `search_engine` service to query the vector database.
6.  The `search_engine` service returns the most relevant results to the agent.
7.  The agent uses the results to generate a response, which is then sent back to the user through the Telegram bot.

## Deployment - Infrastructure (AWS)

The project is designed to be deployed on AWS using an EC2 instance and a Load Balancer. The `deployment.yaml` file in the `.github/workflows` directory contains a GitHub Actions workflow that automates the deployment process.

The workflow performs the following steps:

1.  Builds the Docker image for the agent.
2.  Pushes the Docker image to Amazon ECR.
3.  Connects to the EC2 instance via SSH.
4.  Pulls the latest Docker image from ECR.
5.  Stops and removes the old container.
6.  Runs the new container with the updated image.
