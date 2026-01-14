#!/usr/bin/env python3
"""
Database module for lead enrichment system.

Provides SQLite-backed storage for lead tables with:
- Dynamic column schema
- Transaction support
- Incremental updates
- Execution tracking

Error-first pattern: All functions return (result, error) tuples.
"""

import sqlite3
from pathlib import Path
from typing import Optional
from datetime import datetime
import json
from threading import Lock
import hashlib


class LeadDB:
    """SQLite database for a single lead table."""

    def __init__(self, db_path: Path):
        """
        Initialize LeadDB with path to database file.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None
        self._lock = Lock()  # Thread safety for updates

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if self.conn:
            self.conn.close()

    def connect(self) -> str:
        """
        Connect to database.

        Returns:
            error: Empty string on success, error message on failure
        """
        try:
            self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
            self.conn.row_factory = sqlite3.Row  # Dict-like access
            # Enable WAL mode for concurrent reads during writes
            self.conn.execute("PRAGMA journal_mode=WAL")
            return ""
        except Exception as e:
            return f"connect error: {e}"

    def init_schema(self) -> str:
        """
        Initialize database schema (create tables if not exist).

        Returns:
            error: Empty string on success, error message on failure
        """
        if not self.conn:
            return "not connected"

        try:
            cursor = self.conn.cursor()

            # Create all tables
            cursor.executescript("""
                -- Main data table with dynamic columns
                CREATE TABLE IF NOT EXISTS leads (
                    _id INTEGER PRIMARY KEY AUTOINCREMENT,
                    _source_row_index INTEGER,
                    _created_at TEXT DEFAULT (datetime('now')),
                    _updated_at TEXT DEFAULT (datetime('now')),
                    _status TEXT DEFAULT 'pending',
                    _error TEXT
                );

                -- Column metadata (track which node produced which column)
                CREATE TABLE IF NOT EXISTS columns (
                    column_name TEXT PRIMARY KEY,
                    column_type TEXT,
                    source TEXT,
                    created_at TEXT DEFAULT (datetime('now')),
                    description TEXT
                );

                -- Workflow execution history
                CREATE TABLE IF NOT EXISTS executions (
                    execution_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    workflow_type TEXT,
                    workflow_name TEXT,
                    started_at TEXT DEFAULT (datetime('now')),
                    completed_at TEXT,
                    total_rows INTEGER,
                    success_count INTEGER,
                    failed_count INTEGER,
                    config TEXT,
                    output_path TEXT
                );

                -- Row-level execution tracking
                CREATE TABLE IF NOT EXISTS row_executions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    execution_id INTEGER,
                    row_id INTEGER,
                    node_name TEXT,
                    started_at TEXT DEFAULT (datetime('now')),
                    completed_at TEXT,
                    status TEXT,
                    error TEXT,
                    FOREIGN KEY (execution_id) REFERENCES executions(execution_id),
                    FOREIGN KEY (row_id) REFERENCES leads(_id)
                );

                -- Indexes for performance
                CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(_status);
                CREATE INDEX IF NOT EXISTS idx_row_executions_execution ON row_executions(execution_id);
                CREATE INDEX IF NOT EXISTS idx_row_executions_row ON row_executions(row_id);

                -- Node-level cache keyed by (node_name + input_hash + config_hash)
                CREATE TABLE IF NOT EXISTS node_cache (
                    cache_key TEXT PRIMARY KEY,
                    node_name TEXT,
                    input_hash TEXT,
                    config_hash TEXT,
                    created_at TEXT DEFAULT (datetime('now')),
                    result_json TEXT,
                    error TEXT
                );

                CREATE INDEX IF NOT EXISTS idx_node_cache_node ON node_cache(node_name);
                CREATE INDEX IF NOT EXISTS idx_node_cache_hashes ON node_cache(input_hash, config_hash);
            """)

            # Add forward-compatible columns (SQLite lacks ADD COLUMN IF NOT EXISTS)
            err = self._ensure_column("row_executions", "input_hash", "TEXT")
            if err:
                return err
            err = self._ensure_column("row_executions", "config_hash", "TEXT")
            if err:
                return err
            err = self._ensure_column("row_executions", "cache_hit", "INTEGER")
            if err:
                return err

            self.conn.commit()
            return ""
        except Exception as e:
            return f"init_schema error: {e}"

    @staticmethod
    def _quote_ident(identifier: str) -> str:
        """
        Quote an SQLite identifier safely (column/table name).

        Uses double-quote escaping per SQLite rules.
        """
        if identifier is None:
            raise ValueError("identifier is None")
        return '"' + str(identifier).replace('"', '""') + '"'

    def _ensure_column(self, table: str, column_name: str, column_type: str) -> str:
        """Ensure a column exists on a table; adds it if missing."""
        if not self.conn:
            return "not connected"

        try:
            cursor = self.conn.cursor()
            cursor.execute(f"PRAGMA table_info({self._quote_ident(table)})")
            existing = {row[1] for row in cursor.fetchall()}

            if column_name in existing:
                return ""

            cursor.execute(
                f"ALTER TABLE {self._quote_ident(table)} "
                f"ADD COLUMN {self._quote_ident(column_name)} {column_type}"
            )
            self.conn.commit()
            return ""
        except Exception as e:
            return f"ensure_column error: {e}"

    def import_csv(self, csv_rows: list[dict]) -> tuple[int, str]:
        """
        Import CSV rows into database.

        Args:
            csv_rows: List of dicts representing CSV rows

        Returns:
            (row_count, error): Number of rows imported and error message
        """
        if not self.conn:
            return 0, "not connected"

        if not csv_rows:
            return 0, "empty csv_rows"

        try:
            with self._lock:
                cursor = self.conn.cursor()

                # Get CSV columns (all keys from first row)
                csv_columns = list(csv_rows[0].keys())

                # Add columns to schema
                for col in csv_columns:
                    err = self._add_column_if_needed(col, "csv")
                    if err:
                        return 0, err

                # Insert rows
                insert_columns = ["_source_row_index"] + csv_columns
                columns_str = ", ".join([self._quote_ident(c) for c in insert_columns])
                for idx, row in enumerate(csv_rows):
                    placeholders = ", ".join(["?"] * len(insert_columns))
                    values = [idx] + [row.get(col, "") for col in csv_columns]

                    cursor.execute(
                        f"INSERT INTO leads ({columns_str}) VALUES ({placeholders})",
                        values
                    )

                self.conn.commit()
                return len(csv_rows), ""

        except Exception as e:
            if self.conn:
                self.conn.rollback()
            return 0, f"import_csv error: {e}"

    def _add_column_if_needed(self, column_name: str, source: str) -> str:
        """
        Add column to leads table if it doesn't exist (internal method).

        Args:
            column_name: Name of column to add
            source: Source of column ('csv' or node name)

        Returns:
            error: Empty string on success, error message on failure
        """
        try:
            cursor = self.conn.cursor()

            # Check if column exists
            cursor.execute("PRAGMA table_info(leads)")
            existing = {row[1] for row in cursor.fetchall()}

            if column_name not in existing:
                # SQLite ALTER TABLE limitation: can't add with constraints
                # Use TEXT for all dynamic columns (simplifies schema)
                cursor.execute(f"ALTER TABLE leads ADD COLUMN {self._quote_ident(column_name)} TEXT")

                # Record metadata
                cursor.execute("""
                    INSERT OR IGNORE INTO columns (column_name, column_type, source)
                    VALUES (?, 'text', ?)
                """, (column_name, source))

                self.conn.commit()

            return ""
        except Exception as e:
            return f"add_column error: {e}"

    def get_rows(self, status: Optional[str] = None, limit: Optional[int] = None) -> tuple[list[dict], str]:
        """
        Get rows from database, optionally filtered by status.

        Args:
            status: Filter by status ('pending', 'processing', 'completed', 'failed'), None for all
            limit: Maximum number of rows to return, None for all

        Returns:
            (rows, error): List of row dicts and error message
        """
        if not self.conn:
            return [], "not connected"

        try:
            cursor = self.conn.cursor()

            query = "SELECT * FROM leads"
            params = []

            if status:
                query += " WHERE _status = ?"
                params.append(status)

            if limit:
                query += " LIMIT ?"
                params.append(limit)

            cursor.execute(query, params)
            rows = [dict(row) for row in cursor.fetchall()]

            return rows, ""
        except Exception as e:
            return [], f"get_rows error: {e}"

    def filter_rows(self, where_clause: str) -> tuple[list[dict], str]:
        """
        Filter rows using a SQL WHERE clause.

        Args:
            where_clause: SQL WHERE condition (e.g., "is_b2b = 1" or "status = 'active'")

        Returns:
            (rows, error): List of filtered row dicts and error message
        """
        if not self.conn:
            return [], "not connected"

        if not where_clause or not where_clause.strip():
            return [], "empty where_clause"

        try:
            cursor = self.conn.cursor()

            # Build query with WHERE clause
            query = f"SELECT * FROM leads WHERE {where_clause}"

            cursor.execute(query)
            rows = [dict(row) for row in cursor.fetchall()]

            return rows, ""
        except Exception as e:
            return [], f"filter_rows error: {e}"

    def update_row(self, row_id: int, updates: dict, status: Optional[str] = None, error: Optional[str] = None) -> str:
        """
        Update a row with enrichment data.

        Args:
            row_id: Row ID (_id column)
            updates: Dict of column: value pairs to update
            status: Optional status to set ('completed', 'failed', etc.)
            error: Optional error message to record

        Returns:
            error: Empty string on success, error message on failure
        """
        if not self.conn:
            return "not connected"

        try:
            with self._lock:
                cursor = self.conn.cursor()

                # Add columns for new fields
                for col in updates.keys():
                    err = self._add_column_if_needed(col, "enrichment")
                    if err:
                        return err

                # Build UPDATE query
                set_clauses = []
                values = []

                # Add update columns
                for col, val in updates.items():
                    set_clauses.append(f"{self._quote_ident(col)} = ?")
                    values.append(val)

                # Always update timestamp
                set_clauses.append("_updated_at = datetime('now')")

                # Optional status update
                if status:
                    set_clauses.append("_status = ?")
                    values.append(status)

                # Optional error update
                if error is not None:
                    set_clauses.append("_error = ?")
                    values.append(error if error else None)

                # Add row_id for WHERE clause
                values.append(row_id)

                set_clause = ", ".join(set_clauses)
                cursor.execute(
                    f"UPDATE leads SET {set_clause} WHERE _id = ?",
                    values
                )

                self.conn.commit()
                return ""

        except Exception as e:
            if self.conn:
                self.conn.rollback()
            return f"update_row error: {e}"

    def start_execution(self, workflow_type: str, workflow_name: str, total_rows: int, config: Optional[dict] = None) -> tuple[int, str]:
        """
        Start a new execution and return execution_id.

        Args:
            workflow_type: Type of workflow ('graph' or 'integration')
            workflow_name: Name of workflow/graph
            total_rows: Total number of rows to process
            config: Optional config dict

        Returns:
            (execution_id, error): Execution ID and error message
        """
        if not self.conn:
            return 0, "not connected"

        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO executions (workflow_type, workflow_name, total_rows, config)
                VALUES (?, ?, ?, ?)
            """, (workflow_type, workflow_name, total_rows, json.dumps(config or {})))

            self.conn.commit()
            return cursor.lastrowid, ""
        except Exception as e:
            return 0, f"start_execution error: {e}"

    def complete_execution(self, execution_id: int, success_count: int, failed_count: int, output_path: Optional[str] = None) -> str:
        """
        Mark execution as complete.

        Args:
            execution_id: Execution ID from start_execution
            success_count: Number of successful rows
            failed_count: Number of failed rows
            output_path: Optional path to exported CSV

        Returns:
            error: Empty string on success, error message on failure
        """
        if not self.conn:
            return "not connected"

        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                UPDATE executions
                SET completed_at = datetime('now'),
                    success_count = ?,
                    failed_count = ?,
                    output_path = ?
                WHERE execution_id = ?
            """, (success_count, failed_count, output_path, execution_id))

            self.conn.commit()
            return ""
        except Exception as e:
            return f"complete_execution error: {e}"

    def has_completed_row_execution(self, row_id: int, node_name: str, input_hash: str, config_hash: str) -> tuple[bool, str]:
        """Return True if this row has already completed this node for the same inputs/config."""
        if not self.conn:
            return False, "not connected"

        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """
                SELECT 1
                FROM row_executions
                WHERE row_id = ?
                  AND node_name = ?
                  AND input_hash = ?
                  AND config_hash = ?
                  AND status = 'completed'
                LIMIT 1
                """,
                (row_id, node_name, input_hash, config_hash),
            )
            return cursor.fetchone() is not None, ""
        except Exception as e:
            return False, f"has_completed_row_execution error: {e}"

    def start_row_execution(
        self,
        execution_id: int,
        row_id: int,
        node_name: str,
        input_hash: str,
        config_hash: str,
        cache_hit: bool,
    ) -> tuple[int, str]:
        """Insert a row_executions record and return its ID."""
        if not self.conn:
            return 0, "not connected"

        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """
                INSERT INTO row_executions (execution_id, row_id, node_name, status, input_hash, config_hash, cache_hit)
                VALUES (?, ?, ?, 'running', ?, ?, ?)
                """,
                (execution_id, row_id, node_name, input_hash, config_hash, 1 if cache_hit else 0),
            )
            self.conn.commit()
            return cursor.lastrowid, ""
        except Exception as e:
            return 0, f"start_row_execution error: {e}"

    def complete_row_execution(self, row_execution_id: int, status: str, error: Optional[str]) -> str:
        """Mark a row_executions record as completed/failed."""
        if not self.conn:
            return "not connected"

        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """
                UPDATE row_executions
                SET completed_at = datetime('now'),
                    status = ?,
                    error = ?
                WHERE id = ?
                """,
                (status, error if error else None, row_execution_id),
            )
            self.conn.commit()
            return ""
        except Exception as e:
            return f"complete_row_execution error: {e}"

    @staticmethod
    def _sha256(text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def get_cache_entry(self, cache_key: str) -> tuple[Optional[dict], str, str]:
        """
        Get a cached node result.

        Returns:
            (result_dict_or_none, cached_error, error)
        """
        if not self.conn:
            return None, "", "not connected"

        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT result_json, error FROM node_cache WHERE cache_key = ?",
                (cache_key,),
            )
            row = cursor.fetchone()
            if not row:
                return None, "", ""

            cached_error = row[1] or ""
            result_json = row[0] or ""
            if not result_json:
                return None, cached_error, ""

            try:
                result = json.loads(result_json)
            except Exception:
                return None, cached_error, ""

            return result, cached_error, ""
        except Exception as e:
            return None, "", f"get_cache_entry error: {e}"

    def set_cache_entry(
        self,
        cache_key: str,
        node_name: str,
        input_hash: str,
        config_hash: str,
        result: dict,
        error: str,
    ) -> str:
        """Upsert a cached node result."""
        if not self.conn:
            return "not connected"

        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """
                INSERT INTO node_cache (cache_key, node_name, input_hash, config_hash, result_json, error)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(cache_key) DO UPDATE SET
                    created_at = datetime('now'),
                    result_json = excluded.result_json,
                    error = excluded.error
                """,
                (cache_key, node_name, input_hash, config_hash, json.dumps(result), error if error else None),
            )
            self.conn.commit()
            return ""
        except Exception as e:
            return f"set_cache_entry error: {e}"

    def export_to_csv(self, output_path: Optional[Path] = None) -> tuple[list[dict], str]:
        """
        Export all rows to CSV format (list of dicts).
        Internal columns (starting with _) are excluded.

        Args:
            output_path: Unused (kept for compatibility)

        Returns:
            (rows, error): List of row dicts (without internal columns) and error message
        """
        if not self.conn:
            return [], "not connected"

        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM leads")
            rows = [dict(row) for row in cursor.fetchall()]

            # Remove internal columns (starting with _)
            clean_rows = []
            for row in rows:
                clean_row = {k: v for k, v in row.items() if not k.startswith('_')}
                clean_rows.append(clean_row)

            return clean_rows, ""
        except Exception as e:
            return [], f"export_to_csv error: {e}"

    def get_stats(self) -> tuple[dict, str]:
        """
        Get database statistics.

        Returns:
            (stats, error): Dict with stats and error message
        """
        if not self.conn:
            return {}, "not connected"

        try:
            cursor = self.conn.cursor()

            # Count rows by status
            cursor.execute("""
                SELECT _status, COUNT(*) as count
                FROM leads
                GROUP BY _status
            """)
            status_counts = {row[0]: row[1] for row in cursor.fetchall()}

            # Total rows
            cursor.execute("SELECT COUNT(*) FROM leads")
            total_rows = cursor.fetchone()[0]

            # Column count
            cursor.execute("PRAGMA table_info(leads)")
            all_cols = cursor.fetchall()
            data_cols = [col[1] for col in all_cols if not col[1].startswith('_')]

            stats = {
                "total_rows": total_rows,
                "status_counts": status_counts,
                "column_count": len(data_cols),
                "data_columns": data_cols
            }

            return stats, ""
        except Exception as e:
            return {}, f"get_stats error: {e}"
