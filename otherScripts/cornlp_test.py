'''
 * Created by filip on 04/12/2019
'''

import re
from pycorenlp import StanfordCoreNLP
import pandas as pd

df = pd.read_csv('/home/fadamik/Documents/training_data_snorkel_1k_full_rand.txt', sep='\t', header=0,
                 error_bad_lines=True, encoding="ISO-8859–1")

df = df.iloc[:1000]
nlp = StanfordCoreNLP('http://localhost:9000')


def find_question(text):
    sentences = text.split('.')
    for sentence in sentences:
        if len(sentence) > 1500:
            text = text[:1500]
            break

    output = nlp.annotate(text, properties={
        'annotators': 'tokenize,ssplit,pos,depparse,parse',
        'outputFormat': 'json'
    })

    pattern1 = re.compile("SQ")
    pattern2 = re.compile("SBARQ")

    try:
        questions = []
        for sentence in output['sentences']:

            question = []
            question1 = re.findall(pattern1, sentence['parse'])
            question2 = re.findall(pattern2, sentence['parse'])

            question = question1 + question2

            if len(question1) > 0 or len(question2) > 0:
                print(question)

            if question:
                questions.append(question)

        if questions:
            return len(questions)
        else:
            return 0
    except TypeError:
        return 0


df['questions'] = df['document_text'].apply(find_question)

print(df.head())

df.to_csv("/home/fadamik/Documents/training_data_snorkel_1k_full_rand_quest.txt", sep="\t", header=True)
# print(output['sentences'][0]['parse'].split('\n')[1])
