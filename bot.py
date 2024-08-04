from config import KEY
from config import APIURL
from datetime import datetime, timedelta
import telebot
import requests

bot = telebot.TeleBot(KEY)
user_dates = {}
user_last_command = {}
def get_date(command):
    if command == '/hoje':
        return datetime.now()
    elif command == '/amanha':
        return datetime.now() + timedelta(days=1)
    return None

@bot.message_handler(commands=["hoje"])
def hoje(msg):
    tse = get_date('/hoje')
    # print(tmw.strftime("%Y-%m-%d"))
    params = {
        'date': f'{tse.strftime("%Y-%m-%d")}'
        , 'country':'BRA'
    }
    params2 = {
        'date': f'{tse.strftime("%Y-%m-%d")}'
        , 'competitor' : 'Brazil'
    }
    response = requests.get(f"{APIURL}/events", params=params)
    data = response.json()
    data_list = data.get('data', [])

    response2 = requests.get(f"{APIURL}/events", params=params2)
    data2 = response2.json()
    data_list2 = data2.get('data', [])
    

    mensagem = f"Lista dos eventos com participação *BRASILEIRA* hoje ({tse.strftime('%d/%m/%Y')})\n(Clique para exibir os detalhes) \n"
    esportes_adicionados = set()
    for item in data_list:
        esporte = item.get('discipline_name', 'Desconhecido')
        status = item.get('status', None)
        if esporte not in esportes_adicionados:
            esportes_adicionados.add(esporte)
            if(status == "Finished"):
                mensagem += f"""/{esporte.lower()}"""
                mensagem += f" - *Finalizado* \n"
            else:
                mensagem += f"""/{esporte.lower()}\n"""
        
    for item in data_list2:
        esporte = item.get('discipline_name', 'Desconhecido')
        status = item.get('status', None)
    
        if esporte not in esportes_adicionados:
            esportes_adicionados.add(esporte)
            if status == "Finished":
                mensagem += f"""/{esporte.lower()} - *Finalizado* \n"""
            else:
                mensagem += f"""/{esporte.lower()}\n"""

    mensagem +="\n/amanha"

    user_dates[msg.chat.id] = {'date': tse, 'command': 'hoje'}
    user_last_command[msg.chat.id] = 'hoje'
    
    bot.send_message(msg.chat.id, mensagem, parse_mode='Markdown')

@bot.message_handler(commands=["amanha"])
def amanha(msg):
    tse = get_date('/amanha')
    # print(tmw.strftime("%Y-%m-%d"))
    params = {
        'date': f'{tse.strftime("%Y-%m-%d")}'
        , 'country':'BRA'
    }
    params2 = {
        'date': f'{tse.strftime("%Y-%m-%d")}'
        , 'competitor' : 'Brazil'
    }
    response = requests.get(f"{APIURL}/events", params=params)
    data = response.json()
    data_list = data.get('data', [])

    response2 = requests.get(f"{APIURL}/events", params=params2)
    data2 = response2.json()
    data_list2 = data2.get('data', [])
    

    mensagem = f"Lista dos eventos com participação *BRASILEIRA* amanhã ({tse.strftime('%d/%m/%Y')})\n(Clique para exibir os detalhes) \n"
    esportes_adicionados = set()

    
    for item in data_list:
        esporte = item.get('discipline_name', 'Desconhecido')
        status = item.get('status', None)
        if esporte not in esportes_adicionados:
            esportes_adicionados.add(esporte)
            if(status == "Finished"):
                mensagem += f"""/{esporte.lower()}"""
                mensagem += f" - *Finalizado* \n"
            else:
                mensagem += f"""/{esporte.lower()}\n"""


    for item in data_list2:
        esporte = item.get('discipline_name', 'Desconhecido')
        status = item.get('status', None)
    
        if esporte not in esportes_adicionados:
            esportes_adicionados.add(esporte)
            if status == "Finished":
                mensagem += f"""/{esporte.lower()} - *Finalizado* \n"""
            else:
                mensagem += f"""/{esporte.lower()}\n"""
    mensagem +="\n/hoje"
    
    
    user_dates[msg.chat.id] = {'date': tse, 'command': 'amanha'}
    user_last_command[msg.chat.id] = 'amanha'

    bot.send_message(msg.chat.id, mensagem, parse_mode='Markdown')

