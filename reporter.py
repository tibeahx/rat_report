import os
import time
import requests
from fake_useragent import UserAgent

# change this address for the required one
reward_addr = "0x8A6b6C1E895bdEb4C83F0A625e24FAF54a003CF8"


def set_headers(token: str) -> dict[str, str]:
    ua = UserAgent
    headers = {
        'Accept': 'application/vnd.github+json',
        'Authorization': token,
        'User-Agent': str(ua.chrome),
        'X-GitHub-Api-Version': '2022-11-28',
        'Connection': 'keep-alive',
        'Accept-Language': 'ru',
    }

    return headers


def expose_rat_address(repo_url: str, token: str) -> str:
    try:
        resp = requests.get(repo_url, headers=set_headers(token))
        resp.raise_for_status()
        json_data = resp.json()
        
        rat_addr = ""
        target_key = 'body'
        if isinstance(json_data, dict):
            for issue in json_data:
                if target_key in issue:
                    value = issue[target_key]
                    target_substring = '(If Eligible)'
                    idx = value.find(target_substring)
                    if idx != -1:
                        found = idx + len(target_substring) + 1
                        rat_addr = value[found:].strip()

    except requests.exceptions.RequestException as err:
        print(f"error getting rat address: {err}")
        return ""
    
    print(f"found rat address: '{rat_addr}'")

    return rat_addr


def report_rat(rat_addr: str, repo_url: str, token: str):
    layout = (f"Reported addresses: '{rat_addr}\n"
              f"Description: 'mamy ebal'\n"
              f"Detailed Methodology & Walkthrough: mamy dauna ebal\n"
              f"Reward Address (If Eligible) {reward_addr}")

    opts = {
        'owner': 'LayerZero-Labs',
        'repo': 'sybil-report',
        'title': '[Sybil Report]',
        'body': layout,
    }

    try:
        response = requests.post(repo_url, json=opts, headers=set_headers(token))
        response.raise_for_status()
        return response

    except requests.exceptions.RequestException as err:
        print(f"An error occurred while reporting rat address: {err}")
        return None


def start(url: str, token: str):
    try:
        rat_addr = expose_rat_address(repo_url=url, token=token)
        if rat_addr:
            response = report_rat(rat_addr=rat_addr, repo_url=url, token=token)
            if response and response.status_code == 201:
                print(f"reported rat address: '{rat_addr}'")
            elif response:
                print(f"failed to report rat address: '{rat_addr}' with status: {response.status_code}")
            else:
                print(f"failed to report rat address: '{rat_addr}'")

    except Exception as err:
        print(f"An unexpected error occurred: {err}")


def main():
    token = os.getenv("TOKEN")
    url = "https://api.github.com/repos/LayerZero-Labs/sybil-report/issues"

    while True:
        start(url=url, token=token)
        time.sleep(0.5)


if __name__ == '__main__':
    main()
