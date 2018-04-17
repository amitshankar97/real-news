from newsapi import NewsApiClient
import os
import requests
import sendgrid
from sendgrid.helpers.mail import *
import datetime



api = NewsApiClient(api_key=os.environ['API_KEY'])

sourcesDict = {'ABC News': {'id': 'abc-news', 'url': 'http://abcnews.go.com'}, 'Al Jazeera English': {'id': 'al-jazeera-english', 'url': 'http://www.aljazeera.com'}, 'Ars Technica': {'id': 'ars-technica', 'url': 'http://arstechnica.com'}, 'Associated Press': {'id': 'associated-press', 'url': 'https://apnews.com/'}, 'Axios': {'id': 'axios', 'url': 'https://www.axios.com'}, 'Bleacher Report': {'id': 'bleacher-report', 'url': 'http://www.bleacherreport.com'}, 'Bloomberg': {'id': 'bloomberg', 'url': 'http://www.bloomberg.com'}, 'Breitbart News': {'id': 'breitbart-news', 'url': 'http://www.breitbart.com'}, 'Business Insider': {'id': 'business-insider', 'url': 'http://www.businessinsider.com'}, 'Buzzfeed': {'id': 'buzzfeed', 'url': 'https://www.buzzfeed.com'}, 'CBS News': {'id': 'cbs-news', 'url': 'http://www.cbsnews.com'}, 'CNBC': {'id': 'cnbc', 'url': 'http://www.cnbc.com'}, 'CNN': {'id': 'cnn', 'url': 'http://us.cnn.com'}, 'CNN Spanish': {'id': 'cnn-es', 'url': 'http://cnnespanol.cnn.com/'}, 'Crypto Coins News': {'id': 'crypto-coins-news', 'url': 'https://www.ccn.com'}, 'Engadget': {'id': 'engadget', 'url': 'https://www.engadget.com'}, 'Entertainment Weekly': {'id': 'entertainment-weekly', 'url': 'http://www.ew.com'}, 'ESPN': {'id': 'espn', 'url': 'http://espn.go.com'}, 'ESPN Cric Info': {'id': 'espn-cric-info', 'url': 'http://www.espncricinfo.com/'}, 'Fortune': {'id': 'fortune', 'url': 'http://fortune.com'}, 'Fox News': {'id': 'fox-news', 'url': 'http://www.foxnews.com'}, 'Fox Sports': {'id': 'fox-sports', 'url': 'http://www.foxsports.com'}, 'Google News': {'id': 'google-news', 'url': 'https://news.google.com'}, 'Hacker News': {'id': 'hacker-news', 'url': 'https://news.ycombinator.com'}, 'IGN': {'id': 'ign', 'url': 'http://www.ign.com'}, 'Mashable': {'id': 'mashable', 'url': 'http://mashable.com'}, 'Medical News Today': {'id': 'medical-news-today', 'url': 'http://www.medicalnewstoday.com'}, 'MSNBC': {'id': 'msnbc', 'url': 'http://www.msnbc.com'}, 'MTV News': {'id': 'mtv-news', 'url': 'http://www.mtv.com/news'}, 'National Geographic': {'id': 'national-geographic', 'url': 'http://news.nationalgeographic.com'}, 'NBC News': {'id': 'nbc-news', 'url': 'http://www.nbcnews.com'}, 'New Scientist': {'id': 'new-scientist', 'url': 'https://www.newscientist.com/section/news'}, 'Newsweek': {'id': 'newsweek', 'url': 'http://www.newsweek.com'}, 'New York Magazine': {'id': 'new-york-magazine', 'url': 'http://nymag.com'}, 'Next Big Future': {'id': 'next-big-future', 'url': 'https://www.nextbigfuture.com'}, 'NFL News': {'id': 'nfl-news', 'url': 'http://www.nfl.com/news'}, 'NHL News': {'id': 'nhl-news', 'url': 'https://www.nhl.com/news'}, 'Politico': {'id': 'politico', 'url': 'https://www.politico.com'}, 'Polygon': {'id': 'polygon', 'url': 'http://www.polygon.com'}, 'Recode': {'id': 'recode', 'url': 'http://www.recode.net'}, 'Reddit /r/all': {'id': 'reddit-r-all', 'url': 'https://www.reddit.com/r/all'}, 'Reuters': {'id': 'reuters', 'url': 'http://www.reuters.com'}, 'TechCrunch': {'id': 'techcrunch', 'url': 'https://techcrunch.com'}, 'TechRadar': {'id': 'techradar', 'url': 'http://www.techradar.com'}, 'The Hill': {'id': 'the-hill', 'url': 'http://thehill.com'}, 'The Huffington Post': {'id': 'the-huffington-post', 'url': 'http://www.huffingtonpost.com'}, 'The New York Times': {'id': 'the-new-york-times', 'url': 'http://www.nytimes.com'}, 'The Next Web': {'id': 'the-next-web', 'url': 'http://thenextweb.com'}, 'The Verge': {'id': 'the-verge', 'url': 'http://www.theverge.com'}, 'The Wall Street Journal': {'id': 'the-wall-street-journal', 'url': 'http://www.wsj.com'}, 'The Washington Post': {'id': 'the-washington-post', 'url': 'https://www.washingtonpost.com'}, 'Time': {'id': 'time', 'url': 'http://time.com'}, 'USA Today': {'id': 'usa-today', 'url': 'http://www.usatoday.com/news'}, 'Vice News': {'id': 'vice-news', 'url': 'https://news.vice.com'}, 'Wired': {'id': 'wired', 'url': 'https://www.wired.com'}}

