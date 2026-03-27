"""Embedding pipeline — chunks documents and stores vectors in pgvector. Phase 2."""

from app.workers.celery_app import celery_app
import logging

logger = logging.getLogger(__name__)


@celery_app.task(name="app.workers.embedding_pipeline.embed_document")
def embed_document(document_id: str, document_type: str):
    logger.info(f"Embedding {document_type}:{document_id} — not yet implemented")
    return {"status": "not_implemented"}
