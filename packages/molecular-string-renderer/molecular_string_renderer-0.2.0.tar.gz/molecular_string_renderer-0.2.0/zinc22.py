#!/usr/bin/env python3
"""
Script to process a CSV file and generate molecular structure images.

This script reads a CSV file containing molecular data, generates images for each
molecule using the molecular-string-renderer library, and creates a new CSV with
image paths added.
"""

import logging
import sys
from pathlib import Path
import pandas as pd
from tqdm import tqdm
import random
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor, as_completed

from molecular_string_renderer import render_molecule, RenderConfig


def setup_logging() -> None:
    """Configure logging for the script."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("csv_image_generation.log")
        ]
    )


def create_output_directory(output_dir: Path) -> None:
    """Create the output directory if it doesn't exist.
    
    Args:
        output_dir: Path to the output directory
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    logging.info(f"Created output directory: {output_dir}")


def create_randomized_render_config() -> tuple[RenderConfig, dict[str, any]]:
    """Create a RenderConfig with comprehensive randomization.
    
    Returns:
        Tuple of (RenderConfig with randomized parameters, metadata dict)
    """
    # Default values for reference
    defaults = {
        "width": 512,
        "height": 512,
        "background_color": "#ffffff",
        "atom_label_font_size": 12,
        "bond_line_width": 2.0,
        "dpi": 150,
        "show_hydrogen": False,
        "show_carbon": False
    }
    
    # 1. Random image dimensions (reasonable range for molecular structures)
    width = random.choice([256, 384, 512, 640, 768])
    height = width  # Keep square aspect ratio
    
    # 2. Random background colors - avoid colors that conflict with atom labels
    # Atom label colors: C=black, O=red, N=blue, S=yellow, P=orange, etc.
    # Safe backgrounds: whites, light greys, very light blues/greens
    bg_options = [
        # Whites and light greys
        *[f"#{v:02x}{v:02x}{v:02x}" for v in range(240, 256)],  # Light greys to white
        # Very light blues (avoid confusion with nitrogen)
        "#f0f8ff", "#f5f5ff", "#fafafa", "#f8f8ff",
        # Very light greens (safe from common atom colors)
        "#f0fff0", "#f5fffa", "#fafffa",
        # Very light yellows (be careful with sulfur, but these are very pale)
        "#fffffe", "#fffffa", "#fefefe"
    ]
    background_color = random.choice(bg_options)
    
    # 3. Random font size (reasonable range for readability)
    # font_size = random.randint(8, 20)
    font_size = 12
    
    # 4. Random bond line width
    # bond_width = random.uniform(0.8, 4.0)
    bond_width = 2.0
    
    # 5. Random DPI (affects image quality/sharpness)
    dpi = random.choice([72, 96, 150, 200, 300])
    
    # 6. Random binary choices for atom labeling
    # show_hydrogen = random.choice([True, False])
    show_hydrogen = False
    
    show_carbon = random.choice([True, False])
    
    # 7. Random binary choice for antialiasing
    antialias = random.choice([True, False])
    
    # Create metadata to track what was randomized
    metadata = {
        "width": width,
        "height": height,
        "background_color": background_color,
        "atom_label_font_size": font_size,
        "bond_line_width": round(bond_width, 2),
        "dpi": dpi,
        "show_hydrogen": show_hydrogen,
        "show_carbon": show_carbon,
        "antialias": antialias,
        # Track deltas from defaults
        "font_size_delta": font_size - defaults["atom_label_font_size"],
        "bond_width_delta": round(bond_width - defaults["bond_line_width"], 2),
        "size_factor": width / defaults["width"],
        "dpi_factor": dpi / defaults["dpi"]
    }
    
    config = RenderConfig(
        width=width,
        height=height,
        background_color=background_color,
        atom_label_font_size=font_size,
        bond_line_width=bond_width,
        dpi=dpi,
        antialias=antialias,
        show_hydrogen=show_hydrogen,
        show_carbon=show_carbon
    )
    
    return config, metadata


