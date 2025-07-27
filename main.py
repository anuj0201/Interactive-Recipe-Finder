import base64
import streamlit as st
import requests
import speech_recognition as sr
import google.generativeai as genai
from gtts import gTTS
import pygame
import time
import os
import pymongo

# Configuration
#get all those api key access first

# Initialize pygame for audio playback
pygame.mixer.init()

# Connect to MongoDB Atlas
client = pymongo.MongoClient(MONGO_URI)
db = client.get_database('users')
recipes_collection = db.get_collection('recipes')

def insert_recipe_to_db(recipe_data):
    try:
        recipes_collection.insert_one(recipe_data)
        st.success("Recipe added to database successfully!")
    except Exception as e:
        st.error(f"Failed to insert recipe into database: {e}")

def configure_generative_api():
    genai.configure(api_key=GENERATIVE_API_KEY)

def query_generative_api(prompt):
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Failed to connect to the Generative API: {e}")
    return None

def fetch_recipes(query):
    response = requests.get(
        "https://api.spoonacular.com/recipes/complexSearch",
        params={
            "query": query,
            "apiKey": SPOONACULAR_API_KEY,
            "addRecipeInformation": True,
            "number": 5,
        },
    )
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Spoonacular API Error: {response.status_code}")
        return None

def fetch_recipe_details(recipe_id):
    response = requests.get(
        f"https://api.spoonacular.com/recipes/{recipe_id}/information",
        params={"apiKey": SPOONACULAR_API_KEY},
    )
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Failed to fetch recipe details: {response.status_code}")
        return None

def fetch_youtube_video(query):
    youtube_url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "maxResults": 1,
        "q": f"{query} recipe",
        "key": YOUTUBE_API_KEY,
    }
    response = requests.get(youtube_url, params=params)
    if response.status_code == 200:
        items = response.json().get("items", [])
        if items:
            video_id = items[0]["id"].get("videoId")
            return f"https://www.youtube.com/watch?v={video_id}"
    else:
        st.error(f"YouTube API Error: {response.status_code}")
    return None

def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("Listening... Speak now!")
        try:
            audio = recognizer.listen(source, timeout=5)
            text = recognizer.recognize_google(audio)
            return text
        except sr.UnknownValueError:
            st.error("Could not understand audio.")
        except sr.RequestError as e:
            st.error(f"Speech recognition error: {e}")
    return None

def translate_text(text, target_language):
    url = f"https://translation.googleapis.com/language/translate/v2"
    params = {
        "q": text,
        "target": target_language,
        "key": TRANSLATE_API_KEY,
    }
    try:
        response = requests.post(url, data=params)
        if response.status_code == 200:
            result = response.json()
            return result['data']['translations'][0]['translatedText']
        else:
            st.error(f"Translation API Error: {response.status_code}")
    except Exception as e:
        st.error(f"Failed to connect to the Translation API: {e}")
    return text

def text_to_speech(text):
    try:
        unique_filename = f"response_{int(time.time())}.mp3"
        tts = gTTS(text=text, lang="en")
        tts.save(unique_filename)
        pygame.mixer.music.load(unique_filename)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            continue
        os.remove(unique_filename)
    except Exception as e:
        st.error(f"Error in Text-to-Speech: {e}")

def analyze_image(image):
    # First, use the Vision API to get labels from the image
    vision_url = f"https://vision.googleapis.com/v1/images:annotate?key={VISION_API_KEY}"
    image_bytes = image.read()
    image_base64 = base64.b64encode(image_bytes).decode("utf-8")
    headers = {"Content-Type": "application/json"}
    data = {
        "requests": [
            {
                "image": {"content": image_base64},
                "features": [{"type": "LABEL_DETECTION", "maxResults": 10}],
            }
        ]
    }
    response = requests.post(vision_url, json=data, headers=headers)
    if response.status_code == 200:
        annotations = response.json()
        labels = [label["description"] for label in annotations["responses"][0]["labelAnnotations"]]
        # Combine the labels into a single string to form a prompt for the Generative API
        labels_str = ', '.join(labels)
        prompt = f"Describe the contents of an image that contains: {labels_str}. Be detailed about the food, ingredients, and possible recipes."
        ai_description = query_generative_api(prompt)
        if ai_description:
            return ai_description
    else:
        st.error(f"Vision API Error: {response.status_code}")
        return None

# Default language
language = 'en'

