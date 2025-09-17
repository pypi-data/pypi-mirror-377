import time
import requests
from terminut import log
from typing import Dict
from enum import Enum


class Services(Enum):
    CAPSOLVER = "https://api.capsolver.com"
    ANTICAPTCHA = "https://api.anti-captcha.com"
    CAPBYPASS = "https://api.capbypass.com"
    CAPMONSTER = "https://api.capmonster.cloud"
    HCOPTCHA = "https://api.hcoptcha.com/api"
    CAPGURU = "http://api.captcha.guru"
    _24CAP = "https://24captcha.online"
    DORTCAP = "https://api.dortware.club"
    DEXVCAP = "http://api.dexv.lol"

    @staticmethod
    def get_services():
        return {service.name: service.value for service in Services}


class Solver:
    def __init__(
        self,
        session: requests.Session,
        service: str = "CAPSOLVER",
        cap_key: str = None,
        site_key: str = "4c672d35-0701-42b2-88c3-78380b0db560",
        site_url: str = "https://discord.com",
        rq_data: str = None,
        user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/122.0",
    ):
        if not cap_key:
            raise ValueError("A captcha service key is required to solve the captcha.")

        self.session = session
        self.service = Services[service]
        self.cap_key = cap_key
        self.site_key = site_key
        self.site_url = (
            site_url if site_url.startswith("http") else f"https://{site_url}"
        )
        self.rq_data = rq_data
        self.user_agent = user_agent

    def solve_captcha(self) -> str:
        domain = self.service.value

        solver_functions = {
            Services.HCOPTCHA: self.solve_hcop,
            Services.DORTCAP: self.dortcap_solver,
            Services.CAPGURU: self.solve_secondary,
            Services._24CAP: self.solve_secondary,
        }

        if self.service in solver_functions:
            return solver_functions[self.service](domain)
        else:
            return self.solve_generic(domain)

    def solve_generic(self, domain: str, task_type: str = "HCaptchaTask") -> str:
        try:
            data = {
                "clientKey": self.cap_key,
                "task": {
                    "type": task_type,
                    "websiteURL": self.site_url,
                    "websiteKey": self.site_key,
                    "enterprisePayload": (
                        {"rqdata": self.rq_data} if self.rq_data else None
                    ),
                    "userAgent": self.user_agent,
                    "proxy": self.get_proxy_from_session(self.session),
                },
            }
            resp1 = requests.post(f"{domain}/createTask", json=data)
            if resp1.status_code != 200:
                raise requests.exceptions.RequestException(
                    f"Request failed with status code: {resp1.status_code}"
                )

            invalid_errs = [
                "ERROR_WRONG_USER_KEY"
                "ERROR_KEY_DENIED_ACCESS",
                "ERROR_KEY_DOES_NOT_EXIST",
                "ERROR_ZERO_BALANCE",
            ]
            if any(error_name in resp1.text for error_name in invalid_errs):
                log.error("Invalid Captcha Service Key!")
                return ""

            resp_json = resp1.json()
            if resp_json.get("errorId") == 0:
                task_id = resp_json.get("taskId")
                
                data = {"clientKey": self.cap_key, "taskId": task_id}
                res = requests.post(f"{domain}/getTaskResult", json=data)
                status = res.json().get("status")

                while status == "processing":
                    time.sleep(1)
                    res = requests.post(f"{domain}/getTaskResult", json=data)
                    status = res.json().get("status")

                resp = res.json() if status == "ready" else None
            
                if resp:
                    return resp.get("solution").get("gRecaptchaResponse", "")
                else:
                    return self.solve_generic(domain)
            else:
                return self.solve_generic(domain)
        except requests.exceptions.RequestException as e:
            log.error(f"Error solving captcha: {e}")
            return ""

    def solve_hcop(self, domain: str) -> str:
        try:
            task_type = "hcaptchaEnterprise"
            data = {
                "api_key": self.cap_key,
                "task_type": task_type,
                "data": {
                    "url": self.site_url,
                    "sitekey": self.site_key,
                    "proxy": self.get_proxy_from_session(self.session),
                },
            }
            resp1 = requests.post(f"{domain}/createTask", json=data, timeout=60)
            if "Wrong API key" in resp1.text:
                log.error("Invalid Captcha Service Key!")
                return ""

            resp_json = resp1.json()
            if not resp_json.get("error"):
                task_id = resp_json.get("task_id")
                resp = self.wait_and_get_hcop_solution(domain, task_id)
                if resp:
                    return resp.get("task").get("captcha_key", "")
                else:
                    return self.solve_captcha()
            else:
                log.debug(resp_json.get("message"))
                return self.solve_hcop(domain)
        except requests.exceptions.RequestException as e:
            log.error(f"Error solving HCaptcha: {e}")
            return ""

    def wait_and_get_hcop_solution(self, domain: str, task_id: str) -> Dict:
        data = {"api_key": self.cap_key, "task_id": task_id}
        resp = requests.post(f"{domain}/getTaskData", json=data, timeout=60)
        status = resp.json().get("task").get("state")

        while status == "processing":
            time.sleep(1)
            resp = requests.post(f"{domain}/getTaskData", json=data, timeout=60)
            status = resp.json().get("task").get("state")

        return resp.json() if status == "completed" else None

    def solve_secondary(self, domain: str) -> str:
        try:
            payload = {
                "key": self.cap_key,
                "method": "hcaptcha",
                "sitekey": self.site_key,
                "pageurl": self.site_url,
                "enterprise": True,
                "json": 1,
            }
            res = requests.post(f"{domain}/in.php", json=payload)
            invalid_errs = [
                "ERROR_WRONG_USER_KEY"
                "ERROR_KEY_DENIED_ACCESS",
                "ERROR_KEY_DOES_NOT_EXIST",
                "ERROR_ZERO_BALANCE",
            ]
            if any(error_name in res.text for error_name in invalid_errs):
                log.error("Invalid Captcha Service Key!")
                return ""

            request_id = res.json().get("request")
            resp = self.wait_for_secondary_solution(domain, request_id)
            return resp if resp else ""
        except requests.exceptions.RequestException as e:
            log.error(f"Error solving secondary captcha: {e}")
            return ""

    def wait_for_secondary_solution(self, domain: str, request_id: str) -> str:
        payload = {
            "key": self.cap_key,
            "action": "get",
            "id": f"{request_id}",
            "json": 1,
        }
        res = requests.post(f"{domain}/res.php", json=payload)
        while res.json().get("request") == "CAPCHA_NOT_READY":
            res = requests.post(f"{domain}/res.php", json=payload)
            time.sleep(1)

        return res.json().get("request")

    def dortcap_solver(self, domain: str):
        payload = {
            "api_key": self.cap_key,
            "site_key": self.site_key,
            "site_url": self.site_url,
        }
        res = requests.post(f"{domain}/solve/hcaptcha-pay-per-use", json=payload)
        if token := res.json().get("token"):
            return token
        return self.dortcap_solver(domain)

    def solve_nocapai(self, _):
        apikey = "apikey"
        token_api = "https://token.nocaptchaai.com/token"

        headers = {"Content-Type": "application/json", "apikey": apikey}
        payload = {
            "type": "hcaptcha",
            "url": self.site_url,
            "sitekey": self.site_key,
            "useragent": self.user_agent,
        }

        response = requests.post(token_api, json=payload, headers=headers).json()
        time.sleep(5)

        while True:
            sts = requests.get(response["url"], headers=headers).json()
            if sts["status"] == "processed":
                return sts["token"]
            elif sts["status"] == "failed":
                print("fail to solve dogshit solver nocaptchaiai")

            time.sleep(1)

    @staticmethod
    def get_proxy_from_session(session: requests.Session) -> str:
        proxy = session.proxies.get("http")
        if proxy:
            protocol, session_proxy = proxy.split("://")
            user_pass, host_port = (
                session_proxy.split("@")
                if "@" in session_proxy
                else (None, session_proxy)
            )
            user_pass_parts = user_pass.split(":") if user_pass else []
            if len(user_pass_parts) == 2:
                user, password = user_pass_parts
                return f"{protocol}://{user}:{password}@{host_port}"
            return f"{protocol}://{host_port}"
        return ""
