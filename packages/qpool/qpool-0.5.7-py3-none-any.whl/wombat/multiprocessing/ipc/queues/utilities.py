from queue import Empty
from typing import Any, List, Type

from pydantic import BaseModel

from wombat.multiprocessing.ipc.queues.trait_queue import TraitQueue
from wombat.multiprocessing.traits.models import EOQ, Task, TaskResult


def rehydrate_model_from_dict(
    data_dict: dict, trait_registry: dict[str, Type[BaseModel]]
) -> BaseModel:
    """Reconstructs a Pydantic model from a dictionary received via IPC."""
    if data_dict.get("sentinel") == "EOQ":
        return EOQ()

    # Common logic for rehydrating traits within Task or TaskResult
    if "traits" in data_dict:
        instantiated_traits = []
        for trait_data in data_dict.get("traits", []):
            if isinstance(trait_data, dict):
                trait_name = trait_data.get("trait_name")
                if trait_registry and trait_name in trait_registry:
                    TraitModel = trait_registry[trait_name]
                    instantiated_traits.append(TraitModel.model_validate(trait_data))
                else:
                    # An unknown trait dictionary indicates a potential configuration mismatch
                    # between the sender and receiver. Instead of silently dropping it,
                    # we must raise an error to ensure data integrity.
                    raise TypeError(
                        f"Unknown trait '{trait_name}' encountered during deserialization. "
                        "Ensure this trait is registered on the receiving end."
                    )
            else:
                instantiated_traits.append(trait_data)
        data_dict["traits"] = instantiated_traits

    if "task_id" in data_dict:
        return TaskResult.model_validate(data_dict)

    if "action" in data_dict:
        # Task.create_with_traits also does validation and trait sorting
        return Task.create_with_traits(data_dict, trait_registry=trait_registry)

    return data_dict


def drain_queue_non_blocking(
    trait_queue: TraitQueue, trait_registry: dict[str, Any]
) -> List[BaseModel]:
    """
    Drains a queue of all currently available items, without blocking.
    Reconstructs Pydantic models from dictionaries if necessary.
    """
    results = []
    while True:
        try:
            result_data = trait_queue.get_nowait()
            if trait_queue.joinable:
                trait_queue.task_done()

            # Reconstruct model from dictionary if needed.
            if isinstance(result_data, dict):
                result = rehydrate_model_from_dict(result_data, trait_registry=trait_registry)
            else:
                result = result_data

            results.append(result)
        except Empty:
            break  # The queue is empty, so we're done.
    return results
