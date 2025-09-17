from typing import List, Optional, Literal, Iterator, Any
from flowfile_core.schemas import transform_schema
from pathlib import Path
import os
from flowfile_core.schemas.analysis_schemas import graphic_walker_schemas as gs_schemas
from flowfile_core.schemas.cloud_storage_schemas import CloudStorageReadSettings, CloudStorageWriteSettings
from flowfile_core.schemas.schemas import SecretRef
from flowfile_core.utils.utils import ensure_similarity_dicts, standardize_col_dtype
from pydantic import BaseModel, Field, model_validator, SecretStr, ConfigDict
import polars as pl


OutputConnectionClass = Literal['output-0', 'output-1', 'output-2', 'output-3', 'output-4',
                                'output-5', 'output-6', 'output-7', 'output-8', 'output-9']

InputConnectionClass = Literal['input-0', 'input-1', 'input-2', 'input-3', 'input-4',
                               'input-5', 'input-6', 'input-7', 'input-8', 'input-9']

InputType = Literal["main", "left", "right"]


class NewDirectory(BaseModel):
    """Defines the information required to create a new directory."""
    source_path: str
    dir_name: str


class RemoveItem(BaseModel):
    """Represents a single item to be removed from a directory or list."""
    path: str
    id: int = -1


class RemoveItemsInput(BaseModel):
    """Defines a list of items to be removed."""
    paths: List[RemoveItem]
    source_path: str


class MinimalFieldInfo(BaseModel):
    """Represents the most basic information about a data field (column)."""
    name: str
    data_type: str = "String"


class ReceivedTableBase(BaseModel):
    """Base model for defining a table received from an external source."""
    id: Optional[int] = None
    name: Optional[str]
    path: str  # This can be an absolute or relative path
    directory: Optional[str] = None
    analysis_file_available: bool = False
    status: Optional[str] = None
    file_type: Optional[str] = None
    fields: List[MinimalFieldInfo] = Field(default_factory=list)
    abs_file_path: Optional[str] = None

    @classmethod
    def create_from_path(cls, path: str):
        """Creates an instance from a file path string."""
        filename = Path(path).name
        return cls(name=filename, path=path)

    @property
    def file_path(self) -> str:
        """Constructs the full file path from the directory and name."""
        if not self.name in self.path:
            return os.path.join(self.path, self.name)
        else:
            return self.path

    def set_absolute_filepath(self):
        """Resolves the path to an absolute file path."""
        base_path = Path(self.path).expanduser()
        if not base_path.is_absolute():
            base_path = Path.cwd() / base_path
        if self.name and self.name not in base_path.name:
            base_path = base_path / self.name
        self.abs_file_path = str(base_path.resolve())

    @model_validator(mode='after')
    def populate_abs_file_path(self):
        """Ensures the absolute file path is populated after validation."""
        if not self.abs_file_path:
            self.set_absolute_filepath()
        return self


class ReceivedCsvTable(ReceivedTableBase):
    """Defines settings for reading a CSV file."""
    file_type: str = 'csv'
    reference: str = ''
    starting_from_line: int = 0
    delimiter: str = ','
    has_headers: bool = True
    encoding: Optional[str] = 'utf-8'
    parquet_ref: Optional[str] = None
    row_delimiter: str = '\n'
    quote_char: str = '"'
    infer_schema_length: int = 10_000
    truncate_ragged_lines: bool = False
    ignore_errors: bool = False


class ReceivedJsonTable(ReceivedCsvTable):
    """Defines settings for reading a JSON file (inherits from CSV settings)."""
    pass


class ReceivedParquetTable(ReceivedTableBase):
    """Defines settings for reading a Parquet file."""
    file_type: str = 'parquet'


class ReceivedExcelTable(ReceivedTableBase):
    """Defines settings for reading an Excel file."""
    sheet_name: Optional[str] = None
    start_row: int = 0
    start_column: int = 0
    end_row: int = 0
    end_column: int = 0
    has_headers: bool = True
    type_inference: bool = False

    def validate_range_values(self):
        """Validates that the Excel cell range is logical."""
        for attribute in [self.start_row, self.start_column, self.end_row, self.end_column]:
            if not isinstance(attribute, int) or attribute < 0:
                raise ValueError("Row and column indices must be non-negative integers")
        if (self.end_row > 0 and self.start_row > self.end_row) or \
           (self.end_column > 0 and self.start_column > self.end_column):
            raise ValueError("Start row/column must not be greater than end row/column")


