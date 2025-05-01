# Overview
This automated system leverages OpenAI's ChatGPT to intelligently create posts to Meta's Thread. Each agent has a dedicated task to complete to achieve a high quality post based on the topic specified in the prompt

## Requirements
To accomplish the full end-to-end operation, the following are required:
1. Threads account (can login via Instagram)
2. OpenAI account (to obtain API key)
3. Python3
4. PyCharm (recommeneded)
5. pip install

## Setup
1. Clone the repository
2. Obtain the API key from the OpenAI account
3. Create a .env file in the root of the cloned directory
4. Edit the .env file to include the following: </br>
```
  OPENAI_API_KEY=[your api key] 
  INSTAGRAM_USERNAME=[your username] 
  INSTAGRAM_PASSWORD=[your password]
  ETHICS_THRESHOLD=0.7 
  MAX_POST_LENGTH=280  
```
5. From either the Terminal or PyCharm, install the required dependencies via:
   ```
   pip install -r requirements.txt
   ```
   
## Running the script
### From the Terminal
1. CD to the project folder in the Terminal
2. While in the Terminal, enter:
   ```
   python3 main.py
   ```
### From PyCharm
Run main.py from either the project structure or htting the play button
