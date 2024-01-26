import os
import re
import yaml
import random
import numpy as np
import pandas as pd
from num_to_words import num_to_word
import pickle


def generate_number(num_length, generate_from=range(0,10)):
    if num_length == 0:
        raise ValueError('can not generate 0 length number')
    else:
        number = random.choices(generate_from, k=num_length)
    return list(map(str, number))


def get_chuncked_list(lst):
    chunks = random.choice(range(len(lst)))
    if chunks == 0:
        return [lst]
    else:
        chunked_list = [list(array) for array in np.array_split(np.array(lst), chunks)]
        # print('chunked_list', chunked_list)
        return chunked_list


def number_to_words(number_list, lang):
    num_in_words = list()
    for lst in number_list:
        joined_list = ''.join(lst)
        num_in_words.append(num_to_word(joined_list, lang=lang))
    num_in_words = ' '.join(num_in_words)
    num_in_words = num_in_words.replace(',', '')
    num_in_words = num_in_words.replace('-', ' ')
    if lang == 'hi':
        zero = random.choice([ 'शून्य', 'ज़िरो', 'जिरो', 'जीरो', 'ज़ीरो'])
        if 'शून्य' in num_in_words:
            num_in_words = num_in_words.replace('शून्य', zero, 1)
    return num_in_words.replace('\u200b', '')


def get_mobile_number(lang):
    mobile_number = [random.choice([6, 7, 8, 9])] + generate_number(num_length=9)
    mobile_number = list(map(str, mobile_number))
    chuncked_list = get_chuncked_list(mobile_number)
    mobile_number = number_to_words(chuncked_list, lang=lang)
    return mobile_number


def get_amount_of_money(lang, rs_variations_dict, num_length=random.choice(range(1, 5))):
    if num_length == 0:
        raise ValueError('can not generate 0 length amount of money')
    elif num_length == 1:
        number = [random.choice(range(1, 10))]
    else:
        number = [random.choice(range(1, 10))] + random.choices(range(0, 10), k=num_length-1)

    number = list(map(str, number))
    number = [''.join(number)]
    amount_of_money = number_to_words(number, lang=lang)
    rs_varirations = rs_variations_dict[lang]
    rs_variation = random.choice(rs_varirations)
    
    if random.choice(['start', 'end']) == 'start':
        amount_of_money = f'{rs_variation} {amount_of_money}'
    else:
        amount_of_money = f'{amount_of_money} {rs_variation}'
    
    return amount_of_money


def get_alphanumeric_number(lang, num_length, alpha_length, alphabets_dict = None):
    if alpha_length > 0:
        lang_alphabets = alphabets_dict[lang]
        alphabets_list = random.choices(lang_alphabets, k=alpha_length)
        alphabets_str = random.choice([' ', '']).join(alphabets_list)
    else: 
        alphabets_str = ''
        
    if num_length > 0:
        number = generate_number(num_length = num_length)
        number_in_words = number_to_words(number, lang)
    else:
        number_in_words = ''
        
    alphanumeric_number = f'{alphabets_str} {number_in_words}'
    return alphanumeric_number.strip()


def get_vehicle_number(lang, rto_dict, alphabets_dict):
    
    """ 
    generate vehicle numebrs e.g. KA 51 A 1234 or KA 51 AB 1234
    including BH series e.g. 22 BH 1234 AA    
    
    """
    four_digit_number = generate_number(num_length=4)
    chuncked_list = get_chuncked_list(four_digit_number)
    four_digit_number_in_words = number_to_words(chuncked_list, lang=lang)

    one_two_alphabets = get_alphanumeric_number(
                                lang, 
                                num_length = 0, 
                                alpha_length = random.choice([1, 2]),
                                alphabets_dict = alphabets_dict
                                )

    if random.choices(['BH', 'Non-BH'], weights=[.2, .8], k=1)[0] == 'BH':
        reg_year = ['2'] + [str(random.choice(range(10)))]
        chuncked_list = get_chuncked_list(reg_year)
        reg_year_in_words = number_to_words(chuncked_list, lang=lang)
        if lang == 'hi':
            vehicle_number = vehicle_number = f'{reg_year_in_words} बी एच {four_digit_number_in_words} {one_two_alphabets}' 
        else:
            vehicle_number = f'{reg_year_in_words} b h {four_digit_number_in_words} {one_two_alphabets}'
    else:    
        lang_rto_code_list = rto_dict[lang]
        rto_state_code = random.choice(lang_rto_code_list)
        rto_number_code = generate_number(num_length=2)
        chuncked_list = get_chuncked_list(rto_number_code)
        rto_number_code_in_words = number_to_words(chuncked_list, lang=lang)
        vehicle_number = f'{rto_state_code} {rto_number_code_in_words} {one_two_alphabets} {four_digit_number_in_words}'
    return vehicle_number
        

def save_formatted_data(lang, file_name, lines):
    data = pd.DataFrame(lines, columns=['sentence'])
    data['intent'] = f"{file_name.split('.')[0]}"
    data['language'] = lang

    save_dir_path = os.path.join(os.getcwd(), 'formatted_data', lang)
    file_name = f"{file_name.split('.')[0]}.csv"
    file_path = os.path.join(save_dir_path, file_name)
    
    if os.path.isfile(file_path):
        data.to_csv(file_path, mode='a', header=False, index=False)
        return f'\n{file_name} data for "{lang}" is Appended to file: {file_path}'
    else:
        data.to_csv(file_path, header=True, index=False)
        return f'\n{file_name} data for "{lang}" is Saved in file: {file_path}'



