# json-object-generator
Given a joi object schema generate all possible json objects.

Note: This won't generate all possible json objects perfectly, however this will really help in generating combinations so that we can choose which ones we need and which ones we don't.

# Setup
`pip install google-generativeai`

## Create API Key and update config
You can create an API key from Google AI studio and use it here. Put it in the config.json. 

# Update Joi schema file
Update joi_schema_input.txt with the fully resolvable schema.

# Run the program
`python main.py`

Modify the number of testcases as per your need in main.py.

## Sample output
Ouput is a dict where the key is the description and the value is the json object dict.

{'Valid person object with all required fields': ```{'firstName': 'John', 'lastName': 'Doe', 'age': 25, 'email': 'johndoe@example.com', 'address': {'street': '123 Main Street', 'city': 'Springfield', 'zipCode': '12345'}, 'phone': '123-456-7890', 'isAdmin': False, 'hobbies': ['running', 'hiking', 'camping'], 'isActive': True, 'createdAt': '2023-03-08T18:30:00.000Z'}```}

