# FetchPoint

A Python library for SharePoint Online integration with federated authentication support.

## Overview

FetchPoint is a clean, enterprise-ready library for SharePoint Online integration with federated authentication support. Provides secure, read-only access to files stored in SharePoint document libraries with comprehensive error handling, metadata extraction, and Excel file focus. Designed for enterprise environments with Azure AD and federated authentication.

## Key Features

- **Federated Authentication**: Azure AD and enterprise identity provider support
- **Read-Only Operations**: Secure file listing and downloading
- **Excel Focus**: Optimized for .xlsx, .xls, .xlsm, .xlsb files
- **Path Validation**: Hierarchical folder navigation with detailed error reporting
- **Context Manager**: Clean resource management
- **Comprehensive Error Handling**: Detailed diagnostics for troubleshooting
- **No Environment Dependencies**: Explicit configuration required (environment variables optional)

## Installation

```bash
uv add fetchpoint
```

## Quick Start

```python
from fetchpoint import SharePointClient, create_sharepoint_config

# Create configuration
config = create_sharepoint_config(
    username="user@company.com",
    password="your_password",
    sharepoint_url="https://company.sharepoint.com/sites/project"
)

# Use context manager (recommended)
with SharePointClient(config) as client:
    # List Excel files
    files = client.list_excel_files(
        library_name="Documents",
        folder_path="General/Reports"
    )

    # Download files
    results = client.download_files(
        library_name="Documents",
        folder_path="General/Reports",
        filenames=files,
        download_dir="./downloads"
    )
```

## Configuration

### Method 1: Explicit Configuration

```python
from fetchpoint import create_sharepoint_config

config = create_sharepoint_config(
    username="user@company.com",           # Required: SharePoint username (email)
    password="your_password",              # Required: User password
    sharepoint_url="https://company.sharepoint.com/sites/yoursite",  # Required: SharePoint site URL
    timeout_seconds=30,                    # Optional: Connection timeout (default: 30)
    max_file_size_mb=100                   # Optional: File size limit (default: 100)
)
```

### Method 2: Dictionary Configuration

```python
from fetchpoint import SharePointClient

client = SharePointClient.from_dict({
    "username": "user@company.com",
    "password": "your_password",
    "sharepoint_url": "https://company.sharepoint.com/sites/yoursite"
})
```

### Method 3: MSAL Authentication (App-Only Access)

For app-only access using Azure AD application credentials:

```python
from fetchpoint import SharePointClient, create_sharepoint_msal_config

# Create MSAL configuration
config = create_sharepoint_msal_config(
    client_id="your-azure-app-client-id",        # Required: Azure AD Application (client) ID
    client_secret="your-azure-app-secret",       # Required: Azure AD Application secret
    tenant_id="your-azure-tenant-id",            # Required: Azure AD Tenant ID
    sharepoint_url="https://company.sharepoint.com/sites/yoursite",  # Required: SharePoint site URL
    timeout_seconds=30,                          # Optional: Connection timeout (default: 30)
    max_file_size_mb=100                         # Optional: File size limit (default: 100)
)

# Use with SharePointClient
with SharePointClient(config) as client:
    files = client.list_excel_files("Documents", "General/Reports")
```

#### MSAL Dictionary Configuration

```python
from fetchpoint import SharePointClient, create_msal_config_from_dict

config = create_msal_config_from_dict({
    "client_id": "your-azure-app-client-id",
    "client_secret": "your-azure-app-secret",
    "tenant_id": "your-azure-tenant-id",
    "sharepoint_url": "https://company.sharepoint.com/sites/yoursite"
})

client = SharePointClient(config)
```

#### Direct MSAL Context Creation

```python
from fetchpoint import create_sharepoint_context, SharePointMSALConfig

# Create configuration model directly
config = SharePointMSALConfig(
    client_id="your-azure-app-client-id",
    client_secret="your-azure-app-secret",
    tenant_id="your-azure-tenant-id",
    sharepoint_url="https://company.sharepoint.com/sites/yoursite"
)

# Create authenticated context
context = create_sharepoint_context(config)
```

### Method 4: Environment Variables (Deprecated)

> **⚠️ Deprecated**: Environment variable configuration is deprecated. Use explicit configuration methods above for better security and clarity.

