
from openai import OpenAI
import os, requests


def generateimage(chapter_content, storyfile):
    client = OpenAI(api_key=os.getenv("GPT_API_KEY"))

    response = client.images.generate(
        model="dall-e-3",
        prompt=f"이미지의 내용: {chapter_content}. 스타일은 Illustration으로 해줘",
        #Style: Illustration. Create an illustration incorporating a vivid palette with an emphasis on shades of azure and emerald, augmented by splashes of gold for contrast and visual interest. The style should evoke the intricate detail and whimsy of early 20th-century storybook illustrations, blending realism with fantastical elements to create a sense of wonder and enchantment. The composition should be rich in texture, with a soft, luminous lighting that enhances the magical atmosphere. Attention to the interplay of light and shadow will add depth and dimensionality, inviting the viewer to delve into the scene. DON'T include ANY text in this image. DON'T include colour palettes in this image.
        size="1024x1024",
        quality="standard",
        n=1,
    )

    image_url = response.data[0].url
    filename = f"image_{chapter_content[:10].replace(' ', '_')}.png"
    filepath = os.path.join("images", filename)

    image_response = requests.get(image_url)
    if image_response.status_code == 200:
        with open(filepath, "wb") as file:
            file.write(image_response.content)
    else:
        print("Failed to download the image.")
        return ""

    return filepath
