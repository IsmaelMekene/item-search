#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import os
from pinecone import Pinecone, ServerlessSpec
from pinecone_text.sparse import BM25Encoder
from datasets import load_dataset
from sentence_transformers import SentenceTransformer
import torch
from io import BytesIO
from base64 import b64encode
from tqdm.auto import tqdm
from constants import *



# initialize connection to pinecone (get API key at app.pinecone.io)
api_key = PINECONE_API_KEY or os.getenv(PINECONE_API_KEY) # or "PINECONE_API_KEY"
# find your environment next to the api key in pinecone console
env = PINECONE_ENVIRONMENT or os.getenv(PINECONE_ENVIRONMENT) # or "PINECONE_ENVIRONMENT"



class SearchItem():
    def __init__(self, api_key=None, env=None, device='cuda' if torch.cuda.is_available() else 'cpu'):
        self.api_key = api_key 
        self.environment = env 
        self.pinecone_instance = self.connect_to_pinecone(self.api_key,self.environment)
        self.index = self.pinecone_instance.Index('clip')
        self.images, self.metadata = self.load_fashion_dataset()
        self.clip_model = self.initialize_clip_model(device=device)
        self.bm25 = self.initialize_bm25_encoder(self.metadata)



    def connect_to_pinecone(self, api_key, env):
        api_key = api_key or os.getenv('PINECONE_API_KEY')
        env = env or os.getenv('PINECONE_ENVIRONMENT')
        
        if not api_key or not env:
            raise ValueError("Pinecone API key and environment are required.")
        
        pinecone_instance = Pinecone(api_key=api_key, environment=env)
        return pinecone_instance
    
    def load_fashion_dataset(self):
        fashion = load_dataset("ashraq/fashion-product-images-small", split="train")
        images = fashion["image"]
        metadata = fashion.remove_columns("image").to_pandas()
        return images, metadata
    
    def initialize_clip_model(self, device='cuda' if torch.cuda.is_available() else 'cpu'):
        model = SentenceTransformer('sentence-transformers/clip-ViT-B-32', device=device)
        return model
    
    def initialize_bm25_encoder(self, metadata):
        bm25 = BM25Encoder()
        bm25.fit(metadata['productDisplayName'])
        return bm25
    
    @staticmethod
    def hybrid_scale(dense, sparse, alpha=0.05):
        """Hybrid vector scaling using a convex combination

        alpha * dense + (1 - alpha) * sparse

        Args:
            dense: Array of floats representing
            sparse: a dict of `indices` and `values`
            alpha: float between 0 and 1 where 0 == sparse only
                and 1 == dense only
        """
        if alpha < 0 or alpha > 1:
            raise ValueError("Alpha must be between 0 and 1")
        
        # Scale sparse and dense vectors to create hybrid search vectors
        hsparse = {
            'indices': sparse['indices'],
            'values': [v * (1 - alpha) for v in sparse['values']]
        }
        hdense = [v * alpha for v in dense]
        
        return hdense, hsparse
    

if __name__ == "__main__":


    fashion_processor = SearchItem(api_key, env)
    
    query = "blue shoes"
    # create sparse and dense vectors
    sparse = fashion_processor.bm25.encode_queries(query)
    dense = fashion_processor.clip_model.encode(query).tolist()

    hdense, hsparse = fashion_processor.hybrid_scale(dense, sparse)

    result = fashion_processor.index.query(
        top_k=5,
        vector=hdense,
        sparse_vector=hsparse,
        include_metadata=True
    )

    imgs = [fashion_processor.images[int(r["id"])] for r in result["matches"]]

    print('Ok')
    # breakpoint()
