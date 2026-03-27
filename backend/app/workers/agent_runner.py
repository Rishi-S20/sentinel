"""Agent runner — executes the belief update cycle for due agents. Phase 3."""

from app.workers.celery_app import celery_app
import logging

logger = logging.getLogger(__name__)


@celery_app.task(name="app.workers.agent_runner.run_due_agents")
def run_due_agents():
    logger.info("Agent runner running — not yet implemented")
    return {"status": "not_implemented"}


@celery_app.task(name="app.workers.agent_runner.run_single_agent")
def run_single_agent(agent_id: str):
    logger.info(f"Running agent {agent_id} — not yet implemented")
    return {"status": "not_implemented"}
