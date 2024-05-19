import os
import asyncio
import aiohttp
from fake_useragent import UserAgent

# сhange this address for the required one
reward_addr = "0x8A6b6C1E895bdEb4C83F0A625e24FAF54a003CF8"


def set_headers(token: str) -> dict:
    ua = UserAgent()
    headers = {
        'Accept': 'application/vnd.github+json',
        'Authorization': f'Bearer {token}',
        'User-Agent': ua.chrome,
        'X-GitHub-Api-Version': '2022-11-28',
        'Connection': 'keep-alive',
        'Accept-Language': 'ru',
    }
    return headers


async def expose_rat_address(session: aiohttp.ClientSession, repo_url: str, token: str) -> str:
    headers = set_headers(token)
    rat_addr = set()
    
    try:
        async with session.get(repo_url, headers=headers, ssl=False) as resp:
            resp.raise_for_status()
            json_data = await resp.json()
        
        if isinstance(json_data, list):
            for issue in json_data:
                if 'body' in issue:
                    value = issue['body']
                    target_substring = '(If Eligible)'
                    idx = value.find(target_substring)
                    if idx != -1:
                        found = idx + len(target_substring) + 1
                        rat_addr = value[found:].strip()
                        break                     
    except aiohttp.ClientError as err:
        print(f"error getting rat address: {err}")
    
    print(f"found rat address: '{rat_addr}'")
    return rat_addr


async def report_rat(session: aiohttp.ClientSession, rat_addr: str, repo_url: str, token: str):
    layout = (f"Reported addresses: '{rat_addr}'\n"
              f"Description: 'mamy ebal'\n"
              f"Detailed Methodology & Walkthrough: mamy dauna ebal\n"
              f"Reward Address (If Eligible) {reward_addr}")

    opts = {
        'owner': 'LayerZero-Labs',
        'repo': 'sybil-report',
        'title': '[Sybil Report]',
        'body': layout,
    }

    headers = set_headers(token)
    try:
        async with session.post(repo_url, json=opts, headers=headers, ssl=False) as response:
            response.raise_for_status()
            return response
    except aiohttp.ClientError as err:
        print(f"error reporting rat: {err}")
        return None


async def start(url: str, token: str, semaphore: asyncio.Semaphore):
    async with semaphore:
        async with aiohttp.ClientSession() as session:
            rat_addr = await expose_rat_address(session, repo_url=url, token=token)
            if rat_addr:
                response = await report_rat(session, rat_addr=rat_addr, repo_url=url, token=token)
                if response and response.status == 201:
                    print(f"reported rat address: '{rat_addr}'")
                elif response:
                    print(f"failed to report rat address: '{rat_addr}' with status: {response.status}")
                else:
                    print(f"failed to report rat address: '{rat_addr}'")


async def main(threads_num: int):
    token = os.getenv("TOKEN")
    url = "https://api.github.com/repos/LayerZero-Labs/sybil-report/issues"
    ctx_manager = asyncio.Semaphore(threads_num)

    while True:
        tasks = [start(url=url, token=token, semaphore=ctx_manager) for _ in range(threads_num)]
        await asyncio.gather(*tasks)
        #sleep if needed
        #await asyncio.sleep(1)


if __name__ == '__main__':
    threads_num = 1  # increase if needed
    asyncio.run(main(threads_num))