MAX_QUESTION = 10

#This is the welcome message for when a user starts the skill without a specific intent.
WELCOME_MESSAGE = ('Welcome to Real News!  You can ask me for news from various sources'
                   ' such as CNN or The Washington Post by saying, "give me the headlines from the washington post."'
                   ' You can also ask me for the headlines across sources by saying, "give me the headlines."'
                   ' You can get a list of sources by saying, "give me the list of sources."'
                   ' What would you like to do?')

HTML_MSG_1 = '<!doctype html> <html> <head> <meta name="viewport" content="width=device-width"> <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"> <title>Simple Transactional Email</title> <style> /* ------------------------------------- INLINED WITH htmlemail.io/inline ------------------------------------- */ /* ------------------------------------- RESPONSIVE AND MOBILE FRIENDLY STYLES ------------------------------------- */ @media only screen and (max-width: 620px) { table[class=body] h1 { font-size: 28px !important; margin-bottom: 10px !important; } table[class=body] p, table[class=body] ul, table[class=body] ol, table[class=body] td, table[class=body] span, table[class=body] a { font-size: 16px !important; } table[class=body] .wrapper, table[class=body] .article { padding: 10px !important; } table[class=body] .content { padding: 0 !important; } table[class=body] .container { padding: 0 !important; width: 100% !important; } table[class=body] .main { border-left-width: 0 !important; border-radius: 0 !important; border-right-width: 0 !important; } table[class=body] .btn table { width: 100% !important; } table[class=body] .btn a { width: 100% !important; } table[class=body] .img-responsive { height: auto !important; max-width: 100% !important; width: auto !important; } } /* ------------------------------------- PRESERVE THESE STYLES IN THE HEAD ------------------------------------- */ @media all { .ExternalClass { width: 100%; } .ExternalClass, .ExternalClass p, .ExternalClass span, .ExternalClass font, .ExternalClass td, .ExternalClass div { line-height: 100%; } .apple-link a { color: inherit !important; font-family: inherit !important; font-size: inherit !important; font-weight: inherit !important; line-height: inherit !important; text-decoration: none !important; } .btn-primary table td:hover { background-color: #34495e !important; } .btn-primary a:hover { background-color: #34495e !important; border-color: #34495e !important; } } </style> </head> <body class="" style="background-color: #f6f6f6; font-family: sans-serif; -webkit-font-smoothing: antialiased; font-size: 14px; line-height: 1.4; margin: 0; padding: 0; -ms-text-size-adjust: 100%; -webkit-text-size-adjust: 100%;"> <table border="0" cellpadding="0" cellspacing="0" class="body" style="border-collapse: separate; mso-table-lspace: 0pt; mso-table-rspace: 0pt; width: 100%; background-color: #f6f6f6;"> <tr> <td style="font-family: sans-serif; font-size: 14px; vertical-align: top;">&nbsp;</td> <td class="container" style="font-family: sans-serif; font-size: 14px; vertical-align: top; display: block; Margin: 0 auto; max-width: 580px; padding: 10px; width: 580px;"> <div class="content" style="box-sizing: border-box; display: block; Margin: 0 auto; max-width: 580px; padding: 10px;"> <!-- START CENTERED WHITE CONTAINER --> <span class="preheader" style="color: transparent; display: none; height: 0; max-height: 0; max-width: 0; opacity: 0; overflow: hidden; mso-hide: all; visibility: hidden; width: 0;">Here is your requested news briefing from the Real News skill.</span> <table class="main" style="border-collapse: separate; mso-table-lspace: 0pt; mso-table-rspace: 0pt; width: 100%; background: #ffffff; border-radius: 3px;"> <!-- START MAIN CONTENT AREA --> <tr> <td class="wrapper" style="font-family: sans-serif; font-size: 14px; vertical-align: top; box-sizing: border-box; padding: 20px;"> <table border="0" cellpadding="0" cellspacing="0" style="border-collapse: separate; mso-table-lspace: 0pt; mso-table-rspace: 0pt; width: 100%;"> <tr> <td style="font-family: sans-serif; font-size: 14px; vertical-align: top;"> '
HTML_MSG_2 = '</td> </tr> </table> </td> </tr> <!-- END MAIN CONTENT AREA --> </table> <!-- START FOOTER --> <div class="footer" style="clear: both; Margin-top: 10px; text-align: center; width: 100%;"> <table border="0" cellpadding="0" cellspacing="0" style="border-collapse: separate; mso-table-lspace: 0pt; mso-table-rspace: 0pt; width: 100%;"> <tr> <td class="content-block" style="font-family: sans-serif; vertical-align: top; padding-bottom: 10px; padding-top: 10px; font-size: 12px; color: #999999; text-align: center;"> <span class="apple-link" style="color: #999999; font-size: 12px; text-align: center;">Real News</span> <br> Don\'t like these emails? <a href="https://realnewsapp.github.io/unlink.html" style="text-decoration: underline; color: #999999; font-size: 12px; text-align: center;">Unlink your Amazon account</a>. </td> </tr> <tr> <td class="content-block powered-by" style="font-family: sans-serif; vertical-align: top; padding-bottom: 10px; padding-top: 10px; font-size: 12px; color: #999999; text-align: center;"> Powered by <a href="https://newsapi.org" style="color: #999999; font-size: 12px; text-align: center; text-decoration: none;">NewsAPI.org</a>. </td> </tr> </table> </div> <!-- END FOOTER --> <!-- END CENTERED WHITE CONTAINER --> </div> </td> <td style="font-family: sans-serif; font-size: 14px; vertical-align: top;">&nbsp;</td> </tr> </table> </body> </html>'

