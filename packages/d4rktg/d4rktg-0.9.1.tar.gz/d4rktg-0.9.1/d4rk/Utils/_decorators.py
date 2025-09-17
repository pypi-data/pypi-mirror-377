import os
import asyncio
import functools

from typing import Union
from pyrogram import Client , filters
from d4rk.Logs import setup_logger
from pyrogram.types import Message , CallbackQuery , ChatPrivileges

from ._delete import delete
from ._ractions import Reacts
from dotenv import load_dotenv
load_dotenv()

logger = setup_logger(__name__)

OWNER = int(os.getenv("OWNER", 7859877609))


def authorize(
    sudo=False,
    admin=False,
    permission=None,
):
    async def func(flt, client, message: Union[Message, CallbackQuery]):
        try:
            user = message.from_user
            if not user:
                logger.warning(f"Unauthorized access attempt from non-user message: {message}")
                return False

            me = await client.get_me()
            is_admin = False

            if admin:
                if message.chat.type.name.lower() in ["group", "supergroup"]:
                    role = await client.get_chat_member(message.chat.id, user.id)
                    myrole = await client.get_chat_member(message.chat.id, me.id)

                    role_status = getattr(role.status, "name", role.status).lower()
                    myrole_status = getattr(myrole.status, "name", myrole.status).lower()

                    if role_status in ["creator", "administrator"] and \
                       myrole_status in ["creator", "administrator"]:

                        if permission:
                            privileges = getattr(role, "privileges", None)
                            myprivileges = getattr(myrole, "privileges", None)
                            if privileges and myprivileges:
                                has_permission = getattr(privileges, permission, False)
                                has_my_permission = getattr(myprivileges, permission, False)
                                if has_permission and has_my_permission:
                                    is_admin = True
                                else:
                                    return False
                        else:
                            is_admin = True
                else:
                    return False

            authorized = (
                (user.id == OWNER)
                or (sudo and str(user.id) in getattr(client, "sudo_users", []))
                or is_admin
            )
            return bool(authorized)
        except Exception as e:
            logger.error(f"Error in authorize filter: {e}")
            return bool(user.id == user.id)

    return filters.create(func, sudo=sudo,admin=admin,permission=permission)
