from openai import OpenAI
import os
from dotenv import load_dotenv
import yaml

def load_config():
    load_dotenv()
    config = {}
    config['threads_username'] = os.getenv("INSTAGRAM_USERNAME")
    config['threads_password'] = os.getenv("INSTAGRAM_PASSWORD")
    config['openai_api_key']   = os.getenv("OPENAI_API_KEY")
    if not config['openai_api_key']:
        raise Exception("Missing OPENAI_API_KEY in .env")
    # Instantiate the Responses API client
    config['openai_client'] = OpenAI(api_key=config['openai_api_key'])
    # Load ethical policy
    policy_file = os.getenv("ETHICAL_POLICY_FILE", "ethical_policy.yaml")
    with open(policy_file, 'r') as f:
        config['policy'] = yaml.safe_load(f)
    return config
