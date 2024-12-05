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
            text = re.sub('\n',' ', text)
            text = re.sub('rt',' ', text)
            text = re.sub('user',' ', text)
            text = re.sub('((www\.[^\s]+)|(https?://[^\s]+)|(http?://[^\s]+))',' ',text)
            text = re.sub('  +',' ', text)
            text = re.sub('[^0-9a-zA-Z]+', ' ', text)
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
def text_processing_upload():

    file = request.files.get('file')
    dfdata = pd.read_csv(file,encoding="latin-1")
    dfdata1 = pd.DataFrame(dfdata)
    list_kata_alay = dfalay['kata_alay'].to_list()
    list_kata_baku = dfalay['kata_baku'].to_list()
    dict_kata_alay = {alay:baku for alay, baku in zip(list_kata_alay, list_kata_baku)}
    dict_abusive = {kasar:'***' for kasar in dfabusive['ABUSIVE'].to_list()} 
    dict_gabungan = {**dict_kata_alay, **dict_abusive}

    dfdata['Tweet'] = dfdata['Tweet'].str.replace(dfdata, dict_gabungan)
    filter = dfdata['Tweet'] == dict_gabungan
    df = pd.DataFrame({'raw_text':[raw_text1],'clean_text':[clean_text1]})
    df.to_sql('text_cleaning',conn, if_exists= 'append', index = False)
    json_response = {
        'status_code': 200,
        'description': "Cleaning text from user input",
        'raw_data': raw_text1,
        'clean_data': clean_text1
    }
    response_data = jsonify(dfdata['Tweet'].T.head().to_dict())
    return response_data

if __name__ == '__main__':
    app.run()
