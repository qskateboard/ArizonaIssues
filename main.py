import datetime
import json
import random
import re
import threading
import time
import datetime

import requests
import telebot
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton


import bypass
import api
import utils
from operations import *

actions = {}
t_id = "1259320494"

main_token = "28"
beta_token = "539l5c"
vk_token = ""

bot = telebot.TeleBot(main_token, parse_mode="html")
ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
cookie = utils.read_file("cookies")
to_check = "1589"
rules = json.loads(open("PR.bind", "r", encoding="windows-1251").read())
auto_ans = True
log_timer = 0

track_users = [5, 21]
ans_reward = 4
ignore_threads = []
run_time = time.time()

database = [
    {
        "chat": "-1001567410754",  # 1464601473
        "category": "1589",
        "scope": "form,su,punish,open",
        "prefix": "жб сост#",
        "url": "1567410754",
        "valid": utils.post_validator,
        "invalid": "invalid",
    },
    {
        "chat": "-1001567410754",  # 1464601473
        "category": "1588",
        "scope": "form,su,punish,open",
        "prefix": "жб не сост#",
        "url": "1567410754",
        "valid": utils.post_validator2,
        "invalid": "invalid2",
    },
    {
        "chat": "-1001567410754",  # 1464601473
        "category": "1591",
        "scope": "form,band,punish,open",
        "prefix": "жб банды#",
        "url": "1567410754",
        "valid": utils.post_validator3,
        "invalid": "invalid3",
    },
]

fractions = {
    "Полиция г. Лос-Сантос": "МЮ",
    "Полиция г.Сан-Фиерро": "МЮ",
    "Областная полиция": "МЮ",
    "ФБР": "МЮ",
    "Больница г. Лос-Сантос": "МЗ",
    "Правительство": "Право",
    "Тюрьма строгого режима": "МО",
    "Больница г. Сан-Фиерро": "МЗ",
    "Инструкторы": "ЦА",
    "Новостное агенство": "СМИ",
    "Армия г. Лос-Сантос": "МО",
    "Центральный Банк": "ЦА",
    "Больница г. Лас-Вентурас": "МЗ",
    "Полиция г. Лас-Вентурас": "МЮ",
    "Новостное агенство ЛВ": "СМИ",
    "Новостное агенство СФ": "СМИ",
    "Армия г.Сан-Фиерро": "МО",
    "Страховая компания": "ЦА",
    "Grove Street Gang": "Гетто",
    "Los Santos Vagos Gang": "Гетто",
    "The Ballas Gang": "Гетто",
    "Varios Los Aztecas Gang": "Гетто",
    "The Rifa Gang": "Гетто",
    "Russian Mafia": "Мафия",
    "Yakuza": "Мафия",
    "La Cosa Nostra": "Мафия",
    "Warlock MC": "Мафия",
    "Night Wolfs": "Гетто",
}

fractions_gs = {
    "all": ['Alex_Benson', "nik446"],
    "МЮ": ['Austin_Brown', "id443005795"],
    "МО": ['Daniel_Benson', "denaz_open23"],
    "МЗ": ['Thomas_Wooden', "id489855168"],
    "СМИ": ['Jacob_Wimpod', "id196364641"],
    "Гетто": ['Dino_Santi', "dino.lane"],
    "Мафия": ['Steven_Murphy', "id447479953"],
    "Право": ['Frachesko_Wayne', "tommyari"],
    "ЦА": ['Frachesko_Wayne', "tommyari"],
}


def replace_vk_links(text):
    pattern = r'\[id(\d+)\|([^\]]+)\]'
    replacement = r"<a href='https://vk.com/id\1'>\2</a>"
    return re.sub(pattern, replacement, text)


def checker_leaders(chat):
    try:
        found = False
        url = "https://forum.arizona-rp.com/forums/{}/".format(chat['category'])
        for thread in api.get_threads(url):
            print(thread)
            if not thread['closed'] and thread['unread']:

                content = api.get_thread(thread['link'].replace("unread", ""))

                try:
                    issue, created = Issue.get_or_create(link=thread['link'], defaults={"title": content[0]})
                except Exception as e:
                    created = True
                if not created:
                    continue

                nickname = utils.parse_nickname(content[0])
                frac = "Нет данных"
                gs = fractions_gs["all"]
                if nickname:
                    player = utils.get_player(nickname)
                    if player:
                        try:
                            frac = player['org']
                            try:
                                gs = fractions_gs[fractions[player['org']]]
                            except:
                                pass
                        except:
                            pass

                # api.edit_thread(thread['link'], 15, 1, 1)

                msg = "‼️ Новая жалоба на лидера ‼️\n\n"
                msg += "🗒 {}\n\n".format(content[0])
                msg += "👥 Лидер: {}\n".format(nickname)
                msg += "👤 Автор: {}\n".format(thread['creator'])
                msg += "🖥 Организация: {}\n".format(frac)
                msg += "💡 ГС: [{}|{}]\n\n".format(gs[1], gs[0])
                msg += "🔏 Ссылка: {}".format(thread['link'])

                payload = {
                    "random_id": random.randint(1, 10000000),
                    "chat_id": "597",
                    "message": msg,
                    "dont_parse_links": "0",
                    "disable_mentions": "0",
                    "intent": "default",
                    "access_token": "",
                    "v": "5.131",
                }
                requests.post("https://api.vk.com/method/messages.send", data=payload)

                found = True
        if found:
            api.set_unread(url)
        print(datetime.datetime.now())
    except Exception as e:
        s, r = getattr(e, 'message', str(e)), getattr(e, 'message', repr(e))
        print('s:', s, 'len(s):', len(s))


