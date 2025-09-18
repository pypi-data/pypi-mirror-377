import asyncio
import functools
import logging
import pathlib
import shutil
import tempfile
import time
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import get_context
from typing import Optional

import numpy as np
from PIL import Image

from benchmarks.tasks import (
    add_nebula_layer_cf,
    add_planetoid_cf,
    add_starburst_effect_cf,
    final_success_task_cf,
    start_nebula_pipeline_cf,
)

logger = logging.getLogger(__name__)


# A mapping of function names to actual functions for the CF benchmark
CF_ACTION_REGISTRY = {
    "start_nebula_pipeline_cf": start_nebula_pipeline_cf,
    "add_nebula_layer_cf": add_nebula_layer_cf,
    "add_starburst_effect_cf": add_starburst_effect_cf,
    "add_planetoid_cf": add_planetoid_cf,
    "final_success_task_cf": final_success_task_cf,
}


async def run_concurrent_futures_image_pipeline(
    num_images: int,
    num_workers: int,
    image_size: tuple[int, int],
    num_layers: int,
    benchmark_name: Optional[str] = None,
) -> float:
    """
    Runs the image processing benchmark using concurrent.futures.ProcessPoolExecutor.

    This version demonstrates how a dynamic pipeline must be orchestrated manually
    from the main process when not using a framework with dynamic task production
    capabilities like Wombat.
    """
    logger.info("--- Running concurrent.futures Dynamic Image Pipeline Benchmark ---")
    logger.info(
        f"Images: {num_images}, Workers: {num_workers}, Size: {image_size}, Layers: {num_layers}"
    )

    base_dir = tempfile.mkdtemp(prefix="cf_benchmark_")
    initial_dir = pathlib.Path(base_dir) / "initial"
    transformed_dir = pathlib.Path(base_dir) / "transformed"
    initial_dir.mkdir()
    transformed_dir.mkdir()

    final_image_files = []
    loop = asyncio.get_running_loop()
    start_time = time.monotonic()

    try:
        with ProcessPoolExecutor(
            max_workers=num_workers, mp_context=get_context("spawn")
        ) as executor:
            # The orchestrator now has to manually track the state of each pipeline.
            futures = set()
            for i in range(num_images):
                output_path = str(initial_dir / f"image_start_{i}.png")
                # Wrap the blocking submit call to run in the event loop's executor
                p_func = functools.partial(
                    start_nebula_pipeline_cf,
                    output_path=output_path,
                    size=image_size,
                    max_iterations=num_layers,
                )
                future = loop.run_in_executor(executor, p_func)
                futures.add(future)

            tasks_in_flight = num_images

            while tasks_in_flight > 0:
                # Wait for the next future to complete
                done, futures = await asyncio.wait(
                    futures, return_when=asyncio.FIRST_COMPLETED
                )

                for future in done:
                    result = await future
                    tasks_in_flight -= 1  # One task step completed

                    if result is None:
                        # File not found, pipeline terminates.
                        continue

                    # The worker function returns the next action(s) to take.
                    # It can be a single final task (str), a single next action (tuple),
                    # or a list of next actions (list of tuples).
                    next_actions = []
                    if isinstance(result, str):
                        # This was a final_success_task, the result is the path.
                        final_image_files.append(pathlib.Path(result))
                    elif isinstance(result, list):
                        # A list of next actions to take.
                        next_actions.extend(result)
                    elif isinstance(result, tuple):
                        # A single next action.
                        next_actions.append(result)

                    for action in next_actions:
                        next_action_name, kwargs = action
                        next_func = CF_ACTION_REGISTRY[next_action_name]

                        # Submit the next step of the pipeline
                        p_func = functools.partial(next_func, **kwargs)
                        new_future = loop.run_in_executor(executor, p_func)
                        futures.add(new_future)
                        tasks_in_flight += 1  # A new task step was added

        end_time = time.monotonic()

        # Phase 3: Create mosaic in the main thread (same as wombat version)
        logger.info("Phase 3: Assembling mosaic...")
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
                    / "concurrent_futures"
                    / benchmark_name
                )
                artifacts_dir.mkdir(parents=True, exist_ok=True)
                mosaic_path = artifacts_dir / "mosaic.png"
                mosaic.save(mosaic_path)
                logger.info(f"Phase 3: Mosaic saved to {mosaic_path}")
            else:
                mosaic_path = pathlib.Path(base_dir) / "mosaic.png"
                mosaic.save(mosaic_path)
                logger.info(f"Phase 3: Mosaic saved to {mosaic_path}")

    finally:
        shutil.rmtree(base_dir)
        logger.info(f"Cleaned up temporary directory: {base_dir}")

    duration = end_time - start_time
    logger.info(
        f"[concurrent.futures Image Pipeline] Total time: {duration:.2f} seconds"
    )
    return duration
