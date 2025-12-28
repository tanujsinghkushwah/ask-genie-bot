"""Image generation services."""

import io
import random
import urllib.parse
import requests
from PIL import Image, ImageDraw, ImageFont
import textwrap


class ImageGenerator:
    """Image generation using Pollinations API with local fallback."""
    
    @staticmethod
    def create_tech_themed_image(topic: str, title: str) -> io.BytesIO:
        """Generate a tech-themed image with gradient background and network nodes."""
        try:
            print(f"Creating tech-themed image for: {topic}")
            width, height = 1200, 630
            image = Image.new('RGB', (width, height), color='white')
            draw = ImageDraw.Draw(image)

            for y in range(height):
                r = int(20 + (50 * (1 - y / height)))  # Dark blue to lighter blue
                g = int(40 + (80 * (y / height)))
                b = int(80 + (120 * (y / height)))
                for x in range(width):
                    r_mod = r + int(20 * (x / width))
                    g_mod = g + int(10 * (x / width))
                    draw.point((x, y), fill=(r_mod, g_mod, b))

            nodes = []
            for _ in range(20):
                x = random.randint(50, width-50)
                y = random.randint(50, height-50)
                size = random.randint(5, 15)
                nodes.append((x, y, size))

            for i in range(len(nodes)):
                for j in range(i+1, min(i+4, len(nodes))):
                    x1, y1, _ = nodes[i]
                    x2, y2, _ = nodes[j]
                    dist = ((x2-x1)**2 + (y2-y1)**2)**0.5
                    if dist < 300:
                        draw.line((x1, y1, x2, y2), fill=(180, 220, 255, 128), width=1)

            for x, y, size in nodes:
                draw.ellipse((x-size, y-size, x+size, y+size), 
                             fill=(220, 240, 255), 
                             outline=(255, 255, 255))

            for _ in range(8):
                x = random.randint(0, width)
                y = random.randint(0, height)
                size = random.randint(50, 150)
                for s in range(size, 0, -10):
                    opacity = int(100 * (s/size))
                    draw.ellipse((x-s, y-s, x+s, y+s), 
                                outline=(255, 255, 255, opacity),
                                width=2)
            try:
                try:
                    title_font = ImageFont.truetype("arial.ttf", 60)
                    subtitle_font = ImageFont.truetype("arial.ttf", 30)
                except:
                    title_font = ImageFont.load_default()
                    subtitle_font = ImageFont.load_default()

                overlay = Image.new('RGBA', (width, 200), (0, 0, 0, 150))
                image.paste(overlay, (0, height-200), overlay)
                title_wrapped = textwrap.fill(title, width=30)

                draw.text((width//2, height-120), title_wrapped, 
                         fill=(255, 255, 255), 
                         font=title_font, 
                         anchor="mm", 
                         align="center")

                draw.text((width//2, height-40), "AskMeGenie", 
                         fill=(200, 200, 255), 
                         font=subtitle_font,
                         anchor="mm")
                
            except Exception as e:
                print(f"Error adding text to image: {e}")

            image_path = "generated_image.jpg"
            image.save(image_path)
            print(f"Image saved to {image_path}")

            img_buffer = io.BytesIO()
            image.save(img_buffer, format='JPEG', quality=95)
            img_buffer.seek(0)
            return img_buffer
            
        except Exception as e:
            print(f"Error creating tech-themed image: {e}")
            image = Image.new('RGB', (800, 500), color=(20, 40, 80))
            draw = ImageDraw.Draw(image)
            draw.rectangle((10, 10, 790, 490), outline=(255, 255, 255), width=5)
            
            img_buffer = io.BytesIO()
            image.save(img_buffer, format='JPEG')
            img_buffer.seek(0)
            return img_buffer
    
    @staticmethod
    def create_image_with_pollinations_api(prompt: str, fallback_generator=None) -> io.BytesIO:
        """Generate image using Pollinations.ai API with local fallback."""
        try:
            print(f"Generating image using Pollinations.ai with prompt: {prompt}")
            encoded_prompt = urllib.parse.quote(prompt)
            url = f"https://image.pollinations.ai/prompt/{encoded_prompt}"
            params = {
                "width": 1200,
                "height": 630,
                "seed": random.randint(1000, 9999),
                "model": "flux",  # Options: flux, stable-diffusion, dreamshaper, etc.
                "enhance": "true",
                "private": "false"
            }

            print("Sending request to Pollinations.ai...")
            response = requests.get(url, params=params, stream=True, timeout=60)
            response.raise_for_status()  # Raise exception for non-200 responses
            
            print(f"Response received, status: {response.status_code}")

            image_data = response.content
            
            if not image_data:
                print("No image data found in response")
                raise Exception("No image data in response")
            
            print(f"Received image data, length: {len(image_data)} bytes")

            img_buffer = io.BytesIO(image_data)
            img = Image.open(img_buffer)
            img.verify()

            img_buffer.seek(0)
            img = Image.open(img_buffer)
            img.save("pollinations_image.jpg")
            print(f"Image saved as 'pollinations_image.jpg'")

            img_buffer.seek(0)
            return img_buffer
            
        except Exception as e:
            print(f"Error generating image with Pollinations.ai: {e}")
            print("Falling back to local image generation...")
            if fallback_generator:
                return fallback_generator(prompt, prompt)
            else:
                return ImageGenerator.create_tech_themed_image(prompt, prompt)




