import openai

openai.api_key = 'OPENAI_API_KEY'

def generate_response(prompt, model='gpt-3.5-turbo'):
    response = openai.Completion.create(
        engine=model,
        prompt=prompt,
        max_tokens=150
    )
    return response.choices[0].text.strip()
