from telegram.ext import Updater, MessageHandler, Filters
import telegram
import openai
import locationtagger
from bardapi import Bard
from moviepy.editor import AudioFileClip


bard = Bard(
    token="Your-BARD-API-Key")


openai.api_key = "Your-OpenAI-API-Key"
TELEGRAM_API_TOKEN = "Telegram-API-Key"

messages = [{"role": "system", "content": "You are Super Telegram GPT, a virtual agricultural \
            advisor in a Telegram bot that performs following task:\
            1. Answer only agricultural-related questions: You are knowledgeable about crop diseases, \
            pest management, weed control, fertilizer recommendations, and other agricultural \
            practices. When users ask questions related to agriculture, provide informative and \
            helpful responses.\
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


def text_message(update, context):
    text = update.message.text

    # Using BARD for getting real time weather updates and government schemes for farmers
    try:
        if "weather" in text.lower() or "Weather" in text.lower() or "scheme" in text.lower() or "policy" in text.lower() or \
            "subsidy" in text.lower() or "schemes" in text.lower() or "policies" in text.lower() or \
                "subsidies" in text.lower():
            if "weather" in text.lower() or "Weather" in text.lower():
                t = text.upper().split()    # here t is in list data type
                text_1 = ' '.join(map(str, t))   # convert list to string
                place_entity = locationtagger.find_locations(text=text_1)
                city = place_entity.cities
                region = place_entity.regions
                country = place_entity.countries
                print(f"City: {city}")
                print(f"Region: {region}")
                print(f"Country: {country}")
                x = text.split()
                days = 0
                for i in x:
                    if i.isnumeric():
                        days = i
                if days == 0:
                    days = 3

                if city:
                    msg = f"What is current weather of {city}, and also provide accurate forecasting \
                        for next {days} days"
                elif region:
                    msg = f"What is current weather of {region}, and also provide accurate forecasting \
                        for next {days} days"
                elif country:
                    msg = f"What is current weather of {country}, and also provide accurate forecasting \
                        for next {days} days"
                else:
                    raise Exception

            # for government schemes and subsidies
            if "scheme" in text.lower() or "policy" in text.lower() or "subsidy" in text.lower() \
                    or "schemes" in text.lower() or "policies" in text.lower() or "subsidies" in text.lower():
                msg = "provide latest government schemes and subsidies for farmers and their benefits"

            print(f"Bard Reply: {msg}")
            summary = bard.get_answer(str(msg))
            Bard_reply = summary["content"]
            print(f"{Bard_reply}")
            update.message.reply_text(
                text=f"*[Bot]:* {Bard_reply}", parse_mode=telegram.ParseMode.HTML)

        else:
            # Using OpenAI for rest of queries of farmers
            messages.append({"role": "user", "content": update.message.text})
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.7
            )
            ChatGPT_reply = response["choices"][0]["message"]["content"]
            print(f"GPT reply: {ChatGPT_reply}")
            update.message.reply_text(
                text=f"*[Bot]:* {ChatGPT_reply}", parse_mode=telegram.ParseMode.MARKDOWN)
            messages.append({"role": "assistant", "content": ChatGPT_reply})
    except:
        err_msg = "Kindly re-write the Query correctly or mention city or region clearly in order in case of Weather Updates and forecasting!"
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
    # Using BARD for getting real time weather updates and government schemes for farmers
    try:
        if "weather" in text.lower() or "Weather" in text.lower() or "scheme" in text.lower() or "policy" in text.lower() or \
            "subsidy" in text.lower() or "schemes" in text.lower() or "policies" in text.lower() or \
                "subsidies" in text.lower():
            if "weather" in text.lower() or "Weather" in text.lower():
                t = text.upper().split()    # here t is in list data type
                text_1 = ' '.join(map(str, t))   # convert list to string
                place_entity = locationtagger.find_locations(text=text_1)
                city = place_entity.cities
                region = place_entity.regions
                country = place_entity.countries
                print(f"City: {city}")
                print(f"Region: {region}")
                print(f"Country: {country}")
                x = text.split()
                days = 0
                for i in x:
                    if i.isnumeric():
                        days = i
                if days == 0:
                    days = 3

                if city:
                    msg = f"What is current weather of {city}, and also provide accurate forecasting \
                        for next {days} days"
                elif region:
                    msg = f"What is current weather of {region}, and also provide accurate forecasting \
                        for next {days} days"
                elif country:
                    msg = f"What is current weather of {country}, and also provide accurate forecasting \
                        for next {days} days"
                else:
                    raise Exception

            # for government schemes and subsidies
            if "scheme" in text.lower() or "policy" in text.lower() or "subsidy" in text.lower() \
                    or "schemes" in text.lower() or "policies" in text.lower() or "subsidies" in text.lower():
                msg = "provide latest government schemes and subsidies for farmers and their benefits"

            print(f"Bard Reply: {msg}")
            summary = bard.get_answer(str(msg))
            Bard_reply = summary["content"]
            print(f"{Bard_reply}")
            update.message.reply_text(
                text=f"*[Bot]:* {Bard_reply}", parse_mode=telegram.ParseMode.HTML)

        else:
            # Using OpenAI for rest of queries of farmers
            messages.append({"role": "user", "content": transcript})
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.7
            )
            ChatGPT_reply = response["choices"][0]["message"]["content"]
            print(f"GPT reply: {ChatGPT_reply}")
            update.message.reply_text(
                text=f"*[Bot]:* {ChatGPT_reply}", parse_mode=telegram.ParseMode.MARKDOWN)
            messages.append({"role": "assistant", "content": ChatGPT_reply})
    except:
        err_msg = "Kindly re-write the Query correctly or mention city or region clearly in order in case of Weather Updates and forecasting!"
        update.message.reply_text(
            text=f"*[Bot]:* {err_msg}", parse_mode=telegram.ParseMode.MARKDOWN)


updater = Updater(TELEGRAM_API_TOKEN, use_context=True)
dispatcher = updater.dispatcher
dispatcher.add_handler(MessageHandler(
    Filters.text & (~Filters.command), text_message))
dispatcher.add_handler(MessageHandler(Filters.voice, voice_message))
updater.start_polling()
updater.idle()
