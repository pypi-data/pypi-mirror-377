import csv
import logging
from dataclasses import dataclass
from typing import TypeAlias

import pandas as pd

from comma_fixer.schema import Schema

InvalidEntry: TypeAlias = tuple[int, str]
ParsedEntry: TypeAlias = list[str]
logger = logging.getLogger("Parsed Logs")


@dataclass
class Parsed:
    """
    Parsed class produced from calling `fix_file` in Fixer.

    Attributes:
        _schema (Schema): Schema of dataset.
        _processed (str): CSV of dataset stored as a string.
        _invalid_line_numbers (list[InvalidEntry]): List of invalid entries containing line number and entry.
        _skip_first_line (bool): Whether the original CSV file had headers as the first row.
    """

    _schema: Schema
    _processed: str
    _invalid_entries: list[InvalidEntry]
    _skip_first_line: bool

    @classmethod
    def new(
        cls,
        schema: Schema,
        processed_csv: str,
        invalid_entries: list[InvalidEntry],
        skip_first_line: bool,
    ) -> "Parsed":
        """
        Creates an empty Parsed object with specified Schema.

        Args:
            schema (Schema): Schema of dataset.
            processed_csv (str): Processed CSV as a string.
            invalid_entries (list[InvalidEntry]): List of invalid entries with line index.
            skip_first_line (bool): Whether the first line was skipped in original input file.

        Returns:
            Parsed. Parsed object with specified schema.
        """
        return Parsed(
            _schema=schema,
            _processed=processed_csv,
            _invalid_entries=invalid_entries,
            _skip_first_line=skip_first_line,
        )

    def export_to_csv_best_effort(self, filepath: str, encoding: str = "utf-8"):
        """
        Exports valid entries to CSV at specified filepath.

        Converts valid entries into DataFrame before exporting to CSV.

        Args:
            filepath (str): Filepath of CSV file to create and write to.
            encoding (str): Encoding to use when exporting to CSV. Default "utf-8".
        """
        processed_to_csv = pd.DataFrame(self._schema.get_series_dict())
        for line_number, line in enumerate(self._processed.split("\n")):
            if self._skip_first_line:
                line_number += 1
            if (line_number, line) not in self._invalid_entries:
                parsed_csv = list(csv.reader([line]))[0]
                processed_to_csv.loc[len(processed_to_csv)] = parsed_csv
        logger.info(processed_to_csv.info())
        return processed_to_csv.to_csv(filepath, index=False, encoding=encoding)

    def convert_to_dataframe_best_effort(self) -> pd.DataFrame:
        """
        Converts valid entries into a DataFrame.
        """
        convert_to_dataframe = pd.DataFrame(self._schema.get_series_dict())
        for line_number, line in enumerate(self._processed.split("\n")):
            if self._skip_first_line:
                line_number += 1
            if (line_number, line) not in self._invalid_entries:
                parsed_csv = list(csv.reader([line]))[0]
                convert_to_dataframe.loc[len(convert_to_dataframe)] = parsed_csv
        logger.info(convert_to_dataframe.info())
        return convert_to_dataframe

    def print_all_invalid_entries(self):
        """
        Prints all the invalid entries with their line index respective to
        the original CSV file.
        """
        print("Index\tLine entry")
        for invalid_index, invalid_line in self._invalid_entries:
            print(f"{invalid_index}\t{invalid_line}")

    def export_invalid_entries_to_csv(self, filepath: str, encoding: str = "utf-8"):
        """
        Exports invalid entries to CSV at specified filepath.

        Writes line index respective to original input CSV file of each
        invalid entry into DataFrame object and exports to CSV.

        Args:
            filepath (str): Filepath of CSV file to create and write to.
            encoding (str): Encoding to use when exporting to CSV. Default "utf-8".
        """
        processed_to_csv = pd.DataFrame(columns=["line number", "invalid entry"])
        for invalid_index, invalid_line in self._invalid_entries:
            processed_to_csv.loc[len(processed_to_csv)] = [invalid_index, invalid_line]
        logger.info(processed_to_csv.info())
        return processed_to_csv.to_csv(filepath, index=False, encoding=encoding)

    def convert_invalid_entries_to_dataframe(self):
        """
        Returns invalid entries as a dataframe of line indices and invalid entries.

        Args:
            filepath (str): Filepath of CSV file to create and write to.
            encoding (str): Encoding to use when exporting to CSV. Default "utf-8".
        """
        processed_to_csv = pd.DataFrame(columns=["line number", "invalid entry"])
        for invalid_index, invalid_line in self._invalid_entries:
            processed_to_csv.loc[len(processed_to_csv)] = [invalid_index, invalid_line]
        logger.info(processed_to_csv.info())
        return processed_to_csv

    def invalid_entries_count(self) -> int:
        return len(self._invalid_entries)

    def __eq__(self, other) -> bool:
        if not isinstance(other, Parsed):
            return False
        else:
            if not len(self._processed) == len(other._processed) or not len(
                self._invalid_entries
            ) == len(other._invalid_entries):
                return False
            # Check if the columns are exactly the same
            if not self._schema == other._schema:
                return False
            if not self._invalid_entries == other._invalid_entries:
                return False
            if not self._processed == other._processed:
                return False
            return True