EMAIL_HEADER_IMG = 'data:image/png;base64,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'


#This is the message a user will hear when they start a quiz.
SKILLTITLE = "Real News"

#This is the message a user will hear when they try to cancel or stop the skill"
#or when they finish a quiz.
EXIT_SKILL_MESSAGE = "Thank you for using Real News! Goodbye!"

#This is the message a user will hear after they ask (and hear) about a specific data element.
# REPROMPT_SPEECH = "Which other source would you like to hear news from?"
REPROMPT_HEADLINE = "Would you like to hear more about this?"
NEXT_HEADLINE = "Would you like to hear the next headline?"
EMAIL_HEADLINE = "Would you like me to email you a link to this article?"
NO_DESCRIPTION = "This article does not have a summary. Would you still like me to email you a link to this article?"

#This is the message a user will hear when they ask Alexa for help in your skill.
HELP_MESSAGE = ("You can say something like, \"Alexa, ask Real to give me the headlines\" to get the headlines. "
                "You can also ask for news from a source by saying, \""
                "Alexa, ask Real News to give me the news from source\". "
                "What would you like to do?")

LOGIN_MESSAGE = "You need to login with Amazon before we can send you an email. Check the Alexa app for more details."

#If you don't want to use cards in your skill, set the USE_CARDS_FLAG to false.
#If you set it to true, you will need an image for each item in your data.
USE_CARDS_FLAG = False

