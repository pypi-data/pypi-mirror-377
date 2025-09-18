def quack_node(user_input: str, duck) -> str:
    return f"Quack! You said: {user_input}"

NODES = {
    "quack_node": quack_node
}
