from dataclasses import dataclass, asdict, field
from typing import Optional
from re2 import search


class AgentProperties:
    @staticmethod
    def extract_browser(user_agent: str) -> list[str]:
        """_summary_

        Args:
            user_agent (str): _description_

        Returns:
            ["browser_name", "browser_version"]
        """
        browser_patterns = {
            "Discord Client": r"discord/([\d.]+)",
            "Chrome": r"Chrome/([\d.]+)",
            "Firefox": r"Firefox/([\d.]+)",
            "Edge": r"Edge/([\d.]+)",
            "Safari": r"Safari/([\d.]+)",
            "Opera": r"OPR/([\d.]+)|Opera/([\d.]+)",
        }

        for browser, pattern in browser_patterns.items():
            match = search(pattern, user_agent)
            if match:
                return [browser, str(match.group(1))]

        return ["Firefox", "125.0"]


class DiscordProperties:
    BUILD_NUMBER: int = 268356

    @dataclass
    class X_Super_Properties:
        os:                  Optional[str] = None
        browser:             Optional[str] = None
        device:              Optional[str] = None
        system_locale:       Optional[str] = None
        client_version:      Optional[str] = None
        release_channel:     Optional[str] = None
        device_vendor_id:    Optional[str] = None
        os_version:          Optional[str] = None
        client_build_number: Optional[int] = None
        browser_user_agent:  Optional[str] = None
        browser_version:     Optional[str] = None
        os_arch:             Optional[str] = None
        app_arch:            Optional[str] = None
        native_build_number: Optional[int] = None

        def to_dict(self):
            return {key: value for key, value in asdict(self).items() if value}

    @dataclass
    class X_Track(X_Super_Properties):
        build_number: Optional[int] = 9999

class Agents:
    @dataclass
    class Browser:
        device_type: str = "Windows"
        user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0"
        browser_name, browser_version = AgentProperties.extract_browser(user_agent)

        Xsup = DiscordProperties.X_Super_Properties(
            os=device_type,
            browser=browser_name,
            device="",
            system_locale="en-US",
            browser_user_agent=user_agent,
            browser_version=browser_version,
            os_version="10",
            release_channel="stable",
            client_build_number=str(DiscordProperties.BUILD_NUMBER),
        )

    @dataclass
    class Desktop:
        user_agent: str = "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) discord/1.0.9034 Chrome/108.0.5359.215 Electron/22.3.26 Safari/537.36"
        device_type = "Windows"
        Xsup = DiscordProperties.X_Super_Properties(
            os=device_type,
            browser="Discord Client",
            release_channel="stable",
            client_version="1.0.9034",
            os_version="10.0.22631",
            os_arch="x64",
            app_arch="ia32",
            system_locale="en-US",
            browser_user_agent=user_agent,
            browser_version="22.3.26", # Electron version
            client_build_number=str(DiscordProperties.BUILD_NUMBER),
            native_build_number=44142,
        )

    @dataclass
    class Mobile:
        user_agent_mobile = "Discord-Android/170014;RNA"
        device_type: str = "Android"

        Xsup = DiscordProperties.X_Super_Properties(
            os="",
            browser="Discord Android",
            device="RMX2117L1",
            system_locale="en-US",
            browser_user_agent=user_agent_mobile,
            browser_version="",
            os_version="31",
            release_channel="googleRelease",
            client_build_number=1750160087099,
        )
