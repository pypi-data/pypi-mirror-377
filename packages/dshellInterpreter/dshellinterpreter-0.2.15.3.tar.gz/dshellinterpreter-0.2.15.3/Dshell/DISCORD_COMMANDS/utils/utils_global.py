__all__ = [
    "utils_len",
]

async def utils_len(value):
    """
    Return the length of a list, or a string
    :param value:
    :return:
    """
    from ..._DshellParser.ast_nodes import ListNode
    if not isinstance(value, (str, ListNode)):
        raise TypeError(f"value must be a list or a string in len command, not {type(value)}")

    return len(value)