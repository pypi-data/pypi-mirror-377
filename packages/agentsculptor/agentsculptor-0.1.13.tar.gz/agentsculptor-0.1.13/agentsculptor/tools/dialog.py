# tools/dialog.py
import sys
from agentsculptor.utils.logging import setup_logging, get_logger

setup_logging("DEBUG")
logger = get_logger()

class DialogManager:
    @staticmethod
    def choose_file(candidates: list, instruction: str) -> list:
        """Ask the user to pick one or more files if multiple matches found."""
        if not candidates:
            logger.stop("No candidate files found.")
            return []

        if len(candidates) == 1:
            return candidates  # only one option → auto-choose

        logger.dialog("Multiple files match your request:")
        for i, f in enumerate(candidates, 1):
            print(f"  {i}. {f}")
        print(f"  {len(candidates)+1}. All of the above")

        choice = input("Enter number: ").strip()
        try:
            choice_int = int(choice)
            if choice_int == len(candidates) + 1:
                return candidates
            return [candidates[choice_int - 1]]
        except (ValueError, IndexError):
            logger.stop("Invalid choice, aborting.")
            sys.exit(1)

    @staticmethod
    def confirm_action(files: list, instruction: str) -> bool:
        """Ask the user to confirm before applying instruction."""
        logger.dialog("I am about to apply the following instruction:")
        print(f"  Instruction: {instruction}")
        print("  Target files:")
        for f in files:
            print(f"   - {f}")
        choice = input("Proceed? (y/n): ").strip().lower()
        return choice == "y"
    
    @staticmethod
    def confirm_file_creation(path, instruction):
        logger.dialog(f"The instruction may require creating a new file: {path}")
        choice = input("Do you allow creating new files? (y/n): ").strip().lower()
        return choice == "y"
