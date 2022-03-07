import os

from random import randint
from urllib.parse import unquote, urlsplit

import requests

from environs import Env

BASE_VK_URL = 'https://api.vk.com/method/'

API_VERSION = 5.131


def get_comics_metadata(comics_num=353):
    metadata_url = f'https://xkcd.com/{comics_num}/info.0.json'
    response = requests.get(metadata_url)
    response.raise_for_status
    return response.json()


def get_comics_image(url, comics_name):
    response = requests.get(url)
    response.raise_for_status
    with open(comics_name, 'wb') as new_comics:
        new_comics.write(response.content)


def get_upload_url(vk_token):
    params = {
        'access_token': vk_token,
        'v': API_VERSION
    }
    response = requests.get(
        f'{BASE_VK_URL}photos.getWallUploadServer',
        params=params
    )
    response.raise_for_status
    return response.json()['response']['upload_url']


def get_upload_info(upload_url, photo, vk_token):
    params = {
        'access_token': vk_token,
        'v': API_VERSION
    }
    with open(photo, 'rb') as file:
        files = {'photo': file}
        response = requests.post(upload_url, params=params, files=files)
        response.raise_for_status
        return response.json()


def save_wall_photo(upload_info, vk_token):
    params = {
        'photo': upload_info['photo'],
        'server': upload_info['server'],
        'hash': upload_info['hash'],
        'access_token': vk_token,
        'v': API_VERSION
    }
    photo_detailes = requests.post(
        f'{BASE_VK_URL}photos.saveWallPhoto',
        params=params
    )
    photo_detailes.raise_for_status
    return photo_detailes.json()


def post_photo_wall(photo_detailes, group_id, vk_token, text):
    params = {
        'owner_id': -group_id,
        'access_token': vk_token,
        'v': API_VERSION,
        'attachments': (
            f'photo{photo_detailes["response"][0]["owner_id"]}_'
            f'{photo_detailes["response"][0]["id"]}'
        ),
        'message': text
    }
    response = requests.post(
        'https://api.vk.com/method/wall.post',
        params=params
    )
    response.raise_for_status


def how_much_comics():
    response = requests.get('https://xkcd.com/info.0.json')
    response.raise_for_status
    return response.json()['num']


if __name__ == '__main__':
    env = Env()
    env.read_env()

    vk_token = env.str('VK_TOKEN')
    group_id = env.int('GROUP_ID')

    try:
        comics_num = randint(1, how_much_comics())
        comics_metadata = get_comics_metadata(comics_num)
        comics_url = comics_metadata['img']
        author_comment = comics_metadata['alt']
        _, comics_name = os.path.split(unquote(urlsplit(comics_url).path))
        get_comics_image(comics_url, comics_name)

        upload_url = get_upload_url(vk_token)
        upload_info = get_upload_info(upload_url, comics_name, vk_token)
        photo_detailes = save_wall_photo(upload_info, vk_token)
        post_photo_wall(photo_detailes, group_id, vk_token, author_comment)

    except requests.exceptions.JSONDecodeError as error:
        print(f'Sorry, broken JSON from vk API.\n\n{error}')

    except requests.exceptions.HTTPError as error:
        print(f'Sorry, connection error:\n\n{error}')

    finally:
        os.remove(comics_name)
