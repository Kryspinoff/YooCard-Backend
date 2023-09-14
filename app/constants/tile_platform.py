from collections import namedtuple
from enum import Enum

PlatformData = namedtuple("PlatformData", ["title", "url_pattern"])


class TilePlatformEnum(Enum):
    FACEBOOK = PlatformData("Facebook", "https://www.facebook.com")
    INSTAGRAM = PlatformData("Instagram", "https://www.instagram.com")
    WHATSAPP = PlatformData("WhatsApp", "whatsapp://send?")
    TELEGRAM = PlatformData("Telegram", "https://t.me")
    TWITTER = PlatformData("Twitter", "https://twitter.com")
    PINTEREST = PlatformData("Pinterest", "https://pl.pinterest.com/")
    YOUTUBE = PlatformData("Youtube", "https://www.youtube.com")
    REDDIT = PlatformData("Reddit", "https://www.reddit.com")
    SKYPE = PlatformData("Skype", "https://join.skype.com/invite")
    VIBER = PlatformData("Viber", "viber://pa")
    SIGNAL = PlatformData("Signal", "signal://")
    SNAPCHAT = PlatformData("Snapchat", "snapchat://")
    TIKTOK = PlatformData("TikTok", "tiktok://")
    LINKEDIN = "linkedin"
    WECHAT = "wechat"
    WEBSITE = "website"
