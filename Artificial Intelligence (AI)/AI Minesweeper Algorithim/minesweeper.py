import itertools
import random


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
        # Checking if the count is greater than 0 and the number of cells equals the count
        if self.count > 0 and len(self.cells) == self.count:
            # Returning all cells as they are all mines
            return {cell for cell in self.cells}
        # Returning an empty set otherwise
        return set()

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0:
            return {cell for cell in self.cells}
        return set()

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        # First check to see if cell is one of the cells included in the sentence
        if cell in self.cells:
            # Remove it and decrement count by one
            self.cells = self.cells - {cell}
            self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        # First check to see if cell is one of the cells included in the sentence
        if cell in self.cells:
            # Remove it
            self.cells = self.cells - {cell}


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
        # Marking as a move that has been made
        self.moves_made.add(cell)

        # Marking as safe
        self.mark_safe(cell)

        # Gathering all neighboring cells in a list
        neighbors = [
            (i, j) 
            for i in range(cell[0] - 1, cell[0] + 2) 
            for j in range(cell[1] - 1, cell[1] + 2)
            if (i, j) != cell and 0 <= i < self.height and 0 <= j < self.width
        ]

        sentence_cells = set()
        for neighbor in neighbors:
            if neighbor in self.mines:
                # Reducing count for known mines
                count -= 1
            elif neighbor not in self.safes:
                # Adding undetermined cells to the sentence
                sentence_cells.add(neighbor)

        if sentence_cells:
            # Adding a new sentence to the KB
            new_sentence = Sentence(sentence_cells, count)
            self.knowledge.append(new_sentence)

        while True:
            new_safes = set()
            new_mines = set()
            for sentence in self.knowledge:
                # Finding all known safes and known mines
                new_safes.update(sentence.known_safes())
                new_mines.update(sentence.known_mines())

            if not new_safes and not new_mines:
                break
            
            # Marking all new safes and new mines
            for safe in new_safes:
                self.mark_safe(safe)
            for mine in new_mines:
                self.mark_mine(mine)

        # Infering new sentences
        """
        1. For each existing sentence in the knowledge base I will do the following:
            For each other sentence in the knowledge base I will do the following:
            i. If the two sentences are not the same:
                - Check if the first sentence is a subset of the second sentence
                - If it is then I will do the following:
                    - Identify the cells that are in the second sentence but not in the first sentence
                    - Calculate the number of mines in the newly identified cells by subtracting the number of mines in the first sentence from the number of mines in the second sentence
                    - Create a new sentence with the newly identified cells and the calculated number of mines
                    - Check if this new sentence is not already present in the knowledge base and not in the list of newly inferred sentences
                    - If it is not present, add this new sentence to the list of newly inferred sentences
        2. Add all newly inferred sentences to the knowledge base
        """
        new_sentences = []
        for s1 in self.knowledge:
            for s2 in self.knowledge:
                # If the two sentences are the same we skip it
                if s1 == s2:
                    continue
                # Checking if the cells in s1 are a subset of the cells in s2
                if s1.cells.issubset(s2.cells):
                    # Calculating the inferred cells by substracting the cells in s1 from s2
                    inferred_cells = s2.cells - s1.cells
                    # Doing the same but for the count
                    inferred_count = s2.count - s1.count
                    new_sentence = Sentence(inferred_cells, inferred_count)
                    # If the new sentence is not in the KB and not previously added to new_sentences then we append it to the list
                    if new_sentence not in self.knowledge and new_sentence not in new_sentences:
                        new_sentences.append(new_sentence)
        # Adding the new sentences to the KB
        self.knowledge.extend(new_sentences)

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        # Going over safe cells
        for safe in self.safes:
            # Checking if it has not been moved
            if safe not in self.moves_made:
                # Returning it as the next move
                return safe
        # In case no safe move can be guranteed
        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        # Set to contain all possible moves that have not been made and are not mines
        possible_moves = set()

        for i in range(self.height):
            for j in range(self.width):
                # Checking if the condition for the set is true (move not made and not a mine)
                if (i, j) not in self.moves_made and (i, j) not in self.mines:
                    possible_moves.add((i, j))

        if possible_moves:
            # If there are moves in the set then a move from the set is returned
            return random.choice(tuple(possible_moves))

        # In case there are no possible moves
        return None