# IMGenAI
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1PlTCQoYTQsKt1K7N6QINGfQzf5uz4_vJ?usp=sharing)

This is a project for generating images from text prompts using [Diffusers]() on [Google Colab]() VM with desktop app.

# Setup server:
1. Save a copy of [this colab notebook](https://colab.research.google.com/drive/1PlTCQoYTQsKt1K7N6QINGfQzf5uz4_vJ?usp=sharing) on your Google Drive.
2. Create secret key "NGROK_AUTHTOKEN" with your [ngrok authtoken](https://dashboard.ngrok.com/get-started/your-authtoken).
3. Select Stable Diffusion model in "Setting up Stable Diffusion pipeline" tab or use [custom text-to-image model](https://huggingface.co/models?pipeline_tag=text-to-image&library=diffusers&sort=trending).
4. Run all cells and wait 'till server run.
5. Copy server's public url to IMGenAI app.

# Setup desktop app:

Download latest [release version](https://github.com/oderline/IMGenAI/releases) of IMGenAI app (or it's source code). In the app, paste server's public url to "Enter server address" field. Load prompt settings from text file or set it manually. Click "Generate" button and wait server's responce.

# Setup python environment:

~~~

~~~
