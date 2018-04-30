from newsapi import NewsApiClient
import os
import requests
import sendgrid
from sendgrid.helpers.mail import *
from constants import *


api = NewsApiClient(api_key=os.environ['API_KEY'])

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

    print('intent_name', intent_name)


    if 'dialogState' in request:
        #delegate to Alexa until dialog sequence is complete
        if request['dialogState'] == "STARTED" or request['dialogState'] == "IN_PROGRESS":
            return dialog_response("", False)

    # process the intents
    if intent_name == "ListSources":
        return listSources(request)
    elif intent_name == "keywordNews":
        if 'attributes' in session:
            # if 'intent' in session['attributes']:
            #     if session['attributes']['intent'] == "Headlines":
            #         session['attributes']['intent'] = "switchToKeyword"
            #     else:
            #         session['attributes']['intent'] = "keywordNews"
            if 'articles' in session:
                session['attributes'].pop('articles')

        return keywordNews(request, intent, session)


    elif intent_name == "CategoryNews":
        if 'attributes' in session:
            # if 'intent' in session['attributes']:
            #     if session['attributes']['intent'] == "Headlines":
            #         session['attributes']['intent'] = "switchToKeyword"
            #     else:
            #         session['attributes']['intent'] = "keywordNews"
            if 'articles' in session:
                session['attributes'].pop('articles')

        return categoryNews(request, intent, session)

    elif intent_name == "SourcedNews":
        if 'attributes' in session:
            # if 'intent' in session['attributes']:
            #     if session['attributes']['intent'] == "Headlines":
            #         session['attributes']['intent'] = "switchToSource"
            #     else:
            #         session['attributes']['intent'] = "sourcedNews"
            if 'articles' in session:
                session['attributes'].pop('articles')

        return sourcedNews(request, intent, session)

    elif intent_name == "Headlines":
        if 'attributes' in session:
            # if 'intent' in session['attributes']:
            #     if session['attributes']['intent'] == "sourcedNews":
            #         session['attributes']['intent'] = "switchToHeadlines"
            #     else:
            #         session['attributes']['intent'] = "Headlines"
            if 'articles' in session:
                session['attributes'].pop('articles')

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


# --------------- List Available Sources -----------------
def listSources(request):
    """ Get the names of all the sources from the dictionary"""
    sourceNames = sourcesDict.keys()

    msg = "Here are the sources: "

    i = 1
    for source in sourceNames:
        if i == 1:
            msg += source
            i += 1
            continue
        msg += ", " + source
        i += 1

    msg += "."

    return response({}, response_plain_text(msg, True))

# --------------- Navigation controls -----------------
def skip(session):
    if 'attributes' not in session:
        return response({}, response_plain_text("", True))

    session['attributes']['headline_index'] += 1
    return headlines(session)

def previous(session):
    if 'attributes' not in session:
        return response({}, response_plain_text("", True))

    if 'headline_index' in session['attributes']:
        if session['attributes']['headline_index'] != 0:
            session['attributes']['headline_index'] -= 1
    else:
        session['attributes']['headline_index'] = 0

    return headlines(session)

# --------------- Headlines entry point -----------------
def headlines(session):
    if 'attributes' not in session:
        res = api.get_top_headlines()

        if(res['status'] == "error"):
            if(res['code'] == 'apiKeyExhausted' or res['code'] == 'rateLimited'):
                return response({}, response_plain_text(OUT_OF_REQUESTS, True))
        
        articles = res['articles']
        session['attributes'] = {}
        session['attributes']['headline_index'] = 0
        session['attributes']['articles'] = articles

    elif 'articles' not in session['attributes']:

        res = api.get_top_headlines()

        if(res['status'] == "error"):
            if(res['code'] == 'apiKeyExhausted' or res['code'] == 'rateLimited'):
                return response({}, response_plain_text(OUT_OF_REQUESTS, True))
        
        articles = res['articles']
        session['attributes']['headline_index'] = 0
        session['attributes']['articles'] = articles

    else:

        # if 'intent' in session['attributes']:
        #     print('intent in headlines:', session['attributes']['intent'])
        #     if 'intent' == 'switchToHeadlines':
        #         session['attributes']['intent'] = "Headlines"
        #         session['attributes'].pop('articles')
        #         print('after pop', session)
        #         return headlines(session)
        #     elif 'intent' == 'switchToSource':
        #         session['attributes']['intent'] = "sourcedNews"
        #         session['attributes'].pop('articles')
        #         return headlines(session)
        #     elif 'intent' == 'switchToKeyword':
        #         session['attributes']['intent'] = "keywordNews"
        #         session['attributes'].pop('articles')
        #         return headlines(session)
        #         
        #


        # End if out of headlines, there's probably a better way to handle this
        # but this works for now
        if session['attributes']['headline_index'] >= len(session['attributes']['articles']):
            return do_stop(session)

        articles = session['attributes']['articles']
    
    msg = ""
    article = articles[session['attributes']['headline_index']]

    # for article in articles:
    msg += "From " + article['source']['name'] + ": "
    msg += article['title']
    msg += ". "
    msg += REPROMPT_HEADLINE

    articlesToEmail = []

    if 'articlesToEmail' in session['attributes']:
        articlesToEmail = session['attributes']['articlesToEmail']

    intent_name = ""
    if 'intent' in session['attributes']:
        intent_name = session['attributes']['intent']
    else:
        intent_name = "Headlines"

    attributes = {
        "state": globals()['STATE'], 
        "headline_index": session['attributes']['headline_index'],
        "articles": session['attributes']['articles'],
        "dialogStatus": "readTitle",
        'articlesToEmail': articlesToEmail,
        "intent": intent_name
    }

    return response(attributes, response_plain_text(msg, False))

