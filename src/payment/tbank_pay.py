import hashlib
import string
import random
import aiohttp
from aiohttp import ClientSession


headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'Connection': 'keep-alive',
}


def get_random_id() -> str:
    string.ascii_letter = 'abcdefghijklmnopqrstuvwxyz1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    simvols = ''
    for i in range(0, 10):
        simvols += str(random.choice(string.ascii_letters))
    return simvols


def get_token(datas: dict):
    del datas['Token']
    items = []
    for i, j in datas.items():
        if type(j) is not dict:
            items.append({i: j})
    items.append({"Password": "60qa0kwm3e7vllle"})
    items = sorted(items, key=max)
    #print(''.join(str(i[list(i.keys())[0]]) for i in items))
    return str(hashlib.sha256(''.join(str(i[list(i.keys())[0]]) for i in items).encode('utf-8')).hexdigest())


async def init_payment(amount: int, description: str, user_id: int) -> dict:
    json = {
        "TerminalKey": "1730455815051",
        "Amount": amount,
        "OrderId": get_random_id(),
        "Token": "",
        "Description": description,
        "CustomerKey": f"{user_id}",
        "Recurrent": "Y",
        "PayType": "O",
        "Language": "ru",
    }
    json["Token"] = get_token(json)
    print('json к запросу Init:', json)
    async with ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as client:
        async with client.post('https://securepay.tinkoff.ru/v2/Init', headers=headers, json=json) as response:
            data = await response.json()
            print('json полученный после запроса Init: ', data)
            payment_id = data['PaymentId']
            url = data['PaymentURL']
            return {
                'payment_id': payment_id,
                'url': url
            }


async def check_payment(payment_id) -> bool:
    new_json = {
        "TerminalKey": "1730455815051",
        "Token": '',
        "PaymentId": payment_id
    }
    new_json['Token'] = get_token(new_json)
    print('json к запросу GetState: ', new_json)
    async with ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as client:
        async with client.post('https://securepay.tinkoff.ru/v2/GetState', headers=headers, json=new_json) as response:
            data = await response.json()
            print('json после запроса GetState', data)
            if data['Success'] != True:
                raise Exception(data['ErrorCode'])
            if data['Status'] != 'CONFIRMED':
                return False
            return True
