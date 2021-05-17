from logger import log
from parsing.webpage_parser import valid_address
from scoring.credibility_evaluation import evaluate_webpage

# toggle some file-specific logging messages
LOGGING_ENABLED = True


def start_service():
    log("[Main] Alpaca init", LOGGING_ENABLED)
    _handle_input()


def _handle_input():
    """Waits for and handles user input. If a valid webpage URL is submitted, retrieves and prints the webpage's
    credibility score. Terminates on input **exit** or **quit**.
    """

    while True:
        user_input = input("\nEnter webpage address: ")

        if user_input.lower() in ["exit", "quit"]:
            log("[Main] Alpaca end", LOGGING_ENABLED)
            break

        if valid_address(user_input):
            score = evaluate_webpage(user_input)
            if 0 <= score <= 1:
                print("Webpage score: {:.5f} for {}".format(score, user_input))
            else:
                print("Score could not be calculated")

        else:
            print("Invalid address")


if __name__ == "__main__":
    start_service()
