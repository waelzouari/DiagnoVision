from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class Prediction:
    outcome: str
    horizon: str
    value: float
    model_version: str
    limitations: list[str]

class PredictiveModel(ABC):
    @abstractmethod
    def predict(self, features: dict[str, float | None]) -> Prediction: ...

class NoModelAvailable(PredictiveModel):
    def predict(self, features: dict[str, float | None]) -> Prediction:
        raise RuntimeError("No clinically validated predictive model is configured")

