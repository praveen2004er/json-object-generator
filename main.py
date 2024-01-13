import argparse
import json
import google.generativeai as genai
import re

BASE_PROMPT = '''
You are given a joi object schema. You need to create one valid testcase with as much attributes as possible.
Also create an appropriate file name based on the testcase's semantic contextual value and print it as part of output.
Respond with only a json object that contain the filename, testcase_description and testcase value, the json object should be wrapped with empty string
'''

BASE_WITH_NEXT_PROMPT = '''
You are given a joi object schema, you need to create all possible test cases as possible.
Generate the json objects one by one.
When i type ===== give me more possible testcase combinations
'''

def read_file_as_string(file_path):
    """
    Reads the contents of a file and returns them as a single string.

    Parameters:
    - file_path (str): The path to the file.

    Returns:
    - str: The contents of the file as a string.
    """
    try:
        with open(file_path, 'r') as file:
            # Read the entire file into a string
            file_contents = file.read()
            return file_contents
    except FileNotFoundError:
        return f"File not found: {file_path}"
    except Exception as e:
        return f"An error occurred: {e}"

def extract_json(json_string_example):
    try:
        json_object = json.loads(json_string_example)
        return json_object
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return None

def remove_json_prefix(input_string):
    # Check if the string starts with "json" (case insensitive)
    if input_string.lower().startswith("json"):
        # Remove the "json" prefix
        result_string = input_string[len("json"):].lstrip()
        return result_string
    else:
        # If the string doesn't start with "json", return the original string
        return input_string


def get_model(api_key):
  genai.configure(api_key=api_key)

  # Set up the model
  generation_config = {
    "temperature": 0.9,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 2048,
  }

  safety_settings = [
    {
      "category": "HARM_CATEGORY_HARASSMENT",
      "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
      "category": "HARM_CATEGORY_HATE_SPEECH",
      "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
      "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
      "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
      "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
      "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
  ]

  model = genai.GenerativeModel(model_name="gemini-pro",
                                generation_config=generation_config,
                                safety_settings=safety_settings)
  return model

def get_json_objs_from_cleaned_response(cleaned_response):
  pattern = re.compile(r"=====([^=]+)=====")
  matches = pattern.findall(cleaned_response)
  json_objs = []
  for match in matches:
    json_string = match.strip()
    try:
      json_obj = json.loads(json_string)
      json_objs.append(json_obj)
    except json.JSONDecodeError as e:
      print(f"Error decoding JSON: {e}")

  return json_objs


def get_json_objs_from_response(responseText):
  responseText = responseText.replace('`', '')
  responseText = responseText.replace('```', '')
  responseText = responseText.replace('json', '')
  cleaned_response = responseText
  return get_json_objs_from_cleaned_response(cleaned_response)



def main():
    api_key = extract_json(read_file_as_string('../config.json'))['api_key']
    joi_object_schema_string = read_file_as_string('joi_schema_input.txt')

    #print(joi_object_schema_string)

    first_prompt_to_generate_json_example =  f"""{BASE_PROMPT}. Here is the joi object 
    ```
    {joi_object_schema_string}
    ```
    """ 

    model = get_model(api_key)
    first_prompt_parts = [first_prompt_to_generate_json_example]

    response = model.generate_content(first_prompt_parts)
    json_string_example = response.text.strip()
    json_string_example = json_string_example.replace('`', '')
    json_string_example = remove_json_prefix(json_string_example)

    next_prompt_to_generate_examples =  f"""{BASE_WITH_NEXT_PROMPT}. Here is the joi object 
    ```
    {joi_object_schema_string}
    ```

    And its corresponding output
    {json_string_example}
    """  

    prompt_parts = [next_prompt_to_generate_examples]
    json_objs = []
    for counter in range(4):
        try:
            response = model.generate_content(prompt_parts)
            responseText = response.text
            last_100_characters = responseText[-100]
            json_objs = json_objs + get_json_objs_from_response(responseText)
            next_prompt = next_prompt_to_generate_examples + last_100_characters + '''
            =====
            '''
            prompt_parts=[next_prompt]
        except Exception as e:
            return f"An error occurred: {e}"



    print(len(json_objs))
    for obj in json_objs:
        print(obj['testcase_description'])



if __name__ == "__main__":
    main()