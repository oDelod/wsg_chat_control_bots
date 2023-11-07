import telebot
import time
import os

# Створюємо об'єкт бота за допомогою токена, отриманого від BotFather
bot = telebot.TeleBot('6202439255:AAEkaq6I283mU6MvoEIKC0hr6Zcq9ZOurBg')

topic_id = 4
chat_id = -1002077133149  # Оновіть на вірний chat_id




# Шлях до файлу для збереження ідентифікаторів адміністраторів
admin_ids_file = "admin_ids.txt"

# Функція для завантаження ідентифікаторів адміністраторів із файлу
def load_admin_ids():
    if os.path.exists(admin_ids_file):
        with open(admin_ids_file, "r") as f:
            return [int(line.strip()) for line in f]
    return []


def save_admin_ids(admin_ids):
    with open(admin_ids_file, "w") as f:
        for admin_id in admin_ids:
            f.write(str(admin_id) + "\n")

admin_ids = load_admin_ids()

# Функція для визначення імені користувача за його user_id
def get_user_name(user_id):
    user = bot.get_chat_member(chat_id, user_id)
    return user.user.first_name

# Функція для отримання ідентифікаторів адміністраторів
def get_admin_ids(chat_id):
    try:
        chat_info = bot.get_chat(chat_id)
        admins = bot.get_chat_administrators(chat_id)
        admin_ids = [admin.user.id for admin in admins]
        return admin_ids
    except Exception as e:
        print(f"Помилка при отриманні ідентифікаторів адміністраторів: {e}")
        return []

# Ось обробник команди для отримання ідентифікаторів адміністраторів


@bot.message_handler(commands=['get_admin_ids'])
def handle_get_admin_ids(message):
    chat_id = message.chat.id
    update_admin_ids(chat_id)  # Оновити ідентифікатори адміністраторів
    admin_ids = get_admin_ids(chat_id)
    if admin_ids:
        bot.send_message(chat_id, f"Ідентифікатори адміністраторів чату отримані")
        # bot.send_message(chat_id, f"Ідентифікатори адміністраторів чату: {admin_ids}")
    else:
        bot.send_message(chat_id, "Не вдалося отримати ідентифікатори адміністраторів.")


# Ваша інша логіка тут

# Після запиту на ідентифікатори адміністраторів, оновіть їх і збережіть у файл
# Наприклад:
def update_admin_ids(chat_id):
    global admin_ids
    admin_ids = get_admin_ids(chat_id)
    save_admin_ids(admin_ids)

# Механізм заборони писання в правилах------------------------------

# визначаємо функцію, яка буде обробляти повідомлення від користувачів
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    # перевіряємо, чи має повідомлення message_thread_id
    if message.message_thread_id == topic_id:
        user_id = message.from_user.id

        # Перевірка, чи користувач є адміністратором
        if user_id in admin_ids:
            # якщо ні, то ігноруємо повідомлення
            pass
        else:
            # Якщо користувач не є адміністратором, відправляємо його нік та видаляємо повідомлення користувача негайно
            user_name = get_user_name(user_id)
            sent_message = bot.reply_to(message, f"{user_name}, ви не можете писати в цій гілці, тому ваше повідомлення було видалено")
            # Запускаємо функцію для видалення повідомлення користувача негайно
            delete_user_message(message.chat.id, message.message_id)
            # Зберегти message_id відповіді бота
            message_id_to_delete = sent_message.message_id
            # Видалити відповідь бота через 5 секунд
            time.sleep(5)
            bot.delete_message(chat_id, message_id_to_delete)
    else:
        # якщо ні, то ігноруємо повідомлення
        pass
# Функція для видалення повідомлення користувача через певний час
def delete_user_message(chat_id, message_id, delay=1):
    time.sleep(delay)
    try:
        bot.delete_message(chat_id, message_id)
    except telebot.apihelper.ApiTelegramException as e:
        print(f"Помилка при видаленні повідомлення користувача: {e}")
# Функція для збереження ідентифікаторів адміністраторів у файлі



#Вітнання та прощання з людьми -----------------------------------------
# Ось обробник повідомлень, який вітає нових учасників чату
@bot.message_handler(func=lambda message: hasattr(message, 'new_chat_members'), content_types=['new_chat_members'])
def welcome_new_members(message):
    for user in message.new_chat_members:
        user_name = user.first_name
        bot.send_message(message.chat.id, f"Ласкаво просимо, {user_name}, до чату!")

# Ось обробник повідомлень, який прощається з учасниками, які покидають чат
@bot.message_handler(func=lambda message: hasattr(message, 'left_chat_member'), content_types=['left_chat_member'])
def goodbye_member(message):
    user_name = message.left_chat_member.first_name
    bot.send_message(message.chat.id, f"До побачення, {user_name}!")




# запускаємо бота
bot.polling(non_stop=True)