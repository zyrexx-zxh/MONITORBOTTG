import os
import re
from pyrogram import Client, filters, enums
from pyrogram.types import ChatPrivileges

# --- CONFIGURATION ---
API_ID = 30150739 
API_HASH = "c1403e995a27e4474771009fb65cf5b7"
BOT_TOKEN = "8714740374:AAEmTRvcMPOBvfVGSEKI9BDZHlEg9CTGloE" # <--- Yahan token daal

FORUM_GC_ID = -1003800395326
CHAT_GC_ID = -1003741678126

warns = {}

app = Client("VantixManager", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

async def is_admin(chat_id, user_id):
    try:
        member = await app.get_chat_member(chat_id, user_id)
        return member.status in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]
    except:
        return False

@app.on_message(filters.group & ~filters.service)
async def handle_spam(client, message):
    if not message.from_user: return
    user_id = message.from_user.id
    chat_id = message.chat.id
    text = message.text or message.caption or ""

    if await is_admin(chat_id, user_id): return

    has_link = re.search(r'(https?://[^\s]+|t\.me/[^\s]+)', text)
    should_delete = False
    
    if chat_id == CHAT_GC_ID:
        if has_link or any(word in text.lower() for word in ["sell", "buy", "promotion", "available", "dm for"]):
            should_delete = True
    elif chat_id == FORUM_GC_ID:
        if has_link:
            should_delete = True

    if should_delete:
        try:
            await message.delete()
            warn_key = f"{chat_id}_{user_id}"
            warns[warn_key] = warns.get(warn_key, 0) + 1
            
            if warns[warn_key] >= 3:
                await client.ban_chat_member(chat_id, user_id)
                await client.send_message(chat_id, f"❌ {message.from_user.mention} ko 3 warnings ke baad BAN kar diya gaya!")
                warns[warn_key] = 0
            else:
                await client.send_message(chat_id, f"⚠️ {message.from_user.mention}, No Promo/Links! Warning: {warns[warn_key]}/3")
        except:
            pass

@app.on_message(filters.command("ban", prefixes=".") & filters.group)
async def ban_cmd(client, message):
    if not await is_admin(message.chat.id, message.from_user.id): return
    if message.reply_to_message:
        await client.ban_chat_member(message.chat.id, message.reply_to_message.from_user.id)
        await message.reply_text("🔨 User Banned!")

@app.on_message(filters.command("mute", prefixes=".") & filters.group)
async def mute_cmd(client, message):
    if not await is_admin(message.chat.id, message.from_user.id): return
    if message.reply_to_message:
        await client.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id, enums.ChatPermissions())
        await message.reply_text("🤫 Muted!")

@app.on_message(filters.command("promote", prefixes=".") & filters.group)
async def promote_cmd(client, message):
    if not await is_admin(message.chat.id, message.from_user.id): return
    if message.reply_to_message:
        await client.promote_chat_member(message.chat.id, message.reply_to_message.from_user.id, 
            privileges=ChatPrivileges(can_manage_chat=True, can_delete_messages=True, can_restrict_members=True))
        await message.reply_text("👑 Promoted to Admin!")

print("Vantix Manager is Live...")
app.run()
                
