import os
import requests
import random
import time
import json
import logging
from faker import Faker
from datetime import datetime
from flask import Flask, request
import threading
from concurrent.futures import ThreadPoolExecutor

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

fake = Faker()

# ============ CONFIGURATION ============
BOT_TOKEN = os.environ.get('BOT_TOKEN', '8815044105:AAFF9ekYN74wnLQPFUQ3Tm5RA8g4MHvqq0Q')
CHAT_ID = int(os.environ.get('CHAT_ID', -1004455513816))
WEBHOOK_URL = os.environ.get('WEBHOOK_URL', 'https://your-app.onrender.com/webhook')

# Channel Links (Update these)
CHANNEL_LINKS = {
    'main': 'https://t.me/atulfroxt',
    'carding': 'https://t.me/+sT1N0pne6sQzNTFl',
    'charge': 'https://t.me/+rzRUgyJfia84NjBl',
    'vip': 'https://t.me/+u9cv-q_x57xkNzA1',
    'paid_dumps': 'https://t.me/+yn-01TbWsfk2NTU1',
    'web': 'https://your-website.com',
    'approved_cards': 'https://t.me/aaproved_card07'
}

# Start Image URL
START_IMAGE = "https://ibb.co/vx25TtC0"  # Replace with your image

# ============ CARD BINS ============
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
    'ADDITION FINANCIAL CREDIT UNION', 'GOLDMAN SACHS',
    'MORGAN STANLEY', 'JPMORGAN CHASE', 'AMERICAN EXPRESS'
]

CARD_LEVELS = ['CLASSIC', 'GOLD', 'PLATINUM', 'SIGNATURE', 'WORLD ELITE', 'BLACK']

# ============ TELEGRAM API FUNCTIONS ============

def send_telegram_message(chat_id, text, reply_markup=None, photo=None, parse_mode='HTML', disable_web_page_preview=True):
    """Send message to Telegram"""
    telegram_api = f'https://api.telegram.org/bot{BOT_TOKEN}'
    
    try:
        if photo:
            data = {
                'chat_id': chat_id,
                'caption': text,
                'parse_mode': parse_mode,
                'disable_web_page_preview': disable_web_page_preview,
                'reply_markup': json.dumps(reply_markup) if reply_markup else None
            }
            files = {'photo': requests.get(photo).content}
            response = requests.post(f'{telegram_api}/sendPhoto', data=data, files=files)
        else:
            data = {
                'chat_id': chat_id,
                'text': text,
                'parse_mode': parse_mode,
                'disable_web_page_preview': disable_web_page_preview,
                'reply_markup': json.dumps(reply_markup) if reply_markup else None
            }
            response = requests.post(f'{telegram_api}/sendMessage', data=data)
        
        return response.json()
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        return None

def edit_telegram_message(chat_id, message_id, text, reply_markup=None, parse_mode='HTML'):
    """Edit existing message"""
    telegram_api = f'https://api.telegram.org/bot{BOT_TOKEN}'
    
    try:
        data = {
            'chat_id': chat_id,
            'message_id': message_id,
            'text': text,
            'parse_mode': parse_mode,
            'reply_markup': json.dumps(reply_markup) if reply_markup else None
        }
        response = requests.post(f'{telegram_api}/editMessageText', data=data)
        return response.json()
    except Exception as e:
        logger.error(f"Error editing message: {e}")
        return None

# ============ CARD GENERATION FUNCTIONS ============

def generate_card_number(card_type):
    """Generate valid card number"""
    if card_type == 'Visa':
        if random.random() < 0.7:
            bin_prefix = random.choice(HIGH_HIT_VISA)
        else:
            bin_prefix = random.choice(VISA_BINS)
    else:  # Mastercard
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

def generate_card():
    """Generate complete card details"""
    card_type = random.choices(['Visa', 'Mastercard'], weights=[55, 45], k=1)[0]
    card_number = generate_card_number(card_type)
    
    month = str(random.randint(1, 12)).zfill(2)
    year = str(random.randint(27, 38)).zfill(2)
    cvv = str(random.randint(100, 999)).zfill(3)
    
    bin_number = card_number[:6]
    bank = random.choice(PREMIUM_BANKS)
    level = random.choices(CARD_LEVELS, weights=[5, 10, 30, 25, 20, 10], k=1)[0]
    card_type_display = random.choice(['DEBIT', 'CREDIT'])
    
    return {
        'card_number': card_number,
        'month': month,
        'year': year,
        'cvv': cvv,
        'card_type': card_type.upper(),
        'bin': bin_number,
        'bank': bank,
        'level': level,
        'country': 'UNITED STATES',
        'country_flag': '🇺🇸',
        'type': card_type_display,
        'is_high_hit': any(bin_number.startswith(b) for b in HIGH_HIT_VISA + HIGH_HIT_MASTERCARD)
    }

