import os
from google.cloud import texttospeech

# Load credentials explicitly ideally, or rely on GOOGLE_APPLICATION_CREDENTIALS
# We will use the file path 'credentials.json' already in backend/
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "credentials.json"

client = texttospeech.TextToSpeechClient()

def get_google_tts(text: str, language_code: str = "en-US") -> bytes:
    """
    Synthesize speech using Google Cloud TTS.
    Returns: Bytes of MP3 audio
    """
    
    # Map friendly locale to Google Voice names
    # See: https://cloud.google.com/text-to-speech/docs/voices
    voice_map = {
        "hi-IN": {"name": "hi-IN-Neural2-A", "ssml_gender": texttospeech.SsmlVoiceGender.FEMALE},
        "te-IN": {"name": "te-IN-Standard-A", "ssml_gender": texttospeech.SsmlVoiceGender.FEMALE},
        "kn-IN": {"name": "kn-IN-Standard-A", "ssml_gender": texttospeech.SsmlVoiceGender.FEMALE},
        "en-IN": {"name": "en-IN-Neural2-A", "ssml_gender": texttospeech.SsmlVoiceGender.FEMALE},
        "en-US": {"name": "en-US-Neural2-F", "ssml_gender": texttospeech.SsmlVoiceGender.FEMALE},
    }
    
    # Default to en-US if not found
    config = voice_map.get(language_code, voice_map["en-US"])

    input_text = texttospeech.SynthesisInput(text=text)

    voice = texttospeech.VoiceSelectionParams(
        language_code=language_code,
        name=config["name"],
        ssml_gender=config["ssml_gender"]
    )

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    response = client.synthesize_speech(
        request={"input": input_text, "voice": voice, "audio_config": audio_config}
    )

    return response.audio_content