# --------------- Add to email list and prompt user -----------------
def ask_next_headline(session):

    articlesToEmail = []

    if 'articlesToEmail' in session['attributes']:
        articlesToEmail = session['attributes']['articlesToEmail']

    articles = session['attributes']['articles']
    articleToSend = articles[session['attributes']['headline_index']]

    articlesToEmail.append(articleToSend)

    attributes = {
        "state" : globals()['STATE'], 
        "headline_index" : session['attributes']['headline_index'],
        "articles" : session['attributes']['articles'],
        "dialogStatus": "readEmail",
        "articlesToEmail": articlesToEmail
    }

    if 'formattedSource' in session['attributes']:
        attributes["formattedSource"]= session['attributes']['formattedSource']

    if 'keyword' in session['attributes']:
        attributes["keyword"]= session['attributes']['keyword']

    if 'intent' in session['attributes']:
        attributes['intent'] = session['attributes']['intent']
    else:
        attributes['intent'] = "Headlines"

    if session['attributes']['headline_index'] >= len(session['attributes']['articles']):
        return do_stop()

    alexaMsg = "Okay. Would you like to hear the next headline?"

    return response(attributes, response_plain_text(alexaMsg, False))


# --------------- Read description -----------------
def read_headline(session):
    if 'articles' not in session['attributes']:

        res = api.get_top_headlines()

        if(res['status'] == "error"):
            if(res['code'] == 'apiKeyExhausted' or res['code'] == 'rateLimited'):
                return response({}, response_plain_text(OUT_OF_REQUESTS, True))

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
    
    if article['description'] is not None:
        msg += article['description']
        msg += ". "
        # msg += NEXT_HEADLINE
        msg += EMAIL_HEADLINE
    else:
        msg += NO_DESCRIPTION

    articlesToEmail = []

    if 'articlesToEmail' in session['attributes']:
        articlesToEmail = session['attributes']['articlesToEmail']

    attributes = {
        "state" : globals()['STATE'], 
        "headline_index" : session['attributes']['headline_index'],
        "articles" : session['attributes']['articles'],
        "dialogStatus": "readDescription",
        "articlesToEmail": articlesToEmail
    }

    if 'formattedSource' in session['attributes']:
        attributes["formattedSource"] = session['attributes']['formattedSource']


    if 'keyword' in session['attributes']:
        attributes["keyword"] = session['attributes']['keyword']


    if 'intent' in session['attributes']:
        attributes['intent'] = session['attributes']['intent']
    else:
        attributes['intent'] = "Headlines"

    return response(attributes, response_plain_text(msg, False))

