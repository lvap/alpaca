from urllib.parse import urlparse

from scoring.credibility_evaluation import evaluate_webpage
from logger import log

# toggle some file-specific logging messages
LOGGING_ENABLED = True


def start_service():
    log("[Main] Alpaca init", LOGGING_ENABLED)
    _handle_input()


def _handle_input():
    """Waits for and handles user input. If a valid webpage URL is submitted, retrieves and prints the webpage's
    credibility score. Exits on input **exit** or **quit**.
    """

    while True:
        user_input = input("\nEnter webpage address: ")

        if user_input.lower() in ["exit", "quit"]:
            log("[Main] Alpaca end", LOGGING_ENABLED)
            break

        if valid_address(user_input):
            score = evaluate_webpage(user_input)
            if 0 <= score <= 1:
                print("Webpage score: {:.3f} for {}".format(score, user_input))
            else:
                print("Score could not be calculated.")
                log("[Main] Illegal error score {}".format(score))

        else:
            print("Invalid address.")


def valid_address(user_input: str) -> bool:
    """Returns True if the given string is a valid http or https URL, False otherwise."""

    try:
        result = urlparse(user_input)
        return all([result.scheme, result.netloc, result.path]) and result.scheme in ["http", "https"]
    except ValueError:
        return False


if __name__ == "__main__":
    start_service()
