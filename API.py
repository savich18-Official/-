import requests
import json
import logging
import os
from typing import Dict, Tuple

from dotenv import load_dotenv, find_dotenv


load_dotenv(find_dotenv())
KEY = os.getenv('KEY')
result_request = dict()
async def request_data(result: Tuple) -> Dict:
    """
    Функция для формирования URL запроса и возвращения полученного результата
    """
    sort_field = result[2]
    sort_type = result[3]
    limit = result[4]
    type_number = result[5]
    search_range = result[6]
    page = result[7]

    url = "https://api.kinopoisk.dev/v1/movie?selectFields=id%20name%20type%20rating%20year%20poster&sortField={sort_field}&sortType={sort_type}&page={page}&limit={limit}&typeNumber={type_number}&rating.kp={search_range}"\
        .format(sort_field=sort_field,
                page=page,
                sort_type=sort_type,
                limit=limit,
                type_number=type_number,
                search_range=search_range)

    logging.info(f'Сформированный кортеж запроса: {result}\nURL ссылка запроса: {url}')

    headers = {'X-API-KEY': KEY}
    response = requests.request('GET', url=url, headers=headers)
    data = json.loads(response.text)
    result_request[result[0]] = data['docs']

    # with open('test.json', 'w', encoding='utf-8') as file:
    #     json.dump(data, file, indent=4, ensure_ascii=False)

    return result_request
