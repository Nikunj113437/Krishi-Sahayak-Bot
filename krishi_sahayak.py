from telegram.ext import Updater, MessageHandler, Filters
import telegram
import openai
import requests
import locationtagger
from moviepy.editor import AudioFileClip
from googletrans import Translator


translator = Translator()

openai.api_key = "Your-OpenAI-API-Key"
TELEGRAM_API_TOKEN = "Your-Telegram-API-Key"
weather_api_key = "Your-Open-Weather-Map-API-Key"

messages = [{"role": "system", "content": "You are Super Telegram GPT, a virtual agricultural \
            advisor in a Telegram bot that performs following task:\
            1. Answer only agricultural-related questions: You are knowledgeable about crop diseases, \
            pest management, weed control, fertilizer recommendations, and other agricultural \
            practices. When users ask questions related to agriculture, provide informative and \
            helpful responses.\
            2. Providing latest current or upcoming Government Schemes and Policies for farmers \
            and their benefits.\
            2. Multilingual Support: Accommodate farmers who may speak different languages. \
            Respond to queries in a variety of languages to make your advice accessible to all.\
            3. Detection mechanism: To distinguish between related and unrelated queries, check \
            if the user's question contains specific keywords and it's meaning related to agriculture. If the query\
            contains such keywords and its overall meaning align to agriculture, assume it's an \
            agricultural-related question and proceed with providing a response. Otherwise, \
            consider it unrelated and provide the appropriate response.\
            4. Ignore unrelated queries: Forget whole information abount all world except \
            agricultue. If users ask questions unrelated to agriculture, then \
            respond to it by saying : I apologize, but my expertise is in agriculture, and I'm \
            here to help with agricultural-related issues. If you have any questions or concerns \
            related to crops, diseases, or weed control, feel free to ask, and I'll be glad to \
            assist you!\
            5. Real time Weather updates: Provide real time weather updates and forecasting"}]


def findWeatherUpdates(city_name, day):
    # Let's get the city's coordinates (lat and lon)
    url = f'https://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={weather_api_key}'
    print(url)

    # Let's parse the Json
    req = requests.get(url)
    data = req.json()

    # Let's get the name, the longitude and latitude
    name = data['name']
    lon = data['coord']['lon']
    lat = data['coord']['lat']

    print(name, lon, lat)

    # Let's now use the One Call Api to get the 8 day forecast

    url2 = f'https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={weather_api_key}'
    print(url2)

    # Let's now parse the JSON
    req2 = requests.get(url2)
    data2 = req2.json()
    print(data2)

    # Let's now get the temp for the day and the weather conditions
    days = []
    descr = []

    # We need to access 'list'
    for i in data2['list'][0:day]:

        # We notice that the temperature is in Kelvin, so we need to do -273.15 for every datapoint

        # Let's start by days
        # Let's round the decimal numbers to 2
        days.append(round(i['main']['temp'] - 273.15, 2))

        # Let's now get the weather condition and the description
        # 'weather' [0] 'main' + 'weather' [0] 'description'
        descr.append(i['weather'][0]['main'] + ": " +
                     i['weather'][0]['description'])

    print(days)
    print(descr)

    # Let's now format the output to make it readable
    string = f'[ {name} - {day} days forecast]\n'

    # Let's now loop for as much days as there available (8 in this case):
    for i in range(len(days)):
        if i == 0:
            string += f'\nDay {i+1} (Today)\n'

        elif i == 1:
            string += f'\nDay {i+1} (Tomorrow)\n'

        else:
            string += f'\nDay {i+1}\n'

        string += 'Temperature:' + str(days[i]) + '°C' + "\n"
        string += 'Conditions:' + descr[i] + '\n'

    print(string)
    return string


