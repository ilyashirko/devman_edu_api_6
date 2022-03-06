from urllib import response
import requests
from environs import Env
from urllib.parse import unquote, urlsplit
from random import randint
import os
import time


BASE_VK_URL = 'https://api.vk.com/method/'

def get_comics_metadata(comics_num=353):
    metadata_url = f'https://xkcd.com/{comics_num}/info.0.json'
    response = requests.get(metadata_url)
    response.raise_for_status
    return response.json()


def get_comics(url, comics_name):
    response = requests.get(url)
    response.raise_for_status
    with open(f'Files/{comics_name}', 'wb') as new_comics:
        new_comics.write(response.content)


def get_upload_url(vk_token):
    params = {
        'access_token': vk_token,
        'v': 5.131
    }
    response = requests.get(f'{BASE_VK_URL}photos.getWallUploadServer', params=params)
    print(f'1\n\n{response.text}')
    response.raise_for_status
    return response.json()['response']['upload_url']


def get_upload_info(upload_url, photo, vk_token):
    params = {
        'access_token': vk_token,
        'v': 5.131
    }
    with open(photo, 'rb') as file:
        files = {'photo': file}
        response = requests.post(upload_url, params=params, files=files)
        print(response)
        print(f'2\n\n{response.text}')
        response.raise_for_status
        return response.json()


def save_wall_photo(upload_info, vk_token):
    params = {
        'photo': upload_info['photo'],
        'server': upload_info['server'],
        'hash': upload_info['hash'],
        'access_token': vk_token,
        'v': 5.131
    }
    photo_detailes = requests.post(f'{BASE_VK_URL}photos.saveWallPhoto', params=params)
    photo_detailes.raise_for_status
    return photo_detailes.json()


def post_photo_wall(photo_detailes, group_id, vk_token, text):
    params = {
        'owner_id': -group_id,
        'access_token': vk_token,
        'v': 5.131,
        'attachments': f'photo{photo_detailes["response"][0]["owner_id"]}_{photo_detailes["response"][0]["id"]}',
        'message': text
    }
    response = requests.post('https://api.vk.com/method/wall.post', params=params)
    response.raise_for_status


def how_much_comics():
    response = requests.get('https://xkcd.com/info.0.json')
    response.raise_for_status
    return response.json()['num']


if __name__ == '__main__':
    env = Env()
    env.read_env()

    client_id = env.int('VK_CLIENT_ID')
    vk_token = env.str('VK_TOKEN')
    group_id = env.int('GROUP_ID')
    
    
    

    comics_num = randint(1, how_much_comics())
    print(f'TRYED GET {comics_num}')
    
    comics_metadata = get_comics_metadata(comics_num)
    comics_url = comics_metadata['img']
    author_comment = comics_metadata['alt']
    _, comics_name = os.path.split(unquote(urlsplit(comics_url).path))
    get_comics(comics_url, comics_name)

    upload_url = get_upload_url(vk_token)
    try:
        upload_info = get_upload_info(upload_url, f'Files/{comics_name}', vk_token)
    except requests.exceptions.JSONDecodeError:
        pass
    photo_detailes = save_wall_photo(upload_info, vk_token)
    post_photo_wall(photo_detailes, group_id, vk_token, author_comment)
    time.sleep(3)
    
    