def get_entity_input_data(lang):
  with open(f'entity_data/entities-{lang}.yaml') as f:
    entities_dict = yaml.load(f, yaml.BaseLoader)

  entity_variations_dict = dict()
  for key in entities_dict:
      entity_variations_dict[key] = list()
      for entity_name in entities_dict[key]:
          entity_variations_dict[key] = entity_variations_dict[key] + entities_dict[key].get(entity_name)

  with open("entity_data/rto_codes.yaml") as f:
      rto_dict = yaml.load(f, yaml.BaseLoader)

  with open("entity_data/rs_variations.yaml") as f:
      rs_variations_dict = yaml.load(f, yaml.BaseLoader)

  with open("entity_data/entity_types_mapping.yaml") as f:
      entity_mapping_dict = yaml.load(f, yaml.BaseLoader)

  with open("entity_data/alphabets.yaml") as f:
      alphabets_dict = yaml.load(f, yaml.BaseLoader)

  entity_data =  (
                  entities_dict,
                  entity_variations_dict,
                  rto_dict,
                  rs_variations_dict,
                  entity_mapping_dict,
                  alphabets_dict
                  )
  print('--- entity input data prepared ---')
  return entity_data


def get_data_file_list(lang):
  data_file_path = os.path.join(os.getcwd(), 'curated_data', lang)
  data_files = os.listdir(data_file_path)
  data_files = [file for file in data_files if file.endswith(".txt")]
  return (data_files, data_file_path)


def get_lines(data_file_path, file_name):
  with open(f'{os.path.join(data_file_path, file_name)}', 'r', encoding='utf-8-sig') as f:
    lines = f.readlines()
    lines = [line.strip() for line in lines]
    lines = [line for line in lines if not line.startswith("#")]
    lines = [line for line in lines if len(line) > 0]
    lines = [line.strip('."|') for line in lines]
    lines = [line.replace('"?', '') for line in lines]
    lines = [line.replace('|', ' ') for line in lines]  # repleace Poorn Viraam with space
    return lines


def fill_placeholders(lang):
  placeholder_pattern = re.compile('<[a-z_]*>')

  entity_data = get_entity_input_data(lang)
  entities_dict = entity_data[0]
  entity_variations_dict = entity_data[1]
  rto_dict = entity_data[2]
  rs_variations_dict = entity_data[3]
  entity_mapping_dict = entity_data[4]
  alphabets_dict = entity_data[5]

  data_files, data_file_path = get_data_file_list(lang)

  for file_name in data_files:
    lines_with_placeholder = get_lines(data_file_path, file_name)

    updated_lines = list()
    for line in lines_with_placeholder:
        placeholders = placeholder_pattern.findall(line)
        if placeholders:
            for placeholder in placeholders:
                if placeholder in entity_mapping_dict['closed_set_entities']:
                    entity_variations = entity_variations_dict[placeholder.strip('<>')]
                    line = line.replace(placeholder, random.choice(entity_variations))

                elif placeholder in entity_mapping_dict['open_set_entities']:
                    if placeholder == '<amount_of_money>':
                        amount_of_money = get_amount_of_money(lang, rs_variations_dict)
                        line = line.replace(placeholder, amount_of_money)

                    elif placeholder == '<mobile_number>':
                        mobile_number = get_mobile_number(lang)
                        line = line.replace(placeholder, mobile_number)

                    elif placeholder == '<vehicle_number>':
                        vehicle_number = get_vehicle_number(lang, rto_dict, alphabets_dict)
                        line = line.replace(placeholder, vehicle_number)

                    elif placeholder == '<policy_number>':
                        policy_number = generate_number(random.choice(range(8,14)))
                        policy_number = number_to_words(policy_number, lang)
                        line = line.replace(placeholder, policy_number)

                    elif placeholder == '<bank_account_number>':
                        bank_account_number = generate_number(random.choice(range(10,15)))
                        bank_account_number = number_to_words(bank_account_number, lang)
                        line = line.replace(placeholder, bank_account_number)

                    elif placeholder == '<bu_number_for_electricity>':
                        bu_number = generate_number(4)
                        bu_number = number_to_words(bu_number, lang)
                        line = line.replace(placeholder, bu_number)

                    elif placeholder == '<consumer_number>':
                        consumer_number = generate_number(random.choice(range(6,10)))
                        consumer_number = number_to_words(consumer_number, lang)
                        line = line.replace(placeholder, consumer_number)

                    elif placeholder == '<loan_account_number>':
                        loan_account_number = get_alphanumeric_number(lang, 6, 2, alphabets_dict)
                        line = line.replace(placeholder, loan_account_number)
                else:
                    raise ValueError(f'placeholder: {placeholder} not in any entity type.')
            updated_lines.append(line)
        else:
            updated_lines.append(line)

    print(save_formatted_data(lang, file_name, updated_lines))




import torch

class Dataset(torch.utils.data.Dataset):
    def __init__(self, encodings, labels=None, labels_to_ids=None):
        self.encodings = encodings
        self.labels = labels
        self.labels_to_ids = labels_to_ids

    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        if self.labels:
            item["labels"] = torch.tensor(self.labels_to_ids[self.labels[idx]])
        return item

    def __len__(self):
        return len(self.encodings["input_ids"])
##

            



