"""Core functions for loading and processing AFMImageStacks."""

from pathlib import Path

from playNano.afm_stack import AFMImageStack
from playNano.errors import LoadError
from playNano.processing.pipeline import ProcessingPipeline


def process_stack(
    input_path: Path,
    channel: str,
    steps: list[tuple[str, dict]],
) -> AFMImageStack:
    """
    Load an AFMImageStack, apply the given steps, and return it.

    Raises LoadError on load failure.
    """
    try:
        stack = AFMImageStack.load_data(input_path, channel=channel)
    except Exception as e:
        raise LoadError(f"Failed to load {input_path}") from e

    pipeline = ProcessingPipeline(stack)
    for name, kwargs in steps:
        if name == "clear":
            pipeline.clear_mask()
        elif name == "mask":
            pipeline.add_mask(name, **kwargs)
        else:
            pipeline.add_filter(name, **kwargs)
    pipeline.run()
    return stack
