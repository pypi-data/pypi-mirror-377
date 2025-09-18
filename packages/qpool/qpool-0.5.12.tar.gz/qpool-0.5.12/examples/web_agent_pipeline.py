import asyncio
import logging
import re
import uuid
from typing import Any, List

import aiohttp
from wombat.multiprocessing import (
    OrchestratorBuilder,
    Prop,
    consumes,
    produces,
    requires_props,
    tagged,
    task,
)
from wombat.multiprocessing.systems import ConsumesSystem, ProducesSystem
from wombat.multiprocessing.traits.models import Task
from wombat.multiprocessing.worker import Worker


# 1. Define an initializer for a shared HTTP client Prop.
#    This will be created once per worker process.
async def initialize_http_session():
    """Initializes an aiohttp.ClientSession."""
    return aiohttp.ClientSession()


# --- Agent Task Actions ---

# 2. Define the different agent roles as task functions.

@requires_props(requires_props=["http_session"])
@tagged(tags=["placeholder"])  # Tag is a placeholder, overridden at runtime.
@task
async def fetch_content_agent(worker: Worker, url: str, props: dict[str, Any]) -> str:
    """Agent that fetches the title of a web page."""
    worker.log(f"Fetching title for URL: {url}", logging.INFO)
    http_session: aiohttp.ClientSession = props["http_session"].instance
    try:
        async with http_session.get(url, timeout=10) as response:
            response.raise_for_status()
            text = await response.text()
            # Simple regex to extract the title for demonstration purposes.
            match = re.search(r"<title>(.*?)</title>", text, re.IGNORECASE)
            title = match.group(1).strip() if match else "No title found"
            return f'Content from "{url}": {title}'
    except Exception as e:
        return f'Failed to fetch "{url}": {e!s}'


@tagged(tags=["placeholder"])
@task
def content_task(_worker: Worker, text: str) -> str:
    """A simple task to carry the non-URL text through the system."""
    return text


@consumes(tags=["placeholder"], batch_size=1)  # Placeholder values.
@task
def rebuild_prompt_agent(
    _worker: Worker, consumed_results: List[str] | None = None
) -> str:
    """Agent that reassembles the final prompt from all consumed parts."""
    # The results may arrive out of order, so a simple join is sufficient
    # for this demonstration.
    if consumed_results is None:
        return ""  # Should not happen in a successful run.
    return "\n".join(consumed_results)


@produces
@task
def extract_urls_agent(_worker: Worker, prompt: str) -> List[Task]:
    """
    Agent that extracts URLs from a prompt and produces new tasks.
    It acts as the orchestrator for this sub-workflow.
    """
    # A unique ID to correlate all tasks related to this single prompt.
    correlation_id = str(uuid.uuid4())

    # Find all URLs and the remaining text.
    url_pattern = r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
    urls = re.findall(url_pattern, prompt)
    non_url_text = re.sub(url_pattern, "[WEB CONTENT]", prompt)

    # Create a `fetch_content_agent` for each URL found.
    web_tasks = [
        fetch_content_agent(url=url, tags=[correlation_id]) for url in urls
    ]

    # Create a simple task to hold the non-URL text part.
    text_task = content_task(text=non_url_text, tags=[correlation_id])

    # The total number of results to consume is the text part + all web parts.
    total_parts = len(web_tasks) + 1

    # Dynamically create the final consumer agent, setting its `batch_size` and
    # `tags` to match this specific job.
    rebuilder_agent = rebuild_prompt_agent(
        tags=[correlation_id], batch_size=total_parts
    )

    return web_tasks + [text_task, rebuilder_agent]


# 3. Build and run the Orchestrator.
async def main():
    logging_config = {"to_console": True, "level": logging.INFO}

    builder = (
        OrchestratorBuilder()
        .with_workers(num_workers=4)
        .with_actions(
            [
                extract_urls_agent,
                fetch_content_agent,
                content_task,
                rebuild_prompt_agent,
            ]
        )
        .with_systems([ProducesSystem, ConsumesSystem])
        .with_props(
            {
                "http_session": Prop(
                    initializer=initialize_http_session, use_context_manager=True
                )
            }
        )
        .with_logging(logging_config)
    )

    async with builder.build() as orchestrator:
        while True:
            try:
                prompt = input(
                    "\nEnter a prompt with URLs (e.g., 'Summarize https://google.com and https://wombat-multiprocessing.com') or press Enter to quit:\n> "
                )
                if not prompt:
                    break

                # The entire workflow is started by this single task.
                await orchestrator.add_task(extract_urls_agent(prompt=prompt))
                await orchestrator.finish_tasks()

                print("\n--- Rebuilt Prompt ---")
                for result in orchestrator.get_results():
                    print(result.result)

            except (KeyboardInterrupt, EOFError):
                break


if __name__ == "__main__":
    # To run this example:
    # 1. Install dependencies: pip install aiohttp
    # 2. Run the script: python examples/web_agent_pipeline.py
    asyncio.run(main())
