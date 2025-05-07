import os
import json
import pickle
from pathlib import Path

# File path for saving wardrobe data
WARDROBE_FILE = "data/wardrobe.pkl"
PROFILE_FILE = "data/profile.json"
OUTFITS_FILE = "data/saved_outfits.json"

def ensure_data_dir():
    """Ensure the data directory exists"""
    os.makedirs("data", exist_ok=True)
    os.makedirs("uploads", exist_ok=True)

def save_wardrobe(wardrobe_items):
    """Save wardrobe items to a pickle file"""
    ensure_data_dir()
    with open(WARDROBE_FILE, 'wb') as f:
        pickle.dump(wardrobe_items, f)

def load_wardrobe():
    """Load wardrobe items from pickle file if exists"""
    ensure_data_dir()
    if os.path.exists(WARDROBE_FILE):
        try:
            with open(WARDROBE_FILE, 'rb') as f:
                return pickle.load(f)
        except Exception as e:
            print(f"Error loading wardrobe: {e}")
    
    # Return default wardrobe structure if file doesn't exist or error occurs
    return {
        "tops": [],
        "bottoms": [],
        "dresses": [],
        "shoes": [],
        "accessories": []
    }

def save_profile(profile_data):
    """Save user profile to a JSON file"""
    ensure_data_dir()
    with open(PROFILE_FILE, 'w') as f:
        json.dump({"profile": profile_data}, f)

def load_profile():
    """Load user profile from JSON file if exists"""
    ensure_data_dir()
    if os.path.exists(PROFILE_FILE):
        try:
            with open(PROFILE_FILE, 'r') as f:
                data = json.load(f)
                return data.get("profile", None)
        except Exception as e:
            print(f"Error loading profile: {e}")
    return None

def save_outfits(outfits):
    """Save outfit history to a JSON file"""
    ensure_data_dir()
    with open(OUTFITS_FILE, 'w') as f:
        json.dump({"outfits": outfits}, f)

def load_outfits():
    """Load outfit history from JSON file if exists"""
    ensure_data_dir()
    if os.path.exists(OUTFITS_FILE):
        try:
            with open(OUTFITS_FILE, 'r') as f:
                data = json.load(f)
                return data.get("outfits", [])
        except Exception as e:
            print(f"Error loading outfits: {e}")
    return []

def clean_missing_items(wardrobe_items):
    """Remove any wardrobe items whose image files don't exist anymore"""
    for category in wardrobe_items:
        wardrobe_items[category] = [
            item for item in wardrobe_items[category] 
            if os.path.exists(item.get("image_path", ""))
        ]
    return wardrobe_items 