STATE_START = "Start"

STATE = STATE_START


# --------------- entry point -----------------

def lambda_handler(event, context):
    """ App entry point  """
    
    if event['request']['type'] == "LaunchRequest":
        return on_launch()
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'])


# --------------- response handlers -----------------

def on_intent(request, session):
    """ Called on receipt of an Intent  """

    intent = request['intent']
    intent_name = request['intent']['name']

    print("on_intent " + intent_name)
    # get_state(session)

    if 'dialogState' in request:
        #delegate to Alexa until dialog sequence is complete
        if request['dialogState'] == "STARTED" or request['dialogState'] == "IN_PROGRESS":
            return dialog_response("", False)

    # process the intents
    if intent_name == "ListSources":
        return listSources(request)
    elif intent_name == "SourcedNews":
        return sourcedNews(request, intent, session)
    elif intent_name == "Headlines":
        return headlines(session)
    elif intent_name == "Next":
        return skip(session)
    elif intent_name == "Previous":
        return previous(session)
    elif intent_name == "AMAZON.YesIntent":
        if 'headline_index' in session['attributes']:
            if 'dialogStatus' in session['attributes']:
                if session['attributes']['dialogStatus'] == 'readTitle':
                    return read_headline(session)
                elif session['attributes']['dialogStatus'] == 'readDescription':
                    return ask_next_headline(session)
                elif session['attributes']['dialogStatus'] == 'readEmail':
                    session['attributes']['headline_index'] += 1
                    return headlines(session)
            return headlines(session)


    elif intent_name == "AMAZON.NoIntent":
        if 'dialogStatus' in session['attributes']:
            status = session['attributes']['dialogStatus']

            print(session)

            if status == "readEmail":
                return do_stop(session)
            elif status == "readTitle":
                if 'headline_index' in session['attributes']:
                    session['attributes']['headline_index'] += 1
                
                return headlines(session)
            elif status == "readDescription":
                if 'headline_index' in session['attributes']:
                    session['attributes']['headline_index'] += 1
                
                return headlines(session)
                
        else:
            print("headline_index didn't exist")
            # elif session['attributes']['dialogStatus'] == 'email':
            #     return response_plain_text("Would you like me to email you a link to the article?", True)
        return headlines(session)

    elif intent_name == "AMAZON.HelpIntent":
        return do_help()
    elif intent_name == "AMAZON.StopIntent":
        return do_stop(session)
    elif intent_name == "AMAZON.CancelIntent":
        return do_stop(session)
    else:
        print("invalid intent reply with help")
        return do_help()


def listSources(request):
    """ Get the names of all the sources from the dictionary"""
    sourceNames = sourcesDict.keys()

    msg = "Here are the sources: "

    i = 1
    for source in sourceNames:
        if i == 1:
            msg += source
        msg += ", " + source
        i += 1

    msg += "."

    print(msg)

    return response({}, response_plain_text(msg, True))

def skip(session):
    if 'attributes' not in session:
        return response({}, response_plain_text("", True))

    session['attributes']['headline_index'] += 1
    return headlines(session)

def previous(session):
    print(session)
    if 'attributes' not in session:
        return response({}, response_plain_text("", True))

    if 'headline_index' in session['attributes']:
        if session['attributes']['headline_index'] != 0:
            session['attributes']['headline_index'] -= 1
    else:
        session['attributes']['headline_index'] = 0

    return headlines(session)


