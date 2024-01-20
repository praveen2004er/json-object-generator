import json
import google.generativeai as genai
import re

def remove_json_prefix(input_string):
    if input_string.lower().startswith("json"):
        result_string = input_string[len("json"):].lstrip()
        return result_string
    else:
        return input_string

def extract_json(json_string_example):
    try:
        json_object = json.loads(json_string_example)
        return json_object
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {json_string_example} {e}")
        return None

def get_model(api_key):
  genai.configure(api_key=api_key)

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


def read_file_as_string(file_path):
    try:
        with open(file_path, 'r') as file:
            file_contents = file.read()
            return file_contents
    except FileNotFoundError:
        return f"File not found: {file_path}"
    except Exception as e:
        return f"An error occurred: {e}"

BASE_PROMPT = '''
You are given a joi object schema, you need to create all possible test cases as possible. 
Generate only json. Add an additional attribute to the json called testcase_description and put a proper description there.
Delimit them with =====
When i type ===== give me one more possible testcase combinations



'''

EXAMPLE = '''

here is an example

```
=====
{}
=====
```

'''

def get_json_objs_from_response(response):
  pattern = re.compile(r"=====([^=]+)=====")
  matches = pattern.findall(response)
  json_objs = []
  for match in matches:
    json_string = match.strip()
    try:
      json_obj = json.loads(json_string)
      json_objs.append(json_obj)
    except json.JSONDecodeError as e:
      print(f"Error decoding JSON: {json_string} {e}")

  return json_objs

def generate_json_objects(api_key, joi_object_schema_string, num_of_testcases):
    model = get_model(api_key)

    prompt_to_send =  f"""{BASE_PROMPT}. Here is the joi object 
    ```
    {joi_object_schema_string}
    ```
    """ + EXAMPLE
    prompt_parts = [prompt_to_send]

    json_objs = []
    for counter in range(num_of_testcases):
        try:
            response = model.generate_content(prompt_parts)
            responseText = response.text.strip()
            last_100_characters = responseText[-100]
            responseText = responseText.replace('```', '')
            responseText = remove_json_prefix(responseText)
            json_objs = json_objs + get_json_objs_from_response(responseText)
            next_prompt = prompt_to_send + last_100_characters + '''
=====
            '''
            prompt_parts=[next_prompt]
        except Exception as e:
            return f"An error occurred: {e}"

    return json_objs

def generate_dict_testcase_description_to_json(api_key, joi_object_schema_string, num_of_testcases):
    json_objs = generate_json_objects(api_key, joi_object_schema_string, num_of_testcases)
    description_to_json = {}

    for obj in json_objs:
        description = obj["testcase_description"]
        obj.pop("testcase_description")
        description_to_json[description] = obj
    
    return description_to_json


def main():
    api_key = extract_json(read_file_as_string('config.json'))['api_key']
    joi_object_schema_string = read_file_as_string('joi_schema_input.txt')

    description_to_json_dict = generate_dict_testcase_description_to_json(api_key, joi_object_schema_string, 1)
    print(description_to_json_dict)

if __name__ == "__main__":
    main()