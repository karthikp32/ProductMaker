import logging
from typing import Dict, Any
from infrastructure.event_bus import EventBus

logger = logging.getLogger(__name__)

class Orchestrator:
    """
    The central manager that coordinates agents and enforces governance.
    """
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.running_experiments: Dict[str, Any] = {}
        self._setup_governance()

    def _setup_governance(self):
        """
        Subscribe to critical events to enforce rules.
        """
        self.event_bus.subscribe("EXPERIMENT_STARTED", self._on_experiment_start)
        self.event_bus.subscribe("BUDGET_REQUESTED", self._check_budget)

    def _on_experiment_start(self, payload: Any):
        exp_id = payload.get("experiment_id")
        logger.info(f"Orchestrator: Tracking new experiment {exp_id}")
        self.running_experiments[exp_id] = {"status": "RUNNING", "budget_spent": 0}

    def _check_budget(self, payload: Any):
        """
        Governance Check: Hard stop if budget exceeded.
        """
        exp_id = payload.get("experiment_id")
        amount = payload.get("amount_cents", 0)
        
        # In a real impl, fetch limit from DB
        limit = 20000 # $200.00
        
        current_spend = self.running_experiments.get(exp_id, {}).get("budget_spent", 0)
        
        if current_spend + amount > limit:
            logger.error(f"Orchestrator: BUDGET EXCEEDED for {exp_id}. Denying request.")
            self.event_bus.publish("BUDGET_DENIED", {"experiment_id": exp_id})
        else:
            logger.info(f"Orchestrator: Budget approved for {exp_id}")
            self.running_experiments[exp_id]["budget_spent"] = current_spend + amount
            self.event_bus.publish("BUDGET_APPROVED", {"experiment_id": exp_id})

    def start(self):
        """
        Kick off the system.
        """
        logger.info("Orchestrator started. System ready.")
        self.event_bus.publish("SYSTEM_START", {})