@bot.message_handler(commands=["voltar"])
def voltar(msg):
    if msg.chat.id in user_last_command:
        last_command = user_last_command[msg.chat.id]
        if last_command == 'hoje':
            hoje(msg)
        elif last_command == 'amanha':
            amanha(msg)
    else:
        bot.send_message(msg.chat.id, "Nenhum comando anterior encontrado. Use /hoje ou /amanha para começar.")


@bot.message_handler(func=lambda message: message.text.startswith('/') and message.text not in ['/hoje', '/amanha', '/start', '/voltar'])
def handle_esporte(msg):
    try:
        esporte = msg.text[1:].capitalize() 
        if msg.chat.id not in user_dates:
            bot.send_message(msg.chat.id, "Você precisa primeiro usar o comando /hoje ou /amanha.")
            return
        
        date_query = user_dates[msg.chat.id]['date']
        previous_command = user_dates[msg.chat.id]['command']

        response = requests.get(f'{APIURL}/disciplines')
        data = response.json()
      
        if(esporte == 'Table'):
            disciplinaName = 'Table Tennis'
        else:
            disciplinaName = esporte
        
        discipline_info = ""
        
        for disciplina in data['data']:
            name = disciplina.get('name', None)
            if name == disciplinaName:
                discipline_info = disciplina
                break
        if discipline_info:
            params = {
                'date': f'{date_query.strftime("%Y-%m-%d")}',
                'country': 'BRA',
                'discipline': discipline_info['id']
            }
            
            # print(tmw.strftime("%Y-%m-%d"))
            
            responseEvent = requests.get(f"{APIURL}/events", params=params)

            if(responseEvent.status_code != 200):
                bot.send_message(msg.chat.id, f"Erro na requisição: {response.status_code}")
            
            dataEvent = responseEvent.json()

            data_list = dataEvent.get('data', [])

            esportes_eventos = {}
            for item in data_list:
                sport = item.get('discipline_name', 'Desconhecido')
                event = item.get('detailed_event_name', 'Evento desconhecido')
                status = item.get('status', None)
                ts = item.get('start_date', 'Data não disponível')
                competitors = item.get('competitors', [])

                if ts != 'Data não disponível':
                    try:
                        ts_parsed = datetime.fromisoformat(ts)
                        ts_adjusted = ts_parsed - timedelta(hours=5)
                        ts_formatted = ts_adjusted.strftime('%H:%M:%S')
                    except ValueError:
                        ts_formatted = 'Horário não disponível'
                else:
                    ts_formatted = ts
                
                if sport not in esportes_eventos:
                    esportes_eventos[sport] = {}
                
                if event not in esportes_eventos[sport]:
                    esportes_eventos[sport][event] = {'timestamp': ts_formatted, 'competitors': []}

                    if status == 'Finished':
                        esportes_eventos[sport][event]['status'] = 'Finalizado'
                
                for comp in competitors:
                    compName = comp.get('competitor_name', 'Nome não disponível')
                    compCt = comp.get('country_id', 'País não disponível')
                    esportes_eventos[sport][event]['competitors'].append(f"{compName} - {compCt}")
            
            if(data_list):
                mensagem = f"BRASIL ({date_query.strftime('%d/%m/%Y')})\n\n"
            else:
                mensagem = f"Esporte não encontrado em {date_query.strftime('%d/%m/%Y')}\n/voltar"
            
            for sport, events in esportes_eventos.items():
                mensagem += f"Esporte: *{sport}*\n"
                if(status == 'Finished'):
                    mensagem += f"Status: *Finalizado* \n"
                for event, details in events.items():
                    timestamp = details['timestamp']
                    mensagem += f"Evento: *{event}* (Horário BR: {timestamp})\n"
                    mensagem += "Competitors:\n"
                    for compName in details['competitors']:
                        mensagem += f" - {compName}\n"
                mensagem += "\n /voltar"

            bot.send_message(msg.chat.id, mensagem, parse_mode='Markdown') 
            user_last_command[msg.chat.id] = previous_command
        else:
            bot.send_message(msg.chat.id, "Esporte não encontrado")   
    except Exception as e:
        bot.send_message(msg.chat.id, e) 
        print(e)

def verificar(msg):
    return True

@bot.message_handler(func=verificar)
def responder(msg):
    name = msg.from_user.first_name
    txt = f"""
    Olá, {name}! Boas vindas ao Bot das Olímpiadas Paris 2024!
Escolha um filtro para ver as próximas participações do Brasil!! (clique):
/hoje
/amanha
"""
    bot.reply_to(msg, txt)

bot.polling()