import os
import json
import random
import openai
from time import time, sleep
import textwrap
import yaml


def save_yaml(filepath, data):
    with open(filepath, 'w', encoding='utf-8') as file:
        yaml.dump(data, file, allow_unicode=True)



def save_file(filepath, content):
    with open(filepath, 'w', encoding='utf-8') as outfile:
        outfile.write(content)



def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as infile:
        return infile.read()



def random_persona():
    with open('persona_traits.json') as f:
        data = json.load(f)
    result = ""
    for category, options in data.items():
        random_option = random.choice(options)
        result += f"{category}: {random_option}\n"
    return result



def chatbot(messages, model="gpt-4-0613", temperature=0):
#def chatbot(messages, model="gpt-3.5-turbo-0613", temperature=0):
    openai.api_key = open_file('key_openai.txt')
    max_retry = 7
    retry = 0
    while True:
        try:
            response = openai.ChatCompletion.create(model=model, messages=messages, temperature=temperature)
            text = response['choices'][0]['message']['content']
            #save_yaml('debug/debug_%s.yaml' % time(), messages)
            return text, response['usage']['total_tokens']
        except Exception as oops:
            print(f'\n\nError communicating with OpenAI: "{oops}"')
            if 'maximum context length' in str(oops):
                a = messages.pop(1)
                print('\n\n DEBUG: Trimming oldest message')
                continue
            retry += 1
            if retry >= max_retry:
                print(f"\n\nExiting due to excessive errors in API: {oops}")
                exit(1)
            print(f'\n\nRetrying in {2 ** (retry - 1) * 5} seconds...')
            sleep(2 ** (retry - 1) * 5)



if __name__ == '__main__':
    random.seed()
    while True:
        persona = random_persona()
        print('\n\n\nPERSONA:\n\n', persona)
        system = open_file('system_consensus.txt').replace('<<PERSONA>>', persona)
        messages = list()
        
        ###  first question
        
        messages.append({'role': 'system', 'content': system})
        messages.append({'role': 'user', 'content': "What do you think this persona will think about UBI?"})
        response,tokens = chatbot(messages)
        formatted_lines = [textwrap.fill(line, width=120, initial_indent='    ', subsequent_indent='    ') for line in response.split('\n')]
        formatted_text = '\n'.join(formatted_lines)
        print('\n\n\n', formatted_text)
        
        ### second question
        
        messages.append({'role': 'assistant', 'content': response})
        messages.append({'role': 'user', 'content': "What kind of fiscal policy or UBI implementation do you think would resonate with this persona?"})
        response,tokens = chatbot(messages)
        formatted_lines = [textwrap.fill(line, width=120, initial_indent='    ', subsequent_indent='    ') for line in response.split('\n')]
        formatted_text = '\n'.join(formatted_lines)
        print('\n\n\n', formatted_text)
        
        ### third question
        
        messages.append({'role': 'assistant', 'content': response})
        messages.append({'role': 'user', 'content': "Given this persona and their disposition, can you creatively conjure up a potential UBI policy that has a high chance of reaching consensus with this persona?"})
        response,tokens = chatbot(messages)
        formatted_lines = [textwrap.fill(line, width=120, initial_indent='    ', subsequent_indent='    ') for line in response.split('\n')]
        formatted_text = '\n'.join(formatted_lines)
        print('\n\n\n', formatted_text)
        messages.append({'role': 'assistant', 'content': response})

        filepath = "UBI/persona_%s.yaml" % time()
        save_yaml(filepath, messages)
        exit()