def luhn_check(card_number):
    """Verify card number"""
    digits = [int(d) for d in card_number]
    for i in range(len(digits) - 2, -1, -2):
        digits[i] *= 2
        if digits[i] > 9:
            digits[i] -= 9
    return sum(digits) % 10 == 0

# ============ KEYBOARD BUTTONS ============

async def menu_main_callback(event):
    user_id = event.sender_id
    sender = await event.get_sender()
    name = sender.first_name if sender.first_name else "User"
    msg = f"""🐍 <b>FROXT</b>\n"
<b>SCRAP BOT</b>\n"
━━━━━━━━━━━━━━━━━━━━━━━━\n"
👤 <b>User ID:</b> <code>{user_id}</code>\n"
👤 <b>Name:</b> {username or first_name}\n"
━━━━━━━━━━━━━━━━━━━━━━━━\n"
⚠️ <i>No Channel Added</i>\n"
• Use '🔗 Add Channel' button to add your channel\n"
• <b>Enjoy!</b>"""
    buttons = [
        [Button.url("𝙼𝙰𝙸𝙽", "https://t.me/atulfroxt", style="success"), Button.url("𝙲𝙰𝚁𝙳𝙸𝙽𝙶", "https://t.me/+sT1N0pne6sQzNTFl", style="success")],
        [Button.url("𝙲𝙷𝙰𝚁𝙶𝙴", "https://t.me/+rzRUgyJfia84NjBl", style="success"), Button.url("𝚅𝙸𝙿", "https://t.me/+u9cv-q_x57xkNzA1", style="success")],
        [Button.url("𝙿𝙰𝙸𝙳_𝙳𝚄𝙼𝙿𝚂", "https://t.me/+yn-01TbWsfk2NTU1", style="success"), Button.url("𝚆𝙴𝙱", "https://your-website.com", style="success")],
        [Button.url("𝙰𝙰𝙿𝚁𝙾𝚅𝙴𝙳_𝙲𝙰𝚁𝙳", "https://t.me/aaproved_card07", style="success")]
        [Button.inline("𝙰𝙳𝙳 𝙲𝙷𝙰𝙽𝙽𝙴𝙻", b"menu_close", style="danger")]
    ]
    await event.edit(premium_emoji(msg), buttons=buttons, parse_mode='html', link_preview=False)
    
    # Send with image
    return send_telegram_message(
        chat_id=chat_id,
        text=welcome_text,
        reply_markup=reply_markup,
        photo=START_IMAGE
    )

# ============ COMMAND HANDLERS ============

def handle_start(chat_id, user_id, username, first_name):
    """Handle /start command"""
    
    welcome_text = (
        f"🐍 <b>FROXT</b>\n"
        f"<b>SCRAP BOT</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 <b>User ID:</b> <code>{user_id}</code>\n"
        f"👤 <b>Name:</b> {username or first_name}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"⚠️ <i>No Channel Added</i>\n"
        f"• Use '🔗 Add Channel' button to add your channel\n"
        f"• <b>Enjoy!</b>\n"
    )
    
    return send_telegram_message(
        chat_id=chat_id,
        text=welcome_text,
        reply_markup=get_start_keyboard(),
        photo=START_IMAGE
    )

