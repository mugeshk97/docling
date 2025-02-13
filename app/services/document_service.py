import asyncio
import logging
import os
import tempfile

import aiohttp
import psutil
from pypdf import PdfReader, PdfWriter

from app.config import doc_converter  # Ensure this is pre-initialized

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Limit the number of concurrent tasks (e.g., 3 at a time)
SEMAPHORE = asyncio.Semaphore(3)


async def download_pdf(url: str) -> str:
    """Download PDF and save to a temporary file."""
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            response.raise_for_status()
            content = await response.read()

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        temp_file.write(content)
        return temp_file.name


def split_pdf(pdf_path: str, chunk_size: int = 10) -> list[str]:
    """Split the PDF into chunks of `chunk_size` pages."""
    reader = PdfReader(pdf_path)
    total_pages = len(reader.pages)
    temp_files = []

    for i in range(0, total_pages, chunk_size):
        writer = PdfWriter()
        for j in range(i, min(i + chunk_size, total_pages)):
            writer.add_page(reader.pages[j])

        temp_chunk = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        with open(temp_chunk.name, "wb") as f:
            writer.write(f)
        temp_files.append(temp_chunk.name)

    return temp_files


async def process_chunk(chunk_path: str, index: int) -> tuple[int, str]:
    """Process a single PDF chunk and return its markdown with index, limiting concurrency."""
    async with SEMAPHORE:  # Limit concurrent execution
        result = await asyncio.to_thread(doc_converter.convert, chunk_path)
        os.remove(chunk_path)  # Clean up temp file after processing
        return index, result.document.export_to_markdown()


async def process_document(url: str) -> str:
    """Download, split, process concurrently with limited workers, and return Markdown."""
    pdf_path = await download_pdf(url)
    process = psutil.Process()
    initial_memory = process.memory_info().rss / (1024 * 1024)
    logging.info(f"Initial memory usage: {initial_memory:.2f} MB")

    try:
        chunks = split_pdf(pdf_path)
        tasks = [process_chunk(chunk, i) for i, chunk in enumerate(chunks)]
        results = await asyncio.gather(*tasks)  # Process with concurrency control

        # Sort results by chunk index and merge into one document
        markdown_output = "\n\n".join(text for _, text in sorted(results))

        final_memory = process.memory_info().rss / (1024 * 1024)
        logging.info(f"Final memory usage: {final_memory:.2f} MB")
        logging.info(f"Memory change: {final_memory - initial_memory:.2f} MB")

        return markdown_output

    except Exception as e:
        logging.error(f"Error processing document: {str(e)}")
        raise e

    finally:
        os.remove(pdf_path)  # Cleanup original file
