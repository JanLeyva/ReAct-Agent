# WhatsApp Agent

<img src="docs/img/whatsapp-agent.svg" alt="whatsapp-agent">


### Llamaindex: building agents and multi-agent systems with AgentWorkflow in LlamaIndex

## To check ECS  Fargate scale to 0
[link](https://medium.com/qest/ecs-scale-to-zero-using-cloudfront-8b7dcb61b59b)


## Log in to aws ecr to Pull

**Disclaimer:** use sudo docker login instead of docker login to later pull the image (otherwise no permision is used).
aws ecr get-login-password --region eu-north-1 | sudo docker login --username AWS --password-stdin account_id.dkr.ecr.eu-north-1.amazonaws.com


## Log in to aws ecr to Pull

**Disclaimer:** use sudo docker login instead of docker login to later pull the image (otherwise no permision is used).
aws ecr get-login-password --region eu-north-1 | sudo docker login --username AWS --password-stdin .dkr.ecr.eu-north-1.amazonaws.com


docker pull .dkr.ecr.eu-north-1.amazonaws.com/telegram_agent:latest

## Enable/Disable Telegram WebHook

### Enable
```
curl -X POST "https://api.telegram.org/bot8089666445:TOKEN/setWebhook" -d "url=endpoint"
```

```
curl -X POST "https://api.telegram.org/bot8089666445:TOKEN/deleteWebhook"
```
