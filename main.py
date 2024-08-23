import yt_dlp
import glob, os
from moviepy.editor import VideoFileClip
import whisper
import pysrt
from datetime import timedelta
from googletrans import Translator
import subprocess
import argparse

def download_video(link:str)->str:
    ydl_opts_video = {
                'outtmpl': "_".join("%(id)s.%(ext)s".split()),
            }

    with yt_dlp.YoutubeDL(ydl_opts_video) as ydl:
        error_code = ydl.download(link)
        information=ydl.extract_info(link)
        name_audio=f"{information['id']}"
        final_name=name_audio+".mp4"
    
    return final_name

def extract_audio(video_file):
    video = VideoFileClip(video_file)
    audio = video.audio
    name_audio=video_file.split(".")[0]+".wav"
    audio.write_audiofile(name_audio)
    return name_audio

def format_time(seconds):
    td = timedelta(seconds=seconds)
    return "{:02}:{:02}:{:02},{:03}".format(
        td.seconds // 3600,
        (td.seconds // 60) % 60,
        td.seconds % 60,
        td.microseconds // 1000
    )

def transcribe_audio_to_srt(wav_file_path, srt_file_path, language='en'):
    # Load Whisper model
    model = whisper.load_model("small")

    # Transcribe audio
    result = model.transcribe(wav_file_path, language=language)

    # Create SRT file
    subs = pysrt.SubRipFile()
    for i, segment in enumerate(result['segments']):
        start = format_time(segment['start'])
        end = format_time(segment['end'])
        text = segment['text']

        sub = pysrt.SubRipItem(index=i+1, start=start, end=end, text=text)
        subs.append(sub)

    subs.save(srt_file_path, encoding='utf-8')

# def translate_text(text):
#     translation_answer=ollama.chat(model='llama3.1', messages=[{'role': 'user', 'content': f'Translate: {text}'}])
#     return translation_answer['message']['content']

def translate_subtitles(input_srt_path, output_srt_path, from_lang='en', to_lang='es', keep_both=False):
    # Read the SRT file
    subs = pysrt.open(input_srt_path)
    # ollama.chat(model='llama3.1', messages=[{'role': 'user', 
    #                                          'content': f'Translate all the \
    #                                             the following text presented in chunks from language {from_lang} \
    #                                                 to language {to_lang} taking into account the coherence of the whole text.\
    #                                                     After this message, answer only with the translation of the text.'}])
    # # Translate each subtitle

    # Initialize the translator
    translator = Translator()
    for sub in subs:
        translated_text = translator.translate(sub.text, src=from_lang, dest=to_lang).text
        if keep_both:
            sub.text = f"{sub.text}\n{translated_text}"
        else:
            sub.text = translated_text

    # Save the translated subtitles to a new SRT file
    subs.save(output_srt_path, encoding='utf-8')

    if keep_both:
        return from_lang+"-"+to_lang
    else:
        return to_lang

def add_subtitles_with_ffmpeg(video_path, srt_path, output_path, language='en'):
    # Define the ffmpeg command
    command = [
        'ffmpeg',
        '-i', video_path,
        '-vf', f"subtitles={srt_path}:charenc=UTF-8"+ (":force_style='FontName=SimHei,FontSize=6'"  if "zh-CN" in language else ""),
        '-c:a', 'copy',  # Copy audio without re-encoding
        output_path
    ]

    # Run the ffmpeg command
    subprocess.run(command, check=True)

def del_files(name_video):
    name_audio=name_video.split(".")[0]
    for f in glob.glob(f"{name_audio}.*"):
        os.remove(f)
    os.remove(f"trans_{name_audio}.srt")
    os.rename(f'last_{name_audio}.mp4', f'{name_audio}.mp4')

def main(link:str):
    name_video=download_video(link)
    name_audio=extract_audio(name_video)
    srt_file_path=name_audio.split(".")[0]+".srt"
    transcribe_audio_to_srt(name_audio, srt_file_path, language_origin)
    output_srt_path="trans_"+srt_file_path
    name_sub=translate_subtitles(srt_file_path, output_srt_path, language_origin, language_target, keep_both=keep_both)
    add_subtitles_with_ffmpeg(name_video, output_srt_path, "last_"+name_video, name_sub)
    del_files(name_video)

if __name__=="__main__":
    parser = argparse.ArgumentParser(description='Create a video with subtitles (possibly dual) from a link to a youtube video.')
    parser.add_argument('--link', required=True,
                        help='A youtube link in the format https://www.youtube.com/watch?v=00000000000')
    parser.add_argument('--origin', default="ru",
                        help='Language of the original video. Default: Russian.')
    parser.add_argument('--target', default="en",
                        help='Language of the target subtitles. Default: English')
    parser.add_argument('-b','--both', action="store_true",
                        help='Keep both languages in the subtitle.')

    args = parser.parse_args()
    youtube_link = args.link
    language_origin = args.origin
    language_target= args.target
    keep_both=args.both
    main(youtube_link)

    