def checker(chat, unclosed=False):
    try:
        found = False
        url = "https://forum.arizona-rp.com/forums/{}/".format(chat['category'])
        for thread in api.get_threads(url):
            print(thread)
            if not thread['closed'] and (thread['unread'] or unclosed):

                content = api.get_thread(thread['link'].replace("unread", ""))
                valid = chat["valid"](content)
                nickname = utils.parse_nickname(content[0])

                try:
                    issue = Issue.get_or_create(link=thread['link'], defaults={"title": content[0]})
                except Exception as e:
                    s, r = getattr(e, 'message', str(e)), getattr(e, 'message', repr(e))
                    print('s:', s, 'len(s):', len(s))

                bot.send_message(chat['chat'],
                                 "‼️ <b>Сообщение в жалобе</b> ‼️\n\n🗒 <b>{}</b>\n\n💡 Идентификатор: {}\n👤 Автор: <b>{}</b>\n✍️ Последний ответ: <b>{}</b>\n🖥 По форме: <b>{}</b>\n📌 Закреплена: <b>{}</b>\n\n🔏 Ссылка: <b><a href='{}'>Перейти</a></b>".format(
                                     content[0],
                                     "<code>{}{}</code>".format(chat['prefix'], re.findall("https://forum\.arizona-rp\.com/threads/(.*)/", thread['link'])[0]),
                                     thread['creator'],
                                     thread['latest'],
                                     str(valid).replace("True", "Да").replace("False", "Нет"),
                                     str(thread['pinned']).replace("True", "Да").replace("False", "Нет"),
                                     thread['link'],
                                 ), reply_markup=utils.get_message_markup(thread['link'], chat['scope'], nickname))
                found = True
                try:
                    timecodes = content[1].split("Тайм-код нарушения на видео")[1].split("\\n")[0].replace(" ", "").replace(":", "")
                except:
                    timecodes = ""

                auto_answered = False
                if not valid and auto_ans:
                    # api.send_message(thread['link'], utils.get_form(chat["invalid"]))
                    # api.close_thread(thread['link'])
                    bot.send_message(chat['chat'], "❌ <b>Жалоба не по форме</b>")
                    auto_answered = True

        if found:
            api.set_unread(url)
        print(datetime.datetime.now())
    except Exception as e:
        s, r = getattr(e, 'message', str(e)), getattr(e, 'message', repr(e))
        print('s:', s, 'len(s):', len(s))


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    cmd = str(call.data).split(" ")
    cid = call.message.chat.id

    user = get_user(call.from_user.id, call.from_user.username)
    if str(call.from_user.id) in t_id or True:
        if cmd[0] == "form":
            api.send_message(cmd[1], utils.get_form("invalid"))
            bot.send_message(cid, "🗒 Сообщение <b>успешно</b> отправлено")
            set_issue(cmd[1], user, "Отправил invalid пост", True)
            if user.id in track_users:
                user.balance += ans_reward - 1
                user.save()
                bot.send_message(cid, "💸 На баланс зачислено <b>{} RUB</b> за закрытие жалобы.".format(ans_reward - 1))
        if cmd[0] == "pform":
            api.send_message(cmd[1], utils.get_form("invalid2"))
            bot.send_message(cid, "🗒 Сообщение <b>успешно</b> отправлено")
            set_issue(cmd[1], user, "Отправил invalid2 пост", True)
            if user.id in track_users:
                user.balance += ans_reward - 1
                user.save()
                bot.send_message(cid, "💸 На баланс зачислено <b>{} RUB</b> за закрытие жалобы.".format(ans_reward - 1))
        if cmd[0] == "bform":
            api.send_message(cmd[1], utils.get_form("invalid3"))
            bot.send_message(cid, "🗒 Сообщение <b>успешно</b> отправлено")
            set_issue(cmd[1], user, "Отправил invalid3 пост", True)
            if user.id in track_users:
                user.balance += ans_reward - 1
                user.save()
                bot.send_message(cid, "💸 На баланс зачислено <b>{} RUB</b> за закрытие жалобы.".format(ans_reward - 1))
        if cmd[0] == "id_time":
            api.send_message(cmd[1], utils.get_form("id_time"))
            bot.send_message(cid, "🗒 Сообщение <b>успешно</b> отправлено")
            set_issue(cmd[1], user, "Отправил id_time пост", True)
            if user.id in track_users:
                user.balance += ans_reward - 1
                user.save()
                bot.send_message(cid, "💸 На баланс зачислено <b>{} RUB</b> за закрытие жалобы.".format(ans_reward - 1))
        if cmd[0] == "not_video":
            api.send_message(cmd[1], utils.get_form("no_video"))
            bot.send_message(cid, "🗒 Сообщение <b>успешно</b> отправлено")
            set_issue(cmd[1], user, "Отправил no_video пост", True)
            if user.id in track_users:
                user.balance += ans_reward - 1
                user.save()
                bot.send_message(cid, "💸 На баланс зачислено <b>{} RUB</b> за закрытие жалобы.".format(ans_reward - 1))
        if cmd[0] == "screenshot":
            api.send_message(cmd[1], utils.get_form("screenshot"))
            bot.send_message(cid, "🗒 Сообщение <b>успешно</b> отправлено")
            set_issue(cmd[1], user, "Отправил screenshot пост", True)
            if user.id in track_users:
                user.balance += ans_reward - 1
                user.save()
                bot.send_message(cid, "💸 На баланс зачислено <b>{} RUB</b> за закрытие жалобы.".format(ans_reward - 1))
        if cmd[0] == "timecode":
            api.send_message(cmd[1], utils.get_form("timecode"))
            bot.send_message(cid, "🗒 Сообщение <b>успешно</b> отправлено")
            set_issue(cmd[1], user, "Отправил timecode пост", True)
            if user.id in track_users:
                user.balance += ans_reward - 1
                user.save()
                bot.send_message(cid, "💸 На баланс зачислено <b>{} RUB</b> за закрытие жалобы.".format(ans_reward - 1))
        if cmd[0] == "su":
            api.send_message(cmd[1], utils.get_form("su"))
            bot.send_message(cid, "🗒 Сообщение <b>успешно</b> отправлено")
            set_issue(cmd[1], user, "Отправил su пост", True)
        if cmd[0] == "su_close_nice":
            actions[call.from_user.id] = {"action": "su_close_nice", "url": cmd[1]}
            bot.send_message(cid,
                             "✍️ <b>Дополнение поста</b>\n\n🗒 Не дополнять, отправить: <b>-</b>\n❌ Отменить действие: <b>=</b>")
            set_issue(cmd[1], user, "Отправил su_close_nice пост",)
        if cmd[0] == "su_close_bad":
            api.send_message(cmd[1], utils.get_form("su_close_bad"))
            bot.send_message(cid, "🗒 Сообщение <b>успешно</b> отправлено")
            set_issue(cmd[1], user, "Отправил su_close_bad пост", True)
        if cmd[0] == "band_moment":
            api.send_message(cmd[1], utils.get_form("band_moment"))
            bot.send_message(cid, "🗒 Сообщение <b>успешно</b> отправлено")
            set_issue(cmd[1], user, "Отправил band_moment пост", True)
        if cmd[0] == "band_full_opra":
            api.send_message(cmd[1], utils.get_form("band_full_opra"))
            bot.send_message(cid, "🗒 Сообщение <b>успешно</b> отправлено")
            set_issue(cmd[1], user, "Отправил band_moment пост", True)
        if cmd[0] == "band_close_nice":
            api.send_message(cmd[1], utils.get_form("band_close_nice"))
            bot.send_message(cid, "🗒 Сообщение <b>успешно</b> отправлено")
            set_issue(cmd[1], user, "Отправил band_close_nice пост", True)
            if user.id in track_users:
                user.balance += ans_reward - 1
                user.save()
                bot.send_message(cid, "💸 На баланс зачислено <b>{} RUB</b> за закрытие жалобы.".format(ans_reward - 1))
        if cmd[0] == "punish":
            actions[call.from_user.id] = {"action": "punish", "url": cmd[1]}
            bot.send_message(cid,
                             "✍️ <b>Дополнение поста (наказание)</b>\n\n🗒 Не дополнять, отправить: <b>-</b>\n❌ Отменить действие: <b>=</b>")
            set_issue(cmd[1], user, "Отправил punish пост")
        if cmd[0] == "open":
            api.close_thread(cmd[1])
            reply_time = int(datetime.datetime.now().timestamp()) - call.message.date
            bot.send_message(cid, "🔒 Тема <b>успешно</b> закрыта/открыта\n⏳ <b>Жалоба закрыта за {} сек.</b>".format(reply_time))
            set_issue(cmd[1], user, "Открыл/закрыл жалобу")
        if cmd[0] == "pin":
            api.pin_thread(cmd[1])
            bot.send_message(cid, "📌 Тема <b>успешно</b> закреплена/откреплена")
            set_issue(cmd[1], user, "Закрепил/открепил жалобу")
        if cmd[0] == "begin":
            api.edit_thread(cmd[1], 17, 0, 0)
            reply_time = int(datetime.datetime.now().timestamp()) - call.message.date
            bot.send_message(cid, "✅ <b>Жалоба закрыта и была рассмотрена</b>\n⏳ <b>Жалоба закрыта за {} сек.</b>".format(reply_time))
            set_issue(cmd[1], user, "Рассмотрел жалобу", True)
            user.balance += 5
            user.save()
        if cmd[0] == "stick":
            api.edit_thread(cmd[1], 15, 1, 1)
            bot.send_message(cid, "⚠️ <b>Жалоба закреплена и находится на рассмотрении</b>")
            set_issue(cmd[1], user, "Рассматривает жалобу")

        if cmd[0] == "forum_find":
            posts = api.search_posts(cmd[2])
            message = "🗒 <b>Найденные посты:</b>\n\n"
            for post in posts:
                if cmd[1] == "1" and "Жалоб" not in post['category']:
                    continue
                message += "{} - {}: <a href='{}'>{}</a>\n".format(
                    post['when'],
                    post['author'].replace("<", "[").replace(">", "]"),
                    post['link'],
                    post['title'].replace("<", "[").replace(">", "]")
                )
            bot.send_message(cid, message)
        if cmd[0] == "prefix":
            api.edit_thread(cmd[1], cmd[2], cmd[3], cmd[4])
            bot.edit_message_text("✅ <b>Префикс успешно был установлен</b>", call.message.chat.id, call.message.message_id)
            set_issue(cmd[1], user, "Установил параметры {}, {}, {} на префикс темы".format(cmd[2], cmd[3], cmd[4]))
        if cmd[0] == "edit":
            actions[call.from_user.id] = {"action": "edit", "url": cmd[1]}
            bot.send_message(cid, "✍️ <b>Дополнение поста</b>\n\n🗒 Не дополнять, отправить: <b>-</b>\n❌ Отменить действие: <b>=</b>")
            set_issue(cmd[1], user, "Дополнил пост")
        if cmd[0] == "delete_msg":
            msg: Message = call.message
            bot.delete_message(msg.chat.id, msg.message_id)
        if cmd[0] == "accept_form":
            msg: Message = call.message
            url = re.compile("Сообщение: <a href=\"(.*)\">Перейти</a>").findall(msg.html_text)[0]
            chat_id, message_id = re.compile("https://t\.me/c/(\d+)/(\d+)").findall(url)[0]
            author = re.compile("Автор: (.*)\\n").findall(msg.html_text)[0]
            form = re.compile("<code>(.*)</code>").findall(msg.html_text)[0]

            utils.send_message("-172773148", form)

            bot.send_message("-100" + chat_id, "✅ {}, ваша <a href=\"{}\">форма</a> была <b>успешно</b> одобрена!".format(author, url))
            bot.edit_message_text(msg.html_text.replace("Новая", "Принятая"), msg.chat.id, msg.message_id)
        if cmd[0] == "reject_form":
            msg: Message = call.message
            url = re.compile("Сообщение: <a href=\"(.*)\">Перейти</a>").findall(msg.html_text)[0]
            chat_id, message_id = re.compile("https://t\.me/c/(\d+)/(\d+)").findall(url)[0]
            author = re.compile("Автор: (.*)\\n").findall(msg.html_text)[0]
            bot.send_message("-100" + chat_id,
                             "❌ {}, ваша <a href=\"{}\">форма</a> была <b>отклонена</b>!".format(author, url))
            bot.edit_message_text(msg.html_text.replace("Новая", "Отказанная"), msg.chat.id, msg.message_id)

        if cmd[0] == "myonline":
            if user.role > 3:
                msg: Message = call.message
                history = utils.get_history("-172773148", 1)
                if "Отвечено репортов" in history[0]['text']:
                    bot.edit_message_text(history[0]['text'], msg.chat.id, msg.message_id, reply_markup=utils.get_delete_keyboard())
                elif "Аккаунт" in history[0]['text'] and "не найден" in history[0]['text']:
                    bot.edit_message_text(history[0]['text'], msg.chat.id, msg.message_id,
                                          reply_markup=utils.get_delete_keyboard())
                else:
                    markup = InlineKeyboardMarkup()
                    markup.add(InlineKeyboardButton("✅ Обновить информацию", callback_data=f"myonline"))
                    bot.edit_message_text("🕔 <b>Был отправлен запрос, нажмите кнопку ниже, чтобы проверить его выполнение</b>\n"
                                          f"❌ Информация еще не было получена!\n💡 Timestamp: <b>{str(int(datetime.datetime.now().timestamp()))}</b>", msg.chat.id, msg.message_id,
                                          reply_markup=markup)

        if cmd[0] == "afind":
            if user.role > 3:
                msg: Message = call.message
                history = utils.get_history("-172773148", 1)
                if "Профиль на сайте" in history[0]['text']:
                    bot.edit_message_text(replace_vk_links(history[0]['text']), msg.chat.id, msg.message_id, reply_markup=utils.get_delete_keyboard())
                elif "Аккаунт" in history[0]['text'] and "не найден" in history[0]['text']:
                    bot.edit_message_text(history[0]['text'], msg.chat.id, msg.message_id,
                                          reply_markup=utils.get_delete_keyboard())
                else:
                    markup = InlineKeyboardMarkup()
                    markup.add(InlineKeyboardButton("✅ Обновить информацию", callback_data=f"afind {cmd[1]}"))
                    bot.edit_message_text("🕔 <b>Был отправлен запрос, нажмите кнопку ниже, чтобы проверить его выполнение</b>\n"
                                          f"❌ Информация еще не было получена!\n💡 Timestamp: <b>{str(int(datetime.datetime.now().timestamp()))}</b>", msg.chat.id, msg.message_id,
                                          reply_markup=markup)

        if cmd[0] == "admins":
            if user.role >= 1:
                msg: Message = call.message
                history = utils.get_history("-172773148", 1)
                if "Динамической информации" in history[0]['text']:
                    bot.edit_message_text(replace_vk_links(history[0]['text']), msg.chat.id, msg.message_id,
                                          reply_markup=utils.get_delete_keyboard(), disable_web_page_preview=True)
                else:
                    markup = InlineKeyboardMarkup()
                    markup.add(InlineKeyboardButton("✅ Обновить информацию", callback_data=f"admins"))
                    bot.edit_message_text("🕔 <b>Был отправлен запрос, нажмите кнопку ниже, чтобы проверить его выполнение</b>\n"
                                          f"❌ Информация еще не было получена!\n💡 Timestamp: <b>{str(int(datetime.datetime.now().timestamp()))}</b>", msg.chat.id, msg.message_id,
                                          reply_markup=markup)

        if cmd[0] == "get":
            if user.role > 3:
                msg: Message = call.message
                history = utils.get_history("-172773148", 1)
                if "Дата регистрации" in history[0]['text']:
                    bot.edit_message_text(history[0]['text'], msg.chat.id, msg.message_id, reply_markup=utils.get_delete_keyboard())
                elif "Аккаунт" in history[0]['text'] and "не найден!" in history[0]['text']:
                    bot.edit_message_text(history[0]['text'], msg.chat.id, msg.message_id,
                                          reply_markup=utils.get_delete_keyboard())
                else:
                    markup = InlineKeyboardMarkup()
                    markup.add(InlineKeyboardButton("✅ Обновить информацию", callback_data=f"get {cmd[1]}"))
                    bot.edit_message_text("🕔 <b>Был отправлен запрос, нажмите кнопку ниже, чтобы проверить его выполнение</b>\n"
                                          f"❌ Информация еще не было получена!\n💡 Timestamp: <b>{str(int(datetime.datetime.now().timestamp()))}</b>", msg.chat.id, msg.message_id,
                                          reply_markup=markup)

        if cmd[0] == "getlog":
            if user.role > 3:
                msg: Message = call.message
                history = utils.get_history("-172773148", 1)
                if "Лог за 7 дней" in history[0]['text']:
                    url = "http://admin-tools.ru/vkbot/read_logs.php?str=" + history[0]['text'].split("http://admin-tools.ru/vkbot/read_logs.php?str=")[1]
                    body = requests.get(url).text
                    f = open(f"logs/log-{cmd[1]}.html", "w", encoding="utf8")
                    f.write(body)
                    f.close()
                    bot.edit_message_text(f"✅ <b>Логи по нику {cmd[1]} успешно выгружены сообщением ниже!</b>",
                                          msg.chat.id, msg.message_id)
                    file = open(f"logs/log-{cmd[1]}.html", "r", encoding="utf8")
                    bot.send_document(msg.chat.id, file, caption=f"log-{cmd[1]}.html", reply_markup=utils.get_delete_keyboard())
                    file.close()
                elif "Аккаунт" in history[0]['text'] and "не найден!" in history[0]['text']:
                    bot.edit_message_text(history[0]['text'], msg.chat.id, msg.message_id,
                                          reply_markup=utils.get_delete_keyboard())
                else:
                    markup = InlineKeyboardMarkup()
                    markup.add(InlineKeyboardButton("✅ Обновить информацию", callback_data=f"getlog {cmd[1]}"))
                    bot.edit_message_text("🕔 <b>Был отправлен запрос, нажмите кнопку ниже, чтобы проверить его выполнение</b>\n"
                                          f"❌ Информация еще не было получена!\n💡 Timestamp: <b>{str(int(datetime.datetime.now().timestamp()))}</b>", msg.chat.id, msg.message_id,
                                          reply_markup=markup)

        msg: Message = call.message
        if cmd[0] == "get_stats":
            bot.send_message(msg.chat.id, f"💡 Выбор действия над {cmd[1]}", reply_markup=utils.get_info_keyboard(cmd[1]))

        global log_timer
        if cmd[0] == "get_nick":
            if user.role > 3:
                if datetime.datetime.now().timestamp() - log_timer >= 60:
                    check_self_issues()
                    utils.send_message("-172773148", f"!info {cmd[1]}")
                    log_timer = datetime.datetime.now().timestamp()
                    markup = InlineKeyboardMarkup()
                    markup.add(InlineKeyboardButton("✅ Обновить информацию", callback_data=f"get {cmd[1]}"))
                    bot.send_message(msg.chat.id, "🕔 <b>Был отправлен запрос, нажмите кнопку ниже, чтобы проверить его выполнение</b>", reply_markup=markup)
                else:
                    bot.send_message(msg.chat.id, f"❌ <b>Подождите {60 - (datetime.datetime.now().timestamp() - log_timer)} секунд для выполнения этого запроса!</b>")
        if cmd[0] == "get_log":
            if user.role > 3:
                if datetime.datetime.now().timestamp() - log_timer >= 60:
                    check_self_issues()
                    utils.send_message("-172773148", f"!log {cmd[1]}")
                    log_timer = datetime.datetime.now().timestamp()
                    markup = InlineKeyboardMarkup()
                    markup.add(InlineKeyboardButton("✅ Обновить информацию", callback_data=f"getlog {cmd[1]}"))
                    bot.send_message(msg.chat.id, "🕔 <b>Был отправлен запрос, нажмите кнопку ниже, чтобы проверить его выполнение</b>", reply_markup=markup)
                else:
                    bot.send_message(msg.chat.id, f"❌ <b>Подождите {60 - (datetime.datetime.now().timestamp() - log_timer)} секунд для выполнения этого запроса!</b>")

        if cmd[0] == "get_punish":
            msg_text = "💬 <b>Найденные формы по вашему запросу</b>\n\n"

            forms = Form.select().where(Form.command.contains(cmd[1])).limit(50)
            for _f in forms:
                status = "🕔"
                if _f.status == 1:
                    status = "✅"
                msg_text += "<b>[{}]:</b> {} {}\n".format(str(_f.created).split(".")[0], _f.command, status)
            bot.send_message(msg.chat.id, msg_text)


