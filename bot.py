‎python
‎import telebot
‎from telebot import types
‎import sqlite3
‎
‎API_TOKEN = 8919047648:AAE3vD_CXTab9RZHnbyD8NOH8hbedowYMyw
‎ADMIN_ID = 6345226762  # Replace with your actual Telegram User ID
‎
‎bot = telebot.TeleBot(API_TOKEN)
‎
‎def init_db():
‎    conn = sqlite3.connect('bot_data.db')
‎    cursor = conn.cursor()
‎    cursor.execute('''
‎        CREATE TABLE IF NOT EXISTS users (
‎            user_id INTEGER PRIMARY KEY,
‎            balance REAL DEFAULT 0.0,
‎            pending INTEGER DEFAULT 0,
‎            approved INTEGER DEFAULT 0,
‎            rejected INTEGER DEFAULT 0,
‎            referred_by INTEGER DEFAULT NULL
‎        )
‎    ''')
‎    cursor.execute('''
‎        CREATE TABLE IF NOT EXISTS tasks (
‎            task_id INTEGER PRIMARY KEY AUTOINCREMENT,
‎            user_id INTEGER,
‎            task_code TEXT
‎        )
‎    ''')
‎    conn.commit()
‎    conn.close()
‎
‎def check_user(user_id, referrer_id=None):
‎    conn = sqlite3.connect('bot_data.db')
‎    cursor = conn.cursor()
‎    cursor.execute('SELECT user_id FROM users WHERE user_id = ?', (user_id,))
‎    if not cursor.fetchone():
‎        if referrer_id and int(referrer_id) != user_id:
‎            cursor.execute('INSERT INTO users (user_id, referred_by) VALUES (?, ?)', (user_id, int(referrer_id)))
‎        else:
‎            cursor.execute('INSERT INTO users (user_id) VALUES (?)', (user_id,))
‎        conn.commit()
‎    conn.close()
‎
‎def main_menu():
‎    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
‎    markup.add(
‎        types.KeyboardButton('📝 কাজ •'), types.KeyboardButton('💵 ব্যালেন্স'),
‎        types.KeyboardButton('💰 টাকা উত্তোলন'), types.KeyboardButton('🎁 My Referrals'),
‎        types.KeyboardButton('🎧 সাপোর্ট'), types.KeyboardButton('🙋 আমি নতুন'),
‎        types.KeyboardButton('👑 এডমিন প্যানেল')
‎    )
‎    return markup
‎
‎def admin_menu():
‎    markup = types.InlineKeyboardMarkup(row_width=1)
‎    markup.add(
‎        types.InlineKeyboardButton('📋 পেন্ডিং লিস্ট', callback_data='admin_pending')
‎    )
‎    return markup
‎
‎@bot.message_handler(commands=['start'])
‎def send_welcome(message):
‎    args = message.text.split()
‎    referrer_id = args[1] if len(args) > 1 and args[1].isdigit() else None
‎    check_user(message.from_user.id, referrer_id)
‎    bot.send_message(
‎        message.chat.id, 
‎        f"স্বাগতম {message.from_user.first_name}!\nআমাদের আর্নিং বটের সাথে যুক্ত হওয়ার জন্য আপনাকে ধন্যবাদ। নিচের মেনু থেকে অপশন সিলেক্ট করুন।", 
‎        reply_markup=main_menu()
‎    )
‎
‎@bot.message_handler(func=lambda message: True)
‎def handle_menu_options(message):
‎    user_id = message.from_user.id
‎    check_user(user_id)
‎    
‎    if message.text == '📝 কাজ •':
‎        msg = ("ℹ️ **ইনস্টাগ্রাম 2fa কাজ (৳৩.০০)**\n\n"
‎               "👤 **Username:** `example_user`\n"
‎               "🔐 **Password:** `password123`\n\n"
‎               "👉 একাউন্ট লগইন করে, আপনার **২FA সিক্রেট কোড/ব্যাকআপ কোডটি** নিচে লিখে মেসেজ পাঠান।")
‎        bot.send_message(message.chat.id, msg, parse_mode='Markdown')
‎        bot.register_next_step_handler(message, process_task_submission)
‎
‎    elif message.text == '💵 ব্যালেন্স':
‎        conn = sqlite3.connect('bot_data.db')
‎        cursor = conn.cursor()
‎        cursor.execute('SELECT balance, pending, approved, rejected FROM users WHERE user_id = ?', (user_id,))
‎        row = cursor.fetchone()
‎        conn.close()
‎        balance_msg = (f"💰 **আপনার ব্যালেন্স ও কাজের রিপোর্ট**\n"
‎                       f"━━━━━━━━━━━━━━━━━━\n"
‎                       f"🔥 **মূল ব্যালেন্স:** {row[0]:.2f} BDT\n"
‎                       f"📩 **পেন্ডিং কাজ:** {row[1]} টি\n"
‎                       f"✅ **এপ্রুভড কাজ:** {row[2]} টি\n"
‎                       f"❌ **রিজেক্টেড কাজ:** {row[3]} টি")
‎        bot.send_message(message.chat.id, balance_msg, parse_mode='Markdown')
‎
‎    elif message.text == '💰 টাকা উত্তোলন':
‎        markup = types.InlineKeyboardMarkup(row_width=2)
‎        markup.add(
‎            types.InlineKeyboardButton('bKash', callback_data='withdraw_bkash'),
‎            types.InlineKeyboardButton('Nagad', callback_data='withdraw_nagad')
‎        )
‎        bot.send_message(message.chat.id, "📩 টাকা তোলার মাধ্যম সিলেক্ট করুন:", reply_markup=markup)
‎
‎    elif message.text == '🎁 My Referrals':
‎        conn = sqlite3.connect('bot_data.db')
‎        cursor = conn.cursor()
‎        cursor.execute('SELECT COUNT(*) FROM users WHERE referred_by = ?', (user_id,))
‎        total_referrals = cursor.fetchone()[0]
‎        conn.close()
‎        bot_username = bot.get_me().username
‎        ref_link = f"https://t.me/{bot_username}?start={user_id}"
‎        ref_msg = (f"🎁 **রেফারেল প্রোগ্রাম**\n\n"
‎                   f"আপনার রেফারেল লিংক ব্যবহার করে কাউকে জয়েন করালে বোনাস পাবেন (যদি এডমিন চালু রাখে)।\n\n"
‎                   f"🔗 **আপনার রেফারাল লিংক:**\n{ref_link}\n\n"
‎                   f"👥 **মোট সফল রেফার:** {total_referrals} জন")
‎        bot.send_message(message.chat.id, ref_msg, parse_mode='Markdown')
‎
‎    elif message.text == '🎧 সাপোর্ট':
‎        bot.send_message(message.chat.id, f"🎧 কোনো সমস্যা হলে আমাদের এডমিনের সাথে যোগাযোগ করুন: @YourAdminUsername")
‎
‎    elif message.text == '🙋 আমি নতুন':
‎        instructions = ("🙋 **নতুন ব্যবহারকারীদের জন্য নির্দেশিকা:**\n\n"
‎                        "১. প্রথমে '📝 কাজ •' বাটনে ক্লিক করুন।\n"
‎                        "২. দেওয়া টাস্কের বিবরণ পড়ে কাজটি সম্পন্ন করুন।\n"
‎                        "৩. প্রমাণ (যেমন: কোড বা আইডি) বটের ইনবক্সে লিখে সেন্ড করুন।\n"
‎                        "৪. এডমিন আপনার কাজ যাচাই করে ব্যালেন্স এপ্রুভ করে দেবে।")
‎        bot.send_message(message.chat.id, instructions, parse_mode='Markdown')
‎
‎    elif message.text == '👑 এডমিন প্যানেল':
‎        if user_id == ADMIN_ID:
‎            bot.send_message(message.chat.id, "👑 এডমিন কন্ট্রোল প্যানেল:", reply_markup=admin_menu())
‎        else:
‎            bot.send_message(message.chat.id, "❌ আপনি এই বটের অ্যাডমিন নন!")
‎
‎def process_task_submission(message):
‎    user_id = message.from_user.id
‎    task_code = message.text
‎    if task_code in ['📝 কাজ •', '💵 ব্যালেন্স', '💰 টাকা উত্তোলন', '🎁 My Referrals', '🎧 সাপোর্ট', '🙋 আমি নতুন', '👑 এডমিন প্যানেল']:
‎        handle_menu_options(message)
‎        return
‎    conn = sqlite3.connect('bot_data.db')
‎    cursor = conn.cursor()
‎    cursor.execute('UPDATE users SET pending = pending + 1 WHERE user_id = ?', (user_id,))
‎    cursor.execute('INSERT INTO tasks (user_id, task_code) VALUES (?, ?)', (user_id, task_code))
‎    conn.commit()
‎    conn.close()
‎    bot.send_message(message.chat.id, "👍 আপনার কাজ সফলভাবে গ্রহণ করা হয়েছে। এডমিন ভেরিফাই করার পর ব্যালেন্স যোগ হবে।")
‎    bot.send_message(ADMIN_ID, f"📩 **নতুন কাজ জমা পড়েছে!**\n\n👤 **User ID:** `{user_id}`\n🔑 **Code:** {task_code}\n\nপেন্ডিং চেক করতে এডমিন প্যানেলে যান।", parse_mode='Markdown')
‎
‎def process_withdrawal(message, method):
‎    user_id = message.from_user.id
‎    input_text = message.text
‎    try:
‎        parts = input_text.split()
‎        if len(parts) < 2:
‎            raise ValueError
‎        number = parts[0]
‎        amount = float(parts[1])
‎        conn = sqlite3.connect('bot_data.db')
‎        cursor = conn.cursor()
‎        cursor.execute('SELECT balance FROM users WHERE user_id = ?', (user_id,))
‎        balance = cursor.fetchone()[0]
‎        if amount > balance:
‎            bot.send_message(message.chat.id, "❌ আপনার একাউন্টে পর্যাপ্ত ব্যালেন্স নেই!")
‎            conn.close()
‎            return
‎        if amount < 20:
‎            bot.send_message(message.chat.id, "❌ সর্বনিম্ন উত্তোলন ২০ টাকা।")
‎            conn.close()
‎            return
‎        cursor.execute('UPDATE users SET balance = balance - ? WHERE user_id = ?', (amount, user_id))
‎        conn.commit()
‎        conn.close()
‎        bot.send_message(message.chat.id, f"✅ আপনার {amount:.2f} BDT উত্তোলনের অনুরোধ জমা হয়েছে।")
‎        bot.send_message(ADMIN_ID, f"💰 **টাকা উত্তোলনের রিকোয়েস্ট!**\n\n👤 User: `{user_id}`\n🛠 Method: **{method}**\n📱 Number: `{number}`\n💵 Amount: **{amount:.2f} BDT**", parse_mode='Markdown')
‎    except ValueError:
‎        bot.send_message(message.chat.id, "❌ ভুল ফরম্যাট! দয়া করে আবার চেষ্টা করুন। উদাহরণ: `017XXXXXXXX 50`", parse_mode='Markdown')
‎
‎@bot.callback_query_handler(func=lambda call: True)
‎def callback_inline(call):
‎    conn = sqlite3.connect('bot_data.db')
‎    cursor = conn.cursor()
‎    if call.data.startswith('withdraw_'):
‎        method = call.data.split('_')[1].upper()
‎        bot.answer_callback_query(call.id)
‎        msg = bot.send_message(call.message.chat.id, f"আপনি **{method}** সিলেক্ট করেছেন।\nআপনার নম্বর এবং টাকার পরিমাণ স্পেস দিয়ে একসাথে লিখুন।\n\n👉 উদাহরণ: `01712345678 100`", parse_mode='Markdown')
‎        bot.register_next_step_handler(msg, process_withdrawal, method)
‎    elif call.data == 'admin_pending':
‎        cursor.execute('SELECT * FROM tasks')
‎        rows = cursor.fetchall()
‎        if not rows:
‎            bot.send_message(call.message.chat.id, "কোনো পেন্ডিং কাজ নেই।")
‎        else:
‎            for row in rows:
‎                task_id, target_user, task_code = row
‎                markup = types.InlineKeyboardMarkup()
‎                markup.add(
‎                    types.InlineKeyboardButton('Approve ✅', callback_data=f'app_{task_id}_{target_user}'),
‎                    types.InlineKeyboardButton('Reject ❌', callback_data=f'rej_{task_id}_{target_user}')
‎                )
‎                bot.send_message(call.message.chat.id, f"🆔 **Task ID:** {task_id}\n👤 **User:** `{target_user}`\n🔑 **Code:** `{task_code}`", reply_markup=markup, parse_mode='Markdown')
‎    elif call.data.startswith('app_'):
‎        _, task_id, target_user = call.data.split('_')
‎        target_user = int(target_user)
‎        task_id = int(task_id)
‎        cursor.execute('SELECT task_id FROM tasks WHERE task_id = ?', (task_id,))
‎        if cursor.fetchone():
‎            cursor.execute('UPDATE users SET balance = balance + 3.00, pending = CASE WHEN pending > 0 THEN pending - 1 ELSE 0 END, approved = approved + 1 WHERE user_id = ?', (target_user,))
‎            cursor.execute('DELETE FROM tasks WHERE task_id = ?', (task_id,))
‎            conn.commit()
‎            try:
‎                bot.send_message(target_user, "✅ আপনার জমা দেওয়া কাজটি এপ্রুভ হয়েছে এবং আপনার ব্যালেন্সে ৩.০০ টাকা যোগ হয়েছে!")
‎            except Exception:
‎                pass
‎            bot.edit_message_text(f"✅ টাস্ক #{task_id} এপ্রুভড!", call.message.chat.id, call.message.message_id)
‎        else:
‎            bot.answer_callback_query(call.id, "❌ এই টাস্কটি ইতিমধ্যেই প্রসেস করা হয়েছে।")
‎    elif call.data.startswith('rej_'):
‎        _, task_id, target_user = call.data.split('_')
‎        target_user = int(target_user)
‎        task_id = int(task_id)
‎        cursor.execute('SELECT task_id FROM tasks WHERE task_id = ?', (task_id,))
‎        if cursor.fetchone():
‎            cursor.execute('UPDATE users SET pending = CASE WHEN pending > 0 THEN pending - 1 ELSE 0 END, rejected = rejected + 1 WHERE user_id = ?', (target_user,))
‎            cursor.execute('DELETE FROM tasks WHERE task_id = ?', (task_id,))
‎            conn.commit()
‎            try:
‎                bot.send_message(target_user, "❌ আপনার কাজটি রিজেক্ট করা হয়েছে। সঠিক তথ্য দিয়ে আবার চেষ্টা করুন।")
‎            except Exception:
‎                pass
‎            bot.edit_message_text(f"❌ টাস্ক #{task_id} রিজেক্টেড!", call.message.chat.id, call.message.message_id)
‎        else:
‎            bot.answer_callback_query(call.id, "❌ এই টাস্কটি ইতিমধ্যেই প্রসেস করা হয়েছে।")
‎    conn.close()
‎
‎if __name__ == '__main__':
‎    init_db()
‎    print("Bot is up and running successfully...")
‎    bot.infinity_polling()
‎
‎```
‎
‎```text
‎pyTelegramBotAPI==4.12.0
‎
‎```
‎```text
‎worker: python bot.py
‎
‎```
‎
