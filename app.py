import streamlit as st
import os
import json
import time
import numpy as np
from PIL import Image
import google.generativeai as genai
#from google import genai
#from google.genai import models
#from google.genai import types
from sklearn.neighbors import NearestNeighbors
from dotenv import load_dotenv
import uuid
import utils  # Import the utility functions

# Load environment variables
load_dotenv()

# Configure page
st.set_page_config(
    page_title="AI Personal Stylist",
    page_icon="👗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state with persisted data
if 'wardrobe_items' not in st.session_state:
    st.session_state.wardrobe_items = utils.load_wardrobe()
    
if 'profile' not in st.session_state:
    st.session_state.profile = utils.load_profile()
    
if 'recommended_outfits' not in st.session_state:
    st.session_state.recommended_outfits = []
    
if 'outfit_history' not in st.session_state:
    st.session_state.outfit_history = utils.load_outfits()

# Function to get API key
def get_api_key():
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        return api_key
    else:
        return st.session_state.get("api_key", "")

# Function to initialize Gemini
def initialize_gemini():
    api_key = get_api_key()
    if api_key:
        genai.configure(api_key=api_key)
        return True
    return False

# Function to create embeddings
def embed_text(text):
    """Get embedding using Google's embedding model"""
    try:
        result = genai.embed_content(
            model="models/embedding-001",
            content=text,
            task_type="retrieval_document",
        )
        return np.array(result["embedding"])
    except Exception as e:
        st.error(f"Error creating embedding: {e}")
        return None

# Function to analyze an image
def analyze_image(image):
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = [
            image,
            '''Analyze the person's figure and skin tone. Return in this JSON format:
            {
              "body_shape": "", 
              "skin_tone": "",
              "recommended_colors": [],
              "avoid_styles": [],
              "notes": ""
            }'''
        ]
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Error analyzing image: {e}")
        return None

# Function to analyze clothing item
def analyze_clothing(image):
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = [
            image,
            '''Analyze this clothing item and return in this JSON format:
            {
              "type": "", 
              "color": "",
              "pattern": "",
              "style": "",
              "occasions": []
            }'''
        ]
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Error analyzing clothing: {e}")
        return None

# Function to analyze location image
def analyze_location(image):
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = [
            image,
            '''Analyze this location and return in this JSON format:
            {
              "location_type": "",
              "environment": "",
              "weather_indication": "",
              "dress_code_suggestion": "",
              "notable_features": [],
              "recommended_style_elements": []
            }'''
        ]
        response = model.generate_content(prompt)
        #response = client.models.generate_content(model="gemini-1.5-flash", contents=prompt)
        response_text = response.text
        cleaned_response = response_text
        if "```json" in response_text:
            cleaned_response = response_text.split("```json")[1].split("```")[0].strip()
        elif response_text.startswith("```") and response_text.endswith("```"):
            cleaned_response = response_text.strip("```").strip()
        return cleaned_response
    except Exception as e:
        st.error(f"Error analyzing location: {e}")
        return None

# Function to generate outfits
def generate_outfits(profile, wardrobe_items, location_info=None, time_of_day=None, location_analysis=None):
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        wardrobe_json = json.dumps(wardrobe_items)

                # Build context-aware prompt
        location_context = ""
        if location_info:
            location_context = f"""
            Location Context:
            - Destination: {location_info.get('destination', '')}
            - Activity: {location_info.get('activity', '')}
            - Time of Day: {time_of_day if time_of_day else 'Not specified'}
            """

        if location_analysis:
            location_context += f"""
            Location Analysis:
            {location_analysis}
            """
        
        prompt = f"""
        You're an expert stylist.
        Use the following profile, location context, and available wardrobe items to suggest 3 personalized outfit options:
        
        Profile:
        {profile}

        {location_context}
        
        
        Wardrobe:
        {wardrobe_json}
        
        Generate outfits that:
        1. Only use items available in the wardrobe
        2. Match the location's environment and dress code
        3. Are appropriate for the time of day
        4. Consider the weather and environment
        5. Only use colors from recommended_colors in the profile
        6. Avoid styles from avoid_styles in the profile
        
        Return in JSON format with 3 outfit options.
        The output should have this structure:
        {{
          "outfit_options": [
            {{
              "option_id": 1,
              "name": "Name of outfit",
              "description": "Brief description",
              "items": [
                {{
                  "type": "top/bottom/etc",
                  "item_id": "item ID from wardrobe"
                }},
                ...
              ],
              "occasions": ["casual", "work", etc],
              "weather": "suitable weather condition",
              "time_of_day": "when to wear",
              "location_appropriateness": "why this outfit suits the location"
            }},
            ...
          ]
        }}
        """
        
        response = model.generate_content(prompt, generation_config={"temperature": 0.7})
        response_text = response.text

        # Clean up and parse the JSON response
        cleaned_response = response_text
        if "```json" in response_text:
            # If response is wrapped in markdown code block
            cleaned_response = response_text.split("```json")[1].split("```")[0].strip()
        elif response_text.startswith("```") and response_text.endswith("```"):
            # If response is wrapped in generic code block
            cleaned_response = response_text.strip("```").strip()
            
        return cleaned_response
    except Exception as e:
        st.error(f"Error generating outfits: {e}")
        st.write("Raw response:", response_text if 'response_text' in locals() else "No response received")
        return None

# Design custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5em;
        color: #FF4B4B;
        text-align: center;
        margin-bottom: 20px;
    }
    .sub-header {
        font-size: 1.8em;
        color: #FF4B4B;
        margin-top: 30px;
        margin-bottom: 15px;
    }
    .card {
        background-color: #f9f9f9;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    .item-card {
        background-color: white;
        border-radius: 8px;
        padding: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 10px;
    }
    .profile-info {
        background-color: #e6f3ff;
        border-left: 4px solid #3366ff;
        padding: 15px;
        border-radius: 5px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# App title and description
st.markdown("<h1 class='main-header'>Dress Mind</h1>", unsafe_allow_html=True)
st.markdown("Upload your clothing items and let AI create personalized outfits for your style and body type.")

# Sidebar
with st.sidebar:
    st.header("Settings")
    
    # API Key input
    user_api_key = st.text_input("Enter your Gemini API Key:", value=get_api_key(), type="password")
    if user_api_key:
        st.session_state["api_key"] = user_api_key
        os.environ["GEMINI_API_KEY"] = user_api_key
        initialize_gemini()
    
    st.markdown("---")
    
    # Navigation
    st.subheader("Navigation")
    app_mode = st.radio("", ["Create Profile", "Manage Wardrobe", "Generate Outfits"])
    
    # Clean up wardrobe
    if st.button("Clean Missing Files"):
        st.session_state.wardrobe_items = utils.clean_missing_items(st.session_state.wardrobe_items)
        utils.save_wardrobe(st.session_state.wardrobe_items)
        st.success("Cleaned up missing files!")
        st.rerun()

# Create Profile section
if app_mode == "Create Profile":
    st.markdown("<h2 class='sub-header'>Create Your Style Profile</h2>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.write("Upload a clear photo of yourself (front-facing) to analyze your body shape and skin tone.")
        uploaded_image = st.file_uploader("Upload your photo", type=["jpg", "jpeg", "png"])
        
        col1, col2 = st.columns([1, 1])
        
        if uploaded_image:
            with col1:
                image = Image.open(uploaded_image)
                st.image(image, caption="Your uploaded photo", width=300)
            
            with col2:
                if st.button("Analyze Photo", key="analyze_photo"):
                    if initialize_gemini():
                        with st.spinner("Analyzing your photo..."):
                            profile_analysis = analyze_image(image)
                            if profile_analysis:
                                st.session_state.profile = profile_analysis
                                # Save profile to file
                                utils.save_profile(profile_analysis)
                                st.success("Analysis complete!")
                    else:
                        st.error("Please enter your Gemini API key in the sidebar.")
        
        if st.session_state.profile:
            st.markdown("<div class='profile-info'>", unsafe_allow_html=True)
            st.subheader("Your Style Profile")
            st.write(st.session_state.profile)
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Option to manually edit profile
            if st.checkbox("Edit profile manually"):
                edited_profile = st.text_area("Edit your profile", value=st.session_state.profile, height=300)
                if st.button("Update Profile"):
                    st.session_state.profile = edited_profile
                    # Save updated profile
                    utils.save_profile(edited_profile)
                    st.success("Profile updated!")
        
        st.markdown("</div>", unsafe_allow_html=True)

# Manage Wardrobe section
elif app_mode == "Manage Wardrobe":
    st.markdown("<h2 class='sub-header'>Manage Your Wardrobe</h2>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.write("Upload images of your clothing items to build your digital wardrobe.")
        
        # Clothing category selection
        clothing_type = st.selectbox("Select clothing type", 
                                    ["tops", "bottoms", "dresses", "shoes", "accessories"])
        
        # Upload clothing item
        uploaded_item = st.file_uploader("Upload clothing item", type=["jpg", "jpeg", "png"], key="wardrobe_uploader")
        
        if uploaded_item:
            col1, col2 = st.columns([1, 1])
            
            with col1:
                item_image = Image.open(uploaded_item)
                st.image(item_image, caption=f"New {clothing_type} item", width=250)
                
            with col2:
                if st.button("Add to Wardrobe", key="add_to_wardrobe"):
                    if initialize_gemini():
                        with st.spinner("Analyzing clothing item..."):
                            # Generate unique ID for the item
                            item_id = str(uuid.uuid4())[:8]
                            
                            # Save image file
                            utils.ensure_data_dir()  # Make sure uploads directory exists
                            
                            file_path = f"uploads/{item_id}.jpg"
                            with open(file_path, "wb") as f:
                                f.write(uploaded_item.getbuffer())
                            
                            # Analyze clothing
                            item_analysis = analyze_clothing(item_image)
                            
                            # Add item to wardrobe
                            if item_analysis:
                                try:
                                    # Clean up and parse the JSON response
                                    cleaned_response = item_analysis
                                    if "```json" in item_analysis:
                                        # If response is wrapped in markdown code block
                                        cleaned_response = item_analysis.split("```json")[1].split("```")[0].strip()
                                    elif item_analysis.startswith("```") and item_analysis.endswith("```"):
                                        # If response is wrapped in generic code block
                                        cleaned_response = item_analysis.strip("```").strip()
                                    
                                    # Parse the JSON
                                    item_data = json.loads(cleaned_response)
                                    
                                    # Add debug output
                                    st.write("Raw Response for Debugging:", item_analysis)
                                    
                                    # Add image path and ID
                                    item_data["id"] = item_id
                                    item_data["image_path"] = file_path
                                    
                                    # Add to wardrobe
                                    st.session_state.wardrobe_items[clothing_type].append(item_data)
                                    # Save updated wardrobe
                                    utils.save_wardrobe(st.session_state.wardrobe_items)
                                    st.success(f"Added {item_data['type']} to your wardrobe!")
                                except json.JSONDecodeError as e:
                                    st.error(f"Error parsing JSON response: {e}")
                                    st.write("Raw response:", item_analysis)
                                except Exception as e:
                                    st.error(f"Error processing item: {e}")
                                    st.write("Raw response:", item_analysis)
                    else:
                        st.error("Please enter your Gemini API key in the sidebar.")
        
        # Display wardrobe items
        st.markdown("<h3>Your Wardrobe</h3>", unsafe_allow_html=True)
        
        category_tabs = st.tabs(["Tops", "Bottoms", "Dresses", "Shoes", "Accessories"])
        
        categories = ["tops", "bottoms", "dresses", "shoes", "accessories"]
        
        for i, tab in enumerate(category_tabs):
            with tab:
                category = categories[i]
                if not st.session_state.wardrobe_items[category]:
                    st.write(f"No {category} in your wardrobe yet.")
                else:
                    cols = st.columns(3)
                    for j, item in enumerate(st.session_state.wardrobe_items[category]):
                        with cols[j % 3]:
                            st.markdown(f"<div class='item-card'>", unsafe_allow_html=True)
                            
                            # Check if image exists
                            if os.path.exists(item["image_path"]):
                                st.image(item["image_path"], width=150)
                            else:
                                st.write("Image not found")
                            
                            st.write(f"**{item['type']}**")
                            st.write(f"Color: {item['color']}")
                            
                            # Delete button
                            if st.button(f"Remove", key=f"remove_{category}_{item['id']}"):
                                st.session_state.wardrobe_items[category].remove(item)
                                # Save updated wardrobe
                                utils.save_wardrobe(st.session_state.wardrobe_items)
                                st.rerun()
                                
                            st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)

# Generate Outfits section
elif app_mode == "Generate Outfits":
    st.markdown("<h2 class='sub-header'>Generate Outfits</h2>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        
        # Check if profile and wardrobe items exist
        if not st.session_state.profile:
            st.warning("Please create your style profile first.")
        elif all(len(items) == 0 for items in st.session_state.wardrobe_items.values()):
            st.warning("Please add items to your wardrobe first.")
        else:
           # Location and Time Context
            with st.expander("Set Location and Time Context", expanded=True):
                col1, col2 = st.columns([1, 1])

                with col1:
                    destination = st.text_input("Destination/Location", 
                                              help="Enter the name of your destination (e.g., 'Beach in Bali', 'Paris Museum')")
                    activity = st.text_input("Planned Activity",
                                           help="What will you be doing? (e.g., 'Sightseeing', 'Dinner')")
                    time_of_day = st.selectbox("Time of Day", 
                                             ["Morning", "Afternoon", "Evening", "Night"],
                                             help="Select the time of day for your outfit")

                with col2:
                    st.write("Upload a photo of the location (optional)")
                    location_image = st.file_uploader("Location Image", 
                                                    type=["jpg", "jpeg", "png"],
                                                    help="Upload a photo of your destination for better context")

                    location_analysis = None
                    if location_image:
                        image = Image.open(location_image)
                        st.image(image, caption="Location Image", width=300)

                        if st.button("Analyze Location"):
                            with st.spinner("Analyzing location..."):
                                location_analysis = analyze_location(image)
                                if location_analysis:
                                    st.success("Location analyzed!")
                                    try:
                                        st.json(json.loads(location_analysis))
                                    except Exception:
                                        st.write(location_analysis)

            # Generate outfits button
            if st.button("Generate Outfits"):
                if initialize_gemini():
                    with st.spinner("Generating outfit suggestions..."):
                        location_info = {
                            "destination": destination,
                            "activity": activity
                        } if destination or activity else None

                        outfits = generate_outfits(
                            st.session_state.profile,
                            st.session_state.wardrobe_items,
                            location_info=location_info,
                            time_of_day=time_of_day,
                            location_analysis=location_analysis
                        )
                        
                        if outfits:
                            try:
                                # Parse the JSON
                                outfits_data = json.loads(outfits)
                                st.session_state.recommended_outfits = outfits_data["outfit_options"]
                                st.success("Generated outfit suggestions!")
                            except json.JSONDecodeError as e:
                                st.error(f"Error parsing outfit suggestions: {e}")
                                st.write("Raw response:", outfits)
                            except Exception as e:
                                st.error(f"Error processing outfits: {e}")
                                st.write("Raw response:", outfits)
                else:
                    st.error("Please enter your Gemini API key in the sidebar.")
            
            # Display recommended outfits
            if st.session_state.recommended_outfits:
                st.markdown("<h3>Recommended Outfits</h3>", unsafe_allow_html=True)
                
                for outfit in st.session_state.recommended_outfits:
                    with st.expander(f"{outfit['name']} - {outfit['description']}", expanded=True):
                        # Display context information
                        st.write(f"**Time of Day:** {outfit.get('time_of_day', 'Any time')}")
                        st.write(f"**Occasions:** {', '.join(outfit['occasions'])}")
                        st.write(f"**Weather:** {outfit['weather']}")
                        if 'location_appropriateness' in outfit:
                            st.write(f"**Location Fit:** {outfit['location_appropriateness']}")                        
                        
                        # Display outfit items
                        cols = st.columns(len(outfit['items']))
                        
                        for i, outfit_item in enumerate(outfit['items']):
                            with cols[i]:
                                # Find the item in wardrobe
                                item_found = False
                                for category in st.session_state.wardrobe_items:
                                    for item in st.session_state.wardrobe_items[category]:
                                        if item.get('id') == outfit_item.get('item_id'):
                                            if os.path.exists(item["image_path"]):
                                                st.image(item["image_path"], width=150)
                                            st.write(f"**{item['type']}**")
                                            st.write(f"{item['color']}")
                                            item_found = True
                                            break
                                    if item_found:
                                        break
                                        
                                if not item_found:
                                    st.write("Item not found in wardrobe")
                        
                        # Save outfit button
                        if st.button("Save to Favorites", key=f"save_{outfit['option_id']}"):
                            st.session_state.outfit_history.append(outfit)
                            # Save updated outfit history
                            utils.save_outfits(st.session_state.outfit_history)
                            st.success("Outfit saved to favorites!")
            
            # Display saved outfits
            if st.session_state.outfit_history:
                st.markdown("<h3>Favorite Outfits</h3>", unsafe_allow_html=True)
                for i, saved_outfit in enumerate(st.session_state.outfit_history):
                    st.write(f"{i+1}. {saved_outfit['name']} - {saved_outfit['description']}")
        
        st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("AI Personal Stylist - Your virtual wardrobe assistant") 