@bot.message_handler()
def action_handler(message: Message):
    uid = message.chat.id
    tid = message.from_user.id
    text = message.text
    cmd = str(text).split(" ")
    user = get_user(tid, message.from_user.username)

    try:
        if text == "/test" or text == "/status":
            forum_status = False
            auth_status = False
            try:
                forum = api.session.get("https://forum.arizona-rp.com", timeout=5)
                if forum.status_code == 200:
                    forum_status = True
                    if "Xiangzhao Xuanyunzhe" in forum.text:
                        auth_status = True
            except:
                pass

            msg = "🧑‍💻 <b>Статус работы бота</b>\n\n"
            msg += "🤖 Telegram: <b>✅ Passed</b>\n"
            msg += "🗒 Форум ARZ: <b>{}</b>\n".format("✅ Passed" if forum_status else "❌ Error")
            msg += "👤 Авторизация: <b>{}</b>\n".format("✅ Passed" if auth_status else "❌ Error")
            bot.send_message(uid, msg)
            return
        if text == "/id":
            bot.send_message(uid, "📊 <b>Информация</b>\n\n💬 Chat ID: <b>{}</b>".format(uid))
            return

        if text == "/help":
            msg = "🆘 <b>Помощь по командам</b>\n\n"
            msg += "📊 Статистика жалоб: <b>/stats [ID категории]</b>\n"
            msg += "🆔 ID беседы: <b>/info</b>\n"
            msg += "⏳ Отправить форму: <b>/form [Текст]</b>\n"
            msg += "💡 Статус бота: <b>/test</b>\n\n"
            msg += "🧑‍💻 <i>По всем вопросам, касающиеся бота - @tstname</i>"
            bot.send_message(uid, msg)
            return

        if cmd[0] == "/banfa":
            if not user.username:
                msg = "❌ <b>Сначала установите свой ник через команду /nick</b>"
                return bot.send_message(uid, msg)

            accepted_warns = [6, 7, 9, 12, 15, 16]
            if len(cmd) == 3 and int(cmd[2]) in accepted_warns:
                api.warn_post(cmd[1], cmd[2])
                set_issue("banfa", user, "Предупредил пост {} кодом {}".format(cmd[1], cmd[2]))
                bot.send_message(uid, "✅ <b>Пользователь был успешно предупрежден!</b>\n"
                                      "\n🆔 Ссылка: <b>{}</b>\n👤 Автор: <b>{}</b>".format(cmd[1], "@" + message.from_user.username or "Без ника"))
            else:
                msg = "❌ <b>Неверный ID предупреждения</b>\n\n"
                msg += "6 - Оффтоп\n7 - Реклама\n9 - Флуд\n12 - Неадекватное поведение\n15 - Оск. родных\n16 - Порнография"
                msg += "\n\n💡 Использование: <b>/banfa [Ссылка на пост или ID поста] [ID предупреждения]</b>"
                bot.send_message(uid, msg)
            return

        if cmd[0] == "/prefix":
            if not user.username:
                msg = "❌ <b>Сначала установите свой ник через команду /nick</b>"
                return bot.send_message(uid, msg)

            if len(cmd) == 4:
                thread = api.get_thread(cmd[1])
                bot.send_message(uid, f"<b>💡 Выбор действия</b>\n{thread[0]}", reply_markup=utils.get_prefix_markup(cmd[1], cmd[2], cmd[3]))
                pass
            else:
                msg = "❌ <b>Неверное использование команды</b>\n\n"
                msg += "💡 Использование: <b>/prefix [Ссылка на тему] [Открыто - 0/1] [Закреп - 0/1]</b>\n\n"
                msg += "🕔 <b>Статусы</b>\n1 - Жалоба открыта, 0 - жалоба закрыта\n1 - Закрепить жалобу, 0 - открепить"
                bot.send_message(uid, msg)
            return

        if cmd[0] == "/opra":
            if len(cmd) == 2:
                thread = api.get_thread(cmd[1])
                nick = utils.parse_nickname(thread[0])
                opra_id = cmd[1].split("https://forum.arizona-rp.com/threads/")[1].replace("/", "")

                prefix = utils.get_prefix(user.username)
                if not prefix:
                    msg = "❌ <b>Сначала установите свой ник через команду /nick</b>"
                    return bot.send_message(uid, msg)

                msg = f"<code>/unjailoff {nick} opra#{opra_id} | {prefix}\n{cmd[1]}</code>\n\n💡 <b>Скопируйте текст выше в беседу снятий наказаний</b>"
                bot.send_message(uid, msg)
            else:
                msg = "❌ <b>Неверное использование команды</b>\n\n"
                msg += "💡 Использование: <b>/opra [Ссылку на тему]</b>\n\n"
                bot.send_message(uid, msg)
            return

        if cmd[0] == "/view":
            if len(cmd) > 0:
                thread = api.get_thread(cmd[1])
                msg = "🗒 <b>{}</b>\n\n".format(thread[0])
                msg += thread[1]
                bot.send_message(uid, msg)
            else:
                msg = "❌ <b>Неверное использование команды</b>\n\n"
                msg += "💡 Использование: <b>/view [Ссылку на тему]</b>\n\n"
                bot.send_message(uid, msg)
            return

        if cmd[0] == "/forum":
            if len(cmd) > 1:
                posts = api.search_posts(text.split(" ", 1)[1])

                message = "🗒 <b>Найденные посты:</b>\n\n"
                for post in posts:
                    message += "{} - {}: <a href='{}'>{}</a>\n".format(
                        post['when'],
                        post['author'].replace("<", "[").replace(">", "]"),
                        post['link'],
                        post['title'].replace("<", "[").replace(">", "]")
                    )
                bot.send_message(uid, message)
            else:
                msg = "❌ <b>Неверное использование команды</b>\n\n"
                msg += "💡 Использование: <b>/forum [Ключевые слова]</b>\n\n"
                bot.send_message(uid, msg)
            return

        if cmd[0] == "/nick":
            if len(cmd) >= 2:
                nick = utils.parse_nickname(text.split(" ", 1)[1])
                if nick:
                    user.username = nick
                    user.save()
                    bot.send_message(uid, f"✅ Ваш новый ник: <b>{nick}</b>")
                else:
                    bot.send_message(uid, "❌ <b>Ник не найден</b>")
            else:
                bot.send_message(uid, "❌ <b>Использование: /nick [Ваш ник в игре]</b>")
            return

        if cmd[0] == "/history":
            msg = "💬 <b>Найденные формы по вашему запросу</b>\n\n"

            forms = Form.select().where(Form.command.contains(text.split(" ", 1)[1])).limit(50)
            for _f in forms:
                status = "🕔"
                if _f.status == 1:
                    status = "✅"
                msg += "<b>[{}]:</b> {} {}\n".format(str(_f.created).split(".")[0], _f.command, status)
            return bot.send_message(uid, msg)

        if "779877929" in str(uid):
            return

        if cmd[0] == "/ahistory":
            if user.role < 2:
                return
            msg = "💬 <b>Найденные формы по вашему запросу</b>\n\n"

            forms = Form.select().where(Form.command.contains(text.split(" ", 1)[1])).limit(50)
            for _f in forms:
                status = "🕔"
                if _f.status == 1:
                    status = "✅"
                msg += "@{} <b>[{}]:</b> {} {}\n".format(_f.author.login, str(_f.created).split(".")[0], _f.command, status)
            return bot.send_message(uid, msg)

        if cmd[0] == "/logs" and user.role >= 3:
            if len(cmd) == 3:
                uu = User.get(login=cmd[1].replace("@", ""))
                sql = Action.select().where(Action.user == uu).order_by(Action.id.desc()).limit(cmd[2])
                result = []
                for a in sql:
                    result.append("@{} <b>[{}]</b> <a href='{}'>{}</a>: {}".format(a.user.login, a.created, a.link, a.type, a.message))
                bot.send_message(uid, "Найденные результаты: \n\n" + "\n".join(result))

            if len(cmd) == 2:
                sql = Action.select().where(Action.message.contains(cmd[1])).order_by(Action.id.desc()).limit(25)
                result = []
                for a in sql:
                    result.append("@{} <b>[{}]</b> <a href='{}'>{}</a>: {}".format(a.user.login, a.created, a.link, a.type, a.message))
                bot.send_message(uid, "Найденные результаты: \n\n" + "\n".join(result))
            return

        if cmd[0] == "/edit":
            if len(cmd) > 2:
                data = text.split(" ", 2)
                api.edit_post(data[1], data[2])
                bot.send_message(uid, "✅ <b>Пост успешно отредактирован!</b>")
                set_issue(data[1], user, "Редактирует пост")
            else:
                bot.send_message(uid, "❌ <b>Использование: /edit [ID поста] [HTML Текст]</b>")
            return

        if cmd[0] == "/issues":
            bot.send_message(uid, "⏳ <b>Загрузка информации..</b>")
            for item in database:
                checker(item, True)
                time.sleep(random.Random().randint(1, 8))
            bot.send_message(uid, "✅ <b>Информация успешно загружена!</b>")
            return

        if cmd[0] == "/role":
            if user.role > 10:
                login = cmd[1].replace("@", "")
                sel_user = User.get_or_none(login=login)
                if sel_user:
                    sel_user.role = cmd[2]
                    sel_user.save()
                    bot.send_message(uid, "✅ <b>Статус успешно обновлен!</b>")
                else:
                    bot.send_message(uid, "❌ <b>Указанный пользователь не найден</b>")
            return

        if cmd[0] == "/balance":
            if user.role > 10:
                login = cmd[1].replace("@", "")
                sel_user = User.get_or_none(login=login)
                if sel_user:
                    sel_user.balance = int(cmd[2])
                    sel_user.save()
                    bot.send_message(uid, "✅ <b>Баланс успешно обновлен!</b>")
                else:
                    bot.send_message(uid, "❌ <b>Указанный пользователь не найден</b>")
            return

        if cmd[0] == "/user":
            if len(cmd) == 1:
                us = user
            else:
                if user.role > 2:
                    login = cmd[1].replace("@", "")
                    us = User.get_or_none(login=login)
                    if not us:
                        bot.send_message(uid, "❌ <b>Указанный пользователь не найден</b>")
                else:
                    return

            forms = Form.select().where(Form.author == us, Form.created >= utils.get_monday())
            issues = Issue.select().where(Issue.last_interaction == us, Issue.last_interaction >= utils.get_monday())

            msg = "👤 <b>Статистика @{}</b>\n\n".format(us.login)
            msg += "🗒 Никнейм: <b>{}</b>\n".format(us.username if len(us.username) > 1 else "Не установлен")
            msg += "💸 Баланс: <b>{} RUB</b>\n".format(us.balance)
            msg += "🔏 Доступ: <b>{}</b>\n\n".format(us.role)
            msg += "📅 <b>Информация с понедельника</b>\n\n"
            msg += "📕 Проверено жалоб: <b>{}</b>\n".format(len(forms))
            msg += "⚙️ Отправлено форм: <b>{}</b>\n".format(len(issues))
            return bot.send_message(uid, msg)

        form_cmds = ["/banoff", "/muteoff", "/warnoff", "/jailoff"]
        if cmd[0] in form_cmds:
            if uid != tid:
                mid = str(message.chat.id).replace("-100", "")
                msg = "💡 <b>Новая форма</b>\n\n"
                msg += "🗒 Сообщение: <a href=\"https://t.me/c/{}/{}\"><b>Перейти</b></a>\n".format(mid,
                                                                                                    message.message_id)
                msg += "👤 Автор: <b>{}</b>\n\n".format("@" + message.from_user.username or "Без ника")
                set_issue("forms", user, "Отправил форму " + text)
                if cmd[0] == "/form":
                    msg += "<code>{}</code>".format(text)
                else:
                    msg += "<code>!form {} | X.Xuanyunzhe</code>".format(text)
                bot.send_message(uid, "💡 <b>Форма успешно отправлена на проверку</b>")
                bot.send_message(t_id, msg, reply_markup=utils.get_form_markup(mid, message.message_id))
            else:
                utils.send_message("-172773148", text.split(" ", 1)[1])

                bot.send_message(uid, "💡 <b>Форма успешно отправлена</b>")
            return

        form_cmds = []
        if cmd[0] in form_cmds:
            # utils.add_game_form(text)
            form = Form.create(command=text, author=user, target=cmd[1])
            form.save()
            set_issue("forms", user, "Отправил форму " + text)
            return bot.send_message(uid, "💡 <b>Форма успешно отправлена в очередь</b>")

        if cmd[0] == "/check":
            msg = "💬 <b>Найденные формы по вашему запросу</b>\n\n"

            forms = Form.select().where(Form.command.contains(text.split(" ", 1)[1]), Form.status == 0)
            for _f in forms:
                msg += "<b>[{}]:</b> {}\n".format(str(_f.created).split(".")[0], _f.command)
            return bot.send_message(uid, msg)

        if cmd[0] == "/rcheck":
            msg = "💬 <b>Найденные формы по вашему запросу</b>\n\n"

            forms = Form.select().where(Form.command.contains(text.split(" ", 1)[1]), Form.status == 0)
            for _f in forms:
                msg += "{}\n".format(_f.command)
            return bot.send_message(uid, msg)

        if cmd[0] == "/del":
            msg = "💬 <b>Формы, которые были удалены</b>\n\n"

            forms = Form.select().where(Form.command.contains(text.split(" ", 1)[1]), Form.status == 0)
            set_issue("forms", user, "Удалил форму " + text.split(" ", 1)[1])
            for _f in forms:
                msg += _f.command + "\n"
                _form = Form.get(_f.id)
                _form.status = 1
                _form.save()

            return bot.send_message(uid, msg)

        if cmd[0] == "/delpost":
            if len(cmd) > 1:
                data = text.split(" ", 2)
                api.delete_post(data[1])
                bot.send_message(uid, "✅ <b>Пост успешно удален!</b>")
                set_issue(data[1], user, "Удаляет пост")
                if user.id in track_users:
                    user.balance -= ans_reward + 2
                    user.save()
                    bot.send_message(uid,
                                     "💸 С баланса было снято <b>{} RUB</b> за удаление ответа.".format(ans_reward + 2))
            else:
                bot.send_message(uid, "❌ <b>Использование: /delpost [ID поста]</b>")
            return

        if cmd[0] == "/find":
            result = {}
            to_find = text.split(" ", 1)[1].lower()
            for line in rules:
                if to_find in line["text"].lower():
                    rls = re.compile("(\d{1,2}\..*)\\n").findall(line["text"])
                    for rule in rls:
                        if to_find in rule.lower():
                            try:
                                result[line["name"]].append(rule)
                            except:
                                result[line["name"]] = []
                                result[line["name"]].append(rule)

            counter = 0
            msgs = ["💡 <b>Найденные правила по вашему запросу</b>\n"]
            for k, v in result.items():
                chunk = "\n➡️ <b>{}</b>\n".format(k)
                for item in v:
                    chunk += item.lower().replace(to_find, "<i><b>{}</b></i>".format(to_find)) + "\n"
                    counter += 1
                    if len(msgs[-1]) > 2700:
                        msgs.append(chunk)
                        chunk = ""

                if len(msgs[-1]) > 2700:
                    msgs.append(chunk)
                    chunk = ""
                msgs[-1] += chunk

            msgs[-1] += "\n🗒 Итого найдено <b>{}</b> пунктов.".format(counter)

            for msg in msgs:
                bot.send_message(uid, msg)
            return

        if cmd[0] == "/get_video":
            # video_regex = "((http|https)\:\/\/)?(www\.youtube\.com|youtu\.?be)\/((watch\?v=)?([a-zA-Z0-9]{11}))(&.*)*"
            video_regex = "\[MEDIA=youtube](.{,12})\[/MEDIA]"
            post_id = api.get_thread(cmd[1])
            url = cmd[1] + "#" + post_id[2]
            post = api.get_post(url)
            links = re.compile(video_regex).findall(post["content"])
            for link in links:
                try:
                    video = pafy.new("".join(link))

                    msg = "📹 <b>Информация по видеоролику</b>\n\n"
                    msg += "📕 Название: <b>{}</b>\n".format(video.title)
                    msg += "🕔 Продолжительность: <b>{} секунд</b>\n".format(video.length)
                    msg += "🕹 Качество: <b>{}</b>\n".format(video.getbest().resolution)
                    msg += "👤 Автор: <b>{}</b>\n".format(video.author)
                    msg += "\n💡 Ссылка: <b><a href='https://www.youtube.com/watch?v={}'>Перейти</a></b>".format(video.videoid)
                except:
                    msg = "❌ <b>Видео не доступно</b>"
                bot.send_message(uid, msg)
                return

        if cmd[0] == "/video":
            try:
                video = pafy.new(cmd[1])

                msg = "📹 <b>Информация по видеоролику</b>\n\n"
                msg += "📕 Название: <b>{}</b>\n".format(video.title)
                msg += "🕔 Продолжительность: <b>{} секунд</b>\n".format(video.length)
                msg += "🕹 Качество: <b>{}</b>\n".format(video.getbest().resolution)
                msg += "👤 Автор: <b>{}</b>\n".format(video.author)
            except:
                msg = "❌ <b>Видео не доступно</b>"

            bot.send_message(uid, msg)
            return

        if cmd[0] == "/debug":
            print(eval(cmd[1])(cmd[2]))
            bot.send_message(uid, "Результат был отправлен в консоль.")
            return

        global log_timer
        if cmd[0] == "/get":
            if user.role > 3:
                if datetime.datetime.now().timestamp() - log_timer >= 60:
                    check_self_issues()
                    utils.send_message("-172773148", f"!info {cmd[1]}")
                    log_timer = datetime.datetime.now().timestamp()
                    markup = InlineKeyboardMarkup()
                    markup.add(InlineKeyboardButton("✅ Обновить информацию", callback_data=f"get {cmd[1]}"))
                    return bot.send_message(uid, "🕔 <b>Был отправлен запрос, нажмите кнопку ниже, чтобы проверить его выполнение</b>", reply_markup=markup)
                else:
                    return bot.send_message(uid, f"❌ <b>Подождите {60 - (datetime.datetime.now().timestamp() - log_timer)} секунд для выполнения этого запроса!</b>")

        if cmd[0] == "/getlog":
            if user.role > 3:
                if datetime.datetime.now().timestamp() - log_timer >= 60:
                    check_self_issues()
                    utils.send_message("-172773148", f"!log {cmd[1]}")
                    log_timer = datetime.datetime.now().timestamp()
                    markup = InlineKeyboardMarkup()
                    markup.add(InlineKeyboardButton("✅ Обновить информацию", callback_data=f"getlog {cmd[1]}"))
                    return bot.send_message(uid, "🕔 <b>Был отправлен запрос, нажмите кнопку ниже, чтобы проверить его выполнение</b>", reply_markup=markup)
                else:
                    return bot.send_message(uid, f"❌ <b>Подождите {60 - (datetime.datetime.now().timestamp() - log_timer)} секунд для выполнения этого запроса!</b>")

        if cmd[0] == "/myonline":
            if user.role > 3:
                if datetime.datetime.now().timestamp() - log_timer >= 5:
                    check_self_issues()
                    utils.send_message("-172773148", f"!myonline")
                    log_timer = datetime.datetime.now().timestamp()
                    markup = InlineKeyboardMarkup()
                    markup.add(InlineKeyboardButton("✅ Обновить информацию", callback_data=f"myonline"))
                    return bot.send_message(uid, "🕔 <b>Был отправлен запрос, нажмите кнопку ниже, чтобы проверить его выполнение</b>", reply_markup=markup)
                else:
                    return bot.send_message(uid, f"❌ <b>Подождите {5 - (datetime.datetime.now().timestamp() - log_timer)} секунд для выполнения этого запроса!</b>")

        if cmd[0] == "/admins":
            if user.role >= 1:
                if datetime.datetime.now().timestamp() - log_timer >= 30:
                    check_self_issues()
                    utils.send_message("-172773148", f"!admins")
                    log_timer = datetime.datetime.now().timestamp()
                    markup = InlineKeyboardMarkup()
                    markup.add(InlineKeyboardButton("✅ Обновить информацию", callback_data=f"admins"))
                    return bot.send_message(uid, "🕔 <b>Был отправлен запрос, нажмите кнопку ниже, чтобы проверить его выполнение</b>", reply_markup=markup)
                else:
                    return bot.send_message(uid, f"❌ <b>Подождите {30 - (datetime.datetime.now().timestamp() - log_timer)} секунд для выполнения этого запроса!</b>")

        if cmd[0] == "/afind":
            if user.role > 3:
                prefix = "@pskateboard"
                if len(cmd) == 2:
                    prefix = cmd[1]
                if datetime.datetime.now().timestamp() - log_timer >= 5:
                    check_self_issues()
                    utils.send_message("-172773148", f"!find {prefix}")
                    log_timer = datetime.datetime.now().timestamp()
                    markup = InlineKeyboardMarkup()
                    markup.add(InlineKeyboardButton("✅ Обновить информацию", callback_data=f"afind {prefix}"))
                    return bot.send_message(uid, "🕔 <b>Был отправлен запрос, нажмите кнопку ниже, чтобы проверить его выполнение</b>", reply_markup=markup)
                else:
                    return bot.send_message(uid, f"❌ <b>Подождите {5 - (datetime.datetime.now().timestamp() - log_timer)} секунд для выполнения этого запроса!</b>")

        if cmd[0] == "/player":
            return bot.send_message(uid, f"💡 Выбор действия над {cmd[1]}",
                             reply_markup=utils.get_info_keyboard(cmd[1]))

        if "/stats" in text:
            url = "https://forum.arizona-rp.com/forums/1589/page-{}"
            pages = 20
            active_pages = 0
            if len(cmd) > 1:
                if cmd[1] == "1":
                    url = url.replace("1589", "1588")
                if cmd[1] == "2":
                    url = url.replace("1589", "1590")
                if cmd[1] == "3":
                    url = url.replace("1589", "1591")
                if cmd[1] == "4":
                    url = url.replace("1589", "1592")
                elif len(str(cmd[1])) > 3:
                    url = url.replace("1589", cmd[1])

            msg = bot.send_message(uid, "⚙️ Идёт загрузка информации <b>[0/{}]</b>".format(pages))
            stats = {"top": {}, "closed": 0, "pinned": 0, "opened": 0, "time": {"day": 0, "weekly": 0, "lweek": 0}}
            date = datetime.datetime.now().timestamp() - 60 * 60 * 24 * 7
            try:
                if cmd[2] == "1":
                    date = utils.get_monday()
            except:
                pass
            date_sel = date
            for i in range(1, pages + 1):
                page = url.format(str(i))
                if page == url.format(1):
                    page = page.replace("page-1", "")
                counter = 1
                active_pages += 1
                for thread in api.get_threads(page):
                    if int(thread['closed_date']) >= date_sel:
                        counter += 1
                        if thread['closed']:
                            stats['closed'] += 1
                            if int(thread['closed_date']) >= datetime.datetime.now().timestamp() - 60 * 60 * 24:
                                stats["time"]["day"] += 1
                            if int(thread['closed_date']) >= utils.get_monday():
                                stats["time"]["weekly"] += 1
                            if int(thread['closed_date']) >= date:
                                stats["time"]["lweek"] += 1

                            try:
                                stats['top'][thread['latest']] += 1
                            except:
                                if "Ichiro Nakata" in thread['latest'] or "Christopher_Dills" in thread['latest']:
                                    pass
                                else:
                                    stats['top'][thread['latest']] = 1
                        else:
                            stats['opened'] += 1
                        if thread['pinned']:
                            stats['pinned'] += 1
                if active_pages % 2 == 0:
                    bot.edit_message_text(text="⚙️ Идёт загрузка информации <b>[{}/{}]</b>".format(i, pages),
                                          chat_id=uid, message_id=msg.id)
                if counter < 10:
                    break
            message = "📊 <b>{}</b>\n\n📝 Всего жалоб: <b>{}</b>\n📂 На рассмотрении жалоб: <b>{}</b>\n📌 Закреплено жалоб: <b>{}</b>\n🔒 Закрыто жалоб: <b>{}</b>\n📜 Страниц: <b>{}</b>".format(
                api.get_category(url.replace("page-{}", "")), stats["opened"] + stats["closed"], stats['opened'],
                stats["pinned"], stats["closed"], active_pages
            )
            sort = dict(sorted(stats['top'].items(), key=lambda item: item[1], reverse=True))
            footer = "\n\n"
            pos = 1
            for k, v in sort.items():
                if pos == 10:
                    break
                footer += str(pos) + "️⃣ {}: <b>{} жалоб</b>\n".format(k, v)
                pos += 1
            past_footer = "\n🗓 За сегодня: <b>{} жалоб</b>\n📆 С понедельника: <b>{} жалоб</b>\n📊 За неделю: <b>{} жалоб</b>\n".format(
                stats["time"]["day"], stats["time"]["weekly"], stats["time"]["lweek"])
            bot.edit_message_text(text=message + footer + past_footer, chat_id=uid, message_id=msg.id)
            return

        if actions[tid]["action"] == "su_close_nice":
            form = utils.get_form("su_close_nice")
            if text == "=":
                actions[tid]["action"] = ""
                bot.send_message(uid, "❌ Операция <b>успешно</b> отклонена")
                return
            if text == "-":
                form = form.replace("%TEXT%", "")
            else:
                form = form.replace("%TEXT%", text)
            api.send_message(actions[tid]["url"], form)
            bot.send_message(uid, "🗒 Сообщение <b>успешно</b> отправлено")
            actions[tid] = None

        if actions[tid]["action"] == "punish":
            form = utils.get_form("punish")
            if text == "=":
                actions[tid]["action"] = ""
                bot.send_message(uid, "❌ Операция <b>успешно</b> отклонена")
                return
            if text == "-":
                form = form.replace("%TEXT%", "")
            else:
                form = form.replace("%TEXT%", text)
            api.send_message(actions[tid]["url"], form)
            bot.send_message(uid, "🗒 Сообщение <b>успешно</b> отправлено")
            actions[tid] = None
            if user.id in track_users:
                user.balance += ans_reward
                user.save()
                bot.send_message(uid, "💸 На баланс зачислено <b>{} RUB</b> за закрытие жалобы.".format(ans_reward))

        if actions[tid]["action"] == "edit":
            form = utils.get_form("edit")
            if text == "=":
                actions[tid]["action"] = ""
                bot.send_message(uid, "❌ Операция <b>успешно</b> отклонена")
                return
            if text == "-":
                form = form.replace("%TEXT%", "")
            else:
                form = form.replace("%TEXT%", text)
            api.send_message(actions[tid]["url"], form)
            bot.send_message(uid, "🗒 Сообщение <b>успешно</b> отправлено")
            actions[tid] = None

            if user.id in track_users and "Закрыто." in text:
                user.balance += ans_reward
                user.save()
                bot.send_message(uid, "💸 На баланс зачислено <b>{} RUB</b> за закрытие жалобы.".format(ans_reward))
    except Exception as e:
        s, r = getattr(e, 'message', str(e)), getattr(e, 'message', repr(e))
        print('s:', s, 'len(s):', len(s))
        # print('r:', r, 'len(r):', len(r))
        if text[0] == "/":
            bot.send_message(uid, "❌ <b>Произошла неизвестная ошибка</b>")


