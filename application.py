# import necessary libraries
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from pyautogui import alert
from collections import deque


class Cell:
    def __init__(self):
        self.webElement = None
        self.was_empty = None


class Solve:
    def __init__(self, grid):
        self.grid = grid
        self.ref = [0, 0]

    def __locate_vacant(self):
        for i in range(9):
            for j in range(9):
                if self.grid[i][j] == 0:
                    self.ref[0], self.ref[1] = i, j
                    return True
        return False

    def __is_valid(self, row, col, value):
        for i in range(9):
            if (self.grid[row][i] == value) or (self.grid[i][col] == value):
                return False

        row -= row % 3
        col -= col % 3

        for i in range(3):
            for j in range(3):
                if self.grid[row + i][col + j] == value:
                    return False

        return True

    def solve(self):
        if not self.__locate_vacant():
            return True

        row, col = self.ref

        for number in range(1, 10):
            if self.__is_valid(row, col, number):
                self.grid[row][col] = number
                if self.solve():
                    return True
                self.grid[row][col] = 0

        return False


if __name__ == "__main__":

    game_url = "https://en.sudoku-online.net/sudoku-easy/"
    # game_url = "https://en.sudoku-online.net/"
    # game_url = "https://en.sudoku-online.net/sudoku-difficult/"
    # game_url = "https://en.sudoku-online.net/sudoku-very-difficult/"

    grid = deque(deque(0 for _ in range(9)) for __ in range(9))

    game_table = deque(deque(Cell() for _ in range(9)) for __ in range(9))

    # load grid
    solver = Solve(grid)

    options = ChromeOptions()
    options.add_argument("--start-maximized")

    driver = Chrome(options=options)
    driver.get(url=game_url)

    try:
        start = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#overlay-wrapper > div > div')))
    except TimeoutException:
        driver.close()
        alert("Loading took too much time!")
        quit(0)

    start.click()

    rows = driver.find_element_by_css_selector("#overlay-wrapper > table").find_elements_by_tag_name("tr")

    for i in range(9):
        cells = rows[i].find_elements_by_tag_name("td")
        for j in range(9):
            cell = cells[j]
            if cell.text:
                game_table[i][j].webElement = cell
                game_table[i][j].was_empty = False
                grid[i][j] = int(cell.text)
            else:
                game_table[i][j].webElement = cell
                game_table[i][j].was_empty = True

    resp = solver.solve()

    if not resp:
        alert("Grid is not solvable!")
        driver.close()
        quit(0)

    for i in range(9):
        for j in range(9):
            if game_table[i][j].was_empty:
                game_table[i][j].webElement.send_keys(grid[i][j])
