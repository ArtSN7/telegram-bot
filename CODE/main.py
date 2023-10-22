import datetime

import asyncio
import os
import aiohttp
from data import db_session
from data.user import User

from telegram.ext import Application, MessageHandler, filters
from telegram.ext import CommandHandler, ConversationHandler
from telegram import ReplyKeyboardMarkup, KeyboardButton

from data import config

from functions import gpt, quote, weather, news

#------------------------------------------------------------------
# weather buttond
btn_loc = KeyboardButton('SEND A LOCATION', request_location=True) # button which will ask user to send a location
markup_weather_loc = ReplyKeyboardMarkup([[btn_loc]], one_time_keyboard=True, resize_keyboard=True) # function which will show this button

coords_button = KeyboardButton('/coordinates')
address_button = KeyboardButton('/address')
markup_weather_options = ReplyKeyboardMarkup([[address_button],[coords_button]], one_time_keyboard=True, resize_keyboard=True) # showing weather option buttons

#------------------------------------------------------------------
# news buttons 
reply_keyboard_news = [['/specific_news'], ['/general_news']]
markup_news = ReplyKeyboardMarkup(reply_keyboard_news, one_time_keyboard=True, resize_keyboard=True)

reply_keyboard_news_topic = [['/general'], ['/business'], ['/entertainment'], ['/health'], ['/science'], ['/sports'],['/technology']]
markup_news_topic = ReplyKeyboardMarkup(reply_keyboard_news_topic, one_time_keyboard=True, resize_keyboard=True)


#------------------------------------------------------------------
# help function wich explains abilities of all functions in the bot
async def help_command(update, context):
    await update.message.reply_text('1')


#------------------------------------------------------------------
# start function which is called after user use bot for the first time
async def start_command(update, context):
    user = update.effective_user # getting user info from telegram

    id = user.id #getting user id
    db_sess = db_session.create_session() # creating connection with database

    person = db_sess.query(User).filter(User.tg_id == id).first() # searching for the data in the database which has the same id as the tg user

    if not person: # if person is not in the database, so we add him

        usera = User() # creating user object ( name usera as user is already chosen )
        usera.tg_id = id # adding to the field id in database his tg id
        usera.name = user.mention_html() # getting his name using user.mention_html() and add this name to the name field in the database
        usera.date = datetime.date.today() # adding date of user registration to the date field

        db_sess.add(usera) # adding user with data put to the fields to the database
        db_sess.commit() # commiting and updating our database, from this moment there is an information about this specific user in the database

    # sending message as an asnwer to the start button
    await update.message.reply_html(f"Hello, {user.mention_html()}!\n\nI am AUXXIbot, but friends call me AUX, so you can call me like this ;D\n\nI am your personal assistant that can simplify your life, moreover, you can ask me whatever you want and recieve an answer!\n\nTo see more of my power try /help button :)")



#------------------------------------------------------------------
# chat-gpt function
async def gpt_command(update, context):
    await update.message.reply_text('Please, send a message with your question.') # asking to send a messagew with question 
    return 1 # showing that the next function must be message_answer(update, context)

async def message_answer(update, context):
    txt = update.message.text # gettin text which was sent by user
    answer = gpt.question_gpt(txt) # asking gpt function to give an answer - if something is wrong, it will return error
    await update.message.reply_text("Wait for a little bit... We are looking for the best answer!")
    await update.message.reply_text(f"{answer}") # sending an answer to user
    return ConversationHandler.END # finishing conversation, so the user next message won't be connected to this function



#------------------------------------------------------------------
# quote function
async def quote_command(update, context):
    func = quote.quote() # declaring function call ( procedure that is needed to work with async requests )
    answer = await func # getting response from function
    await update.message.reply_text(f'{answer[0]}') # sending random quote to user

    if answer[1] != "": # if there is a link with author's photo, then we send it
        await context.bot.send_message(update.message.chat_id, text=answer[1]) # sending link to the photo ( tg will represent it )



#------------------------------------------------------------------
# weather function

async def weather_command(update, context):
    await update.message.reply_html(rf"Please, choose how you will send us your location ( by sending text address or by sharing your location using button )",
                                    reply_markup=markup_weather_options)