def headlines(session):
    if 'attributes' not in session:
        res = api.get_top_headlines()
        
        articles = res['articles']
        session['attributes'] = {}
        session['attributes']['headline_index'] = 0
        session['attributes']['articles'] = articles
    elif 'articles' not in session['attributes']:
        print("before api request\n")
        res = api.get_top_headlines()
        
        print("after api request\n")
        
        articles = res['articles']
        session['attributes']['headline_index'] = 0
        session['attributes']['articles'] = articles
    else:
        # End if out of headlines, there's probably a better way to handle this
        # but this works for now
        if session['attributes']['headline_index'] >= len(session['attributes']['articles']):
            return do_stop(session)

        articles = session['attributes']['articles']
    
    print(articles)
    print("\n")

    msg = ""
    article = articles[session['attributes']['headline_index']]

    # for article in articles:
    msg += "From " + article['source']['name'] + ": "
    msg += article['title']
    msg += ". "
    msg += REPROMPT_HEADLINE
        
    print(msg + "\n\n")

    print(articles[0])
    print("\n")

    articlesToEmail = []

    if 'articlesToEmail' in session['attributes']:
        articlesToEmail = session['attributes']['articlesToEmail']

    attributes = {
        "state": globals()['STATE'], 
        "headline_index": session['attributes']['headline_index'],
        "articles": session['attributes']['articles'],
        "dialogStatus": "readTitle",
        'articlesToEmail': articlesToEmail
    }

    return response(attributes, response_plain_text(msg, False))

def ask_next_headline(session):
    articlesToEmail = []

    if 'articlesToEmail' in session['attributes']:
        articlesToEmail = session['attributes']['articlesToEmail']

        print(articlesToEmail)


    articlesToEmail.append(session['attributes']['headline_index'])

    attributes = {
        "state" : globals()['STATE'], 
        "headline_index" : session['attributes']['headline_index'],
        "articles" : session['attributes']['articles'],
        "dialogStatus": "readEmail",
        "articlesToEmail": articlesToEmail
    }

    if session['attributes']['headline_index'] >= len(session['attributes']['articles']):
        return do_stop()

    alexaMsg = "Okay. Would you like to hear the next headline?"

    return response(attributes, response_plain_text(alexaMsg, False))

def read_headline(session):
    if 'articles' not in session['attributes']:

        res = api.get_top_headlines()
        articles = res['articles']
        session['attributes']['headline_index'] = 0
        session['attributes']['articles'] = articles

    else:
        # End if out of headlines, there's probably a better way to handle this
        # but this works for now
        if session['attributes']['headline_index'] == len(session['attributes']['articles']):
            return do_stop(session)

        articles = session['attributes']['articles']
    
    msg = ""
    article = articles[session['attributes']['headline_index']]

    # for article in articles:
    
    if article['description'] is not None:
        msg += article['description']
        msg += " "
        # msg += NEXT_HEADLINE
        msg += EMAIL_HEADLINE
    else:
        msg += NO_DESCRIPTION

    articlesToEmail = []

    if 'articlesToEmail' in session['attributes']:
        articlesToEmail = session['attributes']['articlesToEmail']
    else:
        articlesToEmail.append(session['attributes']['headline_index'])

    attributes = {
        "state" : globals()['STATE'], 
        "headline_index" : session['attributes']['headline_index'],
        "articles" : session['attributes']['articles'],
        "dialogStatus": "readDescription",
        "articlesToEmail": articlesToEmail
    }

    return response(attributes, response_plain_text(msg, False))

def sourcedNews(request, intent, session):

    if 'attributes' not in session or 'articles' not in session['attributes']:

        requestedSource = intent['slots']['source']['value']

        """ Split up and format the requested source """
        formattedSource = ""
        words = requestedSource.split()

        for i in range(len(words)):
            if i == len(words) - 1:
                formattedSource += words[i].lower()
            else:
                formattedSource += words[i].lower() + "-"

        print("formattedSource: " + formattedSource)

        found = False

        for source in sourcesDict.values():
            if source['id'] == formattedSource:
                found = True
                break

        if found == False:
            return response({}, response_plain_text("Sorry. I couldn't find that source.", True))

        res = api.get_top_headlines(sources=formattedSource)
        print(res)
        articles = res['articles']

        session['attributes'] = {}
        session['attributes']['headline_index'] = 0
        session['attributes']['articles'] = articles

    else:
        # End if out of headlines, there's probably a better way to handle this
        # but this works for now
        if session['attributes']['headline_index'] == len(session['attributes']['articles']):
            return do_stop(session)

        articles = session['attributes']['articles']
    
    print(articles)
    print("\n")

    msg = ""
    article = articles[session['attributes']['headline_index']]

    # for article in articles:
    msg += "From " + article['source']['name'] + ": "
    msg += article['title']
    msg += ". "
    msg += REPROMPT_HEADLINE
        
    print(msg + "\n\n")

    print(articles[0])
    print("\n")

    articlesToEmail = []

    if 'articlesToEmail' in session['attributes']:
        articlesToEmail = session['attributes']['articlesToEmail']

    attributes = {
        "state": globals()['STATE'], 
        "headline_index": session['attributes']['headline_index'],
        "articles": session['attributes']['articles'],
        "dialogStatus": "readTitle",
        "articlesToEmail": articlesToEmail
    }

    return response(attributes, response_plain_text(msg, False))

