import json
from PIL import Image, ImageDraw

# Load JSON
json_file = '202404041210_lobby.json'
with open(json_file, 'r') as file:
    data = json.load(file)

# Define image dimensions
image_width = 1000  # Adjust as needed
image_height = 1000  # Adjust as needed
image = Image.new("L", (image_width, image_height), color=255)  # White background (255)

draw = ImageDraw.Draw(image)

# Parse shapes and draw them on the image
for shape in data['shapes']:
    label = shape['label']
    points = shape['points']
    
    # Convert points to integer coordinates and draw
    int_points = [(int(p[0]), int(p[1])) for p in points]
    
    if shape['shape_type'] == 'rectangle':
        draw.rectangle(int_points, fill=0)  # Black for obstacles (0)
    elif shape['shape_type'] == 'polygon':
        draw.polygon(int_points, fill=0)  # Black for obstacles (0)
    elif shape['shape_type'] == 'circle':
        x, y = int_points[0]
        r = int_points[1][0] - x  # Approximate radius
        draw.ellipse([x - r, y - r, x + r, y + r], fill=0)

# Save the PGM file
pgm_path = '../maps/output_map.pgm'
image.save(pgm_path)

print(f"Map saved as {pgm_path}")