def handle_approved_card(chat_id):
    """Generate and send approved card"""
    card_data = generate_card()
    
    # Format card details
    card_details = f"{card_data['card_number']}|{card_data['month']}|20{card_data['year']}|{card_data['cvv']}"
    card_masked = f"{card_data['card_number'][:6]}xxxx|{card_data['month']}|20{card_data['year']}|xxx"
    
    reply_markup = {
            "inline_keyboard": [
                [
                    {"text": "𝚅𝙸𝙿", "url": "https://t.me/+u9cv-q_x57xkNzA1"},
                    {"text": "𝙲𝙷𝙰𝚁𝙶𝙴", "url": "https://t.me/+rzRUgyJfia84NjBl"},
                ],
                [
                    {"text": "Mᴀɪɴ", "url": "https://t.me/atulfroxt"},
                ]
            ]
        }
    
    # High hit badge
    high_hit_badge = " 🔥 HIGH HIT" if card_data['is_high_hit'] else ""
    
    message = (
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"✅ <b>𝗔𝗣𝗣𝗥𝗢𝗩𝗘𝗗</b>{high_hit_badge}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"💳 <b>𝗖𝗖</b> <code>{card_details}</code>\n"
        f"🍀 <b>𝗚𝗲𝗻</b> <code>/gen {card_masked}</code>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"⚠️ <b>𝗕𝗜𝗡</b> {card_data['bin']}\n"
        f"🏦 <b>𝗕𝗸</b> {card_data['bank']}\n"
        f"🍒 <b>𝗕𝗱</b> {card_data['card_type']}\n"
        f"📌 <b>𝗧𝗲</b> {card_data['type']}\n"
        f"👑 <b>𝗟𝘃</b> {card_data['level']}\n"
        f"🌎 <b>𝗖𝗶𝘁𝘆</b> {card_data['country']} {card_data['country_flag']}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"⭐ <b>@{'Scra07bot'}</b>\n"
        f"{datetime.now().strftime('%I:%M %p')}\n"
    )
    
    return send_telegram_message(
        chat_id=chat_id,
        text=message,
        reply_markup=get_card_keyboard()
    )

def handle_channel_link(chat_id, channel_key):
    """Handle channel link buttons"""
    if channel_key in CHANNEL_LINKS:
        url = CHANNEL_LINKS[channel_key]
        names = {
            'main': '🏠 Main Channel',
            'carding': '💳 Carding Channel',
            'charge': '⚡ Charge Channel',
            'vip': '👑 VIP Channel',
            'paid_dumps': '💰 Paid Dumps',
            'web': '🌐 Website'
        }
        
        text = f"{names.get(channel_key, 'Channel')}\n\n{url}"
        
        return send_telegram_message(
            chat_id=chat_id,
            text=text,
            reply_markup=get_single_button_keyboard("🔗 Open", url)
        )

# ============ SCRAPER FUNCTION ============

def scrape_cards_continuous(chat_id, total_cards=100000, delay=0.5):
    """Continuous card scraping"""
    logger.info(f"Starting scraper for chat {chat_id}")
    
    success_count = 0
    stats = {'Visa': 0, 'Mastercard': 0, 'HighHit': 0}
    
    for i in range(1, total_cards + 1):
        # Generate card
        card_data = generate_card()
        
        # Validate
        if not luhn_check(card_data['card_number']):
            continue
        
        # Update stats
        stats[card_data['card_type']] += 1
        if card_data['is_high_hit']:
            stats['HighHit'] += 1
        
        # Send card
        if handle_approved_card(chat_id):
            success_count += 1
        
        # Progress
        if i % 100 == 0:
            logger.info(f"📊 Progress: {i}/{total_cards} | Sent: {success_count} | 🔥 HighHit: {stats['HighHit']}")
        
        # Small delay
        time.sleep(delay)
    
    logger.info(f"✅ Scraping complete. Sent {success_count} cards")
    return success_count