async def weather_command_coords(update, context):
    await update.message.reply_html(rf"To analyse data, you need to send your current location.",
                                    reply_markup=markup_weather_loc)
    return 1

async def weather_command_address(update, context):
    await update.message.reply_html(rf"To analyse data, you need to send address")
    return 1

async def weather_command_response_coords(update, context): # function which works with longitude and latitude 
    long, lang = update.message.location.longitude, update.message.location.latitude # getting user coordinates 
    func = weather.weather_coords((long, lang)) # calling function
    answer = await func # getting response 
    await update.message.reply_text(f"{answer}") # sending response to the user
    return ConversationHandler.END # ending conversation

async def weather_command_response_address(update, context): # function which works with address
    func = weather.weather_address(update.message.text) # calling function
    answer = await func # getting answer
    await update.message.reply_text(f"{answer}") # sending response to the user
    return ConversationHandler.END # ending conversation 

#------------------------------------------------------------------
# news function 
async def news_command(update, context):
    await update.message.reply_html(rf"Please, choose the type of news you want to see.", reply_markup=markup_news) # chose between general and specific


async def general_news(update, context):
    await update.message.reply_html(rf"Please, choose interesting topic.", reply_markup=markup_news_topic) # if user had chosen general news, he would need to choose topic

# functions connected to different topics
async def business(update, context):
    user = update.effective_user # getting user info from telegram

    id = user.id #getting user id
    db_sess = db_session.create_session() # creating connection with database

    person = db_sess.query(User).filter(User.tg_id == id).first() # searching for the data in the database which has the same id as the tg user

    language = person.language # getting user's language

    func = news.get_news('business', language)
    answer = await func
    await update.message.reply_text(f"{answer}")


async def entertainment(update, context):
    user = update.effective_user # getting user info from telegram

    id = user.id #getting user id
    db_sess = db_session.create_session() # creating connection with database

    person = db_sess.query(User).filter(User.tg_id == id).first() # searching for the data in the database which has the same id as the tg user

    language = person.language # getting user's language

    func = news.get_news('entertainment', language)
    answer = await func
    await update.message.reply_text(f"{answer}")


async def general(update, context):
    user = update.effective_user # getting user info from telegram

    id = user.id #getting user id
    db_sess = db_session.create_session() # creating connection with database

    person = db_sess.query(User).filter(User.tg_id == id).first() # searching for the data in the database which has the same id as the tg user

    language = person.language # getting user's language

    func = news.get_news('general', language)
    answer = await func
    await update.message.reply_text(f"{answer}")


async def health(update, context):
    user = update.effective_user # getting user info from telegram

    id = user.id #getting user id
    db_sess = db_session.create_session() # creating connection with database

    person = db_sess.query(User).filter(User.tg_id == id).first() # searching for the data in the database which has the same id as the tg user

    language = person.language # getting user's language

    func = news.get_news('health', language)
    answer = await func
    await update.message.reply_text(f"{answer}")


async def science(update, context):
    user = update.effective_user # getting user info from telegram

    id = user.id #getting user id
    db_sess = db_session.create_session() # creating connection with database

    person = db_sess.query(User).filter(User.tg_id == id).first() # searching for the data in the database which has the same id as the tg user

    language = person.language # getting user's language

    func = news.get_news('science', language)
    answer = await func
    await update.message.reply_text(f"{answer}")


async def sports(update, context):
    user = update.effective_user # getting user info from telegram

    id = user.id #getting user id
    db_sess = db_session.create_session() # creating connection with database

    person = db_sess.query(User).filter(User.tg_id == id).first() # searching for the data in the database which has the same id as the tg user

    language = person.language # getting user's language

    func = news.get_news('sports', language)
    answer = await func
    await update.message.reply_text(f"{answer}")


async def technology(update, context):
    user = update.effective_user # getting user info from telegram

    id = user.id #getting user id
    db_sess = db_session.create_session() # creating connection with database

    person = db_sess.query(User).filter(User.tg_id == id).first() # searching for the data in the database which has the same id as the tg user

    language = person.language # getting user's language

    func = news.get_news('technology', language)
    answer = await func
    await update.message.reply_text(f"{answer}")


