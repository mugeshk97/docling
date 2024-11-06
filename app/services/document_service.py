import logging
import tempfile

import psutil
import requests

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def process_document(url: str):
    from app.config import doc_converter
    
    response = requests.get(url)
    response.raise_for_status()

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        temp_file.write(response.content)
        temp_path = temp_file.name
        logging.info(f"Downloaded file saved to: {temp_path}")

    process = psutil.Process()
    initial_memory = process.memory_info().rss / (1024 * 1024)
    logging.info(f"Initial memory usage: {initial_memory:.2f} MB")

    try:
        # Use the pre-initialized doc_converter
        result = doc_converter.convert(temp_path)
        final_memory = process.memory_info().rss / (1024 * 1024)
        logging.info(f"Final memory usage: {final_memory:.2f} MB")
        logging.info(f"Memory change: {final_memory - initial_memory:.2f} MB")

        return result

    except Exception as e:
        logging.error(f"Error processing document: {str(e)}")
        raise e

    finally:
        import os
        try:
            os.remove(temp_path)
        except OSError as cleanup_error:
            logging.warning(f"Failed to delete temporary file: {cleanup_error}")