# ============ FLASK WEBHOOK ============

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    return """
    <html>
        <head>
            <title>SCRAP BOT</title>
            <style>
                body {
                    background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
                    color: #fff;
                    font-family: Arial, sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                    text-align: center;
                }
                .container {
                    padding: 40px;
                    background: rgba(255,255,255,0.05);
                    border-radius: 20px;
                    border: 1px solid rgba(255,255,255,0.1);
                }
                h1 {
                    font-size: 3em;
                    background: linear-gradient(45deg, #f093fb, #f5576c);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                }
                .status {
                    color: #4ade80;
                    font-size: 1.2em;
                    margin-top: 20px;
                }
                .status::before {
                    content: "● ";
                    animation: blink 1s infinite;
                }
                @keyframes blink {
                    0%, 100% { opacity: 1; }
                    50% { opacity: 0; }
                }
                .buttons {
                    margin-top: 30px;
                    display: flex;
                    gap: 10px;
                    justify-content: center;
                    flex-wrap: wrap;
                }
                .btn {
                    background: rgba(255,255,255,0.1);
                    padding: 10px 20px;
                    border-radius: 10px;
                    border: 1px solid rgba(255,255,255,0.2);
                    color: #fff;
                    text-decoration: none;
                    transition: all 0.3s;
                }
                .btn:hover {
                    background: rgba(255,255,255,0.2);
                    transform: scale(1.05);
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🐍 SCRAP BOT</h1>
                <div class="status">Bot is Online</div>
                <div class="buttons">
                    <span class="btn">💳 Visa</span>
                    <span class="btn">💳 Mastercard</span>
                    <span class="btn">🔥 High Hit</span>
                </div>
            </div>
        </body>
    </html>
    """, 200

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle incoming updates"""
    try:
        update = request.get_json()
        
        if not update:
            return "OK", 200
        
        # Handle message
        if 'message' in update:
            message = update['message']
            chat_id = message['chat']['id']
            user_id = message['from']['id']
            username = message['from'].get('username', 'User')
            first_name = message['from'].get('first_name', 'User')
            
            # Handle commands
            if 'text' in message:
                text = message['text']
                
                if text == '/start':
                    handle_start(chat_id, user_id, username, first_name)
                
                elif text == '/scrape':
                    send_telegram_message(
                        chat_id=chat_id,
                        text="🚀 <b>Starting Scraper...</b>\n\nSending approved cards to this chat!\nPress /stop to stop."
                    )
                    threading.Thread(target=scrape_cards_continuous, args=(chat_id, 100000, 0.5)).start()
                
                elif text == '/stop':
                    send_telegram_message(
                        chat_id=chat_id,
                        text="⛔ <b>Scraper Stopped</b>\n\nTo start again use /scrape"
                    )
                
                elif text.startswith('/gen'):
                    # Handle /gen command
                    send_telegram_message(
                        chat_id=chat_id,
                        text="✅ <b>Card Generated</b>\n\nUse /scrape to get live cards"
                    )
        
        # Handle callback queries (button clicks)
        elif 'callback_query' in update:
            callback = update['callback_query']
            chat_id = callback['message']['chat']['id']
            message_id = callback['message']['message_id']
            data = callback['data']
            
            # Acknowledge callback
            requests.post(
                f'https://api.telegram.org/bot{BOT_TOKEN}/answerCallbackQuery',
                data={'callback_query_id': callback['id']}
            )
            
            # Handle button clicks
            if data == 'main':
                handle_channel_link(chat_id, 'main')
            
            elif data == 'carding':
                handle_channel_link(chat_id, 'carding')
            
            elif data == 'charge':
                handle_channel_link(chat_id, 'charge')
            
            elif data == 'vip':
                handle_channel_link(chat_id, 'vip')
            
            elif data == 'paid_dumps':
                handle_channel_link(chat_id, 'paid_dumps')
            
            elif data == 'web':
                handle_channel_link(chat_id, 'web')
            
            elif data == 'approved_card':
                handle_approved_card(chat_id)
            
            elif data == 'add_channel':
                add_channel_text = (
                    "🔗 <b>Add Channel</b>\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    "📌 <b>How to add bot to your channel:</b>\n\n"
                    "1️⃣ Add @YourBotName as admin to your channel\n"
                    "2️⃣ Send <code>/start</code> in your channel\n"
                    "3️⃣ Bot will start scraping cards there\n\n"
                    "⚠️ Make sure to give bot admin permissions!"
                )
                send_telegram_message(
                    chat_id=chat_id,
                    text=add_channel_text,
                    reply_markup={
                        "inline_keyboard": [
                            [{"text": "Bᴀᴄᴋ", "callback_data": "main"}]
                        ]
                    }
                )
        
        return "OK", 200
    
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return "Error", 500

# ============ MAIN ============

def set_webhook():
    """Set webhook for the bot"""
    try:
        response = requests.get(
            f'https://api.telegram.org/bot{BOT_TOKEN}/setWebhook',
            params={'url': WEBHOOK_URL}
        )
        logger.info(f"Webhook set: {response.json()}")
        return response.json()
    except Exception as e:
        logger.error(f"Failed to set webhook: {e}")
        return None

def keep_alive():
    """Keep the bot running"""
    from threading import Thread
    
    def run():
        app.run(host='0.0.0.0', port=8080)
    
    t = Thread(target=run)
    t.daemon = True
    t.start()

if __name__ == '__main__':
    # Start keep-alive
    keep_alive()
    
    # Set webhook
    set_webhook()
    
    logger.info("🐍 SCRAP BOT Started!")
    logger.info(f"📡 Webhook: {WEBHOOK_URL}")
    logger.info("💳 Cards: Visa & Mastercard")
    logger.info("🔥 High-hit mode enabled")
    
    # Keep the script running
    while True:
        time.sleep(60)
