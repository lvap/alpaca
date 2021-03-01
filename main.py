from urllib.parse import urlparse

from scoring.credibility_evaluation import evaluate_website
from logger import log

# toggle some file-specific logging messages
LOGGING_ENABLED = True


def start_service():
    log("*** alpaca init", LOGGING_ENABLED)
    handle_input()


def handle_input():
    """Waits for user input strings, verifies that they're valid web addresses
    and in that case initiates the scoring process for the website.
    Ends with user input "exit" or "quit".
    """

    while True:
        user_input = input("\nEnter webpage address: ")
        if user_input.lower() in ["exit", "quit"]:
            log("*** alpaca end", LOGGING_ENABLED)
            break

        if valid_address(user_input):
            score = evaluate_website(user_input)
            if 0 <= score <= 1:
                print("Webpage score: {:.3f} for {}".format(score, user_input))
            else:
                print("Score could not be calculated.")
        else:
            print("Invalid address.")


def valid_address(user_input: str) -> bool:
    """Checks whether the given string is a valid http or https URL.

    :param user_input: String to be checked for valid http(s) URL syntax.
    :return: True if user_input is a valid http(s) URL, False otherwise.
    """

    try:
        result = urlparse(user_input)
        return all([result.scheme, result.netloc, result.path]) and result.scheme in ["http", "https"]
    except ValueError:
        return False


if __name__ == "__main__":
    start_service()
