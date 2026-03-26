import os
import json
from openai import OpenAI
from config import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)

# All OpenAI API calls go here — never call from routers or templates.
# Implemented in Week 2 & 3.
