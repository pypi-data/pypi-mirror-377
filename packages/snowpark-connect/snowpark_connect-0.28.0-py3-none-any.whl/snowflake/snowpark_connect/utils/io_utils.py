#
# Copyright (c) 2012-2025 Snowflake Computing Inc. All rights reserved.
#
import contextlib
import functools

from snowflake.snowpark import Session
from snowflake.snowpark_connect.utils.identifiers import FQN


@functools.cache
def file_format(
    session: Session, compression: str, record_delimiter: str = None
) -> str:
    """
    Create a temporary file format for reading text files in Snowpark Connect.
    """
    if record_delimiter is None:
        record_delimiter = "NONE"
        identifier_delimiter = "NONE"
    else:
        record_delimiter = record_delimiter
        # Encode delimiter to ensure that it is a valid identifier
        identifier_delimiter = record_delimiter.encode("utf-8").hex()

    file_format_name = f"IDENTIFIER('__SNOWPARK_CONNECT_TEXT_FILE_FORMAT__{compression}_{identifier_delimiter}')"
    session.sql(
        f"""
    CREATE TEMPORARY FILE FORMAT IF NOT EXISTS  {file_format_name}
    RECORD_DELIMITER = '{record_delimiter}'
    FIELD_DELIMITER = 'NONE'
    EMPTY_FIELD_AS_NULL = FALSE
    COMPRESSION = '{compression}'"""
    ).collect()

    return file_format_name


def get_table_type(
    snowpark_table_name: str,
    snowpark_session: Session,
) -> str:
    fqn = FQN.from_string(snowpark_table_name)
    with contextlib.suppress(Exception):
        if fqn.database is not None:
            return snowpark_session.catalog.getTable(
                table_name=fqn.name, schema=fqn.schema, database=fqn.database
            ).table_type
        elif fqn.schema is not None:
            return snowpark_session.catalog.getTable(
                table_name=fqn.name, schema=fqn.schema
            ).table_type
        else:
            return snowpark_session.catalog.getTable(table_name=fqn.name).table_type
    return "TABLE"
