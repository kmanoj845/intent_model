import random
import numpy as np
from num_to_words import num_to_word
import yaml
import pandas as pd
import os

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
##

            



