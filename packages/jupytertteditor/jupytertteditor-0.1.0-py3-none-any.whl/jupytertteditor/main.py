# Creates a classes that simplifies the process to create and display a truth table.
# To create an instance of the class
#     'classInstance = TruthTable(numberOfVariablesDesired)
# To create a new column that compares two variables
#     'classInstance.createColumn("columnName", not for the first term {given in the form of a bool(True for ~P : False for P)}, Index of the first column you are comparing, Operator to be used {'and', 'or', 'xor', 'implies', and 'iff'}, not for the second term {given in the form of a bool(True for ~P : False for P)}, Index of the second column you are comparing)
# To create a new column that gives the not version of one other column
#     'classInstance.createNotColumn("columnName", Index of the column you are altering)
# To display the truth table
#     'classInstance.display()'

class TruthTable:
    def __init__(self, var_count: int):
        # calculates the number of rows required based on the number of variables needed
        self.num_of_rows = 2 ** var_count
        # Serves as the headers for each column
        head = []
        for i in range(var_count):
            r = int(i/26)
            head.append(f"{chr(65 + i - (26 * r)) * (r+1)}")
        # creates the columns of the initial variables of the truth table
        columns = []
        for i in range(var_count):
            col = []
            col_count = len(columns)
            for x in range(self.num_of_rows // (2 ** col_count)):
                for y in range(2 ** col_count):
                    if x%2 == 0:
                        col.append(True)
                    else:
                        col.append(False)
            columns.append(col)
        self.table = {}
        for i in range(len(head)):
            self.table[head[i]] = [head[i], columns[-(i + 1)]]

    def get_truth_table(self) -> dict:
        return self.table

    def get_num_of_rows(self) -> int:
        return self.num_of_rows

    def change_column_name(self, col_name: str, new_name: str) -> None:
        self.table[new_name] = self.table[col_name]
        self.table[new_name][0] = new_name
        del self.table[col_name]

    # creates a new column based on the bools of two other columns
    def create_column(self, col_name: str, not_x: bool, col_name_x: str, operator: str, not_y: bool, col_name_y: str) -> None:
        col = []
        # determines what operator is being used
        match operator:
            # creates the column for the and operator
            case "and":
                xy = self._format_xy(not_x, col_name_x, not_y, col_name_y)
                for i in range(self.num_of_rows):
                    if xy[0][i] and xy[1][i]:
                        col.append(True)
                    else:
                        col.append(False)
            # creates the column for the or operator
            case "or":
                xy = self._format_xy(not_x, col_name_x, not_y, col_name_y)
                for i in range(self.num_of_rows):
                    if xy[0][i] or xy[1][i]:
                        col.append(True)
                    else:
                        col.append(False)
            # creates the column for the xor operator
            case "xor":
                xy = self._format_xy(not_x, col_name_x, not_y, col_name_y)
                for i in range(self.num_of_rows):
                    if self._xor(xy[0][i], xy[1][i]):
                        col.append(True)
                    else:
                        col.append(False)
            # creates the column for the implies operator
            case "implies":
                xy = self._format_xy(not_x, col_name_x, not_y, col_name_y)
                for i in range(self.num_of_rows):
                    if self._implies(xy[0][i], xy[1][i]):
                        col.append(True)
                    else:
                        col.append(False)
            # creates the column for the iff operator
            case "iff":
                xy = self._format_xy(not_x, col_name_x, not_y, col_name_y)
                for i in range(self.num_of_rows):
                    if self._iff(xy[0][i], xy[1][i]):
                        col.append(True)
                    else:
                        col.append(False)
            # catches when an improper operator is given
            case _:
                print("Invalid operator")
                pass
        self.table[col_name] = [col_name, col]

    def create_not_column(self, col_name: str, col_name_x: str) -> None:
        col = []
        for i in range(self.num_of_rows):
            if self.table[col_name_x][1][i]:
                col.append(False)
            else:
                col.append(True)
        self.table[col_name] = [col_name, col]
    
    def remove_column(self, col_name: str) -> None:
        del self.table[col_name]

    def _format_xy(self, not_x: bool, col_name_x: str, not_y: bool, col_name_y: str):
        col_x = self.table[col_name_x][1]
        col_y = self.table[col_name_y][1]
        new_col_x = []
        new_col_y = []
        if not_x:
            for b in col_x:
                if b:
                    new_col_x.append(False)
                else:
                    new_col_x.append(True)
        else: 
            new_col_x = col_x
        if not_y:
            for b in col_y:
                if b:
                    new_col_y.append(False)
                else:
                    new_col_y.append(True)
        else:
            new_col_y = col_y
        return [new_col_x, new_col_y]

    def _xor(self, p: bool, q: bool) -> bool:
        return p != q

    def _implies(self, p: bool, q: bool) -> bool:
        return not p or q

    def _iff(self, p: bool, q: bool) -> bool:
        return not self.xor(p, q)

    def display(self) -> None:
        header_len = []
        for i in self.table:
            x = len(self.table[i][0])
            if x < 6:
                x = 6
            x += 3
            header_len.append(x)
        x = 0
        for i in self.table:
            print(i.rjust(header_len[x]), end=" |")
            x += 1
        print("")
        for n in range(self.num_of_rows):
            x = 0
            for i in self.table:
                print(str(self.table[i][1][n]).rjust(header_len[x]), end=" |")
                x += 1
            print("")