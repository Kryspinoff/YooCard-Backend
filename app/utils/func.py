import asyncio
import os
import shutil
from typing import Optional

import aiofiles
from fastapi import HTTPException

from app.core.config import settings
from app.models import User
from app.static_files import PATH_STATIC_FILES


class UserPictureManager:
    @classmethod
    async def save_user_picture(cls, *, user_id: int, filename: str, file_contents: bytes) -> str:
        user_picture_folder = PATH_STATIC_FILES + f"/users/pictures/{user_id}"

        if os.path.exists(user_picture_folder):
            await cls.delete_user_picture(user_id=user_id)

        os.makedirs(user_picture_folder, exist_ok=True)
        file_path = os.path.join(user_picture_folder, filename)

        try:
            async with aiofiles.open(file_path, "wb") as file:
                await file.write(file_contents)
        except Exception as e:
            raise HTTPException(status_code=500, detail="Failed to save user picture")

        return f"{settings.DOMAIN}/static/users/pictures/{user_id}/{filename}"

    @classmethod
    async def delete_user_picture(cls, *, user_id: int) -> bool:
        user_picture_folder = PATH_STATIC_FILES + f"/users/pictures/{user_id}"

        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, lambda: shutil.rmtree(user_picture_folder))
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail="User picture not found")
        except Exception as e:
            raise HTTPException(status_code=500, detail="Failed to delete user picture")

        return True


def generate_vcf(user: User) -> str:
    return f"""
BEGIN:VCARD
VERSION:3.0
FN:{user.first_name} {user.last_name}
N:{user.last_name};{user.first_name}
EMAIL:{user.email}
TEL:{user.phone_number or ''}
NOTE:{user.description or ''}
END:VCARD
    """
