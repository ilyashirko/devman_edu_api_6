# Post comics to VK group
This app download one random [comics](https://xkcd.com/) and post it on the VK group wall.  

## How to install
clone repo, activate virtual environment in the root folder, install requirements:
```
$ git clone https://github.com/ilyashirko/devman_edu_api_6
$ cd devman_edu_api_6
$ python3 -m venv env
$ source env/bin/activate
$ pip3 install -r requirements.txt
```

create VK group and save it id to .env file as `GROUP_ID`
create standalone [vk app](https://dev.vk.com) and get authorize token [here](https://vk.com/dev/implicit_flow_user), save it to .env  

Your .env will be look like:
```
VK_TOKEN=8sdf87s6d8f76s8d76f87s6df87s6d87f6s8d6f8s76df8s6df87sd6f8s6d87f6s8df68s7df68s6d
GROUP_ID=9987987987987
```

## Run app
```
python3 share_xkcd_comics.py