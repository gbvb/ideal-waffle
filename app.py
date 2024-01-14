import tornado.ioloop
import tornado.web
import requests
import openai
import os
from bs4 import BeautifulSoup
import nltk
nltk.download('punkt')
nltk.download('stopwords')
from nltk.tokenize import word_tokenize

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

def get_legacy_completion(prompt, model="text-davinci-003"):
    response = openai.Completion.create(
        model=model,
        prompt=prompt,
        temperature=0,
        max_tokens=1000,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    choices = response.choices[0].text
    return choices if choices else None


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello World")

class TopStoriesHandler(tornado.web.RequestHandler):
    def get(self):
        top_stories = get_top_stories()
        self.write("Top Stories: {}".format(top_stories))

class TopStoriesHTMLHandler(tornado.web.RequestHandler):
    def get(self):
        top_stories = get_top_stories()
        html = generate_html_divs(top_stories, self)
        self.write(html)

class TopNewsHTMLHandler(tornado.web.RequestHandler):
    def get(self):
        with open('topnews.html', 'r') as f:
            html = f.read()
        self.write(html)

class BestStoriesHTMLHandler(tornado.web.RequestHandler):
    def get(self):
        best_stories = get_best_stories()
        html = generate_html_divs(best_stories,self)
        self.write(html)

class SummarizeHandler(tornado.web.RequestHandler):
    def get(self):
        url = self.get_argument('url', None)
        if url is None:
            self.write("""
                <form method="get">
                    <label for="url">Enter a URL:</label><br>
                    <input type="text" id="url" name="url"><br>
                    <input type="submit" value="Submit">
                </form>
            """)
        else:
            summary = summarize(url)
            self.write(summary)

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/topstories", TopStoriesHandler),
        (r"/topstorieshtml", TopStoriesHTMLHandler),
        (r"/topnews", TopNewsHTMLHandler),
        (r"/beststorieshtml", BestStoriesHTMLHandler),
        (r"/summary", SummarizeHandler),
    ])

# Caching the top stories
top_stories = None


# define a function to retrieve top stories from Hacker News
def get_top_stories():
    """
    Retrieves the top 10 stories from Hacker News API and returns their details.

    Returns:
        list: A list of dictionaries containing the details of the top 10 stories.
    """
    import requests
    import json
    # retrieve top 10 stories
    top_stories = requests.get("https://hacker-news.firebaseio.com/v0/topstories.json?print=pretty").json()[:10]
    # retrieve top 10 stories' details
    top_stories_details = [requests.get("https://hacker-news.firebaseio.com/v0/item/{}.json?print=pretty".format(id)).json() for id in top_stories]
    # return top 10 stories' details
    return top_stories_details

def get_best_stories():
    best_stories = requests.get("https://hacker-news.firebaseio.com/v0/beststories.json?print=pretty").json()[:10]
    best_stories_details = [requests.get("https://hacker-news.firebaseio.com/v0/item/{}.json?print=pretty".format(id)).json() for id in best_stories]
    return best_stories_details

def summarize(url):
    """
    Summarizes the article at the given URL.

    Args:
        url (str): The URL of the article to be summarized.

    Returns:
        str: The summary of the article.
    """
    # retrieve the article
    article = requests.get(url).text
    # parse the article
    article_parsed = BeautifulSoup(article, 'html.parser')
    text = article_parsed.get_text()
    tokens = word_tokenize(text)
    tokens = tokens[:1000]
    text = ' '.join(tokens)
    summarized_genai = get_completion("Summarize the following text: " + text)
    #summarized_genai = get_legacy_completion("Summarize the following text: " + text)
    print(summarized_genai)

    return summarized_genai

def generate_a_html_div(story):
    html = ''

    url = story.get('url')
    title = story.get('title')
    by = story.get('by')

    if url and title and by:
        html += '<div class="card">\n'
        html += '<h2>{}</h2>\n'.format(title)
        html += '<h3><i>By: {}</i></h3>\n'.format(by)
#        html += '<p>{}</p>\n'.format(summary)
        html += '<a href="#" onclick=showSummary("{}")>Show summary</a>\n'.format(url)
        html += '<a href="{}">Read more</a>\n'.format(url)
        html += '</div>\n'

    return html


def generate_html_divs(top_stories, response):
    html = ''

    for index, story in enumerate(top_stories):
        url = story.get('url')
        title = story.get('title')
        by = story.get('by')
        id = story.get('id')

        if url and title and by:
            html += '<div class="card">\n'
            html += '<h2>{}</h2>\n'.format(title)
            html += '<a href="{}">Read more</a>\n'.format(url)
            html += '<h3>By: {}</h3>\n'.format(by)
            html += '<div id="summary-{}" style="display:block;">\n'.format(id)
            html += '<a href="#" onclick=showSummary("{}","summary-{}")>Show summary</a>  \n'.format(url,id)
            html += '</div>\n'
    return  html
# Sample response from Hacker News API
# {
#   "by" : "dhouston",
#   "descendants" : 71,
#   "id" : 8863,
#   "kids" : [ 8952, 9224, 8917, 8884, 8887, 8943, 8869, 8958, 9005, 9671, 8940, 9067, 8908, 9055, 8865, 8881, 8872, 8873, 8955, 10403, 8903, 8928, 9125, 8998, 8901, 8902, 8907, 8894, 8878, 8870, 8980, 8934, 8876 ],
#   "score" : 111,
#   "time" : 1175714200,
#   "title" : "My YC app: Dropbox - Throw away your USB drive",
#   "type" : "story",
#   "url" : "http://www.getdropbox.com/u/2/screencast.html"
# 
# }


if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()