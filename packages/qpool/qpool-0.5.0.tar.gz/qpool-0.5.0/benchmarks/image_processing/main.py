import argparse
import asyncio
import json
import logging
import sys
from pathlib import Path
from multiprocessing import cpu_count
from typing import TYPE_CHECKING, Literal, Optional

import numpy as np
from pydantic import BaseModel, Field, conint

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))


from benchmarks.image_processing.concurrent_futures_pipeline import (
    run_concurrent_futures_image_pipeline,
)
from benchmarks.image_processing.wombat_pipeline import run_wombat_image_pipeline

if TYPE_CHECKING:
    pass


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# --- Configuration and Main Execution ---


class BenchmarkConfig(BaseModel):
    name: Optional[str] = None
    artifact_name: Optional[str] = None
    benchmark: Literal["image-pipeline", "image-pipeline-cf"] = "image-pipeline"
    workers: Optional[conint(ge=1)] = Field(default_factory=cpu_count)
    num_images: conint(ge=1) = 100
    image_size: tuple[int, int] = (64, 64)
    num_layers: conint(ge=1) = 10
    runs: conint(ge=1) = 1
    fair_mode: bool = True


def run_single_scenario(config: BenchmarkConfig):
    if config.benchmark == "image-pipeline":
        durations = []
        for i in range(config.runs):
            if config.runs > 1:
                logger.info(f"--- Run {i + 1}/{config.runs} ---")
            duration = asyncio.run(
                run_wombat_image_pipeline(
                    num_images=config.num_images,
                    num_workers=config.workers or cpu_count() or 1,
                    image_size=config.image_size,
                    num_layers=config.num_layers,
                    fair_mode=config.fair_mode,
                    benchmark_name=config.artifact_name or config.name,
                )
            )
            durations.append(duration)
        logger.info("--- Summary ---")
        logger.info(f"Image Pipeline Avg Duration: {np.mean(durations):.2f} seconds")
    elif config.benchmark == "image-pipeline-cf":
        durations = []
        for i in range(config.runs):
            if config.runs > 1:
                logger.info(f"--- Run {i + 1}/{config.runs} ---")
            duration = asyncio.run(
                run_concurrent_futures_image_pipeline(
                    num_images=config.num_images,
                    num_workers=config.workers or cpu_count() or 1,
                    image_size=config.image_size,
                    num_layers=config.num_layers,
                    benchmark_name=config.artifact_name or config.name,
                )
            )
            durations.append(duration)
        logger.info("--- Summary ---")
        logger.info(
            f"concurrent.futures Image Pipeline Avg Duration: {np.mean(durations):.2f} seconds"
        )
    else:
        logger.error(f"Unknown benchmark type: {config.benchmark}")
        return


def main():
    parser = argparse.ArgumentParser(
        description="Run benchmark scenarios for Wombat."
    )
    parser.add_argument(
        "--config",
        type=str,
        default="benchmarks/config.json",
        help="Path to the JSON configuration file.",
    )
    args = parser.parse_args()

    try:
        with open(args.config) as f:
            scenarios_data = json.load(f)
    except FileNotFoundError:
        logger.error(f"Configuration file not found at: {args.config}")
        return

    scenarios = [BenchmarkConfig(**data) for data in scenarios_data]

    for scenario in scenarios:
        if scenario.name:
            banner = f" Running Benchmark: {scenario.name} "
            logger.info(
                f"\n{'=' * ((80 - len(banner)) // 2)}{banner}{'=' * ((80 - len(banner)) // 2)}"
            )
        run_single_scenario(scenario)


if __name__ == "__main__":
    main()
