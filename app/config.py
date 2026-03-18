from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    host: str = "0.0.0.0"
    port: int = 8000

    # Paths (relative to project root)
    data_dir: Path = Path("data")
    incoming_dir: Path = Path("data/incoming")
    processed_dir: Path = Path("data/processed")
    results_dir: Path = Path("data/results")

    # Pipeline
    model_path: Path = Path("models/classify_model.onnx")

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    def ensure_dirs(self) -> None:
        """Create all required data directories."""
        for d in [self.incoming_dir, self.processed_dir, self.results_dir]:
            d.mkdir(parents=True, exist_ok=True)


settings = Settings()