def analyze_admins_and_reports(text):
    report_pattern = r'📝Репортов: (\d+)'
    admin_pattern = r'\[LVL (\d+)\] \[id(\d+)\|([^\]]+)\]'

    reports = re.search(report_pattern, text)
    report_count = int(reports.group(1)) if reports else 0

    admins = re.findall(admin_pattern, text)
    online_admins = len(admins)

    print(f"[+] analyze_admins_and_reports, current report {report_count}, current admins {online_admins}")

    if report_count >= 4:
        message = (f"⚠️ Высокое количество репорта: <b>{report_count}</b>\n"
                   f"👮‍♂️ Количество админов в сети: <b>{online_admins}</b>")
        bot.send_message("-1001567410754", message)


def extract_links(message):
    url_pattern = r'https?://[^\s]+'
    links = re.findall(url_pattern, message)
    return links


def check_self_issues():
    try:
        history = utils.get_history("-172773148", 1)
        if "Тебя приветствует ГА Алексей" in history[0]['text']:
            links = extract_links(history[0]['text'])
            bot.send_message("-1001567410754",
                             f"⚠️ <b>Новая жалоба в разделе администраторов</b>\n\n🗒 Ссылка: <b>{links[0]}</b>")
    except:
        pass

def check_high_report():
    while True:
        try:
            check_self_issues()

            utils.send_message("-172773148", "!admins")

            history = ""
            while 1:
                history = utils.get_history("-172773148", 1)
                if "Динамической информации" in history[0]['text']:
                    break
                time.sleep(1)

            if history:
                analyze_admins_and_reports(history[0]['text'])

            time.sleep(600)
        except:
            print("[-] check_high_report error")
            time.sleep(300)


def start_checker():
    while 1:
        for item in database:
            checker(item)
            time.sleep(15.0 + random.randint(5, 15))


def start_gos():
    while 1:
        category = {
            "chat": "-1001567410754",
            "category": "1593",
        }
        checker_leaders(category)
        time.sleep(180)


def main():
    global cookie
    code = bypass.bypass(ua)
    cookie += code[0]
    print(cookie)
    api.setup(ua, cookie)

    threading.Thread(target=bot.infinity_polling).start()
    threading.Thread(target=check_high_report).start()
    # threading.Thread(target=start_checker).start()
    # threading.Thread(target=start_gos).start()


if __name__ == '__main__':
    db.create_tables([User, Form, Issue, Action])
    main()
