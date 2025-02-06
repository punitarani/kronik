from typing import Optional

from .client import client, logger


async def embed_text(text: str) -> Optional[list[float]]:
    logger.debug(f"Embedding text: {text[12:]}")
    result = await client.aio.models.embed_content(model="text-embedding-004", content=text)
    return result.embeddings[0].values


async def embed_texts(texts: list[str]) -> list[Optional[list[float]]]:
    logger.debug(f"Embedding texts: {', '.join([text[12:] for text in texts])}")
    result = await client.aio.models.embed_content(model="text-embedding-004", content=texts)
    return [embedding.values for embedding in result.embeddings]
