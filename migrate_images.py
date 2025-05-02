import os
import csv
import shutil
from datetime import datetime
from pathlib import Path

def migrate_images():
    # Create outfits directory if it doesn't exist
    os.makedirs('outfits', exist_ok=True)
    
    # Create images catalog if it doesn't exist
    if not os.path.exists('outfit_images.csv'):
        with open('outfit_images.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'image_id', 'outfit_id', 'filename', 'generation_timestamp',
                'prompt', 'revised_prompt', 'evaluation_status'
            ])
    
    # Get list of existing outfit images
    image_files = [f for f in os.listdir('.') if f.startswith('outfit_') and f.endswith('.jpg')]
    
    # Group images by outfit timestamp
    outfit_groups = {}
    for img in image_files:
        # Extract timestamp from filename (outfit_YYYYMMDD_HHMMSS_X.jpg)
        parts = img.split('_')
        if len(parts) >= 4:
            timestamp = f"{parts[1]}_{parts[2]}"
            outfit_groups.setdefault(timestamp, []).append(img)
    
    # Process each outfit group
    for timestamp, images in outfit_groups.items():
        outfit_id = f"outfit_{timestamp}"
        outfit_dir = os.path.join('outfits', outfit_id)
        os.makedirs(outfit_dir, exist_ok=True)
        
        # Move images to outfit directory and record in catalog
        with open('outfit_images.csv', 'a', newline='') as f:
            writer = csv.writer(f)
            for img in images:
                # Create new filename in outfit directory
                new_filename = f"image_{timestamp}_{images.index(img)}.jpg"
                new_filepath = os.path.join(outfit_dir, new_filename)
                
                # Move the file
                if os.path.exists(img):
                    shutil.move(img, new_filepath)
                    
                    # Add entry to images catalog
                    writer.writerow([
                        f"img_{timestamp}_{images.index(img)}",
                        outfit_id,
                        new_filename,
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "",  # No prompt available for existing images
                        "",  # No revised prompt available
                        "Generated"  # Mark as already generated
                    ])
    
    print("Migration completed successfully!")

if __name__ == "__main__":
    migrate_images() 