# Language selection
language_map = {
   'English': 'en',
    'Spanish': 'es',
    'French': 'fr',
    'German': 'de',
    'Italian': 'it',
    'Portuguese': 'pt',
    'Russian': 'ru',
    'Japanese': 'ja',
    'Korean': 'ko',
    'Chinese (Simplified)': 'zh-CN',
    'Chinese (Traditional)': 'zh-TW',
    'Hindi': 'hi',
    'Arabic': 'ar',
    'Bengali': 'bn',
    'Urdu': 'ur',
    'Malay': 'ms',
    'Swahili': 'sw',
    'Dutch': 'nl',
    'Greek': 'el',
    'Hebrew': 'he',
    'Turkish': 'tr',
    'Vietnamese': 'vi',
    'Thai': 'th',
    'Polish': 'pl',
    'Ukrainian': 'uk',
    'Czech': 'cs',
    'Hungarian': 'hu',
    'Finnish': 'fi',
    'Swedish': 'sv',
    'Norwegian': 'no',
    'Danish': 'da',
    'Icelandic': 'is',
    'Romanian': 'ro',
    'Bulgarian': 'bg',
    'Serbian': 'sr',
    'Croatian': 'hr',
    'Slovak': 'sk',
    'Slovenian': 'sl',
    'Lithuanian': 'lt',
    'Latvian': 'lv',
    'Estonian': 'et',
    'Filipino': 'tl',
    'Tamil': 'ta',
    'Telugu': 'te',
    'Kannada': 'kn',
    'Malayalam': 'ml',
    'Marathi': 'mr',
    'Punjabi': 'pa',
    'Gujarati': 'gu',
    'Sinhala': 'si',
    'Burmese': 'my',
    'Khmer': 'km',
    'Lao': 'lo',
    'Pashto': 'ps',
    'Persian': 'fa',
    'Amharic': 'am',
    'Hausa': 'ha',
    'Igbo': 'ig',
    'Yoruba': 'yo',
    'Zulu': 'zu',
    'Xhosa': 'xh',
    'Shona': 'sn',
    'Sesotho': 'st',
    'Afrikaans': 'af',
    'Maori': 'mi',
    'Samoan': 'sm',
    'Tongan': 'to',
    'Fijian': 'fj',
    'Hawaiian': 'haw',
    'Mongolian': 'mn',
    'Kazakh': 'kk',
    'Uzbek': 'uz',
    'Kyrgyz': 'ky',
    'Tajik': 'tg',
    'Georgian': 'ka',
    'Armenian': 'hy',
    'Azerbaijani': 'az',
    'Basque': 'eu',
    'Catalan': 'ca',
    'Galician': 'gl',
    'Welsh': 'cy',
    'Irish': 'ga',
    'Scottish Gaelic': 'gd',
    'Breton': 'br',
    'Cornish': 'kw',
    'Luxembourgish': 'lb',
    'Maltese': 'mt',
    'Esperanto': 'eo',
    'Albanian': 'sq',
    'Bosnian': 'bs',
    'Macedonian': 'mk',
    'Montenegrin': 'cnr',
    'Sanskrit': 'sa',
    'Tibetan': 'bo',
    'Nepali': 'ne',
    'Macedonian': 'mk',
}

available_languages = list(language_map.keys())
language_name = st.sidebar.selectbox("", available_languages)
language = language_map[language_name]

# Streamlit UI
st.title(translate_text("Interactive Recipe Finder", language))
st.sidebar.title(translate_text("Navigation", language))
choice = st.sidebar.radio(translate_text("Go to", language), [translate_text("Recipe Finder", language), translate_text("AI Chatbot", language), translate_text("Image Detection", language), translate_text("Voice Search", language)])

configure_generative_api()

if choice == translate_text("Voice Search", language):
    st.header(translate_text("Voice Search", language))
    if st.button(translate_text("Start Voice Search", language), key="voice_search_button"):
        recognized_text = recognize_speech()
        if recognized_text:
            st.write(translate_text(f"You said: {recognized_text}", language))
            ai_response = query_generative_api(recognized_text)
            if ai_response:
                translated_response = translate_text(ai_response, language)
                st.subheader(translate_text("Generated Recipe Instructions and Ingredients:", language))
                st.write(translated_response)
                text_to_speech(translated_response)

elif choice == translate_text("Recipe Finder", language):
    st.header(translate_text("Recipe Finder", language))
    query = st.text_input(translate_text("Enter a dish name:", language))
    if st.button(translate_text("Search", language), key="recipe_search_button"):
        recipes = fetch_recipes(query)
        if recipes and recipes.get("results"):
            for recipe in recipes["results"]:
                recipe_details = fetch_recipe_details(recipe["id"])
                if recipe_details:
                    translated_title = translate_text(recipe_details["title"], language)
                    st.subheader(translated_title)
                    st.image(recipe_details["image"], caption=translated_title, use_container_width=True)
                    st.write(translate_text(f"Ready in {recipe_details['readyInMinutes']} minutes", language))
                    st.write(translate_text("Ingredients:", language))
                    for ingredient in recipe_details.get("extendedIngredients", []):
                        translated_ingredient = translate_text(ingredient['original'], language)
                        st.write(f"- {translated_ingredient}")
                    instructions = recipe_details.get("instructions", "Instructions not available.")
                    translated_instructions = translate_text(instructions, language)
                    st.write(f"{translate_text('Instructions:', language)} {translated_instructions}")
                    video_url = fetch_youtube_video(recipe_details["title"])
                    if video_url:
                        st.video(video_url)
                    st.write("\n")
                    if st.button(translate_text("Save Recipe", language), key=f"save_recipe_{recipe['id']}"):
                        insert_recipe_to_db(recipe_details)

elif choice == translate_text("Image Detection", language):
    st.header(translate_text("Image Detection", language))
    uploaded_image = st.file_uploader(translate_text("Upload an image", language), type=["jpg", "jpeg", "png"])
    if uploaded_image:
        ai_description = analyze_image(uploaded_image)
        if ai_description:
            st.subheader(translate_text("AI Generated Description", language))
            st.write(ai_description)

elif choice == translate_text("AI Chatbot", language):
    st.header(translate_text("AI Chatbot", language))
    prompt = st.text_input(translate_text("Ask a question", language))
    if st.button(translate_text("Get Response", language), key="chatbot_response_button"):
        ai_response = query_generative_api(prompt)
        if ai_response:
            translated_response = translate_text(ai_response, language)
            st.write(translated_response)
