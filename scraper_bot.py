import os
import random
import time
import asyncio
import logging
from datetime import datetime
from telethon import TelegramClient, events, Button
from telethon.tl.types import InputWebDocument
from faker import Faker

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

fake = Faker()

# ============ CONFIGURATION ============
API_ID = int(os.environ.get('API_ID', '35384207'))
API_HASH = os.environ.get('API_HASH', '09c4bc9de62a417ccdd0c69b33912515')
BOT_TOKEN = os.environ.get('BOT_TOKEN', '8815044105:AAFF9ekYN74wnLQPFUQ3Tm5RA8g4MHvqq0Q')

# ============ VISA & MASTERCARD BINS ============
VISA_BINS = [
    '4532', '4539', '4556', '4916', '4929', '4484', '4716', '4026', '4175',
    '4266', '4284', '4310', '4338', '4383', '4405', '4420', '4445', '4462',
    '4486', '4506', '4518', '4537', '4544', '4557', '4564', '4573', '4596',
    '4617', '4627', '4645', '4660', '4674', '4688', '4700', '4720', '4730',
    '4740', '4751', '4761', '4785', '4796', '4800', '4815', '4828', '4844',
    '4850', '4862', '4873', '4885', '4897', '4900', '4910', '4920', '4930',
    '4940', '4950', '4960', '4970', '4980', '4990'
]

MASTERCARD_BINS = [
    '5221', '5223', '5230', '5234', '5244', '5250', '5254', '5260',
    '5263', '5270', '5273', '5280', '5285', '5290', '5299', '5300',
    '5322', '5330', '5340', '5350', '5360', '5370', '5380', '5390',
    '5400', '5410', '5420', '5430', '5440', '5450', '5460', '5470',
    '5480', '5490', '5500', '5510', '5520', '5530', '5540', '5550',
    '5560', '5570', '5580', '5590', '5600', '5610', '5620', '5630',
    '5640', '5650', '5660', '5670', '5680', '5690', '5700', '5710',
    '5720', '5730', '5740', '5750', '5760', '5770', '5780', '5790',
    '5800', '5810', '5820', '5830', '5840', '5850', '5860', '5870',
    '5880', '5890', '5900', '5910', '5920', '5930', '5940', '5950',
    '5960', '5970', '5980', '5990'
]

HIGH_HIT_VISA = ['4532', '4539', '4556', '4916', '4929', '4484', '4716', '4739', '4740', '4026']
HIGH_HIT_MASTERCARD = ['5221', '5223', '5230', '5234', '5244', '5250', '5254', '5260', '5263', '5270']

PREMIUM_BANKS = [
    'CHASE', 'CITIBANK', 'BANK OF AMERICA', 'WELLS FARGO', 
    'CAPITAL ONE', 'US BANK', 'PNC BANK', 'TD BANK',
    'GOLDMAN SACHS', 'MORGAN STANLEY', 'JPMORGAN CHASE'
]

CARD_LEVELS = ['CLASSIC', 'GOLD', 'PLATINUM', 'SIGNATURE', 'WORLD ELITE']

# ============ START IMAGE ============
START_IMAGE = "https://ibb.co/vx25TtC0"

