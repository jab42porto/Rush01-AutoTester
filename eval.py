#!/usr/bin/python3
import subprocess
import sys
import glob
import os
import re
from colorama import Fore, Back

RED = Fore.RED
BLU = Fore.CYAN
YLW = Fore.YELLOW
GRN = Fore.GREEN
WHT = Fore.WHITE

BGRED = Back.RED
BGBLU = Back.BLUE
BGYLW = Back.YELLOW
BGGRN = Back.GREEN
BGWHT = Back.WHITE


def wait_for_choice(msg: str):
    while True:
        answer = input(f'{YLW}{msg}{WHT}')
        if (answer.lower() == "y" or answer.lower() == "yes" or answer == ""):
            return True
        elif (answer.lower() == "n" or answer.lower() == "no"):
            return False
        else:
            print(f"{YLW}Please write 'yes' or 'no'.{WHT}")


def test_suite(size: int):
    print(f'\n{YLW}=== CORRECT TESTS ==={WHT}')
    total_tests: int = 100
    potential_grade = 100
    passed_tests: int = 0
    failed_tests: int = 0

    print(f'{BLU}Running {total_tests} test cases for size {size}...{WHT}')
    for i in range(total_tests):
        print(f'{BLU}Test {i+1}/{total_tests}:{WHT}')
        try:
            clue_array, clue_string = generator(size)
            if not clue_array or not clue_string:
                print(f'{RED}Failed to generate test case{WHT}',
                      file=sys.stderr)
                sys.exit(4)
            student_out = student_output(clue_string).split("\n")
            student_board = [[int(char) for char in row if char.isdigit()]
                             for row in student_out if row.strip()]
            if check_solution(clue_array, student_board, size):
                print_board(clue_array, student_board, size)
                print(f'{GRN}Success!{WHT}\n')
                passed_tests += 1
            else:
                print(f'{RED}Bad output{WHT}')
                print(student_out)
                print(f'{RED}Failed!{WHT}', file=sys.stderr)
                failed_tests += 1
        except (ValueError, IndexError):
            return 0
    potential_grade *= (passed_tests / total_tests)

    if passed_tests == total_tests:
        print(f'{GRN}All {total_tests} tests passed!{WHT}')
        return True
    else:
        print(f'{RED}Failed {failed_tests}/{total_tests} tests.{WHT}')
        print(f'{RED}Program has fundamental errors.{WHT}')
        return False

    return potential_grade


def eliminatory_tests():
    print(f'\n{YLW}=== FAILING TESTS ==={WHT}')
    error_tests = [
        ("Too many arguments", "4 3 2 1 1 2 2 2 4 3 2 1 1 2 2 2 3"),
        ("Too few arguments", "4 3 2 1 1 2 2 2 4 3 2 1 1 2 2"),
        ("Invalid number (6)", "4 3 2 1 1 2 2 2 6 3 2 1 1 2 2 2"),
        ("Invalid number (-1)", "4 3 2 1 1 2 2 2 -1 3 2 1 1 2 2 2"),
        ("Invalid number (0)", "4 3 2 1 1 2 2 2 0 3 2 1 1 2 2 2"),
        ("No spaces", "4321122243211222"),
        ("Non-numeric", "Hello"),
        ("Non-numeric", "4 3 2 1 1 2 2 2 6 3 2 1 a 2 2 2"),
        ("Unsolvable puzzle", "4 3 2 1 1 2 2 2 4 3 2 1 1 2 2 4")
    ]
    failed_tests = 0

    for test_name, test_input in error_tests:
        print(f'{BLU}Test: {test_name}{WHT}')
        print(f'Input: "{test_input}"')

        try:

            process = subprocess.run(
                ["./rush-01", test_input],
                capture_output=True,
                text=True,
                timeout=5
            )

            print('Student\'s output:\n', process.stdout.strip())
            print('Student\'s exit code:', process.returncode)
            if not wait_for_choice("Is the output correct?[Yes|No]: "):
                failed_tests += 1
        except subprocess.TimeoutExpired:
            print(f'{RED}✗ FAIL - Program timed out{WHT}')
            failed_tests += 1
        except Exception as e:
            print(f'{RED}✗ FAIL - Exception: {e}{WHT}')
            failed_tests += 1
    total_tests = len(error_tests)
    if failed_tests == 0:
        print(f'{GRN}All {total_tests} eliminatory tests passed!{WHT}')
        return True
    else:
        print(f'{RED}Failed {failed_tests}/{total_tests} tests.{WHT}')
        return False