class ReceivedTable(ReceivedExcelTable, ReceivedCsvTable, ReceivedParquetTable):
    """A comprehensive model that can represent any type of received table."""
    ...


class OutputCsvTable(BaseModel):
    """Defines settings for writing a CSV file."""
    file_type: str = 'csv'
    delimiter: str = ','
    encoding: str = 'utf-8'


class OutputParquetTable(BaseModel):
    """Defines settings for writing a Parquet file."""
    file_type: str = 'parquet'


class OutputExcelTable(BaseModel):
    """Defines settings for writing an Excel file."""
    file_type: str = 'excel'
    sheet_name: str = 'Sheet1'


class OutputSettings(BaseModel):
    """Defines the complete settings for an output node."""
    name: str
    directory: str
    file_type: str
    fields: Optional[List[str]] = Field(default_factory=list)
    write_mode: str = 'overwrite'
    output_csv_table: Optional[OutputCsvTable] = Field(default_factory=OutputCsvTable)
    output_parquet_table: OutputParquetTable = Field(default_factory=OutputParquetTable)
    output_excel_table: OutputExcelTable = Field(default_factory=OutputExcelTable)
    abs_file_path: Optional[str] = None

    def set_absolute_filepath(self):
        """Resolves the output directory and name into an absolute path."""
        base_path = Path(self.directory)
        if not base_path.is_absolute():
            base_path = Path.cwd() / base_path
        if self.name and self.name not in base_path.name:
            base_path = base_path / self.name
        self.abs_file_path = str(base_path.resolve())

    @model_validator(mode='after')
    def populate_abs_file_path(self):
        """Ensures the absolute file path is populated after validation."""
        self.set_absolute_filepath()
        return self


