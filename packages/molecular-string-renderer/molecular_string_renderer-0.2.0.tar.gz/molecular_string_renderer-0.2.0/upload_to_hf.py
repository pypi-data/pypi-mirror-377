#!/usr/bin/env python3
"""
Upload molecular dataset to Hugging Face Hub.

This script uploads a CSV dataset containing molecular structures and their corresponding
images to Hugging Face Hub, making it suitable for training/evaluating vision language models.
"""

import logging
import pandas as pd
from pathlib import Path
from typing import Optional
import argparse
from PIL import Image
from datasets import Dataset, Features, Value, Image as DatasetImage
from huggingface_hub import login, HfApi

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('hf_upload.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def load_and_validate_dataset(csv_path: str) -> pd.DataFrame:
    """
    Load and validate the molecular dataset.
    
    Args:
        csv_path: Path to the CSV file containing molecular data
        
    Returns:
        Validated pandas DataFrame
        
    Raises:
        ValueError: If dataset validation fails
    """
    logger.info(f"Loading dataset from {csv_path}")
    
    if not Path(csv_path).exists():
        raise ValueError(f"CSV file not found: {csv_path}")
    
    df = pd.read_csv(csv_path)
    logger.info(f"Loaded {len(df)} rows from CSV")
    
    # Validate required columns
    required_columns = ['tranche', 'zincid', 'SMILES', 'SELFIES', 'InChI', 'InChIKey', 'image_path']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")
    
    # Check for missing values in critical columns
    critical_columns = ['SMILES', 'image_path']
    for col in critical_columns:
        missing_count = df[col].isna().sum()
        if missing_count > 0:
            logger.warning(f"Found {missing_count} missing values in column '{col}'")
    
    # Validate image paths exist
    base_path = Path(csv_path).parent
    missing_images = []
    for idx, row in df.head(100).iterrows():  # Check first 100 for performance
        img_path = base_path / row['image_path']
        if not img_path.exists():
            missing_images.append(str(img_path))
    
    if missing_images:
        logger.warning(f"Found {len(missing_images)} missing image files (checked first 100 rows)")
        logger.warning(f"Examples: {missing_images[:5]}")
    
    logger.info("Dataset validation completed")
    return df


def create_hf_dataset(df: pd.DataFrame, base_path: Path, sample_size: Optional[int] = None) -> Dataset:
    """
    Create a Hugging Face Dataset from the molecular DataFrame.
    
    Args:
        df: Pandas DataFrame with molecular data
        base_path: Base path for resolving image paths
        sample_size: Optional sample size for testing (None for full dataset)
        
    Returns:
        Hugging Face Dataset object
    """
    if sample_size:
        logger.info(f"Creating dataset with sample size: {sample_size}")
        df = df.sample(n=min(sample_size, len(df)), random_state=42).reset_index(drop=True)
    else:
        logger.info(f"Creating dataset with full size: {len(df)}")
    
    # Define dataset features
    features = Features({
        'tranche': Value('string'),
        'zincid': Value('string'),
        'smiles': Value('string'),
        'selfies': Value('string'),
        'inchi': Value('string'),
        'inchikey': Value('string'),
        'image': DatasetImage(),
    })
    
    # Prepare data for HF Dataset
    data = []
    failed_images = 0
    
    for idx, row in df.iterrows():
        try:
            img_path = base_path / row['image_path']
            
            # Load and validate image
            if img_path.exists():
                image = Image.open(img_path)
                # Convert to RGB if needed (some formats might be RGBA)
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                
                data.append({
                    'tranche': row['tranche'],
                    'zincid': row['zincid'],
                    'smiles': row['SMILES'],
                    'selfies': row['SELFIES'],
                    'inchi': row['InChI'],
                    'inchikey': row['InChIKey'],
                    'image': image,
                })
            else:
                logger.warning(f"Image not found: {img_path}")
                failed_images += 1
                
        except Exception as e:
            logger.error(f"Error processing row {idx}: {e}")
            failed_images += 1
        
        if (idx + 1) % 1000 == 0:
            logger.info(f"Processed {idx + 1}/{len(df)} rows")
    
    if failed_images > 0:
        logger.warning(f"Failed to process {failed_images} images")
    
    logger.info(f"Successfully processed {len(data)} samples")
    
    # Create Dataset
    dataset = Dataset.from_list(data, features=features)
    return dataset


def upload_to_hub(
    dataset: Dataset,
    dataset_name: str,
    organization: Optional[str] = None,
    private: bool = False,
    description: Optional[str] = None
) -> str:
    """
    Upload dataset to Hugging Face Hub.
    
    Args:
        dataset: Hugging Face Dataset to upload
        dataset_name: Name for the dataset on Hub
        organization: Optional organization name
        private: Whether to make dataset private
        description: Optional dataset description
        
    Returns:
        Dataset repository URL
    """
    # Create full dataset name
    if organization:
        full_name = f"{organization}/{dataset_name}"
    else:
        full_name = dataset_name
    
    logger.info(f"Uploading dataset to: {full_name}")
    
    # Create dataset card content
    if not description:
        description = """
# Molecular Structure Dataset

This dataset contains molecular structures in various string representations (SMILES, SELFIES, InChI) 
along with their corresponding 2D molecular structure images. It's designed for training and evaluating 
vision-language models on molecular understanding tasks.

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

## Citation

If you use this dataset, please cite the original ZINC database and the molecular string representations:

- ZINC Database: https://zinc.docking.org/
- SMILES: Weininger, D. (1988). SMILES, a chemical language and information system.
- SELFIES: Krenn, M., et al. (2020). Self-referencing embedded strings (SELFIES).
- InChI: Heller, S.R., et al. (2015). InChI, the IUPAC International Chemical Identifier.
"""
    
    # Upload dataset
    try:
        dataset.push_to_hub(
            full_name,
            private=private
        )
        
        # Create dataset card
        api = HfApi()
        
        # Create README content
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
- {"10K<n<100K" if len(dataset) < 100000 else "100K<n<1M"}
---

{description}

## Dataset Information

- **Total samples**: {len(dataset):,}
- **Image format**: PNG
- **Molecular representations**: SMILES, SELFIES, InChI, InChI Key
- **Source**: ZINC Database
"""
        
        try:
            api.upload_file(
                path_or_fileobj=readme_content.encode(),
                path_in_repo="README.md",
                repo_id=full_name,
                repo_type="dataset"
            )
            logger.info("✅ Dataset card created successfully")
        except Exception as e:
            logger.warning(f"Could not create dataset card: {e}")
        
        repo_url = f"https://huggingface.co/datasets/{full_name}"
        logger.info(f"Successfully uploaded dataset to: {repo_url}")
        return repo_url
        
    except Exception as e:
        logger.error(f"Failed to upload dataset: {e}")
        raise


def main():
    """Main function to orchestrate the upload process."""
    parser = argparse.ArgumentParser(description="Upload molecular dataset to Hugging Face Hub")
    
    parser.add_argument(
        "--csv-path",
        type=str,
        default="random_deduplicated_all_strs_img.csv",
        help="Path to CSV file containing molecular data"
    )
    
    parser.add_argument(
        "--dataset-name",
        type=str,
        required=True,
        help="Name for the dataset on Hugging Face Hub"
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
        "--sample-size",
        type=int,
        help="Sample size for testing (use full dataset if not specified)"
    )
    
    parser.add_argument(
        "--login",
        action="store_true",
        help="Prompt for Hugging Face login"
    )
    
    args = parser.parse_args()
    
    try:
        # Login to Hugging Face if requested
        if args.login:
            logger.info("Please log in to Hugging Face Hub")
            login()
        
        # Load and validate dataset
        df = load_and_validate_dataset(args.csv_path)
        
        # Create HF dataset
        base_path = Path(args.csv_path).parent
        dataset = create_hf_dataset(df, base_path, args.sample_size)
        
        # Upload to Hub
        repo_url = upload_to_hub(
            dataset,
            args.dataset_name,
            args.organization,
            args.private
        )
        
        logger.info("✅ Dataset upload completed successfully!")
        logger.info(f"📊 Dataset URL: {repo_url}")
        logger.info(f"📈 Total samples: {len(dataset)}")
        
    except Exception as e:
        logger.error(f"❌ Upload failed: {e}")
        raise


if __name__ == "__main__":
    main()
