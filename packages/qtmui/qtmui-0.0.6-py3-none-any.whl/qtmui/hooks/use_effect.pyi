import inspect
from typing import Callable, List
from .use_state import State
from cython import cfunc
def useEffect(callback: Callable, dependencies: List[State]): ...