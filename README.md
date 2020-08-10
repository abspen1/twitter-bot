# Twitter Bot Implementing Redis Database 

This is messing around learning python using tweepy and twitter API to automate twitter functions. Some functions used in this are 
tweeting, replying to mentions, following users back and more. Most of the examples I've seen online were reading and writing from files, however, in my opinion redis is as easy, if not easier, to use.

## Prerequisites
**Twitter Developer Set Up**
* Sign into Twitter at apps.twitter.com
* Create a new application and fill out your information
* Generate your access token
* Write down your needed keys
  * Consumer ID
  * Consumer Secret Key
  * Key ID
  * Secret Key ID

**Redis Setup**
* Download redis and activate your redis server, a simple youtube search will do
* Start running your redis-server
* Next open your redis-cli
  * Be sure to change the requirepass within your config to secure your server
  * Within redis-cli// > config get requirepass
    1. "requirepass"
    2. "This Will Be Empty"
* Set your password
  * Within redis-cli// > config set requirepass yourPasswordHere (recommended at least 32 characters long)



## Running

**This is built to be ran 24/7 using docker.**

```bash
docker pull 10.10.10.1:5000/bot-name \
&& docker run -d \
  --name bot_name \
  --restart unless-stopped \
  -e CONSUMER_KEY="some consumer ID" \
  -e CONSUMER_SECRET="some consumer secret KEY" \
  -e KEY="some key ID" \
  -e SECRET="some secret key ID" \
  -e REDIS_PASS="some password" \
  10.10.10.1:5000/bot-name
```

## Build & Push 

**Bot Container**
```bash
# Make sure you are in the directory that has your Dockerfile and bot script

docker build --no-cache -t 10.10.10.1:5000/bot-name .

docker push 10.10.10.1:5000/bot-name
```

### Contributions are welcomed! 💚
**Talk to me here if you have any ideas [![Issues][1.4]][1]

**Check out my personal bot account here: [![Twitter][1.2]][2]**



<!-- link to issues page -->

[1]: https://github.com/abspen1/twitter-bot/issues

<!-- links to your social media accounts -->

[2]: https://twitter.com/interntendie

<!-- icons without padding -->

[1.2]: http://i.imgur.com/wWzX9uB.png (twitter icon without padding)
[1.4]: https://imgur.com/gallery/oiBlB (mail icon without padding)