def render_single_molecule(args: tuple[str, str, int]) -> tuple[int, bool, str, dict[str, any] | None]:
    """Render a single molecule with comprehensive randomization.
    
    Args:
        args: Tuple of (smiles, output_path, row_index)
        
    Returns:
        Tuple of (row_index, success, error_message, metadata_dict)
    """
    smiles, output_path, row_idx = args
    
    try:
        # Create directory if it doesn't exist
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Create randomized render config for this molecule
        render_config, metadata = create_randomized_render_config()
        
        image = render_molecule(
            smiles,
            format_type="smiles",
            output_format="png",
            render_config=render_config,
            auto_filename=False  # Prevent automatic file saving
        )
        image.save(output_path)
        
        # Add the actual file path to metadata
        metadata["image_path"] = output_path
        
        return (row_idx, True, "", metadata)
    except Exception as e:
        return (row_idx, False, str(e), None)


def generate_image_path(row: pd.Series, output_dir: Path) -> str:
    """Generate the image path for a given row.
    
    Args:
        row: Pandas Series containing the row data
        output_dir: Path to the output directory
        
    Returns:
        String path to the image file
    """
    tranche = row.get("tranche", "unknown")
    zinc_id = row.get("zincid", "unknown")
    tranche_dir = output_dir / tranche
    filename = f"{zinc_id}.png"
    return str(tranche_dir / filename)


