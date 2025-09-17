import os
import sys
import asyncio
import traceback
import random
from datetime import datetime, timedelta

from pyrogram import Client
from pyrogram.errors import FloodWait
from pyrogram.types import BotCommand
from pyrogram.errors.exceptions.bad_request_400 import AccessTokenExpired

from d4rk.Logs import setup_logger

logs_sent = False
logs_lock = asyncio.Lock()

logger = setup_logger(__name__)

class BotManager(Client):
    _bot: Client = None
    _web = True
    _bot_info = None
    _is_connected = False
    _rename = False
    _flood_data = {}
    _loop = None
    _scheduler_thread = None
    font = 0
    sudo_users = []


    def create_client(self,app_name,token):
        self.app_name = app_name
        super().__init__(
            name=app_name,
            api_id=self.api_id,
            api_hash=self.api_hash,
            bot_token=token,
            plugins=self.plugins,
            in_memory=True
            )

    async def handle_flood_wait(self, wait_time: int):

        await asyncio.sleep(wait_time)
        try:await self.powerup(self.app_name)
        except:pass
        
    def _safe_async(self, coro_func):
        if self._loop:asyncio.run_coroutine_threadsafe(coro_func(), self._loop)
        else:logger.error("Event loop is not set for _safe_async")

    async def powerup(self,appname):
        if hasattr(self, "db"):
            self.font = self.db.Settings.get(key="font",datatype=str)
            self.sudo_users = self.db.Settings.get(key="sudo_users",datatype=list,default=[])
            if not self.font:
                logger.info("Font not set, defaulting to font 1")
                self.db.Settings.set("font", "1")
                self.font = 1

        self.create_client(appname,self.token)
        max_retries = 3
        for attempt in range(max_retries):
            try:
                self._loop = asyncio.get_running_loop()
                logger.info(f'Starting bot client... (attempt {attempt + 1}/{max_retries})')
                if not self._is_connected:
                    await asyncio.wait_for(super().start(), timeout=60.0)
                    self._bot_info = await super().get_me()
                    logger.info(f"Bot Client > {self._bot_info.first_name} - @{self._bot_info.username} Started")
                    await self.setup_commands()
                    self._is_connected = True
                    await self.handle_restart()
                    break 

            except asyncio.TimeoutError:
                logger.error(f"Bot start timed out (attempt {attempt + 1})")
                if attempt < max_retries - 1:
                    logger.info("Retrying in 10 seconds...")
                    await asyncio.sleep(10)
                
            except FloodWait as e:
                logger.error(f"FloodWait: {e.value} seconds")
                await self.handle_flood_wait(e.value)
                break

            except AccessTokenExpired:
                logger.error(f"Access token expired (attempt {attempt + 1})")
            except Exception as e:
                logger.error(f"Error starting Client.Stoped !")
                logger.error(traceback.format_exc())
                break
        else:
            logger.error("Failed to start bot after all retry attempts")

        await self.setup_webserver()

    async def powerdown(self, *args):
        global logs_sent, logs_lock
        logger.info("Initiating APP to stop...")
        if self._rename:await super().set_bot_info(lang_code='en',name=self.app_name + " (Offline)")
        self.stop_scheduler()
        today = self.TZ_now.strftime("%Y-%m-%d")
        if hasattr(self, '_web_runner') and self._web_runner:
            await self.web_server.cleanup()
        
        logger.info("Stopping bot client...")
        if self._is_connected and self.LOGS:
            try:
                await self.send_message(chat_id=self.LOGS, text=f"{self._bot_info.mention} stopping...")
            except Exception as e:
                logger.error(f"Error sending stop message for {self._bot_info.first_name}: {e}")

        async with logs_lock:
            if not logs_sent and self._is_connected:
                logs_sent = True
                try:
                    await self.send_document(chat_id=self.LOGS, document=f"logs/log-{today}.txt")
                    logger.info("Log document sent successfully")
                except Exception as e:
                    logger.error(f"Error sending log document: {e}")

        if self._is_connected and self.LOGS:
            try:
                await self.send_message(chat_id=self.LOGS, text=f"{self._bot_info.mention} stopped successfully!")
            except Exception as e:
                logger.error(f"Error sending stop confirmation for {self._bot_info.first_name}: {e}")
            await super().stop()
            await asyncio.sleep(3)

    async def reboot(self):
        try:
            if self._rename:await super().set_bot_info(lang_code='en',name=self.app_name + " (restarting..)")
            logger.info("Initiating APP to reboot...")
            self.stop_scheduler()
            today = self.TZ_now.strftime("%Y-%m-%d")
            if hasattr(self, '_web_runner') and self._web_runner:
                await self.web_server.cleanup()
            if self._is_connected:
                try:
                    if self.LOGS:
                        await self.send_message(chat_id=self.LOGS, text=f"{self._bot_info.mention} rebooting...")
                        await self.send_document(chat_id=self.LOGS, document=f"logs/log-{today}.txt")
                    logger.info(f"{self._bot_info.first_name} - @{self._bot_info.username} is rebooting")
                except Exception as e:
                    logger.error(f"Error sending reboot notification: {e}")
                await super().stop()
                self._is_connected = False
            await asyncio.sleep(2)
            
            logger.info("Restarting process...")
            os.execl(sys.executable, sys.executable, *sys.argv)
        except Exception as e:
            logger.error(f"Error during reboot: {e}")
            os.execl(sys.executable, sys.executable, *sys.argv)

    async def handle_restart(self):
        if os.path.exists('restart.txt'):
            with open('restart.txt', 'r') as file:
                data = file.read().split()
                chat_id = int(data[0])
                Message_id = int(data[1])
            try:await self.send_message(chat_id=self.LOGS, text=f"{self._bot_info.mention} restarted successfully!")
            except Exception as e:logger.error(f"Failed to send restart notification: {e}")
            try:await self.edit_message_text(chat_id=chat_id,message_id=Message_id, text="Bot restarted successfully!")          
            except:
                try:
                    await self.send_message(chat_id=chat_id, text="Bot restarted successfully!",reply_to_message_id=Message_id-1,)
                    await self.delete_messages(chat_id=chat_id,message_ids=Message_id)
                except:pass

            if os.path.exists('restart.txt'):os.remove('restart.txt')
        else:
            try:await self.send_message(chat_id=self.LOGS, text=f"{self._bot_info.mention} started successfully!")
            except Exception as e:logger.error(f"Failed to send start notification: {e}")


    async def setup_commands(self,set_commands=False):
        if self._rename:
            if self._bot_info.first_name != self.app_name:
                await super().set_bot_info(lang_code='en',name=self.app_name)
        if set_commands:
            commands = await super().get_bot_commands()
            if commands == []:
                b_index = self.TOKEN_INDEX + 1
                bot_commands = [
                    BotCommand("start", f"{b_index} Start the bot"),
                    BotCommand("help", f"{b_index} Get help"),
                    BotCommand("logs", f"{b_index} Get logs (Admin only)"),
                    BotCommand("reboot", f"{b_index} Reboot the bot (Admin only)")
                ]
                await super().set_bot_commands(bot_commands)

    async def send_logs(self):
        logger.info("Sending yesterday logs...")
        if not self._is_connected:
            logger.warning("Bot is not connected")
        if self._is_connected:
    
            yesterday = (self.TZ_now - timedelta(days=1)).strftime("%Y-%m-%d")
            try:
                m = await self.send_document(chat_id=self.LOGS, document=f"logs/log-{yesterday}.txt")
                logger.info(f"Logs sent to {m.chat.first_name} - @{m.chat.username}")
            except Exception as e:
                logger.error(f"Error sending logs: {e}")