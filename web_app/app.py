from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from web_app.user_profile import UserProfile, Measurements, PhysicalFeatures, StylePreferences, StylePreference, MeasurementUnit, BustMeasurement, CupSize
from web_app.dress_maker import OutfitGenerator
import json
from datetime import datetime
import os
from pathlib import Path
import logging

app = Flask(__name__)
app.secret_key = os.urandom(24)  # For session management

# Initialize our components
user_profile = UserProfile()
outfit_generator = OutfitGenerator()

logger = logging.getLogger(__name__)

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    
    # Get list of existing users
    existing_users = []
    profiles_dir = Path("user_data/profiles")
    if profiles_dir.exists():
        for profile_file in profiles_dir.glob("*.json"):
            try:
                with open(profile_file, 'r') as f:
                    profile = json.load(f)
                    existing_users.append(profile['name'])
            except Exception as e:
                logger.error(f"Error loading profile {profile_file}: {str(e)}")
    
    return render_template('login.html', existing_users=sorted(existing_users))

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    if user_profile.is_new_user(username):
        return redirect(url_for('create_profile', username=username))
    
    profile = user_profile.load_profile(username)
    if profile:
        session['username'] = username
        return redirect(url_for('dashboard'))
    return render_template('login.html', error="Error loading profile")

@app.route('/create_profile/<username>')
def create_profile(username):
    return render_template('create_profile.html', username=username)

@app.route('/save_profile', methods=['POST'])
def save_profile():
    username = request.form.get('username')
    
    # Handle bust measurement
    bust_value = None
    if request.form.get('bust'):
        if request.form.get('cup_size'):
            # If both bust and cup size are provided, create a BustMeasurement
            bust_value = BustMeasurement(
                band_size=float(request.form.get('bust')),
                cup_size=CupSize(request.form.get('cup_size')),
                unit=MeasurementUnit.INCHES
            )
        else:
            # If only bust measurement is provided, use it as a float
            bust_value = float(request.form.get('bust'))
    
    # Get measurements
    measurements = Measurements(
        height=float(request.form.get('height')),
        height_unit=MeasurementUnit(request.form.get('height_unit')),
        weight=float(request.form.get('weight')),
        weight_unit=MeasurementUnit(request.form.get('weight_unit')),
        bust=bust_value,
        waist=float(request.form.get('waist')) if request.form.get('waist') else None,
        hips=float(request.form.get('hips')) if request.form.get('hips') else None,
        inseam=float(request.form.get('inseam')) if request.form.get('inseam') else None,
        shoulder_width=float(request.form.get('shoulder_width')) if request.form.get('shoulder_width') else None,
        arm_length=float(request.form.get('arm_length')) if request.form.get('arm_length') else None,
        shoe_size=float(request.form.get('shoe_size')) if request.form.get('shoe_size') else None,
        shoe_size_unit=request.form.get('shoe_size_unit') if request.form.get('shoe_size_unit') else None,
        max_heel_height=float(request.form.get('max_heel_height')) if request.form.get('max_heel_height') else None,
        shoe_width=request.form.get('shoe_width') if request.form.get('shoe_width') else None
    )
    
    # Get physical features
    physical_features = PhysicalFeatures(
        eye_color=request.form.get('eye_color'),
        hair_color=request.form.get('hair_color'),
        hair_length=request.form.get('hair_length'),
        skin_tone=request.form.get('skin_tone'),
        body_type=request.form.get('body_type'),
        face_shape=request.form.get('face_shape'),
        distinguishing_features=request.form.get('distinguishing_features').split(',') if request.form.get('distinguishing_features') else None
    )
    
    # Get style preferences
    style_preferences = StylePreferences(
        primary_style=StylePreference(request.form.get('primary_style')),
        secondary_styles={StylePreference(style) for style in request.form.getlist('secondary_styles')},
        favorite_colors=set(request.form.getlist('favorite_colors')),
        favorite_materials=set(request.form.getlist('favorite_materials')),
        preferred_silhouettes=set(request.form.getlist('preferred_silhouettes')),
        style_adaptability=int(request.form.get('style_adaptability')),
        comfort_priority=int(request.form.get('comfort_priority')),
        modesty_level=int(request.form.get('modesty_level')),
        color_preferences={},
        material_preferences={},
        style_restrictions=None,
        seasonal_preferences=None,
        preferred_heel_height=request.form.getlist('preferred_heel_height') if request.form.getlist('preferred_heel_height') else None,
        shoe_styles=request.form.getlist('shoe_styles') if request.form.getlist('shoe_styles') else None
    )
    
    # Create profile
    user_profile.create_profile(username, measurements, physical_features, style_preferences)
    session['username'] = username
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('index'))
    
    username = session['username']
    profile = user_profile.get_profile(username)
    outfit_count = user_profile.get_outfit_count(username)
    style_history = user_profile.get_style_history(username)
    
    return render_template('dashboard.html',
                         username=username,
                         profile=profile,
                         outfit_count=outfit_count,
                         style_history=style_history[-3:])  # Show last 3 outfits

@app.route('/generate_outfit', methods=['POST'])
def generate_outfit():
    if 'username' not in session:
        return jsonify({'error': 'Not logged in'})
    
    username = session['username']
    event = request.form.get('event')
    num_outfits = int(request.form.get('num_outfits', 1))
    variations = int(request.form.get('variations', 1))
    
    outfits = outfit_generator.generate_outfit(
        event=event,
        num_outfits=num_outfits,
        variations_per_outfit=variations,
        user_name=username
    )
    
    # Save outfits to history
    for outfit in outfits:
        user_profile.add_outfit_to_history(username, outfit)
    
    return jsonify({'outfits': outfits})

@app.route('/rate_outfit', methods=['POST'])
def rate_outfit():
    if 'username' not in session:
        return jsonify({'error': 'Not logged in'})
    
    username = session['username']
    outfit_id = request.form.get('outfit_id')
    ratings = {
        'style': int(request.form.get('style_rating')),
        'comfort': int(request.form.get('comfort_rating')),
        'overall': int(request.form.get('overall_rating')),
        'rated_at': datetime.now().isoformat()
    }
    
    user_profile.update_outfit_rating(username, outfit_id, ratings)
    return jsonify({'success': True})

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True) 