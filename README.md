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
curl -X POST "https://api.telegram.org/bot<TOKEN>/setWebhook" -d "url=endpoint"
```

```
curl -X POST "https://api.telegram.org/bot<TOKEN>/deleteWebhook"
```


## 1. Connect to EC2

```
ssh -i ~/.ssh (your .pem key) ec2-user@Public IPv4 address
```

### 2. install docker

```
sudo yum update
sudo yum install docker
```

Start the Docker service:
```
sudo systemctl start docker
```
Add the ec2-user to the docker group so that you can run Docker commands without using sudo:
```
sudo usermod -a -G docker ec2-user
```

### 3. Send files SSH

```
scp -i ~/.ssh/xxxx.pem .env ec2-user@xxx.xx.xx:.env
```

## Webhook example
```
{
  "update_id": 123456789,
  "message": {
    "message_id": 1,
    "from": {
      "id": 12345678,
      "is_bot": false,
      "first_name": "John",
      "last_name": "Doe",
      "username": "johndoe"
    },
    "chat": {
      "id": 12345678,
      "first_name": "John",
      "last_name": "Doe",
      "username": "johndoe",
      "type": "private"
    },
    "date": 1678886400,
    "text": "Hello, bot! How are you?"
  },
  "secret_token": "XXX"
}
```
```
curl -X POST \             
     -H "Content-Type: application/json" \
     -d "$RESPONSE" \
     "$URL_TELEGRAM"
```

Test lambda image locally
```
curl -X POST http://localhost:9000/2015-03-31/functions/function/invocations -d ''
```

## TODO
modify pyproject in two env one for dev with test and extra dependencies other with just the production lib need.

## Enriche Agent Output

Output Example:
```
Base in your request we found:\n\n

1: Equilibribcn: This Italian restaurant is a cozy haven serving up delicious cuisine with a focus on pizza. The inviting atmosphere makes for easy conversation, while the high-quality food and excellent service have reviewers raving. Standout dishes include the signature pizzas with delicious crusts. With reasonable prices offering great value, this establishment is a great spot for a pleasant dining experience. The warm and welcoming ambiance makes it an ideal location for return visits, as evident from the loyal customer base. Whether you're looking for a casual night out or a satisfying meal, this Italian restaurant is a great choice, offering a unique blend of quality, value, and cozy charm.\n

2: Can Sardi Eixample Abi Group: This Italian-inspired restaurant offers a warm and inviting atmosphere, perfect for a casual dining experience. The menu features traditional Italian flavors with a twist, including signature dishes like focaccia and Mortazza. With a focus on personal service, the restaurant provides a welcoming ambiance that keeps customers coming back. The availability of good coffee and wine suggests a mid-range price point. Overall, it's an excellent spot to enjoy a delicious meal and a drink, with a unique approach to traditional Italian cuisine that sets it apart. Whether you're looking for a relaxing bite or a drink, this restaurant is a great choice, offering a cozy and inviting vibe that's sure to leave you wanting more.\n

3: Ristorante Pizzeria Il Piccolo Focone: This cozy trattoria-style pizzeria serves high-quality, thin-crust pizzas with fresh ingredients, including gluten-free options. The atmosphere is inviting and pleasant, with reasonable prices and attentive, friendly service. Standout features include homemade tomato sauce and exceptional pizza dough. The menu also offers popular set lunch options and delicious desserts like tiramisu. While some inconsistencies have been noted, the overall consensus is positive, making this pizzeria a great option for those seeking a satisfying Italian dining experience. With its excellent pizzas and welcoming vibe, it's an ideal choice for a casual, yet satisfyin
```

#### Improvements - TODO:
- [ ] make a summary of a summary of the restaurant with two sentences. 
- [X] Include number and link.
- [X] Restaurant name in bold.
