import random
import copy

class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        if len(self.cells) == self.count:
            return self.cells
        return None

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0:
            return self.cells
        return None

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        new_set = set()
        for c in self.cells:
            if c != cell:
                new_set.add(c)
            else:
                self.count -= 1
        self.cells = new_set


    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        new_set = set()
        for c in self.cells:
            if c != cell:
                new_set.add(c)
        self.cells = new_set


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        #Add cell to made moves and mark as safe
        self.moves_made.add(cell)
        self.mark_safe(cell)

        #Add sentence to knowledge base considering known safes and mines
        i, j = cell
        cells = []
        for row in range(i-1, i+2):
            for col in range(j-1, j+2):
                if row >= 0 and row < self.height and col >= 0 and col < self.width:
                    if (row, col) == cell:
                        continue
                    if (row, col) in self.mines:
                        count -= 1
                    if (row, col) not in self.mines and (row, col) not in self.safes:
                        cells.append((row, col))
        new_sentence = Sentence(cells, count)
        self.knowledge.append(new_sentence)

        #Make new inferences based on knowledge base
        inferences = []
        for sentence in self.knowledge:
            if sentence == new_sentence:
                continue

            if sentence.cells.issubset(new_sentence.cells):
                diff = new_sentence.cells.difference(sentence.cells)
                #Mark new safe cells
                if sentence.count == new_sentence.count:
                    for safe in diff:
                        self.mark_safe(safe)
                #Mark new mines
                elif len(diff) == new_sentence.count - sentence.count:
                    for mine in diff:
                        self.mark_mine(mine)
                #Add new inference
                else:
                    inference = Sentence(diff, new_sentence.count - sentence.count)
                    inferences.append(inference)

            elif new_sentence.cells.issubset(sentence.cells):
                diff = sentence.cells.difference(new_sentence.cells)
                #Mark new safe cells
                if sentence.count == new_sentence.count:
                    for safe in diff:
                        self.mark_safe(safe)
                #Mark new mines
                elif len(diff) == sentence.count - new_sentence.count:
                    for mine in diff:
                        self.mark_mine(mine)
                #Add new inference
                else:
                    inference = Sentence(diff, sentence.count - new_sentence.count)
                    inferences.append(inference)

        #Extend knowledge base and remove duplicate sentences    
        self.knowledge.extend(inferences)
        self.remove_duplicates()

        #Add new known safe cells and mines after inferences
        self.add_known_safes_and_mines()


    def remove_duplicates(self):
        unique_knowledge = []
        for sentence in self.knowledge:
            if sentence not in unique_knowledge:
                unique_knowledge.append(sentence)
        self.knowledge = unique_knowledge


    def add_known_safes_and_mines(self):
        final_knowledge = []
        for s in self.knowledge:
            safes = s.known_safes()
            mines = s.known_mines()
            if safes:
                for safe in safes:
                    self.mark_safe(safe)
            if mines:
                for mine in mines:
                    self.mark_mine(mine)
            if not (safes or mines):
                final_knowledge.append(s)
        self.knowledge = final_knowledge


    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        # for move in self.safes:
        #     if move not in self.moves_made:
        #         return move
        # return None
    
        safeCells = self.safes - self.moves_made
        if not safeCells:
            return None
        move = safeCells.pop()
        return move


    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        possible_moves = []
        for i in range(self.height):
            for j in range(self.width):
                possible_moves.append((i, j))

        while len(possible_moves) != 0:
            random_move = random.choice(possible_moves)
            possible_moves.remove(random_move)
            if random_move not in self.moves_made and random_move not in self.mines:
                return random_move
        return None