# --------------- Sourced News -----------------
def sourcedNews(request, intent, session):

    if ('attributes' not in session) or 'articles' not in session['attributes']:

        requestedSource = intent['slots']['source']['value']

        """ Split up and format the requested source """
        formattedSource = ""
        words = requestedSource.split()

        for i in range(len(words)):
            if i == len(words) - 1:
                formattedSource += words[i].lower()
            else:
                formattedSource += words[i].lower() + "-"


        found = False

        for source in sourcesDict.values():
            if source['id'] == formattedSource:
                found = True
                break

        if found == False:
            return response(session['attributes'], response_plain_text(SOURCE_NOT_FOUND, False))

        res = api.get_top_headlines(sources=formattedSource)


        if(res['status'] == "error"):
            if(res['code'] == 'apiKeyExhausted' or res['code'] == 'rateLimited'):
                return response({}, response_plain_text(OUT_OF_REQUESTS, True))


        articles = res['articles']

        if 'attributes' not in session:
            session['attributes'] = {}
        session['attributes']['headline_index'] = 0
        session['attributes']['articles'] = articles
        session['attributes']['formattedSource'] = formattedSource

    else:
        if 'formattedSource' not in session['attributes']:
            session['attributes'].pop('articles')
            return sourcedNews(request, intent, session)

        if session['attributes']['formattedSource'] != intent['slots']['source']['value']:
            session['attributes'].pop('articles')
            return sourcedNews(request, intent, session)


        # End if out of headlines, there's probably a better way to handle this
        # but this works for now
        if session['attributes']['headline_index'] == len(session['attributes']['articles']):
            return do_stop(session)

        articles = session['attributes']['articles']
    
    msg = ""
    article = articles[session['attributes']['headline_index']]

    # for article in articles:
    msg += "From " + article['source']['name'] + ": "
    msg += article['title']
    msg += ". "
    msg += REPROMPT_HEADLINE
        
    articlesToEmail = []

    if 'articlesToEmail' in session['attributes']:
        articlesToEmail = session['attributes']['articlesToEmail']

    attributes = {
        "state": globals()['STATE'], 
        "headline_index": session['attributes']['headline_index'],
        "articles": session['attributes']['articles'],
        "dialogStatus": "readTitle",
        "articlesToEmail": articlesToEmail,
        "formattedSource": session['attributes']['formattedSource'],
        "intent": "sourcedNews"
    }

    return response(attributes, response_plain_text(msg, False))

def searchKeyword(keyword):
    params = {
                'q': keyword,
                'language': 'en',
                'apiKey': os.environ['API_KEY']
            }

    res = requests.get('https://newsapi.org/v2/top-headlines', verify=False, params=params)

    return res.json()


# --------------- Keyword Search -----------------
def keywordNews(request, intent, session):

    if ('attributes' not in session) or 'articles' not in session['attributes']:

        keyword = intent['slots']['keyword']['value']

        res = searchKeyword(keyword)

        if(res['status'] == "error"):
            if(res['code'] == 'apiKeyExhausted' or res['code'] == 'rateLimited'):
                return response({}, response_plain_text(OUT_OF_REQUESTS, True))

        if res['totalResults'] == 0:
            msg = NO_KEYWORD_NEWS + keyword + '. What would you like to do?'

            attributes = {}
            if 'attributes' in session:
                attributes = session['attributes']

            return response(attributes, response_plain_text(msg, False))


        articles = res['articles']

        if 'attributes' not in session:
            session['attributes'] = {}
        session['attributes']['headline_index'] = 0
        session['attributes']['articles'] = articles
        session['attributes']['keyword'] = keyword

    else:
        if 'keyword' not in session['attributes']:
            session['attributes'].pop('articles')
            return keywordNews(request, intent, session)

        if session['attributes']['keyword'] != intent['slots']['keyword']['value']:
            session['attributes'].pop('articles')
            return keywordNews(request, intent, session)


        # End if out of headlines, there's probably a better way to handle this
        # but this works for now
        if session['attributes']['headline_index'] == len(session['attributes']['articles']):
            return do_stop(session)

        articles = session['attributes']['articles']
    
    msg = ""
    article = articles[session['attributes']['headline_index']]

    # for article in articles:
    msg += "From " + article['source']['name'] + ": "
    msg += article['title']
    msg += ". "
    msg += REPROMPT_HEADLINE
        
    articlesToEmail = []

    if 'articlesToEmail' in session['attributes']:
        articlesToEmail = session['attributes']['articlesToEmail']


    attributes = {
        "state": globals()['STATE'], 
        "headline_index": session['attributes']['headline_index'],
        "articles": session['attributes']['articles'],
        "dialogStatus": "readTitle",
        "articlesToEmail": articlesToEmail,
        "intent": "keywordNews"
    }

    if 'category' in session['attributes']:
        attributes['category'] = session['attributes']['category']

    if 'keyword' in session['attributes']:
        attributes['keyword'] = session['attributes']['keyword']


    return response(attributes, response_plain_text(msg, False))


# --------------- Search by category -----------------
def searchCategory(category):
    params = {
                'category': category,
                'language': 'en',
                'country': 'us',
                'apiKey': os.environ['API_KEY']
            }

    res = requests.get('https://newsapi.org/v2/top-headlines', verify=False, params=params)

    return res.json()


