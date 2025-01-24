import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for variable in self.domains:
            for word in set(self.domains[variable]): # Converting domain to set and iterate
                if len(word) != variable.length: # Checking word length constraint
                    self.domains[variable].remove(word) # Removing inconsistent word

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revised = False # To track if revision occurs
        overlap = self.crossword.overlaps[x, y]
        if overlap is None: # If no overlap then no revision needed
            return False
    
        i, j = overlap
        for word_x in set(self.domains[x]): # Checking each word in x's domain
            remove = True
            for word_y in self.domains[y]: # Checking each word in y's domain
                if word_x[i] == word_y[j]:
                    remove = False
                    break
            if remove: # If no match found remove word_x
                self.domains[x].remove(word_x)
                revised = True
            
        return revised

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        # If arcs is provided use it, otherwise generate all arcs between variables and their neighbors
        queue = arcs if arcs is not None else [(x, y) for x in self.domains for y in self.crossword.neighbors(x)]
    
        while queue:
            x, y = queue.pop(0)
            if self.revise(x, y):
                if not self.domains[x]: # If x's domain is empty return False
                    return False
                for z in self.crossword.neighbors(x) - {y}: # Adding neighboring arcs
                    queue.append((z, x))
    
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        return set(assignment.keys()) == self.crossword.variables


    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        # Iterating over each variable and assigned word
        for variable, word in assignment.items():
            if len(word) != variable.length: # Checking if word length matches variable's length constraint
                return False
            for neighbor in self.crossword.neighbors(variable): # Checking each neighbor of the variable
                if neighbor in assignment:
                    i, j = self.crossword.overlaps[variable, neighbor]
                    if word[i] != assignment[neighbor][j]: # Checking for conflicting characters
                        return False
        
        # Checking for duplicate words in assignment
        return len(set(assignment.values())) == len(assignment.values())

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        # Function to return total conflicts
        def count_conflicts(value):
            conflicts = 0
            # Iterating over neighbors and checking if neighbor is not assigned
            for neighbor in self.crossword.neighbors(var):
                if neighbor not in assignment:
                    i, j = self.crossword.overlaps[var, neighbor] # Getting overlap indices
                    for word in self.domains[neighbor]: # Iterating over words in neighbor's domain
                        if value[i] != word[j]:
                            conflicts += 1
            return conflicts
    
        return sorted(self.domains[var], key=count_conflicts)

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        # List of unassigned variables that are not part of the current assignment
        unassigned_variables = [v for v in self.crossword.variables if v not in assignment]
        
        # Function to calculate heuristics for a variable
        def get_heuristics(var):
            # Returning a tuple of remaining domain size and negative neighbor count
            return (len(self.domains[var]), -len(self.crossword.neighbors(var)))

        return min(unassigned_variables, key=get_heuristics)

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        # Checking if assignment is complete
        if self.assignment_complete(assignment):
            return assignment

        # Selecting unassigned assignment
        var = self.select_unassigned_variable(assignment)

        # Iterating over ordered domain values
        for value in self.order_domain_values(var, assignment):
            new_assignment = assignment.copy()
            new_assignment[var] = value

            # Checking if assignment is consistent
            if self.consistent(new_assignment):
                result = self.backtrack(new_assignment) # Attempting to complete assignment
                if result is not None:
                    return result
    
        return None

def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()