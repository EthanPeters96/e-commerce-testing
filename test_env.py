import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Print the environment variables
print("Environment Variables Test:")
print(f"STRIPE_PUBLISHABLE_KEY: {os.getenv('STRIPE_PUBLISHABLE_KEY')}")
print(f"STRIPE_SECRET_KEY: {os.getenv('STRIPE_SECRET_KEY')}")
print(f"STRIPE_WEBHOOK_SECRET: {os.getenv('STRIPE_WEBHOOK_SECRET')}") 