# --------------- Get news by category -----------------
def categoryNews(request, intent, session):

    if ('attributes' not in session) or 'articles' not in session['attributes']:

        category = intent['slots']['category']['value']

        res = searchCategory(category)

        if(res['status'] == "error"):
            if(res['code'] == 'apiKeyExhausted' or res['code'] == 'rateLimited'):
                return response({}, response_plain_text(OUT_OF_REQUESTS, True))

        if res['totalResults'] == 0 or category not in availableCategories:
            msg = NO_CATEGORY_NEWS

            for i in range(len(availableCategories)):
                if i == 0:
                    msg += availableCategories[i]
                elif i == len(availableCategories) - 1:
                    msg += ' and ' + availableCategories[i]
                else:
                    msg += ', ' + availableCategories[i]

            msg += '. What would you like to do?'
            
            attributes = {}
            if 'attributes' in session:
                attributes = session['attributes']

            return response(attributes, response_plain_text(msg, False))


        articles = res['articles']

        if 'attributes' not in session:
            session['attributes'] = {}
        session['attributes']['headline_index'] = 0
        session['attributes']['articles'] = articles
        session['attributes']['category'] = category

    else:
        if 'category' not in session['attributes']:
            session['attributes'].pop('articles')
            return categoryNews(request, intent, session)

        if session['attributes']['category'] != intent['slots']['category']['value']:
            session['attributes'].pop('articles')
            return categoryNews(request, intent, session)


        # End if out of headlines, there's probably a better way to handle this
        # but this works for now
        if session['attributes']['headline_index'] == len(session['attributes']['articles']):
            return do_stop(session)

        articles = session['attributes']['articles']
    
    msg = ""
    article = articles[session['attributes']['headline_index']]

    # for article in articles:
    msg += "From " + article['source']['name'] + ": "
    msg += article['title']
    msg += ". "
    msg += REPROMPT_HEADLINE
        
    articlesToEmail = []


    attributes = {
        "state": globals()['STATE'], 
        "headline_index": session['attributes']['headline_index'],
        "articles": session['attributes']['articles'],
        "dialogStatus": "readTitle",
        "articlesToEmail": articlesToEmail,
        "intent": "CategoryNews"
    }

    if 'articlesToEmail' in session['attributes']:
        articlesToEmail = session['attributes']['articlesToEmail']

    if 'category' in session['attributes']:
        attributes['category'] = session['attributes']['category']

    if 'keyword' in session['attributes']:
        attributes['keyword'] = session['attributes']['keyword']


    return response(attributes, response_plain_text(msg, False))


# --------------- Exit out of skill and email -----------------

def do_stop(session):
    """  stop the app """

    """ check if there are any articles to be emailed """

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
        msg += "<a href='https://realnewsapp.github.io/' target='_blank' style='text-decoration: none; color: #000000;'>"
        msg += "<br>"
        msg += "<img src='https://realnewsapp.github.io/img/logo.png' style='max-width: 50%; height: auto;' />"
        msg += "<br><br><hr />"
        msg += "</a>"
        msg += "</div>"

        i = 0
        for article in articlesToEmail:
            msg += "<div>"
            msg += "<a href=\"" + article['url'] + "\">"
            msg += "<h2>" + article['title'] + "</h2>"
            msg += "</a>"
            msg += "<p>"
            if  article['description'] is not None:
                msg += article['description']
            msg += "</p><br />"
            if article['source']['name'] in sourcesDict:
                msg += "<a href=\"" + sourcesDict[article['source']['name']]['url'] + "\">"
                msg += article['source']['name']
                msg += "</a>"
            else:
                msg += article['source']['name']
            msg += "</div>"

            if i != len(articlesToEmail) - 1:
                msg += "<hr />"

            i += 1

        msg += HTML_MSG_2

        """ email logic """
        sg = sendgrid.SendGridAPIClient(apikey=os.environ.get('SENDGRID_API_KEY'))
        from_email = Email(os.environ.get('EMAIL_SENDER_ADDRESS'))
        to_email = Email(user_email)

        subject = "Your Real News Digest"
        content = Content("text/html", msg)
        mail = Mail(from_email, subject, to_email, content)
        sendGrid = sg.client.mail.send.post(request_body=mail.get())

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
    

    if request['reason']:
        end_reason = request['reason']
        print("on_session_ended reason: " + end_reason)
    else:
        print("on_session_ended")

def get_state(session):
    """ get and set the current state  """

    global STATE
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