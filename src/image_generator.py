"""Image generation services for creating tech-themed images."""

import io
import random
import urllib.parse
import requests
from PIL import Image, ImageDraw, ImageFont
import textwrap


class ImageGenerator:
    """Service for generating images using various methods."""
    
    @staticmethod
    def create_tech_themed_image(topic: str, title: str) -> io.BytesIO:
        """Generate a visually appealing tech-themed image with text."""
        try:
            print(f"Creating tech-themed image for: {topic}")
            width, height = 1200, 630  # Good size for Twitter
            
            # Create a gradient background
            image = Image.new('RGB', (width, height), color='white')
            draw = ImageDraw.Draw(image)
            
            # Draw colorful gradient background - tech-themed colors
            for y in range(height):
                r = int(20 + (50 * (1 - y / height)))  # Dark blue to lighter blue
                g = int(40 + (80 * (y / height)))
                b = int(80 + (120 * (y / height)))
                for x in range(width):
                    # Add some horizontal variation too
                    r_mod = r + int(20 * (x / width))
                    g_mod = g + int(10 * (x / width))
                    draw.point((x, y), fill=(r_mod, g_mod, b))
            
            # Add some tech-themed decorative elements
            # Network nodes and connections
            nodes = []
            for _ in range(20):
                x = random.randint(50, width-50)
                y = random.randint(50, height-50)
                size = random.randint(5, 15)
                nodes.append((x, y, size))
            
            # Draw connections between nodes
            for i in range(len(nodes)):
                for j in range(i+1, min(i+4, len(nodes))):
                    x1, y1, _ = nodes[i]
                    x2, y2, _ = nodes[j]
                    # Calculate distance
                    dist = ((x2-x1)**2 + (y2-y1)**2)**0.5
                    if dist < 300:  # Only connect nearby nodes
                        # Add some curvature for visual interest
                        draw.line((x1, y1, x2, y2), fill=(180, 220, 255, 128), width=1)
            
            # Draw nodes on top of connections
            for x, y, size in nodes:
                draw.ellipse((x-size, y-size, x+size, y+size), 
                             fill=(220, 240, 255), 
                             outline=(255, 255, 255))
            
            # Add some random larger circles for visual interest
            for _ in range(8):
                x = random.randint(0, width)
                y = random.randint(0, height)
                size = random.randint(50, 150)
                # Semi-transparent circles
                for s in range(size, 0, -10):
                    opacity = int(100 * (s/size))
                    draw.ellipse((x-s, y-s, x+s, y+s), 
                                outline=(255, 255, 255, opacity),
                                width=2)
            
            # Add topic text
            try:
                # Try to load a nice font, fall back to default if not available
                try:
                    title_font = ImageFont.truetype("arial.ttf", 60)
                    subtitle_font = ImageFont.truetype("arial.ttf", 30)
                except:
                    # Fallback fonts
                    title_font = ImageFont.load_default()
                    subtitle_font = ImageFont.load_default()
                
                # Add a semi-transparent overlay for text
                overlay = Image.new('RGBA', (width, 200), (0, 0, 0, 150))
                image.paste(overlay, (0, height-200), overlay)
                
                # Wrap title text to fit
                title_wrapped = textwrap.fill(title, width=30)
                
                # Draw title text
                draw.text((width//2, height-120), title_wrapped, 
                         fill=(255, 255, 255), 
                         font=title_font, 
                         anchor="mm", 
                         align="center")
                
                # Draw subtitle/attribution
                draw.text((width//2, height-40), "AskMeGenie", 
                         fill=(200, 200, 255), 
                         font=subtitle_font,
                         anchor="mm")
                
            except Exception as e:
                print(f"Error adding text to image: {e}")
            
            # Save the image for debugging
            image_path = "generated_image.jpg"
            image.save(image_path)
            print(f"Image saved to {image_path}")
            
            # Return the image as a buffer
            img_buffer = io.BytesIO()
            image.save(img_buffer, format='JPEG', quality=95)
            img_buffer.seek(0)
            return img_buffer
            
        except Exception as e:
            print(f"Error creating tech-themed image: {e}")
            # Create an even simpler fallback image
            image = Image.new('RGB', (800, 500), color=(20, 40, 80))
            draw = ImageDraw.Draw(image)
            draw.rectangle((10, 10, 790, 490), outline=(255, 255, 255), width=5)
            
            img_buffer = io.BytesIO()
            image.save(img_buffer, format='JPEG')
            img_buffer.seek(0)
            return img_buffer
    
    @staticmethod
    def create_image_with_pollinations_api(prompt: str, fallback_generator=None) -> io.BytesIO:
        """Generate an image using Pollinations.ai API (free, no API key required)."""
        try:
            print(f"Generating image using Pollinations.ai with prompt: {prompt}")
            
            # Pollinations.ai free API - no API key needed
            # URL encode the prompt for the URL
            encoded_prompt = urllib.parse.quote(prompt)
            
            # API endpoint with parameters
            url = f"https://image.pollinations.ai/prompt/{encoded_prompt}"
            
            # Parameters for image generation
            params = {
                "width": 1200,
                "height": 630,
                "seed": random.randint(1000, 9999),
                "model": "flux",  # Options: flux, stable-diffusion, dreamshaper, etc.
                "enhance": "true",
                "private": "false"
            }
            
            # Make the API request
            print("Sending request to Pollinations.ai...")
            response = requests.get(url, params=params, stream=True, timeout=60)
            response.raise_for_status()  # Raise exception for non-200 responses
            
            print(f"Response received, status: {response.status_code}")
            
            # Get image data directly (Pollinations returns image bytes)
            image_data = response.content
            
            if not image_data:
                print("No image data found in response")
                raise Exception("No image data in response")
            
            print(f"Received image data, length: {len(image_data)} bytes")
            
            # Create an image buffer
            img_buffer = io.BytesIO(image_data)
            
            # Verify the image by opening it
            img = Image.open(img_buffer)
            img.verify()  # Will raise an exception if it's not a valid image
            
            # Save a copy for debugging
            img_buffer.seek(0)
            img = Image.open(img_buffer)
            img.save("pollinations_image.jpg")
            print(f"Image saved as 'pollinations_image.jpg'")
            
            # Return the image buffer
            img_buffer.seek(0)
            return img_buffer
            
        except Exception as e:
            print(f"Error generating image with Pollinations.ai: {e}")
            print("Falling back to local image generation...")
            # Fall back to local image generation if the API fails
            if fallback_generator:
                return fallback_generator(prompt, prompt)
            else:
                return ImageGenerator.create_tech_themed_image(prompt, prompt)




