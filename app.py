import re
import pandas as pd
import sqlite3
from flask import Flask, jsonify
from pathlib import Path

#Declarating the global variables
conn = sqlite3.connect('database.db') #Make connection to database
dfabusive = pd.read_sql('SELECT * FROM ABUSIVE', conn)#Read abusive from database
dfalay = pd.read_sql('SELECT * FROM kamusalay', conn)#Read kamus alay from database 

db_path = Path(__file__).parent/'database.db'
conn = sqlite3.connect(db_path, check_same_thread=False) 
app = Flask(__name__)

from flask import request
from flasgger import Swagger, LazyString, LazyJSONEncoder
from flasgger import swag_from

app.json_encoder = LazyJSONEncoder
swagger_template = dict(
    info = {
        'title': LazyString(lambda: 'Binar Data Science Bootcamp Gold Challenge (API for Data Cleansing of Hate Speech created by Hariyanto)'),
        'version': LazyString(lambda: '1.0.0'),
        'description': LazyString(lambda: 'API Documentation for Data Cleaning of Hate Speech taken from both text and file')
    },
    host = LazyString(lambda: request.host)
)
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'docs',
            "route": '/docs.json'
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/docs/"
}

swagger = Swagger(app, template=swagger_template,config=swagger_config)

@swag_from("docs/get_api.yml", methods=['GET'])
@app.route('/', methods=['GET'])
#Function for showing home page
def hello_world():
    json_response = {
        'status_code': 200,
        'description': "API Text and File Cleansing",
    }
    response_data = jsonify(json_response)
    return response_data

@swag_from("docs/all_data.yml", methods=['GET'])
@app.route('/text', methods=['GET'])
def show_text_cleaning():
    json_response = pd.read_sql('SELECT * FROM text_cleaning;', conn).to_dict()
    response_data = jsonify(json_response)
    return response_data

@swag_from("docs/text_process.yml", methods=['POST'])
@app.route('/text-processing', methods=['POST'])

def text_processing_input():
    list_kata_alay = dfalay['kata_alay'].to_list()
    list_kata_baku = dfalay['kata_baku'].to_list()
    dict_kata_alay = {alay:baku for alay, baku in zip(list_kata_alay, list_kata_baku)}
    dict_abusive = {kasar:'***' for kasar in dfabusive['ABUSIVE'].to_list()} 
    dict_gabungan = {**dict_kata_alay, **dict_abusive}

    text = request.form.get('text')
    text_split = text.split(' ')
    raw_text = text
#For kata in dfabusive['ABUSIVE'].to_list():
    for kata in text_split:
        if kata in dict_gabungan :
            #Clean puctuation 
            text = re.sub(r'[?:!;.,]','',  text)
            #Remove white space in the leading
            text =  text.lstrip()
            #Remove white space in the trailing
            text =  text.rstrip()
            #Capitalize the text
            text =  text.capitalize()
            #Remove character non-alphanumerical
            text = re.sub(r'\\x[A-Za-z0-9./]+', '',  text)
            #Remove non-ASCII
            text = re.sub(r'[^\x00-\x7F]+','',  text)
            #Remove new line from text in between 
            text = re.sub(r'\\t|\\n|\\r|\t|\r|\n', '',  text)
            #Remove all occurrences of the substring
            text = re.sub('\n','', text)
            text = re.sub('rt','', text)
            text = re.sub('user','', text)
            text = re.sub('  +','', text)
            text = re.sub('((www\.[^\s]+)|(https?://[^\s]+)|(http?://[^\s]+))','',text)
            #Remove multiple white space
            text = re.sub(r'^\s+ | \s+$','',  text)
            text = re.sub(kata,dict_gabungan[kata],text)
            clean_text = text
    df = pd.DataFrame({'raw_text':[raw_text],'clean_text':[clean_text]})
    df.to_sql('text_cleaning',conn, if_exists= 'append', index = False)
    json_response = {
        'status_code': 200,
        'description': "Cleaning text from user input",
        'raw_data': raw_text,
        'clean_data': clean_text
    }
    response_data = jsonify(json_response)
    return response_data

@swag_from("docs/file_process.yml", methods=['POST'])
@app.route('/text-processing_upload', methods=['POST'])

#Function for file cleaning from file
def file_clean():
    file      = request.files['data_file']                                                #Request data file from uploaded file
    file      = pd.read_csv(file, encoding='latin-1')
    # Remove new line from text in between 
    re_tweet = file['Tweet'].str.replace(r'\\t|\\n|\\r|\t|\r|\n', '', regex=True)
    # Replace the number in the first sentence
    re_tweet = re_tweet.str.replace(r'^[0-9].','', regex=True)
    # Remove character non-alphanumerical
    re_tweet = re_tweet.str.replace(r'\\x[A-Za-z0-9./]+', '', regex=True)
    # Remove punctuation
    re_tweet = re_tweet.str.replace(r'[^\w\s]','', regex=True)
    # Remove link 
    re_tweet = re_tweet.str.replace('http[^\s]+|www.[^\s]+|@[^\s]+', '', regex=True)
    # Remove non-ASCII
    re_tweet = re_tweet.str.replace(r'[^\x00-\x7F]+','', regex=True)
    # Remove URL 
    re_tweet = re_tweet.str.replace(r'RT|URL',' ', regex=True)
    # Remove white space in the leading 
    re_tweet = re_tweet.str.lstrip()
    # Remove white space in the trailing
    re_tweet = re_tweet.str.rstrip()
    # Capitalize the text
    re_tweet = re_tweet.str.capitalize()
    # Remove multiple white space
    re_tweet = re_tweet.str.replace(r'^\s+ | \s+$','', regex=True)
    file_regex = re_tweet.to_frame('Raw_text')


    raw_tweet = [file_regex['Raw_text'][raw].split() for raw in range(len(file_regex))]     #Convert each row to list

    substitute_text =[]                                                                     #Make a list for substitute_text
    for tweet in range(len(raw_tweet)):                                                     #Looping thorough raw_text
        substitute_text.append([' '.join([dfalay.get(item,item)for item in raw_tweet[tweet]])]) #Subsitute match word from dict_alay to the new_list and append to the list
    
    #Subsitute the matched words from abusive to the subsitute text
    cencored_text= []
    for text in range(len(substitute_text)):
        my_list = substitute_text[text][0].split()
        text_list = ' '.join(my_list)
        for tag in dfabusive:
            text_list = text_list.replace(tag, '*'*len(tag))
        cencored_text.append(text_list)

    #Convert list to the string
    tweet_dict = {"Raw_text":[],"Clean_text":[]}
    # tweet_dict_clean = {"Clean_text":[]}
    tweet_initial = file['Tweet']
    #Append the data to tweet_dict
    for i in range(len(cencored_text)):
        tweet_dict["Raw_text"].append(tweet_initial[i])
        tweet_dict["Clean_text"].append(''.join(cencored_text[i]))
    tweet_dict = pd.DataFrame(tweet_dict)
    tweet_dict.to_sql('Tweet', conn, if_exists='append', index=False)         #Append the data to database
    tweet_dict_final = tweet_dict.T.to_dict()

    return jsonify(
        clean_file=tweet_dict_final,
        status_code=200
    )

if __name__ == '__main__':
    app.run()
