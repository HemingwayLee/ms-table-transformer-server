#!/bin/bash

echo "First arg: $1"

eval "$(conda shell.bash hook)"
conda activate venv

python /home/app/backend/src/inference.py --mode detect --detection_config_path detection_config.json --detection_model_path /home/app/backend/media/models/pubtables1m_detection_detr_r18.pth --detection_device cpu --image_dir /home/app/backend/media/images/$1 --out_dir /home/app/backend/media/results/ -o --crop_padding 20

