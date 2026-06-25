from master_node2 import app


def run(user_request: str) -> str:
    """
    Execute a user request through the multi-agent graph and return
    the final answer as a string.
    """
    result = app.invoke({"user_request": user_request})
    messages = result.get("messages", [])
    if messages:
        return messages[-1].content

    return str(result.get("query_result", "No answer returned."))



if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        print(run(query))
        sys.exit(0)

    print("Multi-agent assistant ready. Type 'exit' to quit.\n")
    while True:
        try:
            query = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break

        if not query:
            continue
        if query.lower() in {"exit", "quit"}:
            print("Goodbye.")
            break

        answer = run(query)
        print(f"Assistant: {answer}\n")