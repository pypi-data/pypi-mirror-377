from typing import Optional, Union
from tls_client import Session


class Client:
    def __init__(self, token: str) -> None:
        self.token = token
        self.session = Session(
            client_identifier="firefox_120", random_tls_extension_order=True
        )
        # self.headers = {
        #     "Accept-Encoding": "gzip, deflate, br",
        #     "Accept-Language": "en-US,en;q=0.9",
        #     "Cache-Control": "no-cache",
        #     "Connection": "keep-alive, Upgrade",
        #     "Host": "gateway.discord.gg",
        #     "Origin": "https://discord.com",
        #     "Pragma": "no-cache",
        #     "Sec-WebSocket-Extensions": "permessage-deflate",
        #     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0",
        # }
        # self.ws = WebSocket()


class Joiner:
    def __init__(self) -> None:
        pass

    def joinGuild():
        ...


class DM:
    def __init__(self, client: Session) -> None:
        self.client = client

    def openDM(self, user_id: Union[str, int]) -> bool:
        headers = {
            'authority': 'discord.com',
            'accept': '*/*',
            'accept-language': 'en-US',
            'authorization': '',
            'content-type': 'application/json',
            'cookie': '__dcfduid=ae1d3a502d8711ee8e028bb9d766bb7a; __sdcfduid=ae1d3a512d8711ee8e028bb9d766bb7a23864b4cf968a0426d0f19ac93eb8862ffe11052a2d86fe9d7f36c94340e9557; __stripe_mid=adeab7e6-1f2f-4e7c-af50-29ef7a719c66b7d962; cf_clearance=oktZnjY3QFk0ZMXaA2B899bjcd9Q6l62NQZHmp_aIZ0-1708642785-1.0-ASICb9Pb+YmGSuZuwb3QNXud8wwxqkB2+GMQk/JnpAy0bdBYg1LeOEeuzNkw5CqMNLB62twL0ZXoUIc5EejwvZQ=; __cfruid=5923279870df42530e0310a6ceef592b56cc5ddf-1708727291; _cfuvid=_4d.COSoQMhjgL.OgxdDDEFBH_YmNvcNgCqKqmb3R5E-1708727291541-0.0-604800000',
            'origin': 'https://discord.com',
            'referer': 'https://discord.com/channels/1202055614595862598/1209339091930325003',
            'sec-ch-ua': '"Not?A_Brand";v="8", "Chromium";v="108"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) discord/1.0.9034 Chrome/108.0.5359.215 Electron/22.3.26 Safari/537.36',
            'x-context-properties': 'e30=', # {}
            'x-debug-options': 'bugReporterEnabled',
            'x-discord-locale': 'en-US',
            'x-discord-timezone': 'America/Chicago',
            'x-super-properties': 'eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiRGlzY29yZCBDbGllbnQiLCJyZWxlYXNlX2NoYW5uZWwiOiJzdGFibGUiLCJjbGllbnRfdmVyc2lvbiI6IjEuMC45MDM0Iiwib3NfdmVyc2lvbiI6IjEwLjAuMjI2MzEiLCJvc19hcmNoIjoieDY0IiwiYXBwX2FyY2giOiJpYTMyIiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV09XNjQpIEFwcGxlV2ViS2l0LzUzNy4zNiAoS0hUTUwsIGxpa2UgR2Vja28pIGRpc2NvcmQvMS4wLjkwMzQgQ2hyb21lLzEwOC4wLjUzNTkuMjE1IEVsZWN0cm9uLzIyLjMuMjYgU2FmYXJpLzUzNy4zNiIsImJyb3dzZXJfdmVyc2lvbiI6IjIyLjMuMjYiLCJjbGllbnRfYnVpbGRfbnVtYmVyIjoyNjgzNTYsIm5hdGl2ZV9idWlsZF9udW1iZXIiOjQ0MTQyLCJjbGllbnRfZXZlbnRfc291cmNlIjpudWxsfQ==',
        }

        payload = {"recipients":[str(user_id)]}

        response = self.client.post('https://discord.com/api/v9/users/@me/channels', headers=headers, json=payload)
        if response.status_code == 200:
            return True
        return False


    def sendDM():
        ...


class Friend:
    def __init__(self, client: Session) -> None:
        self.common_headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.5",
            "Authorization": "",
            "Connection": "keep-alive",
            "Content-Type": "application/json",
            "Host": "discord.com",
            "Origin": "https://discord.com",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
            "X-Debug-Options": "bugReporterEnabled",
            "X-Discord-Locale": "en-GB",
            "X-Discord-Timezone": "America/Chicago",
            "X-Super-Properties": "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiRmlyZWZveCIsImRldmljZSI6IiIsInN5c3RlbV9sb2NhbGUiOiJlbi1VUyIsImJyb3dzZXJfdXNlcl9hZ2VudCI6Ik1vemlsbGEvNS4wKChXaW5kb3dzIE5UIDEwLjA7IFdpbjY0OyB4NjQ7IHJ2OjEyMC4wKSkpIiwiYnJvd3Nlcl92ZXJzaW9uIjoiMTIwLjAiLCJvc192ZXJzaW9uIjoiMTAiLCJyZWZlcnJlciI6IiIsInJlZmVycmluZ19kb21haW4iOiIiLCJyZWZlcnJlcl9jdXJyZW50IjoiIiwicmVmZXJyaW5nX2RvbWFpbl9jdXJyZW50IjoiIiwicmVsZWFzZV9jaGFubmVsIjoic3RhYmxlIiwiY2xpZW50X2J1aWxkX251bWJlciI6MjUzMDQ3LCJjbGllbnRfZXZlbnRfc291cmNlIjpudWxsLCJkZXNpZ25faWQiOjB9",
        }
        self.client = client

    def send_friend_by_id(self, user_id: str, mutual_guild_id: str):
        # {"op": 14, "d": {"guild_id": mutual_guild_id, "members": [user_id]}}

        headers = {
            **self.common_headers,
            "Referer": f"https://discord.com/channels/{mutual_guild_id}",
            "X-Context-Properties": "eyJsb2NhdGlvbiI6IlVzZXIgUHJvZmlsZSJ9",  # {"location":"User Profile"}
        }
        url = f"https://discord.com/api/v9/users/@me/relationships/{user_id}"
        return self.client.put(url, headers=headers, json={})

    def send_friend_by_username(self, username: str, discrim: Optional[str] = None):
        headers = {
            **self.common_headers,
            "Referer": "https://discord.com/channels/@me",
            "X-Context-Properties": "eyJsb2NhdGlvbiI6IkFkZCBGcmllbmQifQ==",  # {"location":"Add Friend"}
        }
        url = "https://discord.com/api/v9/users/@me/relationships"
        payload = {"username": username, "discriminator": discrim}
        return self.client.post(url, headers=headers, json=payload)


class UDCord(Friend, DM, Joiner):
    def __init__(self) -> None:
        super().__init__()
