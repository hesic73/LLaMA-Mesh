#!/usr/bin/env python3
"""
Script to convert object descriptions to "Create a 3D mesh of XXX" format using OpenAI API.
"""

import json
import os
from pathlib import Path
import asyncio
from openai import AsyncOpenAI
from loguru import logger

# Initialize OpenAI client
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def convert_descriptions_batch(batch_items: list) -> dict:
    """Convert multiple descriptions at once using OpenAI API."""
    
    # Prepare the batch prompt
    batch_text = "You are tasked with converting object descriptions into a specific format for 3D mesh generation.\n\n"
    batch_text += "Convert each description to the format: \"Create a 3D mesh of [concise object description]\"\n\n"
    batch_text += "Guidelines:\n"
    batch_text += "1. Keep the description concise but descriptive\n"
    batch_text += "2. Focus on the key visual and structural features\n"
    batch_text += "3. Make it suitable for 3D mesh generation\n"
    batch_text += "4. Use clear, simple language\n"
    batch_text += "5. The description should be specific enough to generate a recognizable 3D model\n\n"
    batch_text += "Convert the following descriptions:\n\n"
    
    for name, description in batch_items:
        batch_text += f"{name}: {description}\n"
    
    batch_text += "\nReturn the results in the same order, one per line, with only the converted prompts (no object names)."

    try:
        response = await client.responses.create(
            model="gpt-5-nano-2025-08-07",  # Using GPT-5 nano
            reasoning={"effort": "low"},
            input=batch_text,
            max_output_tokens=1500,
        )
        
        converted_lines = response.output_text.split('\n')
        import ipdb; ipdb.set_trace()
        
        # Map results back to object names
        results = {}
        for i, (name, _) in enumerate(batch_items):
            if i < len(converted_lines):
                converted = converted_lines[i].strip()
                results[name] = converted
                logger.info(f"Converted {name}: {converted}")
            else:
                # Fallback if not enough results
                results[name] = f"Create a 3D mesh of {batch_items[i][1]}"
                logger.warning(f"Fallback for {name}")
        
        return results
        
    except Exception as e:
        logger.error(f"Error converting batch: {e}")
        # Fallback to simple format for all items
        results = {}
        for name, description in batch_items:
            results[name] = f"Create a 3D mesh of {description}"
        return results

async def convert_all_descriptions(input_file: str, output_file: str, batch_size: int = 10):
    """Convert all descriptions in the input file."""
    
    # Load input data
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    logger.info(f"Loaded {len(data)} descriptions from {input_file}")
    
    # Convert descriptions in batches
    converted_data = {}
    items = list(data.items())
    
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        logger.info(f"Processing batch {i//batch_size + 1}/{(len(items) + batch_size - 1)//batch_size} ({len(batch)} items)")
        
        # Process batch
        batch_results = await convert_descriptions_batch(batch)
        converted_data.update(batch_results)
        
        # Small delay to avoid rate limiting
        await asyncio.sleep(2)
    
    # Save converted data
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(converted_data, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Saved {len(converted_data)} converted descriptions to {output_file}")

def main():
    """Main function."""
    input_file = "objects_summary.json"
    output_file = "converted_prompts.json"
    
    # Check if input file exists
    if not Path(input_file).exists():
        logger.error(f"Input file {input_file} not found!")
        return
    
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        logger.error("OPENAI_API_KEY environment variable not set!")
        return
    
    logger.info("Starting description conversion...")
    
    # Run the conversion
    asyncio.run(convert_all_descriptions(input_file, output_file))
    
    logger.info("Conversion completed!")

if __name__ == "__main__":
    main()