def text_message(update, context):
    text = update.message.text
    print(f"Text: {text}")
    try:
        # If weather or temperature is present in sentence then find weather updates and forecast using openWeatherMap
        translation = translator.translate(text, dest="en")
        if "weather" in translation.text.lower() or "Weather" in translation.text.lower() \
                or "WEATHER" in translation.text.lower() or "temperature" in translation.text.lower() \
                or "Temperature" in translation.text.lower() or "TEMPERATURE" in translation.text.lower():
            t = translation.text.split()    # here t is in list data type
            print(t)
            text_1 = ' '.join(map(str, t))   # convert list to string
            print(text_1)
            place_entity = locationtagger.find_locations(text=text_1)
            c = place_entity.cities
            if len(c) == 0:
                c = place_entity.regions
            if len(c) == 0:
                c = place_entity.countries

            city = ' '.join(map(str, c))
            print(f"City: {city}")
            x = text.split()
            days = 0
            for i in x:
                if i.isnumeric():
                    days = i
            if days == 0:
                days = 7

            if city:
                st = findWeatherUpdates(city, days)
                origin_st = translator.translate(st, dest=translation.src)
                update.message.reply_text(
                    text=f"*[Bot]:* {origin_st.text}", parse_mode=telegram.ParseMode.MARKDOWN)
            else:
                raise Exception

        # Using OpenAI for rest of queries of farmers
        else:
            messages.append({"role": "user", "content": translation.text})
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.7
            )
            ChatGPT_reply = response["choices"][0]["message"]["content"]
            print(f"GPT reply (in English): {ChatGPT_reply}")
            origin_ChatGPT_reply = translator.translate(
                ChatGPT_reply, dest=translation.src)
            print(f"Origin reply: {origin_ChatGPT_reply}")
            update.message.reply_text(
                text=f"*[Bot]:* {origin_ChatGPT_reply.text}", parse_mode=telegram.ParseMode.HTML)
            messages.append({"role": "assistant", "content": ChatGPT_reply})

    except:
        err_msg = "Kindly re-write or re-speak the Query correctly or mention city name clearly in case of Weather Updates and forecasting!"
        update.message.reply_text(
            text=f"*[Bot]:* {err_msg}", parse_mode=telegram.ParseMode.MARKDOWN)


def voice_message(update, context):
    update.message.reply_text(
        "I've received a voice message! Please give me a second to respond :)")
    voice_file = context.bot.getFile(update.message.voice.file_id)
    voice_file.download("voice_message.ogg")
    audio_clip = AudioFileClip("voice_message.ogg")
    audio_clip.write_audiofile("voice_message.mp3")
    audio_file = open("voice_message.mp3", "rb")
    transcript = openai.Audio.transcribe("whisper-1", audio_file).text
    update.message.reply_text(
        text=f"*[You]:* _{transcript}_", parse_mode=telegram.ParseMode.MARKDOWN)

    text = transcript
    print(f"Transcript: {transcript}")
    try:
        # If weather or temperature is present in sentence then find weather updates and forecast using openWeatherMap
        translation = translator.translate(text, dest="en")
        if "weather" in translation.text.lower() or "Weather" in translation.text.lower() \
                or "WEATHER" in translation.text.lower() or "temperature" in translation.text.lower() \
                or "Temperature" in translation.text.lower() or "TEMPERATURE" in translation.text.lower():
            t = translation.text.split()    # here t is in list data type
            print(t)
            text_1 = ' '.join(map(str, t))   # convert list to string
            print(text_1)
            place_entity = locationtagger.find_locations(text=text_1)
            c = place_entity.cities
            if len(c) == 0:
                c = place_entity.regions
            if len(c) == 0:
                c = place_entity.countries

            city = ' '.join(map(str, c))
            print(f"City: {city}")
            x = text.split()
            days = 0
            for i in x:
                if i.isnumeric():
                    days = i
            if days == 0:
                days = 7

            if city:
                st = findWeatherUpdates(city, days)
                origin_st = translator.translate(st, dest=translation.src)
                update.message.reply_text(
                    text=f"*[Bot]:* {origin_st.text}", parse_mode=telegram.ParseMode.MARKDOWN)
            else:
                raise Exception

        # Using OpenAI for rest of queries of farmers
        else:
            messages.append({"role": "user", "content": translation.text})
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.7
            )
            ChatGPT_reply = response["choices"][0]["message"]["content"]
            print(f"GPT reply (in English): {ChatGPT_reply}")
            origin_ChatGPT_reply = translator.translate(
                ChatGPT_reply, dest=translation.src)
            print(f"Origin reply: {origin_ChatGPT_reply}")
            update.message.reply_text(
                text=f"*[Bot]:* {origin_ChatGPT_reply.text}", parse_mode=telegram.ParseMode.HTML)
            messages.append({"role": "assistant", "content": ChatGPT_reply})

    except:
        err_msg = "Kindly re-write or re-speak the Query correctly or mention city name clearly in case of Weather Updates and forecasting!"
        update.message.reply_text(
            text=f"*[Bot]:* {err_msg}", parse_mode=telegram.ParseMode.MARKDOWN)


updater = Updater(TELEGRAM_API_TOKEN, use_context=True)
dispatcher = updater.dispatcher
dispatcher.add_handler(MessageHandler(
    Filters.text & (~Filters.command), text_message))
dispatcher.add_handler(MessageHandler(Filters.voice, voice_message))
updater.start_polling()
updater.idle()