# ============ TELEGRAM CLIENT ============
bot = TelegramClient('bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# ============ CARD GENERATION FUNCTIONS ============

def generate_card_number(card_type):
    """Generate valid card number"""
    if card_type == 'VISA':
        if random.random() < 0.7:
            bin_prefix = random.choice(HIGH_HIT_VISA)
        else:
            bin_prefix = random.choice(VISA_BINS)
    else:  # MASTERCARD
        if random.random() < 0.7:
            bin_prefix = random.choice(HIGH_HIT_MASTERCARD)
        else:
            bin_prefix = random.choice(MASTERCARD_BINS)
    
    length = 16
    body = bin_prefix + ''.join([str(random.randint(0, 9)) for _ in range(length - len(bin_prefix) - 1)])
    
    # Luhn algorithm
    digits = [int(d) for d in body]
    for i in range(len(digits) - 2, -1, -2):
        digits[i] *= 2
        if digits[i] > 9:
            digits[i] -= 9
    total_sum = sum(digits)
    check_digit = (10 - (total_sum % 10)) % 10
    
    return body + str(check_digit)

def luhn_check(card_number):
    """Verify card number using Luhn algorithm"""
    digits = [int(d) for d in card_number]
    for i in range(len(digits) - 2, -1, -2):
        digits[i] *= 2
        if digits[i] > 9:
            digits[i] -= 9
    return sum(digits) % 10 == 0

def generate_card():
    """Generate complete card details"""
    card_type = random.choices(['VISA', 'MASTERCARD'], weights=[55, 45], k=1)[0]
    card_number = generate_card_number(card_type)
    
    if not luhn_check(card_number):
        return generate_card()
    
    month = str(random.randint(1, 12)).zfill(2)
    year = str(random.randint(27, 38)).zfill(2)
    cvv = str(random.randint(100, 999)).zfill(3)
    
    bin_number = card_number[:6]
    bank = random.choice(PREMIUM_BANKS)
    level = random.choices(CARD_LEVELS, weights=[5, 15, 30, 25, 25], k=1)[0]
    card_type_display = random.choice(['DEBIT', 'CREDIT'])
    
    return {
        'card_number': card_number,
        'month': month,
        'year': year,
        'cvv': cvv,
        'card_type': card_type,
        'bin': bin_number,
        'bank': bank,
        'level': level,
        'country': 'UNITED STATES',
        'country_flag': '🇺🇸',
        'type': card_type_display,
        'is_high_hit': any(bin_number.startswith(b) for b in HIGH_HIT_VISA + HIGH_HIT_MASTERCARD)
    }

# ============ BOT HANDLERS ============

@bot.on(events.NewMessage(pattern='/start'))
async def start_command(event):
    """Handle /start command with image"""
    user_id = event.sender_id
    sender = await event.get_sender()
    name = sender.first_name if sender.first_name else "User"
    
    msg = f"""🐍 <b>FROXT</b>
<b>SCRAP BOT</b>
━━━━━━━━━━━━━━━━━━━━━━━━
👤 <b>User ID:</b> <code>{user_id}</code>
👤 <b>Name:</b> {name}
━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ <i>No Channel Added</i>
• Use '🔗 ADD CHANNEL' button to add your channel
• <b>Enjoy!</b>"""
    
    buttons = [
        [Button.url("𝙼𝙰𝙸𝙽", "https://t.me/atulfroxt", style="success"), Button.url("𝙲𝙰𝚁𝙳𝙸𝙽𝙶", "https://t.me/+sT1N0pne6sQzNTFl", style="success")],
        [Button.url("𝙲𝙷𝙰𝚁𝙶𝙴", "https://t.me/+rzRUgyJfia84NjBl", style="success"), Button.url("𝚅𝙸𝙿", "https://t.me/+u9cv-q_x57xkNzA1", style="success")],
        [Button.url("𝙿𝙰𝙸𝙳_𝙳𝚄𝙼𝙿𝚂", "https://t.me/+yn-01TbWsfk2NTU1", style="success"), Button.url("𝚆𝙴𝙱", "https://your-website.com", style="success")],
        [Button.url("𝙰𝙿𝙿𝚁𝙾𝚅𝙴𝙳_𝙲𝙰𝚁𝙳", "https://t.me/aaproved_card07", style="success"),
        [Button.inline("𝙰𝙳𝙳 𝙲𝙷𝙰𝙽𝙽𝙴𝙻", b"add_channel", style="danger")]
    ]
    
    # Send with image
    try:
        await bot.send_file(
            event.chat_id,
            START_IMAGE,
            caption=msg,
            buttons=buttons,
            parse_mode='html'
        )
    except:
        # If image fails, send text with buttons
        await event.reply(msg, buttons=buttons, parse_mode='html', link_preview=False)

@bot.on(events.NewMessage(pattern='/scrape'))
async def scrape_command(event):
    """Handle /scrape command - Start scraping cards in channel"""
    chat_id = event.chat_id
    
    msg = """🚀 <b>SCRAPER STARTED</b>
━━━━━━━━━━━━━━━━━━━━━━━━
💳 <b>Cards:</b> VISA & MASTERCARD
🔥 <b>Mode:</b> High-Hit
📌 <b>Status:</b> Running...
━━━━━━━━━━━━━━━━━━━━━━━━
Use <code>/stop</code> to stop scraping"""
    
    await event.reply(msg, parse_mode='html')
    
    # Start scraping in background
    asyncio.create_task(scrape_cards_continuous(chat_id))

@bot.on(events.NewMessage(pattern='/stop'))
async def stop_command(event):
    """Handle /stop command"""
    global scraper_running
    scraper_running = False
    
    msg = """⛔ <b>SCRAPER STOPPED</b>
━━━━━━━━━━━━━━━━━━━━━━━━
📊 <b>Total cards sent:</b> {count}
━━━━━━━━━━━━━━━━━━━━━━━━
Use <code>/scrape</code> to start again"""
    
    await event.reply(msg, parse_mode='html')

@bot.on(events.NewMessage(pattern='/gen'))
async def gen_command(event):
    """Handle /gen command - Generate single card"""
    card_data = generate_card()
    await send_approved_card(event.chat_id, card_data)

@bot.on(events.CallbackQuery)
async def callback_handler(event):
    """Handle callback queries from buttons"""
    data = event.data.decode('utf-8')
    
    if data == 'add_channel':
        msg = """🔗 <b>ADD CHANNEL</b>
━━━━━━━━━━━━━━━━━━━━━━━━
📌 <b>How to add bot to your channel:</b>

1️⃣ Add @YourBotName as admin to your channel
2️⃣ Send <code>/start</code> in your channel
3️⃣ Bot will start scraping cards there

⚠️ Make sure to give bot admin permissions!"""
        
        buttons = [[Button.inline("Bᴀᴄᴋ", b"back", style="danger")]]
        await event.edit(msg, buttons=buttons, parse_mode='html')
    
    elif data == 'back':
        # Go back to main menu
        user_id = event.sender_id
        sender = await event.get_sender()
        name = sender.first_name if sender.first_name else "User"
        
        msg = f"""🐍 <b>FROXT</b>
<b>SCRAP BOT</b>
━━━━━━━━━━━━━━━━━━━━━━━━
👤 <b>User ID:</b> <code>{user_id}</code>
👤 <b>Name:</b> {name}
━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ <i>No Channel Added</i>
• Use '🔗 ADD CHANNEL' button to add your channel
• <b>Enjoy!</b>"""
        
        buttons = [
            [Button.url("𝙼𝙰𝙸𝙽", "https://t.me/atulfroxt", style="success"), Button.url("𝙲𝙰𝚁𝙳𝙸𝙽𝙶", "https://t.me/+sT1N0pne6sQzNTFl", style="success")],
            [Button.url("𝙲𝙷𝙰𝚁𝙶𝙴", "https://t.me/+rzRUgyJfia84NjBl", style="success"), Button.url("𝚅𝙸𝙿", "https://t.me/+u9cv-q_x57xkNzA1", style="success")],
            [Button.url("𝙿𝙰𝙸𝙳_𝙳𝚄𝙼𝙿𝚂", "https://t.me/+yn-01TbWsfk2NTU1", style="success"), Button.url("𝚆𝙴𝙱", "https://your-website.com", style="success")],
            [Button.url("𝙰𝙿𝙿𝚁𝙾𝚅𝙴𝙳_𝙲𝙰𝚁𝙳", "https://t.me/aaproved_card07", style="success"),
            [Button.inline("𝙰𝙳𝙳 𝙲𝙷𝙰𝙽𝙽𝙴𝙻", b"add_channel", style="danger")]
        ]
        
        await event.edit(msg, buttons=buttons, parse_mode='html', link_preview=False)
    
    elif data == 'vip':
        await event.answer("👑 VIP Channel: https://t.me/+u9cv-q_x57xkNzA1", alert=True)
    
    elif data == 'charge':
        await event.answer("⚡ Charge Channel: https://t.me/+rzRUgyJfia84NjBl", alert=True)
    
    elif data == 'main':
        await event.answer("🏠 Main Channel: https://t.me/atulfroxt", alert=True)

async def send_approved_card(chat_id, card_data=None):
    """Send approved card to chat"""
    if not card_data:
        card_data = generate_card()
    
    # Format card details
    card_details = f"{card_data['card_number']}|{card_data['month']}|20{card_data['year']}|{card_data['cvv']}"
    card_masked = f"{card_data['card_number'][:6]}xxxx|{card_data['month']}|20{card_data['year']}|xxx"
    
    # High hit badge
    high_hit_badge = " 🔥 HIGH HIT" if card_data['is_high_hit'] else ""
    
    # Card type icon
    card_icon = "4️⃣" if card_data['card_type'] == 'VISA' else "5️⃣"
    
    msg = f"""━━━━━━━━━━━━━━━━━━━━━━━━
✅ <b>𝗔𝗣𝗣𝗥𝗢𝗩𝗘𝗗</b>{high_hit_badge}
━━━━━━━━━━━━━━━━━━━━━━━━
💳 <b>𝗖𝗖</b> <code>{card_details}</code>
🍀 <b>𝗚𝗲𝗻</b> <code>/gen {card_masked}</code>
━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ <b>𝗕𝗜𝗡</b> {card_data['bin']}
🏦 <b>𝗕𝗸</b> {card_data['bank']}
🍒 <b>𝗕𝗱</b> {card_data['card_type']}
📌 <b>𝗧𝗲</b> {card_data['type']
👑 <b>𝗟𝘃</b> {card_data['level']}
🌎 <b>𝗖𝗶𝘁𝘆</b> {card_data['country']} {card_data['country_flag']}
━━━━━━━━━━━━━━━━━━━━━━━━
⭐ <b>@{'Scra07bot'}</b>
{datetime.now().strftime('%I:%M %p')}"""
    
    buttons = [
        [Button.inline("𝚅𝙸𝙿", b"vip", style="success"), Button.inline("𝙲𝙷𝙰𝚁𝙶𝙴", b"charge", style="success"), 
        [Button.inline("Mᴀɪɴ", b"main", style="success")]
    ]
    
    try:
        await bot.send_message(chat_id, msg, buttons=buttons, parse_mode='html', link_preview=False)
        return True
    except Exception as e:
        logger.error(f"Error sending card: {e}")
        return False

# Global variable for scraper control
scraper_running = True

async def scrape_cards_continuous(chat_id, total_cards=1000000, delay=0.5):
    """Continuous card scraping in channel"""
    global scraper_running
    scraper_running = True
    
    logger.info(f"🚀 Starting scraper for chat {chat_id}")
    
    success_count = 0
    stats = {'VISA': 0, 'MASTERCARD': 0, 'HighHit': 0}
    start_time = time.time()
    
    for i in range(1, total_cards + 1):
        if not scraper_running:
            logger.info(f"⛔ Scraper stopped by user")
            break
            
        try:
            # Generate card
            card_data = generate_card()
            
            # Update stats
            stats[card_data['card_type']] += 1
            if card_data['is_high_hit']:
                stats['HighHit'] += 1
            
            # Send card
            if await send_approved_card(chat_id, card_data):
                success_count += 1
            
            # Progress
            if i % 50 == 0:
                elapsed = time.time() - start_time
                rate = i / elapsed if elapsed > 0 else 0
                logger.info(f"📊 Progress: {i} cards | Sent: {success_count} | 🔥 HighHit: {stats['HighHit']} | Rate: {rate:.1f}/s")
            
            # Small delay
            await asyncio.sleep(delay)
            
        except Exception as e:
            logger.error(f"Error in scraper: {e}")
            await asyncio.sleep(2)
    
    # Final summary
    elapsed = time.time() - start_time
    logger.info(f"✅ Scraping complete! Sent {success_count} cards in {elapsed:.1f}s")
    
    # Send summary to chat
    summary = f"""📊 <b>SCRAPING COMPLETE</b>
━━━━━━━━━━━━━━━━━━━━━━━━
✅ <b>Total cards sent:</b> {success_count}
💳 <b>VISA:</b> {stats['VISA']}
💳 <b>MASTERCARD:</b> {stats['MASTERCARD']}
🔥 <b>High-Hit:</b> {stats['HighHit']}
⏱️ <b>Time:</b> {elapsed:.1f}s
━━━━━━━━━━━━━━━━━━━━━━━━
Use <code>/scrape</code> to start again"""
    
    await bot.send_message(chat_id, summary, parse_mode='html')

@bot.on(events.NewMessage)
async def handle_messages(event):
    """Handle messages in channels/groups"""
    # Only respond to commands in channels/groups
    if event.is_channel or event.is_group:
        if event.message.text and event.message.text.startswith('/start'):
            chat_id = event.chat_id
            user_id = event.sender_id
            sender = await event.get_sender()
            name = sender.first_name if sender.first_name else "User"
            
            msg = f"""🐍 <b>FROXT</b>
<b>SCRAP BOT</b>
━━━━━━━━━━━━━━━━━━━━━━━━
👤 <b>User ID:</b> <code>{user_id}</code>
👤 <b>Name:</b> {name}
━━━━━━━━━━━━━━━━━━━━━━━━
✅ <b>Bot added to channel!</b>
• Use <code>/scrape</code> to start scraping
• Use <code>/stop</code> to stop scraping
━━━━━━━━━━━━━━━━━━━━━━━━
💳 <b>Cards:</b> VISA & MASTERCARD
🔥 <b>Mode:</b> High-Hit
━━━━━━━━━━━━━━━━━━━━━━━━
<b>Enjoy!</b>"""
            
            await event.reply(msg, parse_mode='html')

# ============ MAIN ============

async def main():
    """Main function"""
    logger.info("="*50)
    logger.info("🐍 SCRAP BOT STARTED!")
    logger.info("💳 Cards: VISA & MASTERCARD")
    logger.info("🔥 High-hit mode enabled")
    logger.info("📌 Bot is ready!")
    logger.info("="*50)
    
    await bot.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
