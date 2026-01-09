import requests
import asyncio
import random
from pyrogram import filters
from TEAMZYRO import (
    CHARA_CHANNEL_ID,
    collection,
    ZYRO,
    rarity_map,
    require_power
)

# 🔒 Lock taaki DB crash na ho agar tu jaldi jaldi spam kare
padd_lock = asyncio.Lock()

# 🎲 TAGS LIST & SMART MAPPING (Tag -> Anime Name)
# Bot inme se random pick karega
TAG_DATA = {
    'maid': 'Maid Café Collection',
    'waifu': 'Random Waifu',
    'marin-kitagawa': 'My Dress-Up Darling',
    'mori-calliope': 'Hololive',
    'raiden-shogun': 'Genshin Impact',
    'kamisato-ayaka': 'Genshin Impact',
    'ganyu': 'Genshin Impact',
    'uniform': 'School Life',
    'selfies': 'Real Life Collection',
    'nekomimi': 'Animal Girls'
}

# ---------------------------------------------
# 1. HELPER: Find Next ID
# ---------------------------------------------
async def find_available_id():
    cursor = collection.find().sort("id", 1)
    ids = []
    async for doc in cursor:
        if "id" in doc:
            try: ids.append(int(doc["id"]))
            except: continue
    ids.sort()
    for i in range(1, len(ids) + 2):
        if i not in ids: return str(i).zfill(2)
    return str(len(ids) + 1).zfill(2)

# ---------------------------------------------
# 2. COMMAND: /padd (Full Random Add)
# ---------------------------------------------
@ZYRO.on_message(filters.command(["padd"]))
@require_power("add_character")
async def padd_handler(client, message):
    global padd_lock

    if padd_lock.locked():
        return await message.reply_text("⏳ **Ruk ja bhai!** Ek process hone de pehle...")

    async with padd_lock:
        try:
            status = await message.reply_text("🎲 **Rolling Dice...** Random Waifu dhund raha hu...")

            # --- STEP 1: Random Selection ---
            
            # 1. Random Tag Select karo
            selected_tag = random.choice(list(TAG_DATA.keys()))
            
            # 2. Random Rarity Select karo (1 se 6 ke beech safe rehta hai, tu chahe to 15 kar le)
            # Rarity Map: 1=Low, 2=Medium, 3=High, 4=Special, 5=Elite, 6=Exclusive...
            random_rarity_num = random.randint(3, 6) # Maine 3-6 rakha hai taaki achi rarity mile
            rarity_text = rarity_map.get(random_rarity_num, "🔴 High")

            # --- STEP 2: API Call ---
            
            url = 'https://api.waifu.im/search'
            params = {
                'included_tags': [selected_tag],
                'height': '>=2000', # High Quality
                'is_nsfw': 'false'
            }

            response = requests.get(url, params=params, timeout=10)
            img_url = None
            
            if response.status_code == 200:
                data = response.json()
                if 'images' in data and len(data['images']) > 0:
                    img_url = data['images'][0]['url']

            if not img_url:
                return await status.edit(f"❌ API ne dhoka de diya (`{selected_tag}`). Dobara try kar.")

            # --- STEP 3: Data Preparation ---

            # ID Nikalo
            new_id = await find_available_id()

            # Name Banao (raiden-shogun -> Raiden Shogun)
            char_name = selected_tag.replace('-', ' ').title()
            
            # Anime Name Dictionary se uthao
            anime_name = TAG_DATA[selected_tag]

            # Database Object
            character_data = {
                'name': char_name,
                'anime': anime_name,
                'rarity': rarity_text,
                'rarity_number': random_rarity_num,
                'id': new_id,
                'img_url': img_url
            }

            # --- STEP 4: Save & Send ---

            # Database mein daalo
            await collection.insert_one(character_data)

            # Log Channel pe bhejo
            caption_text = (
                f"🎲 **Random Auto-Add**\n"
                f"Character: {char_name}\n"
                f"Anime: {anime_name}\n"
                f"Rarity: {rarity_text}\n"
                f"ID: {new_id}\n"
                f"Added by: {message.from_user.mention}"
            )
            
            try:
                await client.send_photo(chat_id=CHARA_CHANNEL_ID, photo=img_url, caption=caption_text)
            except Exception as e:
                await message.reply_text(f"⚠️ DB Saved, but Channel send failed: {e}")

            # User ko reply
            await status.edit(
                f"✅ **Majduri Successful!**\n\n"
                f"🆔 **ID:** `{new_id}`\n"
                f"👤 **Name:** {char_name}\n"
                f"📺 **Anime:** {anime_name}\n"
                f"💎 **Rarity:** {rarity_text}"
            )

        except Exception as e:
            await status.edit(f"❌ Error: {str(e)}")

