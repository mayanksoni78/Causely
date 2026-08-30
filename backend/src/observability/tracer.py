from datetime import datetime
from dataclasses import dataclass, field

@dataclass
class StepTrace:
    step_name: str
    started_at: datetime
    ended_at: datetime
    inputs: dict
    outputs: dict
    notes: list[str] = field(default_factory=list)

    def to_dict(self):
        return [
            {
                "step_name": self.step_name,
                "started_at": self.started_at.isoformat(),
                "ended_at": self.ended_at.isoformat(),
                "inputs": self.inputs,
                "outputs": self.outputs,
                "notes": self.notes,
            }
        ]

class InvestigationTrace:
    def __init__(self):
        self.steps: list[StepTrace] = []

    def add_step(self, step: StepTrace):
        self.steps.append(step)

    def to_dict(self):
        return [
            {
                "step_name": s.step_name,
                "started_at": s.started_at.isoformat(),
                "ended_at": s.ended_at.isoformat(),
                "inputs": s.inputs,
                "outputs": s.outputs,
                "notes": s.notes,
            }
            for s in self.steps
        ]
