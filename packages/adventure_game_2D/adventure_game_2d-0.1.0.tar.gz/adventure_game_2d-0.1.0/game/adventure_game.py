"""Text-based adventure game."""

import time
from typing import Dict, Generator

import inquirer  # type: ignore
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()


def loader() -> None:
    """Loading screen."""
    with console.status("[bold green]Loading..."):
        for _ in range(10):
            time.sleep(0.1)


def legendary_loader() -> None:
    """Legendary loading screen."""
    console.print("[bold green]It is going to be legend---")

    with console.status("[bold green]Wait for it..."):
        for _ in range(10):
            time.sleep(0.3)

    console.print("[bold green]--dary!!\nLegendary🕴️")


def game_generator() -> Generator[str | Text, None, None]:
    """Manages the entire game.

    Yields:
        str | Text: Moves to other generator of the game.
    """
    console.print("====== Welcome to the adventure game =====", style="blue")

    console.print("General Instructions:", style="#528CD3")
    console.print("1.Always try to give the input correctly.", style="#528CD3")
    console.print("2.If want to quit at any point in time, press [Ctrl+C]", style="#528CD3")
    console.print("That's it enjoy the game folks.", style="#528CD3")

    legendary_loader()

    console.print(
        Panel("\nYou are in a middle of a magical forest🌳🌴🔮", title="Forest", style="green")
    )

    while True:
        try:
            direction = direction_generator()
            message = Text(
                """\nThere are two directions to go.
            \nNorth - There is a beautiful mountain.💀🌋
            \nSouth - There is a breezy river.🌊🏊""",
                style="#9700DE",
            )
            console.print(message)
            prompt = "Enter the direction, you are going: "
            input_direction = None

            if callable(inquirer.prompt):
                input_direction = inquirer.prompt(
                    [
                        inquirer.List(
                            "choice",
                            message=prompt,
                            choices=["North", "South"],
                        )
                    ]
                )

            try:
                yield next(direction)
                if isinstance(input_direction, Dict):
                    direction.send(input_direction["choice"])

                while True:
                    yield next(direction)

            except StopIteration:
                yield Text("\nCame back to selecting direction.⬆️", style="magenta")
                continue

        except ValueError:
            console.print("\nDirection has to be North or South!!!", style="yellow")


def direction_generator() -> Generator[str | Text, str, None]:
    """Controls the direction flow of the game.

    Yields:
        Generator[str, str, None]: Decides to move to north or south.
    """
    while True:
        direction = yield ""
        print(f"\nGoing in {direction}")

        loader()

        game = cave_generator() if direction.lower() == "north" else river_generator()
        try:
            while True:
                yield next(game)

        except StopIteration:
            break


def cave_generator() -> Generator[str | Text, None, None]:
    """Simulates the cave of the game.

    Yields:
        Generator[str, None, None]: Decides whether moves in or out.
    """
    while True:
        try:
            console.print(
                Panel(
                    "There is a dark and haunted cave ahead🌋.", title="Mountain", style="#964B00"
                )
            )
            prompt = "Do you want to enter it?"
            choice = None
            if callable(inquirer.prompt):
                choice = inquirer.prompt(
                    [
                        inquirer.List(
                            "choice",
                            message=prompt,
                            choices=["yes", "no"],
                        )
                    ]
                )
            treasure = treasure_generator()

            loader()

            if isinstance(choice, Dict):
                if choice["choice"] == "yes":
                    try:
                        while True:
                            yield next(treasure)

                    except StopIteration:
                        continue

                else:
                    break

        except ValueError:
            console.print("\nThe answer must be a yes or no!", style="yellow")
            continue


def treasure_generator() -> Generator[str | Text, None, None]:
    """SImulates the treasure.

    Raises:
        ValueError: When incorrect value is given.
        GeneratorExit: When the game finishes.

    Yields:
        Generator[str, None, None]: Prompts the user with the game flow.
    """
    while True:
        try:
            yield "\n"
            console.print(Panel("There is a shiny little chest🪙!!", title="Cave", style="#ffd700"))
            prompt = "Do you want to open it? "
            choice = None
            if callable(inquirer.prompt):
                choice = inquirer.prompt(
                    [
                        inquirer.List(
                            "choice",
                            message=prompt,
                            choices=["yes", "no"],
                        )
                    ]
                )

            loader()

            if isinstance(choice, Dict):
                if choice["choice"] == "yes":
                    legendary_loader()
                    yield Text("Congratulations, Theodore! You win!!!🥳💃🎉", style="green")
                    raise GeneratorExit()

                else:
                    yield Text("Going back to the cave🏔️", style="magenta")
                    break

        except ValueError:
            yield Text("The answer must be a yes or no!", style="yellow")


def river_generator() -> Generator[str | Text, None, None]:
    """Simulates the river.

    Yields:
        Generator[str, None, None]: Decides whether to move in to river or not.
    """
    while True:
        try:
            console.print(
                Panel(
                    "There is a calm and breezy river ahead🌊.", title="On the banks", style="blue"
                )
            )
            prompt = "Do you want to enter it?: "
            choice = None
            if callable(inquirer.prompt):
                choice = inquirer.prompt(
                    [
                        inquirer.List(
                            "choice",
                            message=prompt,
                            choices=["yes", "no"],
                        )
                    ]
                )
            swim = swim_generator()

            loader()

            if isinstance(choice, Dict):
                if choice["choice"] == "yes":
                    try:
                        while True:
                            yield next(swim)

                    except StopIteration:
                        continue

                else:
                    break

        except ValueError:
            console.print("The answer must be a yes or no!", style="yellow")
            continue


def swim_generator() -> Generator[str | Text, None, None]:
    """Simulates the swimming scenario.

    Raises:
        ValueError: Checks for the correct value.
        GeneratorExit: When the game finishes.

    Yields:
        Generator[str, None, None]: Prompts the user with the game flow.
    """
    while True:
        try:
            console.print(Panel("Entered the river", title="River", style="blue"))
            prompt = "Do you want swim in it🏊?: "
            choice = None
            if callable(inquirer.prompt):
                choice = inquirer.prompt(
                    [
                        inquirer.List(
                            "choice",
                            message=prompt,
                            choices=["yes", "no"],
                        )
                    ]
                )

            loader()

            if isinstance(choice, Dict):
                if choice["choice"] == "yes":
                    yield ""
                    yield Text("Damnit, Squid you lost!💀😐", style="red")
                    raise GeneratorExit()

                else:
                    yield ""
                    yield Text("Going out of the river.🌊", style="magenta")
                    break

        except ValueError as err:
            yield Text(f"{err}", style="yellow")


def run() -> None:
    """Runs the game."""
    game = game_generator()

    try:
        while True:
            console.print(next(game))

    except (KeyboardInterrupt, TypeError):
        print("\n\nThank you for playing, see you some other time.")

    except GeneratorExit:
        print("Thank you for playing!!")
        game.close()


if __name__ == "__main__":
    run()
