import random

MAX_ATTEMPTS = 5
MIN_NUMBER = 1
MAX_NUMBER = 9


def get_valid_guess():
    """Prompt the user until a valid integer within [MIN_NUMBER, MAX_NUMBER] is entered."""
    while True:
        raw = input(f"Guess a number (between {MIN_NUMBER} and {MAX_NUMBER}): ").strip()
        if not raw:
            print("Empty input. Please enter a whole number.")
            continue
        try:
            guess = int(raw)
        except ValueError:
            print(f"Invalid input '{raw}'. Please enter a whole number.")
            continue
        if guess < MIN_NUMBER or guess > MAX_NUMBER:
            print(
                f"{guess} is out of range. "
                f"Please enter a number between {MIN_NUMBER} and {MAX_NUMBER}."
            )
            continue
        return guess


def play_game():
    """Run one round of the guessing game. Return True if the player wins."""
    number = random.randint(MIN_NUMBER, MAX_NUMBER)

    print("Number Guessing Game")
    print(
        f"You have {MAX_ATTEMPTS} attempts to guess "
        f"the number between {MIN_NUMBER} and {MAX_NUMBER}."
    )

    for attempt in range(1, MAX_ATTEMPTS + 1):
        guess = get_valid_guess()

        if guess == number:
            print(
                f"Congratulations! You guessed the number {number} "
                f"in {attempt} attempt(s)!"
            )
            return True

        if guess < number:
            print(f"Your guess was too low. Guess a number higher than {guess}.")
        else:
            print(f"Your guess was too high. Guess a number lower than {guess}.")

        remaining = MAX_ATTEMPTS - attempt
        if remaining > 0:
            print(f"Attempts remaining: {remaining}")

    print(
        f"Game over! You have used all {MAX_ATTEMPTS} attempts. "
        f"The number was {number}."
    )
    return False


def main():
    """Entry point: run the game and offer a replay."""
    while True:
        play_game()
        again = input("Play again? (y/n): ").strip().lower()
        if again != "y":
            print("Thanks for playing!")
            break


if __name__ == "__main__":
    main()
