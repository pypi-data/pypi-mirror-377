import logging
import pathlib
import shutil
import tempfile
import time
from typing import Optional

import numpy as np
from PIL import Image

from benchmarks import tasks
from wombat.multiprocessing import (
    OrchestratorBuilder,
)
from wombat.multiprocessing.systems import DelayedSystem, ProducesSystem
from wombat.multiprocessing.ipc.buffer import BufferConfig
from wombat.multiprocessing.traits.lifecycle import Succeeded

logger = logging.getLogger(__name__)


async def run_wombat_image_pipeline(
    num_images: int,
    num_workers: int,
    image_size: tuple[int, int],
    num_layers: int,
    fair_mode: bool = True,
    benchmark_name: Optional[str] = None,
) -> float:
    """
    Runs a dynamic, multi-stage image processing benchmark using Wombat.

    This benchmark kicks off a series of producer tasks. Each task creates an
    image with a random control pixel, which dictates the first step in a
    multi-stage pipeline. Subsequent tasks are dynamically produced based on
    the evolving state of the image's control pixel.
    """
    logger.info("--- Running Wombat Dynamic Image Pipeline Benchmark ---")
    logger.info(
        f"Images: {num_images}, Workers: {num_workers}, Size: {image_size}, Layers: {num_layers}"
    )

    base_dir = tempfile.mkdtemp(prefix="wombat_benchmark_")
    initial_dir = pathlib.Path(base_dir) / "initial"
    transformed_dir = pathlib.Path(base_dir) / "transformed"
    initial_dir.mkdir()
    transformed_dir.mkdir()

    start_time = time.monotonic()

    try:
        builder = (
            OrchestratorBuilder()
            .with_workers(num_workers=num_workers)
            .with_actions(
                [
                    tasks.start_nebula_pipeline,
                    tasks.add_nebula_layer,
                    tasks.final_success_task,
                ]
            )
            .with_systems([ProducesSystem, DelayedSystem])
        )
        builder.without_logging().with_progress_bar(False).with_batch_config(
            BufferConfig(size=1.28e8)
        ).with_profiling()

        async with builder.build() as orchestrator:
            logger.info("Kicking off image processing pipeline...")
            initial_tasks = []
            for i in range(num_images):
                # Each pipeline starts with a unique file path.
                output_path = str(initial_dir / f"image_start_{i}.png")
                initial_tasks.append(
                    tasks.start_nebula_pipeline(
                        output_path=output_path,
                        size=image_size,
                        max_iterations=num_layers,
                    )
                )

            await orchestrator.add_tasks(initial_tasks)
            await orchestrator.finish_tasks()
            all_results = list(orchestrator.get_results())
            logger.info(f"Pipeline finished. Processed {len(all_results)} total tasks.")

        end_time = time.monotonic()

        # Phase 3: Create mosaic in the main thread
        logger.info("Phase 3: Assembling mosaic...")
        # A pipeline is successful if it ends with a successful `final_success_task`.
        # The result of that task is the path to the final image.
        final_image_files = [
            pathlib.Path(r.result)
            for r in all_results
            if r.action == tasks.final_success_task.action_name
            and any(isinstance(t, Succeeded) for t in r.traits)
            and r.result is not None
        ]

        if final_image_files:
            cols = int(np.ceil(np.sqrt(len(final_image_files))))
            rows = int(np.ceil(len(final_image_files) / cols))
            mosaic = Image.new("RGB", (cols * image_size[0], rows * image_size[1]))
            for i, img_path in enumerate(final_image_files):
                if not img_path.exists():
                    continue
                with Image.open(img_path) as img:
                    x, y = (i % cols) * image_size[0], (i // cols) * image_size[1]
                    img_to_paste = img.convert("RGB") if img.mode != "RGB" else img
                    mosaic.paste(img_to_paste, (x, y))
            if benchmark_name:
                artifacts_dir = (
                    pathlib.Path(__file__).parent.parent
                    / "artifacts"
                    / "wombat"
                    / benchmark_name
                )
                artifacts_dir.mkdir(parents=True, exist_ok=True)
                mosaic_path = artifacts_dir / "mosaic.png"
                mosaic.save(mosaic_path)
                logger.info(f"Phase 3: Mosaic saved to {mosaic_path}")
            else:
                # Fallback for safety, though name should always be provided.
                mosaic_path = pathlib.Path(base_dir) / "mosaic.png"
                mosaic.save(mosaic_path)
                logger.info(f"Phase 3: Mosaic saved to {mosaic_path}")

    finally:
        shutil.rmtree(base_dir)
        logger.info(f"Cleaned up temporary directory: {base_dir}")

    duration = end_time - start_time
    logger.info(f"[Image Pipeline] Total time: {duration:.2f} seconds")
    return duration
