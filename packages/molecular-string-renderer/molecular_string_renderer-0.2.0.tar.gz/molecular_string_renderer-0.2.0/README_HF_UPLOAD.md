# Molecular Dataset Upload to Hugging Face Hub

This directory contains scripts to upload your molecular structure dataset to Hugging Face Hub for training/evaluating vision language models.

## Dataset Overview

Your dataset contains **~250k molecular structures** with:
- **SMILES** representations
- **SELFIES** representations  
- **InChI** and **InChIKey** identifiers
- **2D molecular structure images** (PNG format)
- **ZINC database** tranche and molecule IDs

## Quick Start

### 1. Install Dependencies

The required packages are already installed in your virtual environment:
- `huggingface_hub` - For uploading to HF Hub
- `datasets` - For creating HF Dataset format
- `pillow` - For image processing

### 2. Login to Hugging Face

First, you'll need a Hugging Face account and token:

```bash
# Option 1: Login interactively
python upload_to_hf.py --login

# Option 2: Set token as environment variable
export HUGGINGFACE_HUB_TOKEN="your_token_here"
```

### 3. Test Upload (Recommended)

Start with a small sample to test the process:

```bash
python upload_to_hf.py \
  --dataset-name "test-molecular-structures" \
  --sample-size 100 \
  --login
```

### 4. Full Dataset Upload

Once you're satisfied with the test:

```bash
python upload_to_hf.py \
  --dataset-name "zinc-molecular-structures-250k" \
  --login
```

### 5. Upload to Organization (Optional)

If you want to upload to an organization:

```bash
python upload_to_hf.py \
  --dataset-name "molecular-structures-250k" \
  --organization "your-org-name" \
  --login
```

## Command Line Options

```bash
python upload_to_hf.py [OPTIONS]

Options:
  --csv-path TEXT           Path to CSV file (default: random_deduplicated_all_strs_img.csv)
  --dataset-name TEXT       Name for dataset on HF Hub [REQUIRED]
  --organization TEXT       HF organization name (optional)
  --private                 Make dataset private
  --sample-size INTEGER     Sample size for testing (default: full dataset)
  --login                   Prompt for HF login
```

## Dataset Features

The uploaded dataset will have the following structure:

```python
{
    'tranche': string,      # ZINC tranche identifier
    'zincid': string,       # ZINC molecule identifier  
    'smiles': string,       # SMILES representation
    'selfies': string,      # SELFIES representation
    'inchi': string,        # InChI representation
    'inchikey': string,     # InChI Key
    'image': Image,         # 2D molecular structure (PIL Image)
}
```

## Use Cases

This dataset is perfect for:

1. **Vision-Language Model Training**
   - Text-to-image generation of molecular structures
   - Image-to-text generation of molecular representations
   - Multi-modal molecular understanding

2. **Molecular Property Prediction**
   - Cross-modal retrieval between text and images
   - Structure-activity relationship modeling

3. **Chemical Education and Research**
   - Molecular recognition tasks
   - Chemical structure validation

## Dataset Size and Performance

- **Full dataset**: ~250k samples (~several GB with images)
- **Recommended splits**: 
  - Train: 80% (~200k samples)
  - Validation: 10% (~25k samples)  
  - Test: 10% (~25k samples)

## Examples

### Loading the Dataset

```python
from datasets import load_dataset

# Load full dataset
dataset = load_dataset("your-username/zinc-molecular-structures-250k")

# Load specific split
train_data = load_dataset("your-username/zinc-molecular-structures-250k", split="train")

# Load sample for testing
sample = load_dataset("your-username/zinc-molecular-structures-250k", split="train[:100]")
```

### Accessing Data

```python
# Get first sample
sample = dataset['train'][0]

print(f"SMILES: {sample['smiles']}")
print(f"SELFIES: {sample['selfies']}")
print(f"ZINC ID: {sample['zincid']}")

# Display molecular image
sample['image'].show()
```

### Training Example

```python
from transformers import BlipProcessor, BlipForConditionalGeneration
from datasets import load_dataset

# Load model and processor
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

# Load dataset
dataset = load_dataset("your-username/zinc-molecular-structures-250k", split="train[:1000]")

# Process samples for training
def preprocess_function(examples):
    images = [example for example in examples["image"]]
    texts = [f"The SMILES representation is {smiles}" for smiles in examples["smiles"]]
    
    inputs = processor(images, texts, return_tensors="pt", padding=True)
    return inputs

processed_dataset = dataset.map(preprocess_function, batched=True)
```

## File Structure

```
molecular-string-renderer/
├── upload_to_hf.py                           # Main upload script
├── test_upload.py                            # Test script
├── random_deduplicated_all_strs_img.csv      # Your dataset
├── out/                                      # Image directory
│   ├── H27P170/
│   │   └── ZINCrn00000RPfL7.png
│   ├── H28P230/
│   │   └── ZINCst000007djlV.png
│   └── ...
└── README_HF_UPLOAD.md                       # This file
```

## Troubleshooting

### Common Issues

1. **Authentication Error**
   ```bash
   # Make sure you're logged in
   huggingface-cli login
   ```

2. **Large Dataset Upload**
   ```bash
   # For very large datasets, consider uploading in chunks
   python upload_to_hf.py --sample-size 50000 --dataset-name "molecular-chunk-1"
   ```

3. **Memory Issues**
   ```bash
   # Reduce sample size if running out of memory
   python upload_to_hf.py --sample-size 10000
   ```

4. **Missing Images**
   - Check that image paths in CSV are correct
   - Ensure `out/` directory structure matches CSV paths

### Monitoring Upload

The script provides detailed logging:
- Progress updates every 1000 samples
- Warning for missing images
- Final upload statistics

## Citation

If you use this dataset, please cite:

```bibtex
@dataset{zinc_molecular_structures_250k,
  title={ZINC Molecular Structures Dataset with 2D Images},
  author={Your Name},
  year={2025},
  publisher={Hugging Face Hub},
  url={https://huggingface.co/datasets/your-username/zinc-molecular-structures-250k}
}
```

Also consider citing the original sources:
- ZINC Database: https://zinc.docking.org/
- RDKit: https://www.rdkit.org/
- SELFIES: Krenn, M., et al. (2020)

## Support

For issues with the upload process, check:
1. Hugging Face Hub documentation
2. Datasets library documentation  
3. Your internet connection and disk space

Good luck with your upload! 🚀