def check_solution(clue: str, board, size: int):
    try:
        if len(board) != size or any(len(row) != size for row in board):
            return False
        # Checks for duplicates by using set
        for i in range(size):
            if (len(set(board[i])) != size):
                return False
            if (len(set(board[j][i] for j in range(size))) != size):
                return False

        for i in range(size):
            for j in range(size):
                if not (1 <= board[i][j] <= size):
                    return False

        vsight = [[board[j][i] for j in range(size)] for i in range(size)]

        if not (check_view(clue[0], vsight) and
                check_view(clue[1], vsight, reverse=True) and
                check_view(clue[2], board) and
                check_view(clue[3], board, reverse=True)):
            return False
        else:
            return True
    except (ValueError, IndexError, TypeError):
        return False


def student_output(clue):
    try:
        if not re.match(r'^[0-9\s]+$', clue):
            print(f'{RED} Invalid Clue Format{WHT}', file=sys.stderr)
            return ""

        process = subprocess.run(["./rush-01", " ".join(clue)],
                                 text=True, capture_output=True, timeout=10)
    except subprocess.CalledProcessError as e:
        print(f"{RED}Program exited with code:{WHT}", e.returncode)
        print(f"{RED}\n======= Error Output ====={WHT}")
        print(e.stderr)
        return ""
    except subprocess.TimeoutExpired:
        print(f'{RED} Program timed out{WHT}', file=sys.stderr)
        return ""
    except Exception as error:
        print(f'{RED}  Error running program: {error}{WHT}', file=sys.stderr)
        return ""
    return process.stdout


def count_visible(sight_line: str, reverse=False):
    viewed = 0
    hmax = 0
    for block in sight_line[::1 if not reverse else -1]:
        if int(block) > hmax:
            hmax = int(block)
            viewed += 1
    return viewed


def check_view(clue: str, sight_line: str, reverse=False):
    for i in range(len(clue)):
        view = int(clue[i])
        viewed = count_visible(sight_line[i], reverse)
        if viewed != view:
            return False
    return True


def print_board(clue, board, size):
    """
        just a pretty print for the board + clue
    """
    print(' ', *[BLU+c+WHT for c in clue[0]], sep=" ")
    for i in range(size):
        print(BLU+clue[2][i]+WHT, *(b for b in board[i]), BLU+clue[3][i]+WHT)
    print(' ', *[BLU+c+WHT for c in clue[1]], sep=" ")


def generator(size):
    clue = ""
    if not (3 <= size <= 9):
        return None, None
    try:
        process = subprocess.run(["python", "generator.py",
                                  str(size)], timeout=10,
                                 text=True,
                                 capture_output=True)
        if process.returncode != 0:
            print(f'{RED} Generator Failed: {process.stderr}{WHT}',
                  file=sys.stderr)
            return None, None

        lines = process.stdout.split('\n')
        if len(lines) < size + 2:
            print(f'{RED} Invalid generator output{WHT}', file=sys.stderr)
            return None, None

        clue_lines = lines[0]
        clue = clue_lines.replace(' ', '')

        if len(clue) != size * 4:
            print(f'{RED} Invalid clue length{WHT}', file=sys.stderr)
            return None, None

        clue = [clue[i*size:i*size+size] for i in range(4)]

        # make the board for redundant validation, but won't need to return it
        # because we can't compare with student's output
        board = []
        for i in range(2, 2 + size):
            if i < len(lines):
                row = lines[i].replace(' ', '')
                if len(row) == size and row.isdigit():
                    board.append(row)
        if len(board) != size:
            print(f'{RED} Invalid clue length{WHT}', file=sys.stderr)
            return None, None, None
        return clue, clue_lines
    except subprocess.TimeoutExpired:
        print(f"{RED}Generator timed out{WHT}", file=sys.stderr)
        return None, None
    except Exception as error:
        print(f"{RED}Error in generator: {error}{WHT}", file=sys.stderr)
        return None, None


