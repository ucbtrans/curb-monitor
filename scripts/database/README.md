## Setup env var
1. setup env var for credentials

To keep our aws credentails safe, please do not hardcode any credentials in the code. Instead we will set credentails in env vars, and read env vars from code.
In windows
```
$Env:aws_access_key_id = "xxxxxxxxxxxxxxxx"
$Env:aws_secret_access_key = "xxxxxxxxxxzz"
```

In Linux, macos
```
export aws_access_key_id=xxxxxxxxxxxx
export aws_secret_access_key=xxxxxxxx
```