```bash
# Required
SHAREPOINT_URL=https://company.sharepoint.com/sites/yoursite
SHAREPOINT_USERNAME=user@company.com
SHAREPOINT_PASSWORD=your_password

# Optional
SHAREPOINT_TIMEOUT_SECONDS=30
SHAREPOINT_MAX_FILE_SIZE_MB=100
SHAREPOINT_SESSION_TIMEOUT=3600
SHAREPOINT_LOG_LEVEL=INFO
```

**Note**: This method is maintained for backward compatibility but should be avoided in new projects. Use the explicit configuration methods (Methods 1-3) for better security and configuration management.

## API Reference

### SharePointClient

Main client class for SharePoint operations.

#### Methods

**`connect() -> bool`**

- Establish connection to SharePoint
- Returns: `True` if successful

**`test_connection() -> bool`**

- Validate current connection
- Returns: `True` if connection is valid

**`disconnect() -> None`**

- Clean up connection and resources

**`list_excel_files(library_name: str = "Documents", folder_path: Optional[str] = None) -> list[str]`**

- List Excel file names in specified location
- Args: `library_name` (default: "Documents"), `folder_path` (optional, e.g., "General/Reports")
- Returns: List of Excel filenames

**`list_files(library: str, path: list[str]) -> list[FileInfo]`**

- List files with complete metadata
- Args: `library` name, `path` segments
- Returns: List of FileInfo objects with metadata

**`list_folders(library_name: str = "Documents", folder_path: Optional[str] = None) -> list[str]`**

- List folder names in specified location
- Args: `library_name` (default: "Documents"), `folder_path` (optional)
- Returns: List of folder names

**`download_file(library: str, path: list[str], local_path: str) -> None`**

- Download single file
- Args: `library` name, `path` segments including filename, `local_path`

**`download_files(library_name: str, folder_path: str, filenames: list[str], download_dir: str) -> dict`**

- Download multiple files with per-file error handling
- Returns: Dictionary with success/failure status for each file

**`get_file_details(library_name: str, folder_path: Optional[str], filename: str) -> Optional[FileInfo]`**

- Get comprehensive file metadata
- Args: `library_name`, `folder_path` (optional), `filename`
- Returns: FileInfo object with complete metadata, or None if file not found

**`validate_paths(library_name: str = "Documents") -> dict`**

- Validate configured SharePoint paths
- Args: `library_name` (default: "Documents")
- Returns: Validation results with error details and available folders

**`discover_structure(library_name: str = "Documents", max_depth: int = 3) -> dict`**

- Explore SharePoint library structure
- Args: `library_name` (default: "Documents"), `max_depth` (default: 3)
- Returns: Hierarchical representation of folders and files

**`validate_decoupled_paths() -> dict`**

- Validate paths that span different SharePoint libraries
- Each path uses its own library name (first segment)
- Returns: Validation results with library-specific error details

**`get_file_content(library: str, path: list[str]) -> bytes`**

- Get file content as bytes without downloading to disk
- Args: `library` name, `path` segments including filename
- Returns: File content as bytes for in-memory processing

**`read_excel_content(library: str, path: list[str], sheet_name: Optional[str] = None, column_mapping: Optional[dict[str, str]] = None, skip_empty_rows: bool = True) -> list[dict[str, Any]]`**

- Read Excel file directly from SharePoint as structured data
- Args: `library`, `path`, optional `sheet_name`, `column_mapping`, `skip_empty_rows`
- Returns: List of dictionaries representing Excel rows

**`get_excel_sheet_names(library: str, path: list[str]) -> list[str]`**

- Get list of sheet names from an Excel file in SharePoint
- Args: `library` name, `path` segments including filename
- Returns: List of sheet names in the workbook

### Configuration Functions

**`create_sharepoint_config(...) -> SharePointAuthConfig`**

- Create configuration with explicit parameters

**`create_config_from_dict(config_dict: dict) -> SharePointAuthConfig`**

- Create configuration from dictionary

**`create_authenticated_context(config: SharePointAuthConfig) -> ClientContext`**

- Create authenticated SharePoint context

### Models

**`SharePointAuthConfig`**

- Configuration model with validation
- Fields: `username`, `password`, `sharepoint_url`, `timeout_seconds`, `max_file_size_mb`

**`FileInfo`**

- File metadata model
- Fields: `name`, `size_bytes`, `size_mb`, `created_date`, `modified_date`, `file_type`, `library`, `relative_path`, `created_by`, `modified_by`

**`FileType`**

- Enum for supported Excel extensions
- Values: `XLSX`, `XLS`, `XLSM`, `XLSB`

### Exceptions

All exceptions inherit from `SharePointError`:

