from openai import OpenAI
from openai import AzureOpenAI
openai_api_key = "f825f61246354ec090c5703ca4f76418"
openai_api_base = "https://midivi-main-scu1.openai.azure.com/"
client = AzureOpenAI(
  api_key = openai_api_key,  
  api_version = "2024-02-01",
  azure_endpoint = openai_api_base
)
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "Hello"},
    ],
    stream=False
)
print(response.choices[0].message.content)