#!/usr/bin/env python3
"""
Upload molecular dataset to Hugging Face Hub in chunks to handle memory limitations.
"""

import logging
import pandas as pd
from pathlib import Path
import argparse
from datasets import Dataset, Features, Value, Image as DatasetImage, concatenate_datasets
from huggingface_hub import login, HfApi
from PIL import Image
import gc

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('hf_upload_chunks.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def create_chunk_dataset(df_chunk: pd.DataFrame, base_path: Path, chunk_num: int) -> Dataset:
    """
    Create a Hugging Face Dataset from a chunk of the molecular DataFrame.
    
    Args:
        df_chunk: Pandas DataFrame chunk with molecular data
        base_path: Base path for resolving image paths
        chunk_num: Chunk number for logging
        
    Returns:
        Hugging Face Dataset object
    """
    logger.info(f"📦 Processing chunk {chunk_num} with {len(df_chunk)} samples")
    
    # Define dataset features
    features = Features({
        'tranche': Value('string'),
        'zincid': Value('string'),
        'smiles': Value('string'),
        'selfies': Value('string'),
        'inchi': Value('string'),
        'inchikey': Value('string'),
        'image': DatasetImage(),
        # Comprehensive render randomization metadata
        'render_width': Value('int32'),
        'render_height': Value('int32'),
        'render_background_color': Value('string'),
        'render_font_size': Value('int32'),
        'render_font_size_delta': Value('int32'),
        'render_bond_width': Value('float32'),
        'render_bond_width_delta': Value('float32'),
        'render_dpi': Value('int32'),
        'render_dpi_factor': Value('float32'),
        'render_show_hydrogen': Value('bool'),
        'render_show_carbon': Value('bool'),
        'render_antialias': Value('bool'),
        'render_size_factor': Value('float32'),
    })
    
    # Prepare data for HF Dataset
    data = []
    failed_images = 0
    
    for idx, row in df_chunk.iterrows():
        try:
            img_path = base_path / row['image_path']
            
            # Load and validate image
            if img_path.exists():
                image = Image.open(img_path)
                # Convert to RGB if needed
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                
                data.append({
                    'tranche': str(row['tranche']),
                    'zincid': str(row['zincid']),
                    'smiles': str(row['SMILES']),
                    'selfies': str(row['SELFIES']),
                    'inchi': str(row['InChI']),
                    'inchikey': str(row['InChIKey']),
                    'image': image,
                    # Comprehensive render randomization metadata
                    'render_width': int(row.get('render_width', 512)),
                    'render_height': int(row.get('render_height', 512)),
                    'render_background_color': str(row.get('render_background_color', '')),
                    'render_font_size': int(row.get('render_font_size', 12)),
                    'render_font_size_delta': int(row.get('render_font_size_delta', 0)),
                    'render_bond_width': float(row.get('render_bond_width', 2.0)),
                    'render_bond_width_delta': float(row.get('render_bond_width_delta', 0.0)),
                    'render_dpi': int(row.get('render_dpi', 150)),
                    'render_dpi_factor': float(row.get('render_dpi_factor', 1.0)),
                    'render_show_hydrogen': bool(row.get('render_show_hydrogen', True)),
                    'render_show_carbon': bool(row.get('render_show_carbon', False)),
                    'render_antialias': bool(row.get('render_antialias', True)),
                    'render_size_factor': float(row.get('render_size_factor', 1.0)),
                })
            else:
                logger.warning(f"Image not found: {img_path}")
                failed_images += 1
                
        except Exception as e:
            logger.error(f"Error processing row {idx}: {e}")
            failed_images += 1
    
    if failed_images > 0:
        logger.warning(f"📊 Chunk {chunk_num}: Failed to process {failed_images} images")
    
    logger.info(f"✅ Chunk {chunk_num}: Successfully processed {len(data)} samples")
    
    # Create Dataset
    dataset = Dataset.from_list(data, features=features)
    
    # Force garbage collection
    del data
    gc.collect()
    
    return dataset


def upload_in_chunks(
    csv_path: str,
    dataset_name: str,
    chunk_size: int = 25000,
    organization: str = None,
    private: bool = False
) -> str:
    """
    Upload dataset in chunks to handle memory limitations.
    
    Args:
        csv_path: Path to CSV file
        dataset_name: Name for the dataset on Hub
        chunk_size: Number of samples per chunk
        organization: Optional organization name
        private: Whether to make dataset private
        
    Returns:
        Dataset repository URL
    """
    base_path = Path(csv_path).parent
    
    # Create full dataset name
    if organization:
        full_name = f"{organization}/{dataset_name}"
    else:
        full_name = dataset_name
    
    logger.info(f"🚀 Starting chunked upload to: {full_name}")
    logger.info(f"📊 Chunk size: {chunk_size:,} samples")
    
    # Read CSV in chunks
    chunk_datasets = []
    chunk_num = 1
    
    try:
        # Process CSV in chunks
        for chunk_df in pd.read_csv(csv_path, chunksize=chunk_size):
            logger.info(f"🔄 Processing chunk {chunk_num}...")
            
            # Create dataset from chunk
            chunk_dataset = create_chunk_dataset(chunk_df, base_path, chunk_num)
            chunk_datasets.append(chunk_dataset)
            
            # Log progress
            total_processed = chunk_num * chunk_size
            logger.info(f"📈 Progress: {total_processed:,} samples processed")
            
            chunk_num += 1
        
        # Concatenate all chunks
        logger.info(f"🔗 Combining {len(chunk_datasets)} chunks...")
        final_dataset = concatenate_datasets(chunk_datasets)
        
        # Clear chunk datasets from memory
        del chunk_datasets
        gc.collect()
        
        logger.info(f"✅ Final dataset created with {len(final_dataset):,} samples")
        
        # Upload to Hub
        logger.info("☁️ Uploading to Hugging Face Hub...")
        final_dataset.push_to_hub(full_name, private=private)
        
        # Create dataset card
        api = HfApi()
        readme_content = f"""---
title: {dataset_name}
tags:
- chemistry
- molecules
- vision-language
- smiles
- selfies
- inchi
task_categories:
- image-to-text
- text-to-image
language:
- en
size_categories:
- {"100K<n<1M" if len(final_dataset) < 1000000 else "1M<n<10M"}
---

# ZINC Molecular Structures Dataset

This dataset contains {len(final_dataset):,} molecular structures from the ZINC database with their corresponding 2D molecular images.
It's designed for training and evaluating vision-language models on molecular understanding tasks.

## Dataset Structure

- **tranche**: ZINC database tranche identifier
- **zincid**: ZINC database molecule identifier  
- **smiles**: SMILES representation of the molecule
- **selfies**: SELFIES representation of the molecule
- **inchi**: InChI representation of the molecule
- **inchikey**: InChI Key of the molecule
- **image**: 2D molecular structure image (PNG format)

## Use Cases

- Vision-language model training for molecular understanding
- Multi-modal molecular property prediction
- Molecular structure recognition and generation
- Cross-modal retrieval between molecular text and images

## Loading the Dataset

```python
from datasets import load_dataset

# Load full dataset
dataset = load_dataset("{full_name}")

# Load specific split
train_data = load_dataset("{full_name}", split="train")

# Load sample for testing
sample = load_dataset("{full_name}", split="train[:100]")
```

## Citation

If you use this dataset, please cite the original ZINC database and molecular string representations.
"""
        
        try:
            api.upload_file(
                path_or_fileobj=readme_content.encode(),
                path_in_repo="README.md",
                repo_id=full_name,
                repo_type="dataset"
            )
            logger.info("📝 Dataset card created successfully")
        except Exception as e:
            logger.warning(f"Could not create dataset card: {e}")
        
        repo_url = f"https://huggingface.co/datasets/{full_name}"
        logger.info(f"🎉 Successfully uploaded dataset to: {repo_url}")
        return repo_url
        
    except Exception as e:
        logger.error(f"❌ Upload failed: {e}")
        raise


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Upload molecular dataset in chunks")
    
    parser.add_argument(
        "--csv-path",
        type=str,
        default="random_deduplicated_all_strs_img.csv",
        help="Path to CSV file"
    )
    
    parser.add_argument(
        "--dataset-name",
        type=str,
        required=True,
        help="Name for the dataset on Hugging Face Hub"
    )
    
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=25000,
        help="Number of samples per chunk (default: 25000)"
    )
    
    parser.add_argument(
        "--organization",
        type=str,
        help="Hugging Face organization name (optional)"
    )
    
    parser.add_argument(
        "--private",
        action="store_true",
        help="Make dataset private"
    )
    
    parser.add_argument(
        "--login",
        action="store_true",
        help="Prompt for Hugging Face login"
    )
    
    args = parser.parse_args()
    
    try:
        # Login if requested
        if args.login:
            logger.info("Please log in to Hugging Face Hub")
            login()
        
        # Upload in chunks
        repo_url = upload_in_chunks(
            args.csv_path,
            args.dataset_name,
            args.chunk_size,
            args.organization,
            args.private
        )
        
        logger.info("✅ Dataset upload completed successfully!")
        logger.info(f"📊 Dataset URL: {repo_url}")
        
    except Exception as e:
        logger.error(f"❌ Upload failed: {e}")
        raise


if __name__ == "__main__":
    main()
