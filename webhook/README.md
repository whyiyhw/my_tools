# webhook
http to shell exec

## Lightweight pull and exec shell script application

in local linux , go build an execute file

use supervisor to up this app

## php_reload.sh use

change host, use a specific account to deploy app

```txt
origin_host="github.com"
deploy_user="github"
deploy_password="github"
```

- lastest
```shell
curl localhost:8080/api/webhook?token="233"&shell_name="php_reload"&params="path/to/code"&params="1"

# so your can configuration webhook  to trigger git pull & reload php_fpm

# diy your script  , you not need a heavy jenkins
```