def do_stop(session):
    """  stop the app """

    """ check if there are any articles to be emailed """

    print('session in do_stop: ')
    print(session)

    user_email = ""

    if 'articlesToEmail' in session['attributes']:
        articlesToEmail = session['attributes']['articlesToEmail']

        # Exit w/o email if there's nothing to email
        if not articlesToEmail:
            attributes = {"state":globals()['STATE']}
            return response(attributes, response_plain_text(EXIT_SKILL_MESSAGE, True))

        if 'accessToken' not in session['user']:
            attributes = {"state":globals()['STATE']}
            return response(attributes, response_card_login('Real News - Email Setup', LOGIN_MESSAGE, True))
        else:
            request_data = requests.get("https://api.amazon.com/user/profile?access_token=" + session['user']['accessToken'])
            request_json = request_data.json()
            user_email = request_json['email']

        msg = HTML_MSG_1

        articles = session['attributes']['articles']

        msg += "<div align='center'>"
        msg += "<a href='#' style='text-decoration: none; color: #000000;'>"
        msg += "<img src='"
        msg += EMAIL_HEADER_IMG
        msg += "' style='max-width: 50%; height: auto;' /><br><br><hr />"
        msg += "</a>"
        msg += "</div>"

        for i in range(len(articles)):
            if i in articlesToEmail:

                msg += "<div>"
                msg += "<a href=\"" + articles[i]['url'] + "\">"
                msg += "<h2>" + articles[i]['title'] + "</h2>"
                msg += "</a>"
                msg += "<p>"
                if  articles[i]['description'] is not None:
                    msg += articles[i]['description']
                msg += "</p><br />"
                if articles[i]['source']['name'] in sourcesDict:
                    msg += "<a href=\"" + sourcesDict[articles[i]['source']['name']]['url'] + "\">"
                    msg += articles[i]['source']['name']
                    msg += "</a>"
                else:
                    msg += articles[i]['source']['name']
                msg += "</div>"

                if i != len(articles) - 1:
                    msg += "<hr />"
                
                # msg += "<tr>"

                # msg += "<td>"
                # msg += "<a href=\"" + articles[i]['url'] + "\">"
                # msg += "<img height=\"200\" width=\"200\" src=\"" + articles[i]['urlToImage'] + "\" "
                # msg += "</a>"
                # msg += "</td>"

                # msg += "<td>"
                # msg += "<p>"
                # msg += "<a href=\"" + articles[i]['url'] + "\">"
                # msg += "<h2>" + articles[i]['title'] + "</h2> <br />"
                # msg += "</a>"
                # msg += articles[i]['description'] + "<br /><br />"
                # msg += articles[i]['source']['name'] + "<br />"
                # msg += "</p>"
                # msg += "</td>"

                # msg += "<tr>"


        # msg += "</table></body>"
        # msg += "</html>"

        msg += HTML_MSG_2

        # need to get the user's email to send the mail

        sg = sendgrid.SendGridAPIClient(apikey=os.environ.get('SENDGRID_API_KEY'))
        from_email = Email(os.environ.get('EMAIL_SENDER_ADDRESS'))
        to_email = Email(user_email)
        now = datetime.datetime.now()

        subject = "Your Flash Briefing for " + str(now.month) + "/" + str(now.day)
        content = Content("text/html", msg)
        mail = Mail(from_email, subject, to_email, content)
        sendGrid = sg.client.mail.send.post(request_body=mail.get())
        print(sendGrid.status_code)
        print(sendGrid.body)
        print(sendGrid.headers)


    # if 'articlesToEmail' in session['attributes']:
    #     articles = session['attributes']['articles']
    #     for article in articlesToEmail:
    #         print(article)

    attributes = {"state":globals()['STATE']}
    return response(attributes, response_plain_text(EXIT_SKILL_MESSAGE, True))