def check_and_clone_repo(repo: str, login: str):
    print("Checking and cloning the repo.")
    regex_pattern = r'git@vogsphere\.42(porto|lisboa)\.com:vogsphere/intra-uuid-[0-9a-z]{8}-([0-9a-z]{4}-){3}[0-9a-z]{12}-[0-9a-z]{7}-[0-9a-z-]*$'
    if len(repo) <= 93 or not re.match(regex_pattern, repo):
        print("Mak sure you inserted the correct repo's url", file=sys.stderr)
        sys.exit(5)
    command = ["git", "clone", repo, login]
    try:
        subprocess.run(
            command,
            check=True,
            capture_output=True,
            timeout=10,
            text=True
        )
        print("Repository Clone successfully")
    except subprocess.TimeoutExpired:
        print(f"{RED}Git clone timed out{WHT}", file=sys.stderr)
        sys.exit(6)
    except subprocess.CalledProcessError as e:
        print(f"{RED}Error cloning the Repository:{WHT}", e.returncode)
        print(f"{RED}\n======= Error Output ====={WHT}")
        print(e.stderr)
        sys.exit(7)


def compile_project(login: str):
    try:
        source_files = glob.glob(f"{login}/ex00/*.c")
        command = (["cc", "-Wall", "-Werror", "-Wextra"]
                   + source_files
                   + ["-o", "./rush-01"])
        subprocess.run(
            command,
            check=True,
            capture_output=True,
            timeout=10,
            text=True
            )
    except subprocess.TimeoutExpired:
        print(f"{RED}Compiling timed out{WHT}", file=sys.stderr)
        sys.exit(8)
    except subprocess.CalledProcessError as e:
        print(f"{RED}Error compiling:", e.returncode, file=sys.stderr)
        print(f"\n======= Error Output ====={WHT}")
        print(e.stderr)
        sys.exit(9)
    if not os.path.exists('./rush-01'):
        print(f'{RED}Executable not created{WHT}', file=sys.stderr)
        sys.exit(10)


def fetch_login(url: str) -> str:
    if "porto" in url:
        return url[92:]
    elif "lisboa" in url:
        return url[93:]


def main():
    if len(sys.argv) != 3 and len(sys.argv) != 2:
        print(f"{YLW}Usage: [repo url] [size]{WHT}")
        sys.exit(1)
    try:
        if len(sys.argv) == 3:
            size = int(sys.argv[2])
        else:
            size = 4
        if size < 3 or size > 9:
            print(f"{RED}Invalid Size, must be between 3 and 9{WHT}",
                  file=sys.stderr)
            sys.exit(2)
    except ValueError:
        print(f"{RED}Size must be a valid integer{WHT}", file=sys.stderr)
        sys.exit(3)

    url = sys.argv[1]
    login = fetch_login(url)
    if wait_for_choice("Want to clone the Repository?[Yes|No]: "):
        check_and_clone_repo(url, login)
    compile_project(login)
    if not run_norminette(login):
        print(f"{RED}Norminette Error{WHT}")
        return
    test_suite(size)
    eliminatory_tests()


def run_norminette(login):
    try:
        process = subprocess.run(
            ["norminette", f"./{login}"],
            timeout=5
        )
        if process.returncode == 0:
            return True
        else:
            return False
    except subprocess.TimeoutExpired:
        print(f"{RED}Couldn't run norminette{WHT}")
        return False
    except Exception as e:
        print(f"{RED}Norminette failed: {e}{WHT}")
        return False


if __name__ == "__main__":
    main()
    try:
        if wait_for_choice("Want to clear executable?: "):
            if os.path.exists("./rush-01"):
                os.remove("./rush-01")
                print("Executable cleaned up.")
    except Exception as e:
        print(f"Could not clean up executable: {e}")
