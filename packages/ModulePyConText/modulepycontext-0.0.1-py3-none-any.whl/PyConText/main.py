# Imports
import os
import shutil
import keyboard
from ctypes import wintypes
import ctypes


# Define required structures
class COORD(ctypes.Structure):
    _fields_ = [("X", wintypes.SHORT),
                ("Y", wintypes.SHORT)]

class SMALL_RECT(ctypes.Structure):
    _fields_ = [("Left", wintypes.SHORT),
                ("Top", wintypes.SHORT),
                ("Right", wintypes.SHORT),
                ("Bottom", wintypes.SHORT)]

class CONSOLE_SCREEN_BUFFER_INFO(ctypes.Structure):
    _fields_ = [("dwSize", COORD),
                ("dwCursorPosition", COORD),
                ("wAttributes", wintypes.WORD),
                ("srWindow", SMALL_RECT),
                ("dwMaximumWindowSize", COORD)]


# Console functions
class Console():

    @staticmethod
    def get_size() -> tuple:
        """
        Returns the size of the terminal as a named tuple of two integers, columns and lines.

        Parameters
        ----------
        None
        
        Returns
        -------
        collections.namedtuple
            A named tuple of two integers, columns and lines.
        """
        width, height = shutil.get_terminal_size()
        return int(width), int(height)

    @staticmethod
    def clear() -> None:
        """
        Clears the console screen.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        os.system("cls" if os.name == "nt" else "clear")


# Cursor functions
class Cursor():

    @staticmethod
    def move(x:int=0, y:int=0) -> None:
        """
        Moves the cursor to a given position

        Parameters
        ----------
        x : int
            The x position of the cursor starting from 0
        y : int
            The y position of the cursor starting from 0

        Returns
        -------
        None
        """
        print(f"\033[{y};{x}H", end="")
        return

    @staticmethod
    def get_cursor_position() -> tuple:
        """
        Requests the current position of the cursor from the terminal and returns it as a tuple of two integers, the row and column of the cursor.

        Parameters
        ----------
        None

        Returns
        -------
        tuple
            A named tuple of two integers, the row and column of the cursor. If the operation is unsupported returns None.
        """
        h = ctypes.windll.kernel32.GetStdHandle(-11)
        csbi = CONSOLE_SCREEN_BUFFER_INFO()
        success = ctypes.windll.kernel32.GetConsoleScreenBufferInfo(h, ctypes.byref(csbi))
        
        if not success:
            return None
        
        return csbi.dwCursorPosition.Y + 1, csbi.dwCursorPosition.X + 1


# Widget functions
class Widget():

    @staticmethod
    def input(prompt: str, end: str = ": ", erase: bool = True) -> str:
        """
        Reads input from the user and returns it as a string.

        Parameters
        ----------
        prompt : str
            The text to display to the user before reading input
        end : str
            The string to append to the end of the prompt, defaults to ": "
        erase : bool
            Whether to erase the input line after reading, defaults to True

        Returns
        -------
        str
            The input from the user as a string
        """
        input_val = input(prompt+end)
        print("\033[1A\033[2K" if erase else "", end="")
        return input_val

    @staticmethod
    def radio(options: list, selection_character: chr = "*", unselection_character: chr = " ") -> str:
        """
        Creates a radio button menu from a given list of options

        Parameters
        ----------
        options : list
            A list of strings to be used as the options
        selection_character : chr
            The character to use to mark the selected option, defaults to "*"
        unselection_character : chr
            The character to use to mark the unselected options, defaults to " "

        Returns
        -------
        str
        """
        select = 0
        choosing = True

        print("\033[1A\033[2K"*(len(options)+1), end="")
        for i, option in enumerate(options):
            print(f"[{selection_character if i == select else unselection_character}] {option}")

        starting_y, starting_x = Cursor.get_cursor_position()

        while choosing:

            while keyboard.is_pressed("up") or keyboard.is_pressed("down") or keyboard.is_pressed("enter"):
                pass
            key = keyboard.read_key()

            if key == "up":
                Cursor.move(starting_x+1, starting_y+select-len(options))
                print(unselection_character)

                select = max(0, select-1)

                Cursor.move(starting_x+1, starting_y+select-len(options))
                print(selection_character)

            elif key == "down":
                Cursor.move(starting_x+1, starting_y+select-len(options))
                print(unselection_character)

                select = min(len(options)-1, select+1)

                Cursor.move(starting_x+1, starting_y+select-len(options))
                print(selection_character)

            elif key == "enter":
                choosing = False
                Console.clear()
                return options[select]

    @staticmethod
    def output(output, alignment="left"):
        """
        Outputs the given string or list of strings to the console, with optional alignment

        Parameters
        ----------
        output : str or list
            The string or list of strings to output
            If it is a list, each element will be printed on a new line
        alignment : str
            The alignment of the output, either "left", "center", or "right". Defaults to "left"

        Returns
        -------
        None
        """
        if alignment == "left":
            Console.clear()
            if type(output) == str:
                print(output, sep="\n")
            elif type(output) == list:
                for i in output:
                    print(i, sep="\n")
        if alignment == "center":
            width, _ = Console.get_size()
            if type(output) == str:
                print(" "*((width//2)-(len(output)//2)), output, sep="", end="\n")
            elif type(output) == list:
                for i in output:
                    print(" "*((width//2)-(len(i)//2)), i, sep="", end="\n")
        if alignment == "right":
            width, _ = Console.get_size()
            if type(output) == str:
                print(" "*(width-len(output)), output, sep="", end="\n")
            elif type(output) == list:
                for i in output:
                    print(" "*(width-len(i)), i, sep="", end="\n")
