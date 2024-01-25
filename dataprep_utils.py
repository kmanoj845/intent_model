import os
import re
import yaml
import utils
import random
import pandas as pd
import numpy as np
import pickle
from sklearn.decomposition import PCA


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
    lines = [line.replace('"', '') for line in lines]
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
                        amount_of_money = utils.get_amount_of_money(lang, rs_variations_dict)
                        line = line.replace(placeholder, amount_of_money)

                    elif placeholder == '<mobile_number>':
                        mobile_number = utils.get_mobile_number(lang)
                        line = line.replace(placeholder, mobile_number)

                    elif placeholder == '<vehicle_number>':
                        vehicle_number = utils.get_vehicle_number(lang, rto_dict, alphabets_dict)
                        line = line.replace(placeholder, vehicle_number)

                    elif placeholder == '<policy_number>':
                        policy_number = utils.generate_number(random.choice(range(8,14)))
                        policy_number = utils.number_to_words(policy_number, lang)
                        line = line.replace(placeholder, policy_number)

                    elif placeholder == '<bank_account_number>':
                        bank_account_number = utils.generate_number(random.choice(range(10,15)))
                        bank_account_number = utils.number_to_words(bank_account_number, lang)
                        line = line.replace(placeholder, bank_account_number)

                    elif placeholder == '<bu_number_for_electricity>':
                        bu_number = utils.generate_number(4)
                        bu_number = utils.number_to_words(bu_number, lang)
                        line = line.replace(placeholder, bu_number)

                    elif placeholder == '<consumer_number>':
                        consumer_number = utils.generate_number(random.choice(range(6,10)))
                        consumer_number = utils.number_to_words(consumer_number, lang)
                        line = line.replace(placeholder, consumer_number)

                    elif placeholder == '<loan_account_number>':
                        loan_account_number = utils.get_alphanumeric_number(lang, 6, 2, alphabets_dict)
                        line = line.replace(placeholder, loan_account_number)
                else:
                    raise ValueError(f'placeholder: {placeholder} not in any entity type.')
            updated_lines.append(line)
        else:
            updated_lines.append(line)

    print(utils.save_formatted_data(lang, file_name, updated_lines))

