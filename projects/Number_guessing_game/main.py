import random

# Game configuration. The secret number is drawn from [LOW, HIGH] and the
# player gets MAX_ATTEMPTS valid guesses before the game ends.
LOW = 1
HIGH = 9
MAX_ATTEMPTS = 5


def compare_guess(guess, secret):
    """Compare a guess against the secret number.

    Returns "correct", "low" or "high". Pure function (no I/O) so the core
    game logic can be unit-tested and reused.
    """
    if guess == secret:
        return "correct"
    if guess < secret:
        return "low"
    return "high"


def parse_guess(raw, low=LOW, high=HIGH):
    """Turn raw user input into a valid integer guess.

    Raises ValueError with a friendly message when the input is empty, not a
    whole number, or outside the allowed range.
    """
    text = raw.strip()
    if not text:
        raise ValueError("Looks like you didn't type anything. "
                         f"Please enter a number between {low} and {high}.")
    try:
        guess = int(text)
    except ValueError:
        raise ValueError(f'"{text}" is not a whole number. '
                         f"Please enter a number between {low} and {high}.")
    if not low <= guess <= high:
        raise ValueError(f"{guess} is out of range. "
                         f"Please enter a number between {low} and {high}.")
    return guess


def read_guess(low=LOW, high=HIGH):
    """Prompt until the user provides a valid guess and return it as an int.

    Invalid inputs are reported gently and re-prompted; they do not count as
    attempts. Returns None if the input stream is closed (e.g. Ctrl+D).
    """
    while True:
        try:
            raw = input("Your guess: ")
        except EOFError:
            return None
        try:
            return parse_guess(raw, low, high)
        except ValueError as error:
            print(error)


def _attempts_label(count):
    """Return '1 attempt' or 'N attempts' for nicer output."""
    return f"{count} attempt" if count == 1 else f"{count} attempts"


def play_game(low=LOW, high=HIGH, max_attempts=MAX_ATTEMPTS, secret=None):
    """Run one round of the game.

    Returns a tuple (won, attempts, secret). ``secret`` can be passed in to
    make the round deterministic (useful for tests); otherwise it is chosen
    at random.
    """
    if secret is None:
        secret = random.randint(low, high)

    print("Number guessing game")
    print(f"Guess the number between {low} and {high}. "
          f"You have {max_attempts} tries.")

    attempts = 0
    while attempts < max_attempts:
        guess = read_guess(low, high)
        if guess is None:  # input stream closed; stop the round
            print("\nNo more input. Ending the game.")
            return False, attempts, secret

        attempts += 1
        result = compare_guess(guess, secret)

        if result == "correct":
            print(f"CONGRATULATIONS! You guessed the number {secret} "
                  f"in {_attempts_label(attempts)}!")
            return True, attempts, secret

        remaining = max_attempts - attempts
        hint = "higher" if result == "low" else "lower"
        if remaining > 0:
            print(f"Too {result}: try a {hint} number. "
                  f"{_attempts_label(remaining)} left.")
        else:
            print(f"Too {result}.")

    print(f"Out of tries! The number was {secret}. Better luck next time!")
    return False, attempts, secret


def main():
    play_game()


if __name__ == "__main__":
    main()
