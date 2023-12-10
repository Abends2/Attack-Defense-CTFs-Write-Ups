# AD Exploitation Training
This is a collection of small services to train exploit development. In addition to this you will need some iptables magic to DNAT some private IP addresses to the corresponding ports to make it feel like there are actually multiple other teams with an identical setup.

## Deployment
An example deployment script looks as follows (untested):
```
#!/bin/sh

export DEBIAN_FRONTEND=noninteractive && \
apt-get update && \
apt-get upgrade -y && \
apt-get install -y apt-transport-https ca-certificates curl gnupg2 software-properties-common git && \
curl -fsSL https://download.docker.com/linux/debian/gpg | apt-key add - && \
add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/debian $(lsb_release -cs) stable" && \
apt-get update && \
apt-get install -y docker-ce docker-compose && \
git clone https://github.com/ldruschk/ad_exploitation_training.git && \
cd ad_exploitation_training && \
cat > config.env << EOF && docker-compose up -d
REDIS_HOST=redis
SECRET_KEY=set_something_here_which_you_do_not_share
SERVICE_COUNT=3

SERVICE_00_FLAG=enotraining{place_this_flag_in_CTFd}
SERVICE_00_THRESHOLD=1

SERVICE_01_FLAG=enotraining{place_this_flag_in_CTFd}
SERVICE_01_THRESHOLD=40
SERVICE_01_TEAMCOUNT=12

SERVICE_02_FLAG=enotraining{place_this_flag_in_CTFd}
SERVICE_02_THRESHOLD=40
SERVICE_02_TEAMCOUNT=12
EOF

```

## iptables
TODO: document the iptable setup
