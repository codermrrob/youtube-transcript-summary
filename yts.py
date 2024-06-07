import argparse
import requests
from openai import OpenAI
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter, PrettyPrintFormatter, SRTFormatter

class YouTubeMetadata:
    @staticmethod
    def get_video_metadata(video_url):
        oembed_url = f"https://www.youtube.com/oembed?url={video_url}&format=json"

        print(f"Fetching metadata...")
        metadata = {}
        try:
            response = requests.get(oembed_url)
            response.raise_for_status()
            json_data = response.json()
            
            metadata['Title'] = json_data.get('title', 'No title available')
            metadata['Author'] = json_data.get('author_name', 'No author available')
            metadata['Channel'] = json_data.get('author_url', 'No channel available')
        except requests.exceptions.RequestException as e:
            print(f"Error  : failed to fetch meta data: {str(e)}")
            print(f"Code   : {response.status_code}")
            print(f"Reason : {response.reason}")
            print(f"Message: {response.text}")
            print()
        return metadata


class YouTubeTranscript:
    def __init__(self, video_id, languages=['en'], preserve_formatting=True):
        self.video_id = video_id
        self.languages = languages
        self.preserve_formatting = preserve_formatting

    def get_transcript(self):
        print(f"Fetching transcript...")
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(self.video_id)
            transcript = transcript_list.find_transcript(self.languages)
            if self.preserve_formatting:
                transcript = transcript.fetch()
            else:
                transcript = transcript.fetch(remove_formatting=True)
            formatter = TextFormatter()
            formatted_transcript = formatter.format_transcript(transcript)
            return formatted_transcript
        except Exception as e:
            return str(e)


class MarkdownGenerator:
    def create_markdown(self, title, metadata, transcript):
        # Create Markdown content
        markdown_content = f"# {title}\n\n"
        markdown_content += "## Video Metadata\n\n"
        markdown_content += f"**Title:** {metadata.get('Title', 'No title available')}\n\n"
        markdown_content += f"**Author:** {metadata.get('Author', 'No author available')}\n\n"
        markdown_content += f"**Channel:** {metadata.get('Channel', 'No channel available')}\n\n"
        markdown_content += "## Transcript\n\n"
        markdown_content += transcript + "\n"
        return markdown_content



class ContentSummarizer:
    def __init__(self, max_tokens=8192, chars_per_token=4):
        self.max_tokens = max_tokens
        self.chars_per_token = chars_per_token
        
        self.client = OpenAI(base_url='http://localhost:1338/v1/',
                             # required but ignored
                             api_key='llama3-8b-instruct',
                            )

    def summarize_content(self, metadata, content):
        num_tokens = len(content) // self.chars_per_token
        print(f"Content length: {len(content)}")
        print(f"Estimated num_tokens: {num_tokens}")
        print(f"Max tokens: {self.max_tokens}")

        if self.max_tokens < num_tokens:
            print(f"Estimated num_tokens: {num_tokens} exceeds the limit of {self.max_tokens}. This might result in an error or hallucinations.")
            print()
            response = input("Should I truncate the content to the maximum token length? (Y/N): ")
            if response.lower() == 'y':
                content = content[:((self.max_tokens - 1) * self.chars_per_token)]
                print(f"Content truncated to {len(content)}.")
            else:
                print("Operation aborted. Exiting.")
                exit()
        

        print("")
        print(f"# {metadata['Title']}")
        print(f"### {metadata['Author']}")
        print()
        self.stream_summary(content)


    def stream_summary(self, content):
        
        print("")
        prompt = ("Summarize the following text, make sure to include key bullet points, and at the end a sentiment analysis and some commentary (not opinion): " + content)
        
        streamClient  = self.client.chat.completions.create(
            messages=[
                {
                "content": """You are a literary analyst. You will be provided transcripts, articles, news, stories, etc.
                                You will summarize them to capture the essence of the content, keeping the summary concise and informative.
                                You will not alter the sentiment or facts of the content. You will not provide your opinion or analysis.
                                Always highlight key points, sections or features using bullet points.
                                IMPORTANT : Make sure your summary is formatted with line length of 80 characters.
                                Include a sentiment analysis at the end of every summary.""",
                "role": "system"
                },
                {
                "content": prompt,
                "role": "user"
                }
            ],
            stop= ["<|eot_id|>", "<|end_of_text|>", "<|im_end|>"],
            #model='Llama-3-8B-Instruct-Gradient-1048k-Q6_K.gguf',
            model='llama3-8b-instruct',
            temperature = 0.7,
            top_p = 0.95,
            stream = True
        )

        for chunk in streamClient:
            if chunk.choices[0].delta.content is not None:
                print(chunk.choices[0].delta.content, end="")


def main():
    parser = argparse.ArgumentParser(description="Fetch YouTube video transcript and metadata")
    parser.add_argument('-v', '--video', required=True, help="YouTube video URL or ID")
    args = parser.parse_args()

    # Ensure the video_id is correctly extracted
    if "youtube.com" in args.video or "youtu.be" in args.video:
        video_id = args.video.split("v=")[-1].split("&")[0] if "youtube.com" in args.video else args.video.split("/")[-1]
    else:
        video_id = args.video
        
    video_url = f"https://www.youtube.com/watch?v={video_id}"

    metadata_fetcher = YouTubeMetadata()
    metadata = metadata_fetcher.get_video_metadata(video_url)

    transcript_fetcher = YouTubeTranscript(video_id, languages=["en"])
    transcript = transcript_fetcher.get_transcript()

    markdown_generator = MarkdownGenerator()
    content = markdown_generator.create_markdown(metadata['Title'], metadata, transcript)

    summarizer = ContentSummarizer()
    summarizer.summarize_content(metadata, content) 

if __name__ == "__main__":
    main()