async def specific_news(update, context):
    await update.message.reply_text("Enter the topic you are interested in (for example, Microsoft)")
    return 1


async def specific_news_response(update, context):

    func = news.get_spec_news(update.message.text)
    answer = await func
    await update.message.reply_text(f"{answer}")
    return ConversationHandler.END


#------------------------------------------------------------------
# function that stops dialogue with user
async def stop(update, context):
    return ConversationHandler.END # finishing conversation, so the user next message won't be connected to this function


#------------------------------------------------------------------
# functions that controls all the activity in the bot
def main():
    # create an Application object with specific telegram key which I recieved from BotFather
    application = Application.builder().token(config.tg_key).build()
    #------------------------------------------------------------------


    # registrating command handler in order to check what buttons were pressed

    application.add_handler(CommandHandler("start", start_command)) # adding /start command
    application.add_handler(CommandHandler("help", help_command)) # adding /help command
    application.add_handler(CommandHandler("quote", quote_command)) # adding /quote command



    #------------------------------------------------------------------
    # WEATHER COMMAND
    application.add_handler(CommandHandler("weather", weather_command)) # adding /weather command which will start all weather process

    conv_handler_weather = ConversationHandler( # /weather command with coordinates
        entry_points=[CommandHandler("coordinates", weather_command_coords)], # declaring the function which will start the conversation if weather command is called
        states={
            1: [MessageHandler(filters.LOCATION & ~filters.COMMAND, weather_command_response_coords)], # after next message this function will be called ( user must send location message )
        },
        fallbacks=[CommandHandler('stop', stop)] # function which will end conversation
    )
    application.add_handler(conv_handler_weather) # adding /weather command with address

    conv_handler_weather_address = ConversationHandler( # /weather command with coordinates
        entry_points=[CommandHandler("address", weather_command_address)], # declaring the function which will start the conversation if weather command is called
        states={
            1: [MessageHandler(filters.TEXT, weather_command_response_address)], # after next message this function will be called ( user must send location message )
        },
        fallbacks=[CommandHandler('stop', stop)] # function which will end conversation
    )
    application.add_handler(conv_handler_weather_address) # adding /weather command
    #------------------------------------------------------------------

    #------------------------------------------------------------------
    # GPT COMMAND
    conv_handler_gpt = ConversationHandler( # /gpt command
        entry_points=[CommandHandler("gpt", gpt_command)], # declaring the function which will start the conversation if gpt command is called
        states={
            1: [MessageHandler(filters.TEXT, message_answer)], # after next message this function will be called ( user must send text message )
        },
        fallbacks=[CommandHandler('stop', stop)] # function which will end conversation
    )
    application.add_handler(conv_handler_gpt) # adding /gpt command
    #------------------------------------------------------------------
    # NEWS COMMAND
    application.add_handler(CommandHandler("news", news_command))
    application.add_handler(CommandHandler("general_news", general_news))
    application.add_handler(CommandHandler("business", business))
    application.add_handler(CommandHandler("entertainment", entertainment))
    application.add_handler(CommandHandler("general", general))
    application.add_handler(CommandHandler("health", health))
    application.add_handler(CommandHandler("science", science))
    application.add_handler(CommandHandler("sports", sports))
    application.add_handler(CommandHandler("technology", technology))
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('specific_news', specific_news)],
        states={
            1: [MessageHandler(filters.TEXT & ~filters.COMMAND, specific_news_response)],
        },
        fallbacks=[CommandHandler('stop', stop)]
    )
    application.add_handler(conv_handler)

    #------------------------------------------------------------------
    # starting application
    application.run_polling()





#------------------------------------------------------------------
if __name__ == '__main__': # part of the code that set up the environmet 
    
    db_session.global_init("code/db/data.db") # connecting database in the main code code/db/data.db - path to reach the file


    if os.name == 'nt': # if os is windows
        # essential part which will set up "asyncio" library for the specific system
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy()) 
        

    main() # starting main code 