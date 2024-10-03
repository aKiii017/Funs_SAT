from openai import OpenAI
client = OpenAI(
    # This is the default and can be omitted
    base_url="https://api.f2gpt.com/v1",
    api_key="sk-f27nghhUpWfx5ULqL5MNmPmZhZxkRGkkoPbHLis30bCJ0U4z",
)

completion = client.chat.completions.create(
  model="gpt-4o",
  messages=[
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello!"}
  ]
)

print(completion.choices[0].message.content)
