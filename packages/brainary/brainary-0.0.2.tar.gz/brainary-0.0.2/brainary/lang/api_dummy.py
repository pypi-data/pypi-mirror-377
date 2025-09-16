from typing import Any, Callable, List, Dict, Union, Optional

def type(**fields: Dict[str, Dict[str, Any]]) -> Any:
    """
    Dynamically defines a structured data type (class) with named fields and metadata, suitable for use in promptware workflows or schema definitions.

    Args:
        **fields: Each keyword argument defines a field, where:
            - The key is the field name (str).
            - The value is a dictionary containing:
                - "type": the expected Python type (or nested promptware type).
                - "desc": a human-readable description.
                - Optionally: "default" or other metadata.

    Returns:
        A new class with:
            - Strict field validation on initialization.
            - Field access via attributes.
            - `.to_dict()` method for serialization.
            - `.schema()` method to inspect field metadata.

    Example:
        >>> Review = promptware.type(
        ...     text={"type": str, "desc": "review content"},
        ...     author={"type": str, "desc": "reviewer name"}
        ... )
        >>> Movie = promptware.type(
        ...     title={"type": str, "desc": "movie title"},
        ...     year={"type": int, "desc": "release year"},
        ...     reviews={"type": list[Review], "desc": "list of Review objects"}
        ... )
        >>> m = Movie(
        ...     title='Matrix',
        ...     year=1999,
        ...     reviews=[Review(text="Amazing!", author="Bob")]
        ... )
        >>> print(m.title)  # 'Matrix'
        >>> print(m.to_dict())  # {'title': 'Matrix', 'year': 1999, 'reviews': [...]}
    """
    pass


def action(
    instruction: str,
    *params: str,
    executable: Optional[Callable[..., Any]] = None,
    contexts: Optional[List[Any]] = None,
    constraints: Optional[List[Dict[str, Any]]] = None,
    callbacks: Optional[List[Callable[[Any], Any]]] = None,
) -> Any:
    """
    Creates an Action object with a natural language instruction, named parameters, and optional logic encapsulated via an executable hook, constraints, and post-processing.

    Args:
        instruction (str): A LLM-readable instruction describing the action.
        *params (str): Names of required input parameters.
        executable (callable, optional): A function implementing the action logic.
            If provided, it will be called with the given parameters during execution.
        contexts (list, optional): Additional context objects or data influencing the action.
        constraints (list of dict, optional): Rules to validate input parameters (e.g., word limits).
        callbacks (list of callable, optional): Functions to post-process the result.

    Returns:
        A callable Action object with a `.__call__(**kwargs)` method that executes the action. The provided **kwargs must align with the declared `*params` in both name and structure.

    Example:
        >>> Review = promptware.type(text={"type": str, "desc": "review"}, author={"type": str, "desc": "reviewer"})
        >>> Movie = promptware.type(
        ...     title={"type": str, "desc": "movie title"},
        ...     year={"type": int, "desc": "release year"},
        ...     reviews={"type": list[Review], "desc": "list of reviews"}
        ... )
        >>> summarize = promptware.action("Summarize the review", "text", constraints=[{"words": 50}])
        >>> summaries = [summarize(text=r.text) for r in movie.reviews]
    """
    pass


def tool(
    instruction: str,
    *params: str,
) -> Any:
    """
    Defines a tool-like callable object and its required parameters. Useful for external tool or API calls in promptware workflows.

    Args:
        instruction (str): A natural language instruction representing the tool's behavior.
        *params (str): Required input parameter names for the tool.

    Returns:
         A callable Tool object with a `.__call__(**kwargs)` method that executes the action. The provided `**kwargs` must align with the declared `*params` in both name and structure.

    Example:
        >>> get_weather = promptware.tool("Get the weather", "city")
        >>> response = get_weather(city="New York")
        >>> print(response)
    """
    pass


def context(value: Union[str, Dict[str, Any]]) -> Any:
    """
    Defines a reusable context.

    Args:
        value (str or dict): A string (raw instruction) or dictionary (structured context) that represents reusable prompt metadata or guidance for an LLM.

    Returns:
        A context object or formatted string for internal use.

    Example:
        >>> cutoff = promptware.context({"cutoff_year": "2023"})
        >>> language = promptware.context("The given input is written in Chinese")
    """
    pass


def constraint(value: Union[str, Dict[str, Any]]) -> Any:
    """
    Defines a constraint.

    Args:
        value (str or dict): A string (raw instruction) or dictionary (structured context) that represents constraint for an action or object.

    Returns:
        A constraint object or formatted string for internal use.

    Example:
        >>> word_limit = promptware.constraint({"word number": 50})
        >>> language = promptware.constraint("The output should be in Chinese")
    """
    pass



def loop(iterable: Union[str, list, tuple]) -> Any:
    """
    Wraps an iterable or iterable description into a loop structure suitable for use in a promptware.

    Args:
        iterable (str | list | tuple): Either a string describing the iterable (e.g., "a list of API calls") or an actual iterable like a list or tuple.

    Returns:
        A loop wrapper object for promptware systems.

    Example:
        >>> m = Movie(
        ...     title='Matrix',
        ...     year=1999,
        ...     reviews=[Review(text="Amazing!", author="Bob")]
        ... )
        >>> for review in promptware.loop(m.reviews):
        >>>     print(item)
    """
    pass


def judge(condition: str) -> bool:
    """
    Defines a conditional logic unit for control flow in promptware.

    Args:
        condition (str): A natural language or logical condition that the LLM
                         or system will evaluate to True or False.

    Returns:
        A bool variable for decision-making in prompt flow.

    Example:
        >>> if promptware.judge("The API call returns 'Alice'."):
        >>>     print("Positive")
    """
    pass


def exception(desc: str) -> Any:
    """
    Defines a structured exception block for representing a failure, warning,
    or recoverable error in a promptware execution flow.

    Args:
        desc (str): A natural language description of the error condition to handle.

    Returns:
        dict: A structured exception representation for downstream control flow.

    Example:
        >>> try:
        >>>     do_something()
        >>> except promptware.exception("API call fails") as e:
        >>>     retry(e)
    """
    pass


def roleplay(role: str) -> Dict[str, str]:
    """
    Assigns a persona, identity, or behavioral context to the model.

    Args:
        role (str): A natural language description of the model's role or persona.

    Returns:
        dict: A structured role descriptor for use in prompt-based systems.

    Example:
        >>> advisor = promptware.roleplay("You are a legal advisor.")
        >>> print(advisor)
        {'type': 'roleplay', 'role': 'You are a legal advisor.'}
    """
    pass


def examples(example_list: List[Dict[str, Any]]) -> Any:
    """
    Creates a structured set of few-shot examples for in-context learning,
    typically used to guide LLM behavior.

    Args:
        example_list (List[Dict[str, Any]]): 
            A list of example dictionaries, each containing 'input' and 'output' keys.

    Returns:
        dict: A structured object representing reusable few-shot examples.

    Example:
        >>> ex = promptware.examples([
        >>>     {"input": "2 + 2", "output": "4"},
        >>>     {"input": "3 * 5", "output": "15"}
        >>> ])
    """
    pass



import inspect
import sys

API_TABLE = {}
for name, func in inspect.getmembers(sys.modules[__name__], inspect.isfunction):
    signature = inspect.signature(func)
    docstring = inspect.getdoc(func)
    API_TABLE[name] = (f"{name}{signature}", docstring)

API_SPEC = "\n\n".join(f'- {func}:\n"""\n{doc}\n"""' for func, doc in API_TABLE.values())