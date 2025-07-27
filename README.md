# Interactive-Recipe-Finder
The Interactive Recipe Finder is an AI-powered cooking assistant built with Python and Streamlit, designed to help users discover and follow recipes. It integrates several APIs for a rich user experience.

Users can search for recipes by text query, which uses the Spoonacular API to retrieve detailed recipes, ingredients, and instructions. A Google Generative AI chatbot provides step-by-step cooking instructions and answers culinary questions.

For convenience, users can upload images of ingredients or dishes. The Google Cloud Vision API analyzes these images to identify items and suggest relevant recipes, simplifying cooking with available ingredients. Voice search is also supported via the speech_recognition library, allowing hands-free recipe discovery.

To cater to a global audience, the app uses the Google Translate API for multi-language translation of recipe content. Instructions can also be converted to audio using gTTS and played with pygame for hands-free listening while cooking.

The platform also provides related YouTube recipe videos through the YouTube Data API. All recipe data is stored in MongoDB, enabling users to save and revisit recipes.

To run the project, users need Python 3.x and API keys for Spoonacular, Google Generative AI, Google Cloud Vision, Google Translate, YouTube Data API, and a MongoDB URI. This project demonstrates how AI, computer vision, and voice technology can create an intelligent, accessible, and interactive recipe platform.







