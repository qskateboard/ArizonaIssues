import random
from datetime import datetime, timedelta
import requests
import re
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup


def read_file(file):
    try:
        f = open("" + file + ".txt", "r")
        return f.read()
    except:
        f = open("" + file + ".txt", "w")
        f.close()
        return ""


def parse_nickname(text):
    nickname = re.findall("([a-zA-Z]{2,}[_| ][a-zA-Z]{2,})", text)
    if len(nickname) > 0:
        nickname = nickname[0]
        if " " in nickname:
            nickname = nickname.replace(" ", "_")

        words = nickname.split("_")
        for word in words:
            if word[0].islower():
                arr = [*word]
                arr[0] = str(arr[0]).upper()
                nickname = nickname.replace(word, ''.join(arr))
        return nickname
    return False


def get_prefix(username):
    if username:
        words = username.split("_")
        prefix = words[0][0] + "." + words[1]
        return prefix
    return False


def send_message(peer_id, text):
    payload = {
        "random_id": random.randint(1, 10000000),
        "peer_id": peer_id,
        "message": text,
        "dont_parse_links": "0",
        "disable_mentions": "0",
        "intent": "default",
        "access_token": "",
        "v": "5.131",
    }
    requests.post("https://api.vk.com/method/messages.send", data=payload)


def get_history(peer_id, count):
    payload = {
        "peer_id": peer_id,
        "count": count,
        "access_token": "",
        "v": "5.131",
    }
    r = requests.post("https://api.vk.com/method/messages.getHistory", data=payload)
    return r.json()['response']['items']


def get_form(name):
    with open(f"forms/{name}.txt", encoding="utf-8") as f:
        return f.read()


def get_game_form(text):
    content = read_file("forms")
    result = []
    for form in content.split("\n"):
        if text in form:
            result.append(form)
    return result


def del_game_form(text):
    content = read_file("forms")
    result = []
    for form in content.split("\n"):
        if text not in form:
            result.append(form)
    f = open("forms.txt", "w")
    f.write('\n'.join(result))
    f.close()


def add_game_form(text):
    f = open("forms.txt", "a+")
    f.write("\n" + text)
    f.close()


def get_monday():
    now = datetime.now()
    monday = now - timedelta(days=now.weekday())
    time = monday.replace(hour=0, minute=0, second=0)
    return int(time.timestamp())


def get_player(nickname):
    try:
        r = requests.get(f"https://api.vprikol.dev/find?server=16&nick={nickname}&token=")
        if r.status_code == 400 or r.status_code == 422 or r.status_code == 504:
            return False
        return r.json()
    except:
        return False


def post_validator(cnt):
    valid = False
    content = [cnt[0].lower(), cnt[1]]
    if "жалоба на игрока" in content[0] and "причина" in content[0]:
        if "1. Ваш игровой ник" in content[1] and "2. Игровой ник нарушителя" in content[1] and \
                "3. Суть жалобы" in content[1] and "4. Доказательства" in content[1] and \
                "5. Тайм-код нарушения на видео" in content[1] and "6. Тайм-код /id и /time" in content[1] and \
                "7. Я полностью отрицаю своё нарушение и категорически не согласен с выданным мне наказанием" in content[1] and \
                "8. В случае обмана в любом из пунктов жалобы я готов получить бан до 2000 дней за обман" in content[1]:
            valid = True
    return valid


def post_validator2(cnt):
    valid = False
    content = [cnt[0].lower(), cnt[1]]
    if "жалоба на игрока" in content[0] and "причина" in content[0]:
        if "Ваш игровой ник" in content[1] and "Игровой ник нарушителя" in content[1] and \
                "Суть жалобы" in content[1] and "Доказательства" in content[1]:
            valid = True
    return valid


def post_validator3(cnt):
    valid = False
    content = [cnt[0].lower(), cnt[1]]
    if "gilbert" in content[0]:
        if "Ваш игровой ник" in content[1] and "Игровой ник нарушителя" in content[1] and \
                "Суть жалобы" in content[1] and "Доказательства" in content[1]:
            valid = True
    return valid


