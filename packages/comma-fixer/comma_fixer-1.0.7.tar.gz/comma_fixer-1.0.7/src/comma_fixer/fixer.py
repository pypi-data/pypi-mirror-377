import logging
import math
import os
import time
from dataclasses import dataclass
from io import StringIO, TextIOWrapper
from typing import Iterable, Optional, TypeAlias

import networkx as nx
import numpy as np
from networkx import NetworkXNoPath, NodeNotFound

from comma_fixer.parsed import Parsed
from comma_fixer.schema import Schema

ParsedEntry: TypeAlias = list[str]
"""
TypeAlias for rows that have been split or parsed.
"""
Path: TypeAlias = list[tuple[int, int]]
"""
TypeAlias for the shortest path taken in ValidityMatrix by node.
"""
ValidityMatrix: TypeAlias = np.ndarray
"""
TypeAlias for the integer matrix.
"""
InvalidEntry: TypeAlias = tuple[int, str]
"""
TypeAlias for invalid entries, storing line index and the line entry.
"""
logger = logging.getLogger("Fixer Logs")
logging.basicConfig(level=logging.ERROR)


@dataclass
class Fixer:
    """
    Class for fixing malformed CSV files.

    Contains a dataframe to hold processed entries from
    the CSV file, a Schema object which defines the dataframe,
    and a list of invalid entries (i.e. entries that may contain
    more than one method of grouping to fit into schema).

    Attributes:
        schema (`Schema`): Schema object defining the columns
        of the dataset.
    """

    schema: Schema

    @classmethod
    def new(cls, schema: Schema) -> "Fixer":
        """ "
        Create a new Fixer class with a Schema object.

        Args:
            schema (`Schema`): Schema defining column name, type, and
            validity functions.

        Returns:
            Fixer. Fixer object with initialised DataFrame according to Schema.
        """
        return Fixer(schema)

    def process_row(
        self,
        new_entry: str,
        show_possible_parses: bool = False,
        line_index: Optional[int] = None,
    ) -> Optional[ParsedEntry]:
        """
        Processes a new row against the columns in the schema.

        If the entry contains a valid parsing, returns it, otherwise
        returns None.

        Args:
            new_entry (str): Row to be processed.
            show_possible_parses (bool): Print out possible parses for invalid lines
            line_number (Optional[int]): Index of line being processed.

        Returns:
            Optional[ParsedEntry]. Returns processed entry if valid parsing exists,
            and None otherwise.
        """
        parsed_entry = self.__check_valid(new_entry.strip(), line_index=line_index)
        if parsed_entry is None and show_possible_parses:
            self.__all_possible_processed_strings(
                new_entry=new_entry, line_index=line_index
            )
        return parsed_entry

    def __build_csv_row(self, processed_path: str) -> str:
        """
        Builds the CSV format row for easy copy and pasting for
        manual fixing of CSV files.

        Args:
            processed_path (str): A valid parse of the current row.

        Returns:
            str. Valid parse formatted for CSV.
        """
        csv_row = ""
        for token in processed_path:
            if "," in token:
                if len(csv_row) == 0:
                    csv_row = """"{token}" """
                else:
                    csv_row = f"""{csv_row},"{token}" """
                csv_row = csv_row.strip()
            else:
                if len(csv_row) == 0:
                    csv_row = f"{token}"
                else:
                    csv_row = f"{csv_row},{token}"
        return csv_row

    def __all_possible_processed_strings(
        self, new_entry: str, line_index: Optional[int] = None
    ) -> list[ParsedEntry]:
        """
        Processes a new row and returns all possible parsing as a list.

        Args:
            new_entry (str): Row to be processed.
            line_index (Optional[int]): Index of line being processed.

        Returns:
            list[ParsedEntry]. Returns list of all possible parses that would
            make the new entry valid with schema.
        """
        validity_matrix = self.__construct_validity_matrix(new_entry=new_entry)
        tokens = new_entry.split(",")
        (num_tokens, num_cols) = validity_matrix.shape
        paths = self.__find_shortest_paths(validity_matrix=validity_matrix)
        processed_paths = list()

        if paths is not None:
            for path in paths:
                processed_path = self.__construct_processed_entry_from_path(
                    path=path, tokens=tokens, num_cols=num_cols, num_tokens=num_tokens
                )
                if processed_path is None:
                    if line_index is not None:
                        logger.warning(
                            f"Path failed at line index {line_index} - null entry in non-nullable column."
                        )
                    else:
                        logger.warning(
                            "Path failed - null entry in non-nullable column."
                        )
                else:
                    logger.info(processed_path)
                    logger.info(
                        f"""Correct CSV format: {self.__build_csv_row(processed_path=processed_path)}"""
                    )
                    processed_paths.append(processed_path)
        return processed_paths

    def __process_file(
        self,
        file: TextIOWrapper | StringIO,
        skip_first_line: bool = True,
        show_possible_parses: bool = False,
    ) -> Parsed:
        """
        Private function with main logic for processing a CSV file line by line using schema,
        and identifies invalid entries.

        If `show_possible_parses` is set to True, prints out possible parses of invalid entries
        if and only if the invalid entry has multiple possible parsings, and the parsing does
        not result in a null token being placed into a non-nullable column.

        After processing, prints out the number of valid entries against invalid entries.

        Args:
            file (TextIOWrapper): TextIOWrapper stream to read from.
            skip_first_line (bool): Whether or not to skip the first line. Default True.
            show_possible_parses (bool): If set to True, prints out all possible parses of invalid rows.
                Default False.

        Returns:
            Parsed. Parsed object which holds processed lines, invalid lines, and
            function to export parsed lines to CSV.
        """
        processed_csv: str = ""
        invalid_entries: list[InvalidEntry] = list()
        first_row_is_header = skip_first_line

        line_count = 0
        for line in file:
            line = line.strip()
            if not skip_first_line:
                # Process the line
                processed_entry = self.process_row(
                    new_entry=line,
                    show_possible_parses=show_possible_parses,
                    line_index=line_count,
                )
                # If there exists a single path, there is a valid parsing
                if processed_entry is not None:
                    processed_csv = self._add_valid_entry(
                        processed=processed_csv, entry=processed_entry
                    )
                # else, add it to invalid entries list
                else:
                    processed_csv = self._add_invalid_entry(
                        invalid_entries=invalid_entries,
                        processed=processed_csv,
                        line_index=line_count,
                        entry=line,
                    )
                line_count += 1
            else:
                skip_first_line = not skip_first_line
                line_count += 1
        total_entries = line_count - 1 if skip_first_line else line_count

        # Create parsed object for user to interact with
        parsed = Parsed.new(
            schema=self.schema,
            processed_csv=processed_csv,
            invalid_entries=invalid_entries,
            skip_first_line=first_row_is_header,
        )

        print(
            f"File has been processed!\nNumber of total entries: {total_entries}\
            \n Number of invalid entries: {parsed.invalid_entries_count()}"
        )
        return parsed

    def __setup_log_file(self):
        """
        Creates a log subdirectory in the current active directory where the
        code is being run, and writes logs to the file.
        """
        named_tuple = time.localtime()  # get struct_time
        time_string = time.strftime("%Y%m%d_%H%M%S", named_tuple)
        basedir = f"{os.path.curdir}/logs"
        if not os.path.exists(basedir):
            os.makedirs(basedir)
        logging.basicConfig(
            filename=f"./logs/comma_fixer_{time_string}.log",
            level=logging.INFO,
            force=True,
        )

    def fix_file(
        self,
        file: str | Iterable[str],
        encoding: str = "utf-8",
        skip_first_line: bool = True,
        show_possible_parses: bool = False,
        log_file: bool = False,
    ) -> Parsed:
        """
        Processes a CSV file line by line using schema,
        and identifies invalid entries.

        If `show_possible_parses` is set to True, prints out possible parses of invalid entries
        if and only if the invalid entry has multiple possible parsings, and the parsing does
        not result in a null token being placed into a non-nullable column.

        If `log_file` is set to True, creates a log folder in the current directory, and saves the logs
        into the files with the following name format: comma_fixer_%Y%m%d_%H%M%S.log.

        After processing, prints out the number of valid entries against invalid entries.

        Args:
            file (str | TextIOWrapper | StringIO): Filepath of CSV file to be processed, or an already
                opened TextIOWrapper of said file.
            encoding (str): Encoding of the file being passed in. Default utf-8.
            skip_first_line (bool): Whether or not to skip the first line. Default True.
            show_possible_parses (bool): If set to True, logs all possible parses of invalid rows.
                Default False.
            log_file (bool): If set to True, creates a log file. Default False.

        Returns:
            Parsed. Parsed object which holds processed lines, invalid lines, and
            function to export parsed lines to CSV.
        """
        if log_file:
            self.__setup_log_file()
        elif show_possible_parses:
            logging.basicConfig(level=logging.INFO, force=True)
        else:
            logging.basicConfig(level=logging.WARNING, force=True)

        if not isinstance(file, str):
            return self.__process_file(
                file=file,
                skip_first_line=skip_first_line,
                show_possible_parses=show_possible_parses,
            )
        else:
            try:
                with open(file, mode="rt", encoding=encoding) as file:
                    return self.__process_file(
                        file=file,
                        skip_first_line=skip_first_line,
                        show_possible_parses=show_possible_parses,
                    )
            except UnicodeEncodeError:
                logger.warning(
                    f"Encoding invalid -- {encoding}. Failed to process file."
                )

    def _add_valid_entry(self, processed: str, entry: ParsedEntry) -> str:
        """
        Adds a valid entry to the string representation of the CSV with
        quotes around elements containing commas.

        Args:
            processed (str): String representation of CSV of processed items.
            entry (ParsedEntry): List of tokens to be added.

        Returns:
            str. Returns string representation of CSV with new entry appended.
        """
        processed_entry = ""
        for token in entry:
            if "," in token:
                if len(processed_entry) != 0:
                    processed_entry = f'{processed_entry},"{token}"'
                else:
                    processed_entry = f'"{token}"'
            else:
                if len(processed_entry) != 0:
                    processed_entry = f"{processed_entry},{token}"
                else:
                    processed_entry = f"{token}"
        if len(processed) != 0:
            return f"{processed}\n{processed_entry}"
        else:
            return processed_entry

    def _add_invalid_entry(
        self,
        invalid_entries: list[InvalidEntry],
        processed: str,
        line_index: int,
        entry: str,
    ) -> str:
        """
        Adds invalid entries to string representation of the CSV,
        and the list of invalid entries.

        Args:
            invalid_entries (list[InvalidEntry]): List of invalid entries with their line index.
            processed (str): String representation of CSV of processed items.
            line_index (int): Index of invalid entry in original CSV file.
            entry (str): String of invalid entry.

        Returns:
            str. Returns processed string representation of CSV with new entry appended.
        """
        invalid_entries.append(tuple([line_index, entry]))
        if len(processed) != 0:
            return f"{processed}\n{entry}"
        else:
            return entry

    def __check_valid(
        self, new_entry: str, line_index: Optional[int] = None
    ) -> Optional[ParsedEntry]:
        """
        Checks whether a row is valid and returns the parsed entry if valid.

        Tokenises the row by delimiter and checks which tokens can be placed
        in which columns. If a valid parsing exists, returns it as a list of
        tokens.

        Args:
            new_entry (str): Row to be processed.
            line_number (Optional[int]): Index of line being processed.

        Returns:
            Optional[ParsedEntry]: List of parsed tokens if the row is valid.
        """
        # Create validity matrix from schema against tokens
        validity_matrix = self.__construct_validity_matrix(new_entry=new_entry)
        tokens = new_entry.split(",")
        (num_tokens, num_cols) = validity_matrix.shape

        # Find the shortest valid path in validity matrix
        paths = self.__find_shortest_paths(
            validity_matrix=validity_matrix, line_index=line_index
        )

        if paths is not None and len(paths) > 1:
            if line_index is not None:
                logger.warning(
                    f"Multiple paths found at line index {line_index} - needs to be resolved."
                )
            else:
                logger.warning("Multiple paths found -- needs to be resolved")
            return None
        elif paths is not None:
            for path in paths:
                # If there is a unique path,
                # construct the processed row from tokens
                return self.__construct_processed_entry_from_path(
                    path=path,
                    tokens=tokens,
                    num_cols=num_cols,
                    num_tokens=num_tokens,
                    line_index=line_index,
                )
        # Warning log should already been written from __find_shortest_paths
        return None

    def __construct_processed_entry_from_path(
        self,
        path: Path,
        tokens: list[str],
        num_cols: int,
        num_tokens: int,
        line_index: Optional[int] = None,
    ) -> ParsedEntry:
        """
        Constructs a ParsedEntry from a valid path and given tokens.

        Args:
            path (Path): List of tuples of the shortest path that
            creates a parsed entry from the validity matrix.
            tokens (list[str]): List of tokens from splitting entry
            string by the delimiter.
            num_cols (int): Number of columns in schema.
            num_tokens (int): Number of tokens after splitting entry
            string by the delimiter.
            line_number (Optional[int]): Index of line being processed.

        Returns:
            ParsedEntry. List of tokens parsed such that the entry is valid
            according to the schema.
        """
        processed_entry = ["" for _ in range(num_cols)]
        column_names = self.schema.get_column_names()
        previous_col = -1
        logger.debug(f"Path: {path}")

        # For each node in the path, construct the processed row
        # using the tokens
        for step in path:
            if step[0] < num_tokens and step[1] < num_cols:
                # Update the processed entry when the column changes in the path,
                # i.e. (t, c) -> (t+1, c+1)
                if step[1] != previous_col:
                    # If the working string is empty but the column is non-nullable,
                    # then the path is invalid.
                    if (
                        previous_col >= 0
                        and len(processed_entry[previous_col]) == 0
                        and not self.schema.columns[
                            column_names[previous_col]
                        ].is_nullable()
                    ):
                        if line_index is not None:
                            logger.warning(
                                f"Failed at line index {line_index} - Parsed null element into non-null column."
                            )
                        else:
                            logger.warning(
                                "Failed - Parsed null element into non-null column."
                            )
                        return None
                    processed_entry[step[1]] = tokens[step[0]].strip()
                    previous_col = step[1]
                else:
                    # Still on same column
                    # Since it is a valid path, this means that
                    # the current column allows commas
                    if len(processed_entry[step[1]]) == 0:
                        processed_entry[step[1]] = tokens[step[0]].strip()
                    elif len(tokens[step[0]]) != 0:
                        processed_entry[step[1]] = (
                            f"{processed_entry[step[1]]},{tokens[step[0]].strip()}"
                        )
        if (
            previous_col >= 0
            and len(processed_entry[previous_col]) == 0
            and not self.schema.columns[column_names[previous_col]].is_nullable()
        ):
            if line_index is not None:
                logger.warning(
                    f"Failed at line index {line_index} - Parsed null element into non-null column."
                )
            else:
                logger.warning("Failed - Parsed null element into non-null column.")
            return None
        return processed_entry

    def __construct_validity_matrix(self, new_entry: str) -> ValidityMatrix:
        """
        Constructs a validity matrix from the entry string against the
        columns in schema.

        ValidityMatrix of size number of tokens by number of columns in schema,
        where the number of tokens is obtained from splitting entry string by
        the delimiter.

        Entries in the matrix are either 0 or 1, where 0 denotes that the
        token can be placed in that column, and 1 otherwise.

        Args:
            new_entry (str): String to be processed.

        Returns:
            ValidityMatrix. Matrix of size number of tokens by number of columns in schema.
        """
        tokens = new_entry.split(",")
        num_cols = len(self.schema.get_column_names())
        num_tokens = len(tokens)
        validity_matrix = np.ones((num_tokens, num_cols))
        furthest_col = 0

        logger.info(f"Creating validity matrix for line '{new_entry}'")

        # Note that the only movements that can be done are moving
        # - south (next token is in same column)
        # - south east (next token is in the next column)
        for token_index, token in enumerate(tokens):
            first_valid_index = -1
            for column_index, column_name in enumerate(self.schema.get_column_names()):
                # Check first if there is a valid path leading to this element
                preceding_zero = self.__check_preceding_zero_in_path(
                    validity_matrix=validity_matrix,
                    token_index=token_index,
                    column_index=column_index,
                )
                # Update the current element with validity
                if preceding_zero or token_index == 0:
                    validity_matrix[token_index][column_index] = (
                        0
                        if self.schema.is_token_valid(
                            token=token.strip(), column_name=column_name
                        )
                        else 1
                    )
                    if (
                        len(token) == 0
                        and self.schema.columns[column_name].has_commas()
                    ):
                        # If the current token is empty but the column allows
                        # spaces, set this element to valid (may be due to typo).
                        # Process later when building string from path.
                        validity_matrix[token_index][column_index] = 0
                else:
                    continue
                # For storing furthest index to stop processing further columns
                # since we can not move across columns on the same token.
                if (
                    validity_matrix[token_index][column_index] == 0
                    and first_valid_index == -1
                    and token_index == 0
                ):
                    first_valid_index = column_index
                    break
                elif (
                    validity_matrix[token_index][column_index] == 0
                    and column_index > first_valid_index
                ):
                    first_valid_index = column_index
                if token_index != 0 and column_index > furthest_col:
                    break
            furthest_col = (
                first_valid_index
                if first_valid_index >= furthest_col + 1
                else furthest_col
            )
        return validity_matrix

    def __check_preceding_zero_in_path(
        self, validity_matrix: ValidityMatrix, token_index: int, column_index: int
    ) -> bool:
        """
        Checks whether the preceding elements in the matrix given an entry are 0,
        resulting in a valid path.

        Given `(token_index, column_index)`, checks whether the preceding elements
        in the path leading to the current element is valid, which creates a valid
        path.

        Preceding elements is the previous token in the same column,
        and the previous token in the prior columnn.

        Args:
            validity_matrix (ValidityMatrix): Matrix to check whether preceding elements
            in path are valid.
            token_index (int): Current token/row being validated.
            column_index (int): Current column being validated.

        Returns:
            Boolean. Returns True if the path to current element is valid, and False otherwise.
        """
        if column_index > 0 and token_index > 0:
            if (
                validity_matrix[token_index - 1][column_index - 1] == 0
                or validity_matrix[token_index - 1][column_index] == 0
            ):
                return True
        elif column_index == 0 and token_index > 0:
            if validity_matrix[token_index - 1][column_index] == 0:
                return True
        return False

    def __create_graph(self, validity_matrix: ValidityMatrix) -> nx.DiGraph:
        """
        Creates Directed Acyclic Graph for finding valid parsings
        via Single Source Shortest Paths (SSSP).

        Args:
            validity_matrix (ValidityMatrix): Matrix containing which
            tokens can be placed in which columns.

        Returns:
            nx.DiGraph. Returns networkx.DiGraph for running SSSP on.
        """
        (num_tokens, num_columns) = validity_matrix.shape
        columns = self.schema.get_column_names()

        G = nx.DiGraph()
        for row in range(num_tokens):
            for column in range(num_columns):
                add_diagonal_edge: bool = False
                add_vertical_edge: bool = False
                # Handling edge case of matrix (if on last column)
                if (
                    row + 1 < num_tokens
                    and column == num_columns - 1
                    and self.schema.get_column(columns[column]).has_commas()
                ):
                    if (
                        validity_matrix[row][column] != 1
                        and validity_matrix[row + 1][column] != 1
                    ):
                        # Add vertical edge if and only if the
                        # next token can be placed in the same column
                        # and column allows commas
                        add_vertical_edge = True
                elif (
                    row + 1 < num_tokens
                    and column + 1 < num_columns
                    and validity_matrix[row][column] != 1
                ):
                    if validity_matrix[row + 1][column + 1] != 1:
                        # Add diagonal edge if and only if the
                        # next token can be placed in the next column
                        add_diagonal_edge = True
                    if (
                        self.schema.get_column(columns[column]).has_commas()
                        and validity_matrix[row + 1][column] != 1
                    ):
                        # Add vertical edge if and only if the
                        # next token can be placed in the same column
                        # and column allows commas
                        add_vertical_edge = True
                if add_diagonal_edge:
                    G.add_edge(
                        u_of_edge=(row, column),
                        v_of_edge=(row + 1, column + 1),
                        weight=validity_matrix[row][column],
                    )
                if add_vertical_edge:
                    G.add_edge(
                        u_of_edge=(row, column),
                        v_of_edge=(row + 1, column),
                        weight=validity_matrix[row][column],
                    )
        return G

    def __find_shortest_paths(
        self, validity_matrix: ValidityMatrix, line_index: Optional[int] = None
    ) -> Optional[list[Path]]:
        """
        Finds the shortest paths from the constructed validity matrix if one exists using networkx.

        Constructs a networkx directed acyclic graph from the validity matrix and
        finds the shortest paths such that the first token is in the first column, and the
        final token is in the final column.

        Args:
            validity_matrix (ValidityMatrix): Validity matrix constructed from the entry
            to be processed against schema columns.
            line_number (Optional[int]): Index of line being processed.

        Returns:
            Optional[list[Path]]. Returns a list of shortest paths if at least one exists, and
            None otherwise.
        """

        # Construct the network graph from validity matrix,
        # only adding nodes and edges where the value is 0
        # in the validity matrix.
        (num_tokens, num_columns) = validity_matrix.shape
        G = self.__create_graph(validity_matrix=validity_matrix)
        logger.debug(validity_matrix)
        try:
            return list(
                nx.all_shortest_paths(
                    G=G,
                    source=(0, 0),
                    target=(num_tokens - 1, num_columns - 1),
                    weight="weight",
                )
            )
        except NetworkXNoPath:
            if line_index is not None:
                logger.warning(f"No paths found at line index {line_index}.")
            else:
                logger.warning("No paths found")
            return None
        except NodeNotFound:
            if line_index is not None:
                logger.warning(
                    f"Source node (0,0) not found at line index {line_index}."
                )
            else:
                logger.warning("Source node (0,0) not found")
            return None


