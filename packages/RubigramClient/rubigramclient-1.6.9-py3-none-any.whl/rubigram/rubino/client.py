from aiohttp import ClientSession
from typing import Literal, Optional, Union, Any
from random import randint


class Rubino:
    def __init__(self, auth: str):
        self.auth = auth
        self.api = f"https://rubino{randint(1, 30)}.iranlms.ir"
        self.client = {
            "app_name": "Main",
            "app_version": "3.0.2",
            "lang_code": "fa",
            "package": "app.rbmain.a",
            "platform": "Android"
        }

    
    async def reauest(self, method: str, data: dict[str, Any]):
        json = {
            "api_version": "0",
            "auth": self.auth,
            "client": self.client,
            "data": data,
            "method": method
        }
        async with ClientSession() as session:
            async with session.post(self.api, json=json) as response:
                response.raise_for_status()
                return await response.json()

    
    async def get_post_by_share_link(self, post_link: str):
        return await self.reauest("getPostByShareLink", {"share_string": post_link.split("/")[-1]})
    
    
    async def add_post_view_count(self, post_id: str, post_profile_id: str):
        data = {"post_id": post_id, "post_profile_id": post_profile_id}
        return await self.reauest("addPostViewCount", data)
    
    
    async def add_view_story(self, story_profile_id: str, story_ids: Union[str, list[str]], profile_id: Optional[str] = None):
        story_ids = story_ids if isinstance(story_ids, list) else [story_ids]
        data = {"story_profile_id": story_profile_id, "story_ids": story_ids, "profile_id": profile_id}
        return await self.reauest("addViewStory", data)
    
    
    async def is_exist_username(self, username: str):
        username = username.replace("@", "")
        return await self.reauest("isExistUsername", {"username": username})
    
    
    async def create_page(self, username: str, name: str, bio: Optional[str] = None):
        return await self.reauest("createPage", {"username": username, "name": name, "bio": bio})
    
    
    async def add_comment(self, content: str, post_id: str, post_profile_id: str, profile_id: Optional[str] = None):
        rnd = randint(100000, 999999999)
        data = {"content": content, "post_id": post_id, "post_profile_id": post_profile_id, "profile_id": profile_id, "rnd": rnd}
        return await self.reauest("addComment", data)
    
    
    async def request_follow(self, followee_id: str, f_type: Literal["Follow", "Unfollow"] = "Follow", profile_id: Optional[str] = None):
        data = {"f_type": f_type, "followee_id": followee_id, "profile_id": profile_id}
        return self.reauest("requestFollow", data)
    
    
    async def set_block_profile(self, block_id: str, action: Literal["Block", "Unblock"] = "Block", profile_id: Optional[str] = None):
        data = {"block_id": block_id, "action": action, "profile_id": profile_id}
        return self.reauest("setBlockProfile", data)
    
    
    async def get_comments(self, post_id: str, post_profile_id: str, limit: Optional[int] = 100, profile_id: Optional[str] = None):
        data = {
            "post_id": post_id,
            "post_profile_id": post_profile_id,
            "limit": limit,
            "profile_id": profile_id,
            "equal": False,
            "sort": "FromMax"
        }
        return await self.reauest("getComments", data)