- **`AuthenticationError`**: Authentication failures
- **`FederatedAuthError`**: Federated authentication issues (Azure AD specific)
- **`ConnectionError`**: Connection problems
- **`FileNotFoundError`**: File not found in SharePoint
- **`FileDownloadError`**: Download failures
- **`FileSizeLimitError`**: File exceeds size limit
- **`ConfigurationError`**: Invalid configuration
- **`PermissionError`**: Access denied
- **`LibraryNotFoundError`**: Document library not found
- **`InvalidFileTypeError`**: Unsupported file type

## Excel Operations

FetchPoint provides powerful Excel processing capabilities for direct data extraction from SharePoint:

### Reading Excel Data

```python
with SharePointClient(config) as client:
    # Read Excel file as structured data
    data = client.read_excel_content(
        library="Documents",
        path=["General", "Reports", "monthly_data.xlsx"],
        sheet_name="Summary",  # Optional: specify sheet
        column_mapping={"Employee Name": "employee_name", "Salary": "salary"},  # Optional: rename columns
        skip_empty_rows=True  # Optional: skip empty rows
    )
    
    # data is now a list of dictionaries
    for row in data:
        print(f"Employee: {row['employee_name']}, Salary: {row['salary']}")
```

### Working with Excel Sheets

```python
with SharePointClient(config) as client:
    # Get all sheet names in a workbook
    sheets = client.get_excel_sheet_names(
        library="Documents",
        path=["General", "Reports", "workbook.xlsx"]
    )
    print(f"Available sheets: {sheets}")
    
    # Read specific sheet
    data = client.read_excel_content(
        library="Documents",
        path=["General", "Reports", "workbook.xlsx"],
        sheet_name=sheets[0]  # Use first sheet
    )
```

### In-Memory Processing

```python
with SharePointClient(config) as client:
    # Get file content without downloading
    content_bytes = client.get_file_content(
        library="Documents",
        path=["General", "Reports", "data.xlsx"]
    )
    
    # Process bytes with other libraries or save locally
    with open("local_file.xlsx", "wb") as f:
        f.write(content_bytes)
```

## Security

- Passwords stored as `SecretStr` (Pydantic)
- Usernames masked in logs (first 3 characters only)
- Read-only operations only
- Configurable file size limits (default: 100MB)
- No environment dependencies by default

## Error Handling

FetchPoint provides detailed error messages with context:

```python
try:
    with SharePointClient(config) as client:
        files = client.list_excel_files("Documents", "NonExistent/Path")
except LibraryNotFoundError as e:
    print(f"Library error: {e}")
    print(f"Available libraries: {e.context.get('available_libraries', [])}")
```

## Development

For project developers working on the fetchpoint library:

### Setup

```bash
# Install dependencies
uv sync --all-groups

# Build wheel package
uv build --wheel
```

### Development Commands

**Code Quality (run after every change):**

```bash
# Format code
uv run ruff format src

# Lint with auto-fix
uv run ruff check --fix src

# Type checking
uv run pyright src

# Run tests
uv run pytest src -vv

# Run tests with coverage
uv run pytest src --cov=src --cov-report=term-missing
```

**Complete validation workflow:**

```bash
uv run ruff format src && uv run ruff check --fix src && uv run pyright src && uv run pytest src -vv
```

### Testing

- Tests located in `__tests__/` directories co-located with source code
- Use pytest with extensions (pytest-asyncio, pytest-mock, pytest-cov)
- Minimum 90% coverage for critical components

### Version Management

FetchPoint uses a single source of truth for version management:

- **Version Source**: `src/fetchpoint/__init__.py` contains `__version__ = "x.y.z"`
- **Dynamic Configuration**: `pyproject.toml` reads version automatically from `__init__.py`
- **Publishing Workflow**:
  1. Update version in `src/fetchpoint/__init__.py`
  2. Build: `uv build --wheel`
  3. Publish: `uv publish --token $PYPI_TOKEN`

Update `uv.lock` via:

```sh
uv lock --refresh
```

**Version Access:**

```python
import fetchpoint
print(fetchpoint.__version__)  # e.g., "0.2.0"
```

### Publishing Quick Reference

```bash
just validate
rm -rf dist/
uv build --wheel && uv build --sdist
uv publish --token $PYPI_TOKEN
```

## Roadmap

- Enhanced Excel processing capabilities
- Batch operations for large datasets
- Advanced filtering and search features

## License

Open source library for SharePoint Online integration.
