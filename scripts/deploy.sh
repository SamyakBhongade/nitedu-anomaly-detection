#!/bin/bash
echo "Training models..."
python train_models.py

echo "Deploying Cloudflare Worker..."
cd cloudflare && wrangler deploy