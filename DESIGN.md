# Design Decisions

## Web Scraping Tool

We will use **Beautiful Soup** for web scraping. It is a lightweight and easy-to-use library that is well-suited for parsing HTML and XML documents. It is also well-documented and has a large community, which will be helpful if we run into any issues.

## Resume Matching Model

We will use a model from **Hugging Face's Transformers** library for resume matching. This will give us access to a wide range of pre-trained models that can be fine-tuned for our specific needs. This will allow us to achieve high accuracy for text matching and professional text generation, and the ability to fine-tune the model will allow it to "learn" from feedback.

## Deployment

We will use **Docker** to containerize the application. This will make it easy to deploy the application in a local network and also to a cloud platform in the future. We will create a `Dockerfile` for both the frontend and the backend, and a `docker-compose.yml` file to manage the services. We will also create a `docker-compose.override.yml` file to allow for easy customization of the web app port.