class NodeBase(BaseModel):
    """Base model for all nodes in a FlowGraph. Contains common metadata."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    flow_id: int
    node_id: int
    cache_results: Optional[bool] = False
    pos_x: Optional[float] = 0
    pos_y: Optional[float] = 0
    is_setup: Optional[bool] = True
    description: Optional[str] = ''
    user_id: Optional[int] = None
    is_flow_output: Optional[bool] = False
    is_user_defined: Optional[bool] = False  # Indicator if the node is a user defined node


class NodeSingleInput(NodeBase):
    """A base model for any node that takes a single data input."""
    depending_on_id: Optional[int] = -1


class NodeMultiInput(NodeBase):
    """A base model for any node that takes multiple data inputs."""
    depending_on_ids: Optional[List[int]] = [-1]


class NodeSelect(NodeSingleInput):
    """Settings for a node that selects, renames, and reorders columns."""
    keep_missing: bool = True
    select_input: List[transform_schema.SelectInput] = Field(default_factory=list)
    sorted_by: Optional[Literal['none', 'asc', 'desc']] = 'none'


class NodeFilter(NodeSingleInput):
    """Settings for a node that filters rows based on a condition."""
    filter_input: transform_schema.FilterInput


class NodeSort(NodeSingleInput):
    """Settings for a node that sorts the data by one or more columns."""
    sort_input: List[transform_schema.SortByInput] = Field(default_factory=list)


class NodeTextToRows(NodeSingleInput):
    """Settings for a node that splits a text column into multiple rows."""
    text_to_rows_input: transform_schema.TextToRowsInput


class NodeSample(NodeSingleInput):
    """Settings for a node that samples a subset of the data."""
    sample_size: int = 1000


class NodeRecordId(NodeSingleInput):
    """Settings for a node that adds a unique record ID column."""
    record_id_input: transform_schema.RecordIdInput


class NodeJoin(NodeMultiInput):
    """Settings for a node that performs a standard SQL-style join."""
    auto_generate_selection: bool = True
    verify_integrity: bool = True
    join_input: transform_schema.JoinInput
    auto_keep_all: bool = True
    auto_keep_right: bool = True
    auto_keep_left: bool = True


class NodeCrossJoin(NodeMultiInput):
    """Settings for a node that performs a cross join."""
    auto_generate_selection: bool = True
    verify_integrity: bool = True
    cross_join_input: transform_schema.CrossJoinInput
    auto_keep_all: bool = True
    auto_keep_right: bool = True
    auto_keep_left: bool = True


class NodeFuzzyMatch(NodeJoin):
    """Settings for a node that performs a fuzzy join based on string similarity."""
    join_input: transform_schema.FuzzyMatchInput


class NodeDatasource(NodeBase):
    """Base settings for a node that acts as a data source."""
    file_ref: str = None


class RawData(BaseModel):
    """Represents data in a raw, columnar format for manual input."""
    columns: List[MinimalFieldInfo] = None
    data: List[List]

    @classmethod
    def from_pylist(cls, pylist: List[dict]):
        """Creates a RawData object from a list of Python dictionaries."""
        if len(pylist) == 0:
            return cls(columns=[], data=[])
        pylist = ensure_similarity_dicts(pylist)
        values = [standardize_col_dtype([vv for vv in c]) for c in
                  zip(*(r.values() for r in pylist))]
        data_types = (pl.DataType.from_python(type(next((v for v in column_values), None))) for column_values in values)
        columns = [MinimalFieldInfo(name=c, data_type=str(next(data_types))) for c in pylist[0].keys()]
        return cls(columns=columns, data=values)

    def to_pylist(self) -> List[dict]:
        """Converts the RawData object back into a list of Python dictionaries."""
        return [{c.name: self.data[ci][ri] for ci, c in enumerate(self.columns)} for ri in range(len(self.data[0]))]


class NodeManualInput(NodeBase):
    """Settings for a node that allows direct data entry in the UI."""
    raw_data_format: Optional[RawData] = None


class NodeRead(NodeBase):
    """Settings for a node that reads data from a file."""
    received_file: ReceivedTable


class DatabaseConnection(BaseModel):
    """Defines the connection parameters for a database."""
    database_type: str = "postgresql"
    username: Optional[str] = None
    password_ref: Optional[SecretRef] = None
    host: Optional[str] = None
    port: Optional[int] = None
    database: Optional[str] = None
    url: Optional[str] = None


class FullDatabaseConnection(BaseModel):
    """A complete database connection model including the secret password."""
    connection_name: str
    database_type: str = "postgresql"
    username: str
    password: SecretStr
    host: Optional[str] = None
    port: Optional[int] = None
    database: Optional[str] = None
    ssl_enabled: Optional[bool] = False
    url: Optional[str] = None


class FullDatabaseConnectionInterface(BaseModel):
    """A database connection model intended for UI display, omitting the password."""
    connection_name: str
    database_type: str = "postgresql"
    username: str
    host: Optional[str] = None
    port: Optional[int] = None
    database: Optional[str] = None
    ssl_enabled: Optional[bool] = False
    url: Optional[str] = None


class DatabaseSettings(BaseModel):
    """Defines settings for reading from a database, either via table or query."""
    connection_mode: Optional[Literal['inline', 'reference']] = 'inline'
    database_connection: Optional[DatabaseConnection] = None
    database_connection_name: Optional[str] = None
    schema_name: Optional[str] = None
    table_name: Optional[str] = None
    query: Optional[str] = None
    query_mode: Literal['query', 'table', 'reference'] = 'table'

    @model_validator(mode='after')
    def validate_table_or_query(self):
        # Validate that either table_name or query is provided
        if (not self.table_name and not self.query) and self.query_mode == 'inline':
            raise ValueError("Either 'table_name' or 'query' must be provided")

        # Validate correct connection information based on connection_mode
        if self.connection_mode == 'inline' and self.database_connection is None:
            raise ValueError("When 'connection_mode' is 'inline', 'database_connection' must be provided")

        if self.connection_mode == 'reference' and not self.database_connection_name:
            raise ValueError("When 'connection_mode' is 'reference', 'database_connection_name' must be provided")

        return self


class DatabaseWriteSettings(BaseModel):
    """Defines settings for writing data to a database table."""
    connection_mode: Optional[Literal['inline', 'reference']] = 'inline'
    database_connection: Optional[DatabaseConnection] = None
    database_connection_name: Optional[str] = None
    table_name: str
    schema_name: Optional[str] = None
    if_exists: Optional[Literal['append', 'replace', 'fail']] = 'append'


class NodeDatabaseReader(NodeBase):
    """Settings for a node that reads from a database."""
    database_settings: DatabaseSettings
    fields: Optional[List[MinimalFieldInfo]] = None


class NodeDatabaseWriter(NodeSingleInput):
    """Settings for a node that writes data to a database."""
    database_write_settings: DatabaseWriteSettings


class NodeCloudStorageReader(NodeBase):
    """Settings for a node that reads from a cloud storage service (S3, GCS, etc.)."""
    cloud_storage_settings: CloudStorageReadSettings
    fields: Optional[List[MinimalFieldInfo]] = None


class NodeCloudStorageWriter(NodeSingleInput):
    """Settings for a node that writes to a cloud storage service."""
    cloud_storage_settings: CloudStorageWriteSettings


class ExternalSource(BaseModel):
    """Base model for data coming from a predefined external source."""
    orientation: str = 'row'
    fields: Optional[List[MinimalFieldInfo]] = None


class SampleUsers(ExternalSource):
    """Settings for generating a sample dataset of users."""
    SAMPLE_USERS: bool
    class_name: str = "sample_users"
    size: int = 100


class NodeExternalSource(NodeBase):
    """Settings for a node that connects to a registered external data source."""
    identifier: str
    source_settings: SampleUsers


class NodeFormula(NodeSingleInput):
    """Settings for a node that applies a formula to create/modify a column."""
    function: transform_schema.FunctionInput = None


class NodeGroupBy(NodeSingleInput):
    """Settings for a node that performs a group-by and aggregation operation."""
    groupby_input: transform_schema.GroupByInput = None


class NodePromise(NodeBase):
    """A placeholder node for an operation that has not yet been configured."""
    is_setup: bool = False
    node_type: str


class NodeInputConnection(BaseModel):
    """Represents the input side of a connection between two nodes."""
    node_id: int
    connection_class: InputConnectionClass

    def get_node_input_connection_type(self) -> Literal['main', 'right', 'left']:
        """Determines the semantic type of the input (e.g., for a join)."""
        match self.connection_class:
            case 'input-0': return 'main'
            case 'input-1': return 'right'
            case 'input-2': return 'left'
            case _: raise ValueError(f"Unexpected connection_class: {self.connection_class}")


class NodePivot(NodeSingleInput):
    """Settings for a node that pivots data from a long to a wide format."""
    pivot_input: transform_schema.PivotInput = None
    output_fields: Optional[List[MinimalFieldInfo]] = None


class NodeUnpivot(NodeSingleInput):
    """Settings for a node that unpivots data from a wide to a long format."""
    unpivot_input: transform_schema.UnpivotInput = None


class NodeUnion(NodeMultiInput):
    """Settings for a node that concatenates multiple data inputs."""
    union_input: transform_schema.UnionInput = Field(default_factory=transform_schema.UnionInput)


class NodeOutput(NodeSingleInput):
    """Settings for a node that writes its input to a file."""
    output_settings: OutputSettings


class NodeOutputConnection(BaseModel):
    """Represents the output side of a connection between two nodes."""
    node_id: int
    connection_class: OutputConnectionClass


class NodeConnection(BaseModel):
    """Represents a connection (edge) between two nodes in the graph."""
    input_connection: NodeInputConnection
    output_connection: NodeOutputConnection

    @classmethod
    def create_from_simple_input(cls, from_id: int, to_id: int, input_type: InputType = "input-0"):
        """Creates a standard connection between two nodes."""
        match input_type:
            case "main": connection_class: InputConnectionClass = "input-0"
            case "right": connection_class: InputConnectionClass = "input-1"
            case "left": connection_class: InputConnectionClass = "input-2"
            case _: connection_class: InputConnectionClass = "input-0"
        node_input = NodeInputConnection(node_id=to_id, connection_class=connection_class)
        node_output = NodeOutputConnection(node_id=from_id, connection_class='output-0')
        return cls(input_connection=node_input, output_connection=node_output)


class NodeDescription(BaseModel):
    """A simple model for updating a node's description text."""
    description: str = ''


class NodeExploreData(NodeBase):
    """Settings for a node that provides an interactive data exploration interface."""
    graphic_walker_input: Optional[gs_schemas.GraphicWalkerInput] = None


class NodeGraphSolver(NodeSingleInput):
    """Settings for a node that solves graph-based problems (e.g., connected components)."""
    graph_solver_input: transform_schema.GraphSolverInput


class NodeUnique(NodeSingleInput):
    """Settings for a node that returns the unique rows from the data."""
    unique_input: transform_schema.UniqueInput


class NodeRecordCount(NodeSingleInput):
    """Settings for a node that counts the number of records."""
    pass


class NodePolarsCode(NodeMultiInput):
    """Settings for a node that executes arbitrary user-provided Polars code."""
    polars_code_input: transform_schema.PolarsCodeInput


class UserDefinedNode(NodeMultiInput):
    """Settings for a node that contains the user defined node information"""
    settings: Any
