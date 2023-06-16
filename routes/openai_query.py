"""
import re

string = 'MATCH (p:Person {name: "Tom Hanks"})-[:ACTED_IN]->(m:Movie)\nRETURN m.title'
pattern = r'(ACTED)_(IN)'
pattern2 = r'(Person)'
replace_with = r'\1_ON'
replace_with2 = r'Act'

new_string = re.sub(pattern, replace_with, string)
new_string = re.sub(pattern2, replace_with2, new_string)

print(new_string)

"""

import random

import hanspell.spell_checker
from flask import jsonify, Blueprint, session
import flask
import os, re
import openai
from nltk.corpus import wordnet
from gensim import models
from pprint import pprint
from korcen import korcen
from hanspell import spell_checker
import requests
from urllib import request
import zipfile
from flask import send_from_directory, send_file

import os

# # alirezamsh
# from transformers import M2M100ForConditionalGeneration
# from tokenization_small100 import SMALL100Tokenizer
#
# model = M2M100ForConditionalGeneration.from_pretrained("alirezamsh/small100")
# tokenizer = SMALL100Tokenizer.from_pretrained("alirezamsh/small100")

# #facebook
# from transformers import MBartForConditionalGeneration, MBart50TokenizerFast
#
# model = MBartForConditionalGeneration.from_pretrained("facebook/mbart-large-50-many-to-one-mmt")
# tokenizer = MBart50TokenizerFast.from_pretrained("facebook/mbart-large-50-many-to-one-mmt")

openAI = Blueprint("openai_query", __name__, url_prefix="/")

openai.api_key = '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'

mood_list = ['exciting', 'joyful', 'sad', 'calm', 'thrilled', 'quiet', 'bright', 'neat', 'modern', 'cute',
             'sophisticated', 'dark', 'vivid', 'light', 'soft', 'calm', 'deep', 'peaceful', 'boring', 'depressed',
             'dynamic', 'frustrating', 'festival', 'romantic', 'passionate', 'noisy', 'chaotic', 'frightening',
             'critical', 'monotonous', 'solitary', 'empty', 'optimistic', 'pessimistic', 'embarrassed', 'warm', 'cold']

style_list = ['3D', '2D', 'sketch', 'pastel', 'photography', 'oriental painting', 'western painting', 'neon', 'Gothic',
              'future', 'fantasy', 'close-up', 'aerial shot', 'black and white', 'movie', 'drawing', 'child painting',
              'sticker', 'illustration', 'poster', 'character', 'cyberpunk']

# fasttext_model = models.fasttext.load_facebook_model(r'D:\fasttext\cc.en.300.bin.gz')

dir_path = os.path.join(f'{os.getcwd()}', 'save_Image_files')

print(dir_path)