def do_help():
    """ return a help response  """

    global STATE
    STATE = STATE_START
    attributes = {"state":globals()['STATE']}
    return response(attributes, response_plain_text(HELP_MESSAGE, False))

def on_launch():
    """ called on Launch reply with a welcome message """
 
    return get_welcome_message()

def on_session_ended(request):
    """ called on session end  """
    
    print(request)

    if request['reason']:
        end_reason = request['reason']
        print("on_session_ended reason: " + end_reason)
    else:
        print("on_session_ended")

def get_state(session):
    """ get and set the current state  """

    global STATE
    print(session)
    if 'state' in session['attributes']:
        STATE = session['attributes']['state']
    else:
        STATE = STATE_START

# --------------- response string formatters -----------------
def get_welcome_message():
    """ return a welcome message """

    attributes = {"state":globals()['STATE']}
    return response(attributes, response_plain_text(WELCOME_MESSAGE, False))

def response_plain_text(output, endsession):
    """ create a simple json plain text response  """

    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'shouldEndSession': endsession
    }


def response_ssml_text(output, endsession):
    """ create a simple json plain text response  """

    return {
        'outputSpeech': {
            'type': 'SSML',
            'ssml': "<speak>" +output +"</speak>"
        },
        'shouldEndSession': endsession
    }

def response_ssml_text_and_prompt(output, endsession, reprompt_text):
    """ create a Ssml response with prompt  """

    return {
        'outputSpeech': {
            'type': 'SSML',
            'ssml': "<speak>" +output +"</speak>"
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'SSML',
                'ssml': "<speak>" +reprompt_text +"</speak>"
            }
        },
        'shouldEndSession': endsession
    }

def response_card_login(title, output, endsession):
    """ create a simple json plain text response  """

    return {
        'card': {
            'type': 'LinkAccount',
            'title': title,
            'text': output
        },
        'outputSpeech': {
            'type': 'SSML',
            'ssml': "<speak>" +output +"</speak>"
        },
        'shouldEndSession': endsession
    }

def response_ssml_cardimage_prompt(title, output, endsession, cardtext, abbreviation, reprompt):
    """ create a simple json plain text response  """

    smallimage = get_smallimage(abbreviation)
    largeimage = get_largeimage(abbreviation)
    return {
        'card': {
            'type': 'Standard',
            'title': title,
            'text': cardtext,
            'image':{
                'smallimageurl':smallimage,
                'largeimageurl':largeimage
            },
        },
        'outputSpeech': {
            'type': 'SSML',
            'ssml': "<speak>" +output +"</speak>"
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'SSML',
                'ssml': "<speak>" +reprompt +"</speak>"
            }
        },
        'shouldEndSession': endsession
    }

def response_ssml_text_reprompt(output, endsession, reprompt_text):
    """  create a simple json response with a card  """

    return {
        'outputSpeech': {
            'type': 'SSML',
            'ssml': "<speak>" +output +"</speak>"
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'SSML',
                'ssml': "<speak>" +reprompt_text +"</speak>"
            }
        },
        'shouldEndSession': endsession
    }

def dialog_response(attributes, endsession):
    """  create a simple json response with card """

    return {
        'version': '1.0',
        'sessionAttributes': attributes,
        'response':{
            'directives': [
                {
                    'type': 'Dialog.Delegate'
                }
            ],
            'shouldEndSession': endsession
        }
    }

def response(attributes, speech_response):
    """ create a simple json response """

    return {
        'version': '1.0',
        'sessionAttributes': attributes,
        'response': speech_response
    }