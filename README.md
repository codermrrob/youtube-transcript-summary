# Local LLM Youtube Transcript Summary

A mini-project to start to work with a local LLM. My objective was simply to get completions via the api with some kind of tool. Just for the "done that" experience.

There is a lot of useful content on YouTube and some excellent content creators, but there is also a lot of extended waffle, some creators are a lot more verbose than others. I much prefer learning from written word, but I also know the effort to produce this is much greater and the rewards a lot less.

Spending 15+ mins of my time only to find out there was nothing useful for me in the video is frustrating. I thought it would be interesting to see if I could get a summary of the video content to see if it was worth watching. 

Plus it gives me a useful tool to interact with my local LLM API and get some experience.

## My Configuration

LLM Model : llama3-8b-instruct

Hardware : AMD Ryzen 7 5700G, 16Gb, RTX 3060 Ti (you could run llama3 with less, but I think this is about the practical minimum)

Model Runner : [Jan](https://jan.ai/) (I have also experimented with LMStudio, and a little with Ollama, Jan is still a work in progress with API completion still a bit lacking, but it is the slickest and easiest, and has a proper open source license).

## How to run

Create your virtual environment and install the requirements (`pip install -r requirements.txt`)


Nothing here is configurable, you will need to edit the code, but this is meant to be educational so if that's too much for you maybe you are in the wrong place.

Locate the class `ContentSummarizer` and the lines:

```python
self.client = OpenAI(base_url='http://localhost:1338/v1/',
                        # required but ignored
                        api_key='llama3-8b-instruct',
                    )
```
You will need to update the `base_url` to your local model, this is different depending what you are using to run your model. Running locally you can put anything into `api_key`. If your `base_url` points to a cloud hosted model use the `api_key` you get from the model provider.

And that's it you're ready to run one of :

`python yts.py -v <youtube-video-id>`

or

`python yts.py -v <youtube-video-url>`

the response is printed to the terminal and will look something like:

```text
Fetching metadata...
Fetching transcript...
Content length: 13215
Estimated num_tokens: 3303
Max tokens: 8192

# Suno's New AI Tool Turns Any Sound Into a Song
### AI For Humans


This is a transcript of a podcast episode discussing the topic of AI-generated music and audio editing. The hosts, Kevin and Gavin, discuss the capabilities of AI tools in music production and their potential impact on the music industry. They also explore the idea of using AI-generated audio as a creative tool, rather than a replacement for human artists.

Some key points from the transcript include:

* The hosts discuss the limitations of current AI-generated music tools, such as the need for human input and the lack of emotional connection.
* They also talk about the potential benefits of AI-generated music, such as increased accessibility and creativity.
* The hosts mention the concept of "audio fingerprinting" and its potential applications in music recognition and copyright protection.
* They also discuss the idea of using AI-generated audio as a creative tool, and how it could potentially empower human artists to create new and innovative music.

Overall, the transcript provides an interesting discussion on the topic of AI-generated music and its potential impact on the music industry.
```

I am making a token estimate on the input because llama3 has a max 8192 token limit. I don't want to hit that because results become unpredictable. My estimate is ridiculously simple and probably not very accurate, but it's better than nothing. I am assuming a 4 char average per token. This also allows you to reduce the context window if you want to. You will get better model performance with a smaller context.


Followed by title, author (channel) and the summary.

## Next Steps

This iteration is super simple. The next steps are to use code to configure & update an assistant for YouTube summaries. Deploy the transcript scraper and the metadata fetcher as tools for the assistant to use. Provide more detailed instructions and work on consistency and hallucination reduction.

This is not possible with the Jan model runner yet, the assistants API is still in development, so I will probably switch to something like llama3 on Groq. But I really like the idea of running my assistants locally and simple stuff like this is easily handled by the 8bn size of model.

Of course using a bigger model will improve things but so long as there is an open ai compatible API you can use this code with any model.