def process_csv_file(
    input_csv_path: str,
    output_csv_path: str,
    output_dir: str = "out",
    smiles_column: str = "smiles",
    max_workers: int = None
) -> None:
    """Process CSV file and generate molecular images in parallel.
    
    Args:
        input_csv_path: Path to the input CSV file
        output_csv_path: Path to the output CSV file
        output_dir: Directory to save images
        smiles_column: Name of the column containing SMILES strings
        max_workers: Maximum number of parallel workers (default: CPU count)
    """
    # Setup
    setup_logging()
    logging.info("Starting CSV image generation process")
    
    # Set default number of workers
    if max_workers is None:
        max_workers = min(8, (mp.cpu_count() or 1))  # Cap at 8 to avoid overwhelming
    
    logging.info(f"Using {max_workers} parallel workers")
    
    # Validate input file
    input_path = Path(input_csv_path)
    if not input_path.exists():
        logging.error(f"Input CSV file not found: {input_csv_path}")
        sys.exit(1)
    
    # Create output directory
    output_path = Path(output_dir)
    create_output_directory(output_path)
    
    # Read CSV
    logging.info(f"Reading CSV file: {input_csv_path}")
    try:
        df = pd.read_csv(input_csv_path)
        logging.info(f"Loaded {len(df)} rows from CSV")
    except Exception as e:
        logging.error(f"Failed to read CSV file: {e}")
        sys.exit(1)
    
    # Validate required columns
    required_columns = [smiles_column, "tranche", "zincid"]
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        logging.error(f"Missing required columns: {missing_columns}")
        sys.exit(1)
    
    # Add columns for tracking randomization metadata
    df["image_path"] = ""
    df["render_width"] = 0
    df["render_height"] = 0
    df["render_background_color"] = ""
    df["render_font_size"] = 0
    df["render_font_size_delta"] = 0
    df["render_bond_width"] = 0.0
    df["render_bond_width_delta"] = 0.0
    df["render_dpi"] = 0
    df["render_dpi_factor"] = 0.0
    df["render_show_hydrogen"] = True
    df["render_show_carbon"] = False
    df["render_antialias"] = True
    df["render_size_factor"] = 0.0
    
    # Prepare tasks for parallel processing (one task per molecule)
    tasks = []
    
    for idx, row in df.iterrows():
        smiles = row[smiles_column]
        
        # Skip if SMILES is empty or NaN
        if pd.isna(smiles) or smiles == "":
            logging.warning(f"Row {idx}: Empty SMILES string, skipping")
            continue
        
        # Generate image path
        image_path = generate_image_path(row, output_path)
        df.at[idx, "image_path"] = image_path
        
        # Check if image already exists
        if Path(image_path).exists():
            logging.debug(f"Image already exists: {image_path}")
            continue
        
        # Add to tasks
        tasks.append((smiles, image_path, idx))
    
    logging.info(f"Processing {len(tasks)} molecules")
    logging.info(f"Skipping {len(df) - len(tasks)} molecules with existing images")
    
    # Process tasks in parallel with progress bar
    successful_renders = 0
    failed_renders = 0
    
    if tasks:
        logging.info("Starting parallel image generation...")
        
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_task = {executor.submit(render_single_molecule, task): task for task in tasks}
            
            # Process completed tasks with progress bar
            with tqdm(total=len(tasks), desc="Generating images", unit="molecules") as pbar:
                for future in as_completed(future_to_task):
                    row_idx, success, error_msg, metadata = future.result()
                    
                    if success and metadata:
                        successful_renders += 1
                        logging.debug(f"Successfully rendered molecule at row {row_idx}")
                        
                        # Store metadata directly in DataFrame
                        df.at[row_idx, "render_width"] = metadata["width"]
                        df.at[row_idx, "render_height"] = metadata["height"]
                        df.at[row_idx, "render_background_color"] = metadata["background_color"]
                        df.at[row_idx, "render_font_size"] = metadata["atom_label_font_size"]
                        df.at[row_idx, "render_font_size_delta"] = metadata["font_size_delta"]
                        df.at[row_idx, "render_bond_width"] = metadata["bond_line_width"]
                        df.at[row_idx, "render_bond_width_delta"] = metadata["bond_width_delta"]
                        df.at[row_idx, "render_dpi"] = metadata["dpi"]
                        df.at[row_idx, "render_dpi_factor"] = metadata["dpi_factor"]
                        df.at[row_idx, "render_show_hydrogen"] = metadata["show_hydrogen"]
                        df.at[row_idx, "render_show_carbon"] = metadata["show_carbon"]
                        df.at[row_idx, "render_antialias"] = metadata["antialias"]
                        df.at[row_idx, "render_size_factor"] = metadata["size_factor"]
                    else:
                        failed_renders += 1
                        logging.error(f"Failed to render molecule at row {row_idx}: {error_msg}")
                    
                    pbar.update(1)
    else:
        logging.info("No new molecules to process")
        # Count existing images
        successful_renders = len(df[df["image_path"] != ""])
    
    # Save updated CSV
    logging.info(f"Saving updated CSV to: {output_csv_path}")
    try:
        df.to_csv(output_csv_path, index=False)
        logging.info(f"Successfully saved CSV with {len(df)} rows")
    except Exception as e:
        logging.error(f"Failed to save CSV file: {e}")
        sys.exit(1)
    
    # Summary
    total_processed = successful_renders + failed_renders
    logging.info("="*50)
    logging.info("PROCESSING COMPLETE")
    logging.info(f"Total molecules in CSV: {len(df)}")
    logging.info(f"Molecules processed: {total_processed}")
    logging.info(f"Successful renders: {successful_renders}")
    logging.info(f"Failed renders: {failed_renders}")
    if total_processed > 0:
        logging.info(f"Success rate: {successful_renders/total_processed*100:.1f}%")
    logging.info(f"Output CSV: {output_csv_path}")
    logging.info(f"Images directory: {output_dir}")
    logging.info("Each molecule has comprehensive randomization across all render parameters")
    logging.info("="*50)


def main() -> None:
    """Main entry point for the script."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Generate molecular structure images from CSV data with parallelization and randomization"
    )
    parser.add_argument(
        "input_csv",
        help="Path to input CSV file"
    )
    parser.add_argument(
        "-o", "--output",
        default="random_deduplicated_all_strs_img.csv",
        help="Output CSV filename (default: random_deduplicated_all_strs_img.csv)"
    )
    parser.add_argument(
        "-d", "--output-dir",
        default="out",
        help="Output directory for images (default: out)"
    )
    parser.add_argument(
        "-s", "--smiles-column",
        default="SMILES",
        help="Name of SMILES column (default: SMILES)"
    )
    parser.add_argument(
        "-w", "--workers",
        type=int,
        default=None,
        help="Number of parallel workers (default: auto-detect, max 8)"
    )
    
    args = parser.parse_args()
    
    process_csv_file(
        input_csv_path=args.input_csv,
        output_csv_path=args.output,
        output_dir=args.output_dir,
        smiles_column=args.smiles_column,
        max_workers=args.workers
    )


if __name__ == "__main__":
    # Required for multiprocessing on Windows
    mp.set_start_method('spawn', force=True)
    main()