def get_prefix_markup(thread, opened, sticky):
    markup = InlineKeyboardMarkup()

    markup.add(InlineKeyboardButton("⚠️ На рассмотрении", callback_data=f"prefix {thread} 15 {opened} {sticky}"),
               InlineKeyboardButton("✅ Жалоба рассмотрена", callback_data=f"prefix {thread} 17 {opened} {sticky}"))
    markup.add(InlineKeyboardButton("🕔 Опровержение", callback_data=f"prefix {thread} 22 {opened} {sticky}"),
               InlineKeyboardButton("❌ Отказано", callback_data=f"prefix {thread} 18 {opened} {sticky}"))
    markup.add(InlineKeyboardButton("❌", callback_data=f"delete_msg"))

    return markup


def get_message_markup(thread, scopes, nickname=""):
    markup = InlineKeyboardMarkup()
    markup.row_width = 3
    if "form" in scopes:
        markup.add(InlineKeyboardButton("❌ Гос", callback_data=f"form {thread}"),
                   InlineKeyboardButton("❌ Не сост", callback_data=f"pform {thread}"),
                   InlineKeyboardButton("❌ Банды", callback_data=f"bform {thread}"))
        markup.add(InlineKeyboardButton("🖥 Скрин", callback_data=f"screenshot {thread}"),
                   InlineKeyboardButton("🆔 /id или /time", callback_data=f"id_time {thread}"),
                   InlineKeyboardButton("🕔 Таймкоды", callback_data=f"timecode {thread}"),
                   InlineKeyboardButton("📹 Видео не доступно", callback_data=f"not_video {thread}"))
    if "su" in scopes:
        markup.add(InlineKeyboardButton("👮‍♂️ Вам в суд", callback_data=f"su {thread}"),
                   InlineKeyboardButton("👍 Опра принята", callback_data=f"su_close_nice {thread}"),
                   InlineKeyboardButton("👎 Опра не принята", callback_data=f"su_close_bad {thread}"))
    if "band" in scopes:
        markup.add(InlineKeyboardButton("🗿 Опра момента", callback_data=f"band_moment {thread}"),
                   InlineKeyboardButton("🕔 Фулл опра", callback_data=f"band_full_opra {thread}"),
                   InlineKeyboardButton("👍 Опра принята", callback_data=f"band_close_nice {thread}"))
    if "punish" in scopes:
        markup.add(InlineKeyboardButton("‼️ Игрок получит наказание", callback_data=f"punish {thread}"),
                   InlineKeyboardButton("🗒 Свой текст", callback_data=f"edit {thread}"))
    if "open" in scopes:
        markup.add(InlineKeyboardButton("🔒 Закрыть/открыть", callback_data=f"open {thread}"),
                   InlineKeyboardButton("📌 Закрепить/открепить", callback_data=f"pin {thread}"))
    markup.add(InlineKeyboardButton("⚠️ На рассмотрении", callback_data=f"stick {thread}"),
                   InlineKeyboardButton("✅ Жалоба рассмотрена", callback_data=f"begin {thread}"))
    markup.add(InlineKeyboardButton(f"👤 {nickname}", callback_data=f"get_stats {nickname}"))
    return markup


def get_form_markup(chat_id, message_id):
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton("✅ Принять", callback_data=f"accept_form {chat_id} {message_id}"),
               InlineKeyboardButton("❌ Отклонить", callback_data=f"reject_form {chat_id} {message_id}"))

    return markup


def get_info_keyboard(nickname):
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton("👤 Информация", callback_data=f"get_nick {nickname}"),
               InlineKeyboardButton("⚙️ Логи", callback_data=f"get_log {nickname}"))
    markup.add(InlineKeyboardButton("🗒 Поиск по форуму", callback_data=f"forum_find 0 {nickname}"),
               InlineKeyboardButton("💡 Поиск по жалобам", callback_data=f"forum_find 1 {nickname}"))
    markup.add(InlineKeyboardButton("❌ История наказаний", callback_data=f"get_punish {nickname}"))
    markup.add(InlineKeyboardButton("❌", callback_data=f"delete_msg"))

    return markup


def get_delete_keyboard():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("❌", callback_data=f"delete_msg"))
    return markup


def two_factor():
    code = input('Code? ')
    return code, True
