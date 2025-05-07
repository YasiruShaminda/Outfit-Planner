# AI Personal Stylist Assistant

A customizable personal stylist application that generates outfit recommendations based on your own clothes. This application allows you to upload your personal wardrobe items and create personalized outfit combinations based on your body shape, skin tone, and style preferences.

## Features

- **Personal Style Profile**: Upload a photo of yourself to analyze your body shape, skin tone, and get personalized style recommendations
- **Digital Wardrobe**: Upload and categorize your clothing items (tops, bottoms, dresses, shoes, accessories)
- **Outfit Generation**: Generate stylish outfit combinations using only your own wardrobe items
- **Outfit History**: Save your favorite outfit combinations
- **User-friendly Interface**: Clean and intuitive web interface for easy navigation

## Installation

### Prerequisites

- Python 3.8+
- A Gemini API key (from Google AI Studio)

### Setup

1. Clone this repository:
```
git clone https://github.com/yourusername/ai-personal-stylist.git
cd ai-personal-stylist
```

2. Install required packages:
```
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory and add your Gemini API key:
```
GEMINI_API_KEY=your_api_key_here
```

## Usage

1. Run the Streamlit app:
```
streamlit run app.py
```

2. Open your web browser and navigate to the URL displayed in the terminal (usually http://localhost:8501)

3. Use the application:
   - **Create Profile**: Upload a photo of yourself to generate style recommendations
   - **Manage Wardrobe**: Upload and categorize your clothing items
   - **Generate Outfits**: Create outfit combinations based on your profile and wardrobe

## How It Works

1. **Style Profile Creation**:
   - The app uses Google's Gemini AI to analyze your body shape and skin tone
   - It generates personalized color and style recommendations

2. **Wardrobe Management**:
   - Upload images of your clothing items
   - The AI analyzes each item for type, color, pattern, and suitable occasions
   - Items are organized in your digital wardrobe by category

3. **Outfit Generation**:
   - The AI creates outfit combinations based on your profile and available wardrobe items
   - It considers color harmony, style compatibility, and occasion suitability
   - You can save favorite outfits and get new recommendations

## Privacy

- All images and data are stored locally on your device
- Your personal information is not shared with any third parties

## Customization

You can customize the application by:

1. Adding more clothing categories in the `st.session_state.wardrobe_items` dictionary
2. Modifying the UI by editing the CSS in the `st.markdown` section
3. Enhancing the AI prompts in the `analyze_image`, `analyze_clothing`, and `generate_outfits` functions

## Requirements

See `requirements.txt` for the complete list of dependencies.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 