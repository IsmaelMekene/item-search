import os
from pinecone import Pinecone, ServerlessSpec
from pinecone_text.sparse import BM25Encoder
from datasets import load_dataset
from sentence_transformers import SentenceTransformer
import torch
from IPython.core.display import HTML
from io import BytesIO
from base64 import b64encode
from tqdm.auto import tqdm
from PIL import Image
import gradio as gr
from constants import *

from search import SearchItem


# initialize connection to pinecone (get API key at app.pinecone.io)
api_key = PINECONE_API_KEY or os.getenv(PINECONE_API_KEY) # or "PINECONE_API_KEY"
# find your environment next to the api key in pinecone console
env = PINECONE_ENVIRONMENT or os.getenv(PINECONE_ENVIRONMENT) # or "PINECONE_ENVIRONMENT"

fashion_processor = SearchItem(api_key, env)
    

def retrieve_images(query, image=None):
    if image:
        # If image is provided, use retrieve_image_from_image function
        return retrieve_image_from_image(image, query)
    else:
        # If image is not provided, use retrieve_image_from_query function
        return retrieve_image_from_query(query)
    


def retrieve_image_from_query(query):

    # create sparse and dense vectors
    sparse = fashion_processor.bm25.encode_queries(query)
    dense = fashion_processor.clip_model.encode(query).tolist()
    hdense, hsparse = fashion_processor.hybrid_scale(dense, sparse)

    result = fashion_processor.index.query(
        top_k=10,
        vector=hdense,
        sparse_vector=hsparse,
        include_metadata=True
    )

    imgs = [fashion_processor.images[int(r["id"])] for r in result["matches"]]

    return imgs


def retrieve_image_from_image(image, query):

    try:
        # create sparse and dense vectors
        sparse = fashion_processor.bm25.encode_queries(query)
        w, h = 60, 80
        image = Image.open(image.name).resize((w, h))
        dense = fashion_processor.clip_model.encode(image).tolist()
        hdense, hsparse = fashion_processor.hybrid_scale(dense, sparse)


        result = fashion_processor.index.query(
            top_k=10,
            vector=hdense,
            sparse_vector=hsparse,
            include_metadata=True
        )

        imgs = [fashion_processor.images[int(r["id"])] for r in result["matches"]]

        return imgs
    
    except Exception as e:
        print(f"Error processing image: {e}")
        return None



def show_img(image):
    return image.name if image else "No image provided"


with gr.Blocks() as demo:
    gr.Markdown(
    """
    # Shopping Search Engine
    
    Look for the ideal clothing items 😎
    """)
    
    with gr.Row():
        with gr.Column():

            query = gr.Textbox(placeholder="Search Items")
            gr.HTML("OR")
            photo = gr.Image()
            with gr.Row():
                button = gr.UploadButton(label="Upload Image", file_types=["image"])
                textbox = gr.Textbox(placeholder="Additional Details ?")
                submit_button = gr.Button(text="Submit")

        with gr.Column():
            gallery = gr.Gallery().style(
                object_fit='contain',
                height='auto',
                preview=True
            )

    query.submit(fn=lambda query: retrieve_images(query), inputs=[query], outputs=[gallery])
    submit_button.click(fn=lambda image, query: show_img(image), inputs=[button, textbox], outputs=[photo]) \
        .then(fn=lambda image, query: retrieve_images(query, image), inputs=[button, textbox], outputs=[gallery])

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7000)