def create_chunks(
    filepath: str | Iterable[str],
    lines_per_chunk: Optional[int],
    skip_first_line: bool,
) -> list[StringIO]:
    """
    Creates a list of chunks for the user to manually run fix_file on.
    """
    if not isinstance(filepath, str):
        f = filepath
        if skip_first_line:
            f.readline()
        all_text = f.read()
        data = all_text.split("\n")
        chunks: list[StringIO] = list()
        if lines_per_chunk is None:
            chunk_size = int(len(data) / os.cpu_count())
        else:
            chunk_size = lines_per_chunk
        num_chunks = math.ceil(len(data) / chunk_size)
        for i in range(num_chunks):
            chunks.append(
                StringIO("\n".join(data[i * chunk_size : (i + 1) * chunk_size]))
            )
        return chunks
    try:
        with open(filepath) as f:
            if skip_first_line:
                f.readline()
            all_text = f.read()
            data = all_text.split("\n")
            chunks: list[StringIO] = list()
            if lines_per_chunk is None:
                chunk_size = int(len(data) / os.cpu_count())
            else:
                chunk_size = lines_per_chunk
            num_chunks = math.ceil(len(data) / chunk_size)
            for i in range(num_chunks):
                chunks.append(
                    StringIO("\n".join(data[i * chunk_size : (i + 1) * chunk_size]))
                )
            return chunks
    except Exception as e:
        print(e)
