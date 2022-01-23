from ast import Break, Pass
import telebot
import configure
from telebot import types
import requests
#import lxml.html
#from lxml import etree
from bs4  import BeautifulSoup as bs

client = telebot.TeleBot(configure.config["token"])
url_groups = "https://cats.parts/moto/K26/51559/0:0:200512/"

req_parts = []

@client.message_handler(commands = ["start"])

def select_group(message):

    html_text = requests.get(url_groups).text
    group_items = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    soup = bs(html_text, "lxml")
    
    names_groups = soup.find_all(attrs={"class": "etk-hg-link"})
    numbers_groups = soup.find_all("a", href = True) 
    for name, number in zip(names_groups, numbers_groups[34:]):
        numb = number["href"][: -1]
        group_items.add(types.KeyboardButton(f"Группа {numb} - {name.text}"))

    msg = client.send_message(message.chat.id, "Выберите группу для просмотра входящих узлов", reply_markup = group_items)
    client.register_next_step_handler(msg, select_subgroup) # переброс в функцию user_answer


def select_subgroup(message):
    if message.text in ["/start", "/stop", "/restart"]:
        msg_error = f"Неверный ввод. Для перехода в начало нажмите ➡️ /start ⬅️ "
        client.send_message(message.chat.id, msg_error)
        print("Error in select_subgroup")
        Break
    
    else:
        global url_subgroups
        url_subgroups = url_groups + message.text[7:10].strip() + "/"
        html_text = requests.get(url_subgroups).text
        subgroup_items = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        soup = bs(html_text, "lxml")
    
        names_subgroups = soup.find_all(attrs={"class": "etk-node-text"}) 
        numbers_subgroups = soup.find_all(attrs={"class": "etk-node-number"})
        for name_sub, number_sub in zip(names_subgroups, numbers_subgroups):
            subgroup_items.add(types.KeyboardButton(f"Узел {number_sub.text} - {name_sub.text}"))

        msg = client.send_message(message.chat.id, "Выберите узел для просмотра комплектующих элементов", reply_markup = subgroup_items)
        client.register_next_step_handler(msg, select_parts)

def select_parts(message):
    if message.text in ["/start", "/stop", "/restart"]:
        msg_error = f"Неверный ввод. Для перехода в начало нажмите ➡️ /start ⬅️ "
        client.send_message(message.chat.id, msg_error)
        print("Error in select_parts")
        Break
    else:
        req_parts.append("+1")
        print(len(req_parts))
        parts_dict = {}
    
        url_parts = url_subgroups + message.text[5:12].strip() + "/"
        html_text = requests.get(url_parts).text
        soup = bs(html_text, "lxml")
    
        sheme = soup.find("div", class_ =  "etk-spares-image table-responsive").find("img")["src"] #######
        sheme_link = "https://cats.parts" + sheme
        sheme_out = f"Схема: {sheme_link}" 
        client.send_message(message.chat.id, sheme_out)
    
        partnumbers = soup.find_all(attrs={"class": "etk-spares-partnr"})
        parts = soup.find_all(attrs={"class": "etk-spares-name"})
        posit = soup.find_all(attrs={"class": "etk-spares-num"})
    
        for d, pn, p in zip(parts, partnumbers, posit):
            if d.text.strip() != "Наименование":
                if pn.text.strip() != "Номер":
                    if p.text != "№":
                
                        part_position = p.text.strip() # position
                    
                        part_out = d.text.strip() # name of part
                
                        pn_string = pn.text.strip() # partnumber and link
                        pn_string_format = pn_string.split(" ")
                        pn_string_format_final = "+".join(pn_string_format)
                        pn_link = "https://exist.ru/Price/?pcode=" + pn_string_format_final
                
                        key_out = f"№{part_position} {part_out}"
                        data_out = f"Кат. номер: {pn_string}, Ссылка: {pn_link}"
                        parts_dict[key_out] = data_out

        for key in parts_dict:
            item_out = f"{key} {parts_dict[key]}"
            client.send_message(message.chat.id, item_out)

        good_bye = f"Для выхода в начало нажмите ➡️ /start ⬅️"
        client.send_message(message.chat.id, good_bye)

@client.message_handler(commands = ["stop"])
def none_in_tasks(message):
    if message.text != "/start":
        client.send_message(message.chat.id, "Au revoir!")
        msg_error = f"Для перехода в начало нажмите ➡️ /start ⬅️ "
        client.send_message(message.chat.id, msg_error)
        Break
    
client.polling(none_stop=True)