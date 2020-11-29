from urllib.parse import urlparse

from scoring.credibility_evaluation import evaluate_website


def start_service():
    print("alpaca init")
    handle_input()


def handle_input():
    """
    Waits for user input strings, verifies that they're valid web addresses
    and in that case initiates the scoring process for the website.
    Ends with user input "exit" or "quit".
    """
    while True:
        user_input = input("Enter address: ")
        if user_input.lower() in ["exit", "quit"]:
            break

        if user_input.__contains__(".") and not user_input.endswith("/"):
            user_input += "/"

        if valid_address(user_input):
            score = evaluate_website(user_input)
            print("Final score: {:.3f}".format(score))
        else:
            print("Invalid address.")


def valid_address(user_input: str) -> bool:
    """Checks whether the given string is a valid http or https URL."""
    try:
        result = urlparse(user_input)
        return all([result.scheme, result.netloc, result.path]) and result.scheme in ["http", "https"]
    except ValueError:
        return False


if __name__ == "__main__":
    start_service()