print('starting model!!!')
@openAI.route('/openai_query', methods=['POST'])
def openai_query():
    result = {}

    # default setting
    number = 4
    size = 256

    # POST type classification
    if flask.request.content_type == 'application/json':
        parameters = dict(flask.request.get_json())
        number = int(parameters['number'])
        size = parameters['size']

    if not parameters['search']:
        # 사진 -> 고화질 사진으로 번역 처리
        if parameters['styles'] == '사진':
            parameters['styles'] = '고화질 사진'

        # 번역 문장 생성
        if len(parameters['object'].split(',')) > 1:
            object_list = parameters['object'].split(',')
            object_text = '과(와) '.join(object_list)
            text = parameters['moods'] + '분위기의 ' + parameters['theme'] + '주제로 ' + parameters['background'] + '을(를) ' \
                   + parameters['act'] + ' ' + object_text + '을(를) ' + parameters['styles'] + '스타일로'
        else:
            text = parameters['moods'] + '분위기의 ' + parameters['theme'] + '주제로 ' + parameters['background'] + '을(를) ' \
                   + parameters['act'] + parameters['object'] + '을(를) ' + parameters['styles'] + '스타일로'
    else:
        text = parameters['search']

    text = re.sub(' +', ' ', text)

    # # bad-word check, if True bad-word included in sentences
    # if korcen.check(text):
    #     return False
    #
    # # Fixed sentence
    # spelled_sent = hanspell.spell_checker.check(text)
    # checked_sent = spelled_sent.checked
    # if checked_sent != text:
    #     text = checked_sent

    response = openai.Completion.create(
        model="text-davinci-003",
        prompt= 'please, translate to english' + text + 'and Extract the mood, theme, background, style, and object as nouns from this sentence', #
        temperature=0.5,
        max_tokens=500,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0
    )

    response_text = response['choices'][0]['text'].lower()
    pattern = r' - '
    response_text = re.sub(pattern, ':', response_text)

    mood_index = response_text.find('mood')
    theme_index = response_text.find('theme')
    background_index = response_text.find('background')
    object_index = response_text.find('object')
    style_index = response_text.find('style')

    # Pattern processing because results are returned in two ways
    pattern = r'mood|theme|background|style|object'

    mood_val = re.sub(pattern, '', response_text[mood_index:].split(':')[1]).strip()
    theme_val = re.sub(pattern, '', response_text[theme_index:].split(':')[1]).strip()
    background_val = re.sub(pattern, '', response_text[background_index:].split(':')[1]).strip()
    object_val = re.sub(pattern, '', response_text[object_index:].split(':')[1]).strip()
    style_val = re.sub(pattern, '', response_text[style_index:].split(':')[1]).strip()

    if response_text[mood_index:mood_index+4] == 'mood':
        # Create a list of synonyms to use for WordNet
        synonyms = []  # 동의어를 저장할 리스트

        for syn in wordnet.synsets(mood_val):
            for lemma in syn.lemmas():
                synonyms.append(lemma.name())  # lemma.name()은 동의어를 문자열로 반환함

        synonyms = list(set(synonyms))  # set()을 사용하여 중복된 동의어를 제거함

        # Create a list of synonyms to use for datamuse
        datamuse_url = f"https://api.datamuse.com/words?rel_syn={mood_val}"
        datamuse_response = requests.get(datamuse_url)
        datamuse_data = datamuse_response.json()

        if datamuse_data:
            datamuse_synonyms = [d["word"] for d in datamuse_data]
        else:
            datamuse_synonyms = []

        # Examine synonyms
        if mood_val not in mood_list:
            # datamuse api synonyms search, step 1
            for i in datamuse_synonyms:
                if i in mood_list:
                    result['moods'] = i
            else:
                # nltk.wordnet synonyms search, step 2
                for i in synonyms:
                    if i in mood_list:
                        result['moods'] = i
                # else:
                #     # fasttext cosine similarity synonyms search, step 3
                #     most_similarity = -1
                #     for i in mood_list:
                #         if most_similarity < fasttext_model.wv.similarity(mood_val, i):
                #             most_similarity = fasttext_model.wv.similarity(mood_val, i)
                #             result['moods'] = i
        else:
            result['moods'] = mood_val

    if response_text[theme_index:theme_index+5] == 'theme':
        result['theme'] = theme_val

    if response_text[background_index:background_index + 10] == 'background':
        result['background'] = background_val

    if response_text[object_index:object_index + 6] == 'object':
        result['object'] = object_val

    if response_text[style_index:style_index + 5] == 'style':
        # Create a list of synonyms to use for WordNet
        synonyms = []  # 동의어를 저장할 리스트

        for syn in wordnet.synsets(style_val):
            for lemma in syn.lemmas():
                synonyms.append(lemma.name())  # lemma.name()은 동의어를 문자열로 반환함

        synonyms = list(set(synonyms))  # set()을 사용하여 중복된 동의어를 제거함

        # Create a list of synonyms to use for datamuse
        datamuse_url = f"https://api.datamuse.com/words?rel_syn={style_val}"
        datamuse_response = requests.get(datamuse_url)
        datamuse_data = datamuse_response.json()

        if datamuse_data:
            datamuse_synonyms = [d["word"] for d in datamuse_data]
        else:
            datamuse_synonyms = []

        # Examine synonyms
        if style_val not in style_list:
            # datamuse api synonyms search, step 1
            for i in datamuse_synonyms:
                if i in style_list:
                    result['style'] = i
            else:
                # nltk.wordnet synonyms search, step 2
                for i in synonyms:
                    if i in style_list:
                        result['style'] = i
                # else:
                #     # fasttext cosine similarity synonyms search, step 3
                #     most_similarity = -1
                #     for i in style_list:
                #         if most_similarity < fasttext_model.wv.similarity(style_val, i):
                #             most_similarity = fasttext_model.wv.similarity(style_val, i)
                #             result['style'] = i
        else:
            result['style'] = style_val

    # # alirezamsh
    # # translate korean to english
    # tokenizer.tgt_lang = "en"
    # encoded_zh = tokenizer(text, return_tensors="pt")
    # generated_tokens = model.generate(**encoded_zh)
    # text = tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)

    # # Facebook
    # # translate Korean to English
    # tokenizer.src_lang = "ko_KR"
    # encoded_hi = tokenizer(input, return_tensors="pt")
    # generated_tokens = model.generate(**encoded_hi, forced_bos_token_id=tokenizer.lang_code_to_id["en_XX"])
    # text = tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)
    #
    response = openai.Image.create(
        prompt= response['choices'][0]['text'], #text[0],
        n=number,
        size=str(size) + 'x' + str(size)
    )

    result['url'] = []

    if not os.path.exists(dir_path):
        os.makedirs(dir_path, exist_ok=True)

    import make_response
    for idx, res in enumerate(response['data']):
        result['url'].append(res['url'])

        savename = "generated_" + str(idx) + ".png"
        url = result['url'][idx]

        mem = request.urlopen(url).read()
        with open(os.path.join(dir_path, savename), mode="wb") as f:
            f.write(mem)

    file_list = []
    for i in os.listdir(dir_path):
        file_list.append(os.path.join(dir_path, i))

    return 'Completed Dalle Image Download'

@openAI.route('/Image_download/<int:number>', methods=['POST'])
def Image_download(number):
    Image_path = dir_path

    with os.scandir(Image_path) as entries:
        Image_list = [entry.name for entry in entries if entry.is_file() and entry.name.endswith('.png')]
        return send_file(os.path.join(dir_path, Image_list[number]), as_attachment=True)

@openAI.route('/session_clear', methods=['POST'])
def session_clear():
    clear = flask.request.args.get('clear', False)

    if clear:
        session.clear()
        session.modified = True

        file_list = []
        for i in os.listdir(dir_path):
            file_list.append(os.path.join(dir_path, i))
        # 파일 삭제
        for file_name in file_list:
            try:
                # 파일을 닫음
                with open(file_name, 'r') as f:
                    f.close()
                # 파일을 삭제함
                os.remove(file_name)
            except Exception as e:
                print(f"Error while deleting file {file_name}: {e}")
    return 'Completed Dalle Image Delete'
    # finally:
    #     # 세션 초기화
    #     session.clear()
    #     session.modified = True
    #     print('session clear')
    #     import signal
    #     # 파일 삭제
    #     for file_name in file_list:
    #         try:
    #             # 파일을 닫음
    #             with open(file_name, 'r') as f:
    #                 f.close()
    #             # 파일을 삭제함
    #             os.remove(file_name)
    #         except Exception as e:
    #             print(f"Error while deleting file {file_name}: {e}")
