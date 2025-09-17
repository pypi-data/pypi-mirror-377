# from dataclasses import dataclass, fields, field
# from typing import Optional


# @dataclass
# class ClientInfo:
#     version: int
#     os: str
#     client: str


# @dataclass
# class UserData:
#     verified: bool
#     username: str
#     purchased_flags: int
#     pronouns: str
#     premium_type: int
#     premium: bool
#     phone: str
#     nsfw_allowed: bool
#     mobile: bool
#     mfa_enabled: bool
#     id: str
#     has_bounced_email: bool
#     global_name: str
#     flags: int
#     email: str
#     discriminator: str
#     desktop: bool
#     bio: str
#     banner_color: str
#     banner: str
#     avatar_decoration_data: str
#     avatar: str
#     accent_color: str


# @dataclass
# class SessionData:
#     status: str
#     session_id: str
#     client_info: ClientInfo
#     activities: list


# @dataclass
# class UserGuildSettings:
#     version: int
#     partial: bool
#     entries: list


# @dataclass
# class Tutorial:
#     indicators_suppressed: bool
#     indicators_confirmed: list


# @dataclass
# class ReadState:
#     version: int
#     partial: bool
#     entries: list


# @dataclass
# class NotificationSettings:
#     flags: int


# @dataclass
# class D_Data:
#     v: Optional[int] = None
#     users: Optional[list] = None
#     user_guild_settings: Optional[UserGuildSettings] = None
#     user: Optional[UserData] = None
#     tutorial: Optional[Tutorial] = None
#     sessions: Optional[list] = None
#     session_type: Optional[str] = None
#     session_id: Optional[str] = None
#     resume_gateway_url: Optional[str] = None
#     relationships: Optional[list] = None
#     read_state: Optional[ReadState] = None
#     private_channels: Optional[list] = None
#     notification_settings: Optional[NotificationSettings] = None
#     merged_members: Optional[list] = None
#     guilds: Optional[list] = None
#     guild_join_requests: Optional[list] = None
#     guild_experiments: Optional[list] = None
#     geo_ordered_rtc_regions: Optional[list] = None
#     friend_suggestion_count: Optional[int] = None
#     experiments: Optional[list] = None
#     country_code: Optional[str] = None
#     consents: Optional[dict] = None
#     connected_accounts: Optional[list] = None
#     auth_session_id_hash: Optional[str] = None
#     auth: Optional[dict] = None
#     api_code_version: Optional[int] = None
#     analytics_token: Optional[str] = None
#     _trace: Optional[list] = None

#     user_settings_proto: Optional[str] = None
#     required_action: Optional[str] = None


# @dataclass
# class ReadyData:
#     t: str
#     s: int
#     op: int
#     d: D_Data


