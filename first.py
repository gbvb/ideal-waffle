import openai
import os

from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv());
openai.api_key = os.getenv('OPENAI_API_KEY');


def get_completion(prompt, model="gpt-3.5-turbo"):
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0
    )
    choices = response.choices[0].message.content
    return choices if choices else None



my_note= """
I have been listening to one of the early Hacking the org podcast with Charles Humble and Christian Idiodi. As usual, it is an excellent episode. The thing that stuck out to me was the difference between leading and managing. #podcast #prodmgmt\
Leading is about setting shared context and building a culture to solve problems. #leadership\
Managing is about acquiring, coaching and setting objectives for the team to achieve the goals for the business.\
This is an excellent way to think about it. Anyone can be a leader. Thanks to Pejman Milani for this beautiful image.\
"""

prompt = f"""
Proofread and correct the version of the text specified between three backticks. Describe the tone of the note in <tone>. And describe any hashtags i can add in <hashtags>
Review text: '''{my_note}'''
Corrected text: <corrected text>
tone: <tone>
hashtags: <hashtags>
"""
response = get_completion(prompt)
print(response)
