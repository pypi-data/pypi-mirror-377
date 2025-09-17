"""Type definitions and configuration models"""

from enum import Enum
from typing import Any, Optional, Union
from urllib.parse import urlparse

from pydantic import BaseModel, Field, field_validator, computed_field


class AuthMethod(str, Enum):
    """Authentication method enumeration"""
    BASIC = "basic"
    TOKEN = "token"
    PAT = "pat"  # Personal Access Token


class RetryStrategy(str, Enum):
    """Retry strategy enumeration"""
    EXPONENTIAL = "exponential"
    LINEAR = "linear"
    FIXED = "fixed"


class DHIS2Config(BaseModel):
    """
    Configuration model for the DHIS2 client.
    """
    base_url: str = Field(..., description="Base URL of the DHIS2 instance")
    auth: Optional[Union[tuple[str, str], str]] = Field(None, description="Username and password tuple or token string for authentication")
    api_version: Optional[Union[int, str]] = Field(None, description="DHIS2 API version")
    user_agent: str = Field("pydhis2/0.1.0", description="User-Agent for requests")

    # Timeout settings (total) - Increased default for more resilience
    timeout: float = Field(60.0, description="Total request timeout in seconds", gt=0)

    # Concurrency and rate limiting
    rps: float = Field(10.0, description="Requests per second limit", gt=0)
    concurrency: int = Field(10, description="Maximum concurrent connections", gt=0)

    # Compression and caching
    compression: bool = Field(True, description="Whether to enable gzip compression")
    enable_cache: bool = Field(True, description="Whether to enable caching")
    cache_ttl: int = Field(3600, description="Cache TTL in seconds", gt=0)

    # Retry configuration - Increased defaults for more resilience
    max_retries: int = Field(5, description="Maximum retry attempts", ge=0)
    retry_strategy: RetryStrategy = Field(RetryStrategy.EXPONENTIAL, description="Retry strategy")
    retry_base_delay: float = Field(1.5, description="Base retry delay in seconds", gt=0)
    retry_backoff_factor: float = Field(2.0, description="Backoff factor", gt=1.0)
    retry_on_status: list[int] = Field(
        [429, 500, 502, 503, 504], description="HTTP status codes that trigger a retry"
    )

    @field_validator('base_url')
    @classmethod
    def validate_base_url(cls, v: str) -> str:
        """Validate and normalize base URL"""
        if not v:
            raise ValueError("Base URL cannot be empty")
        
        # Basic URL validation
        try:
            parsed = urlparse(v)
            if not parsed.scheme or not parsed.netloc:
                raise ValueError("Invalid URL format")
        except Exception:
            raise ValueError("Invalid URL format")
        
        # Remove trailing slash
        return v.rstrip('/')
    
    @field_validator('auth')
    @classmethod
    def validate_auth(cls, v: Optional[Union[tuple[str, str], str]]) -> Optional[Union[tuple[str, str], str]]:
        """Validate authentication credentials"""
        if v is None:
            return v
        elif isinstance(v, tuple):
            if len(v) != 2:
                raise ValueError("Auth tuple must contain exactly 2 elements (username, password)")
            if not all(isinstance(item, str) and item.strip() for item in v):
                raise ValueError("Auth tuple elements must be non-empty strings")
        elif isinstance(v, str):
            if not v.strip():
                raise ValueError("Auth token cannot be empty")
        else:
            raise ValueError("Auth must be a tuple of (username, password) or a token string")
        return v

    @computed_field
    @property
    def auth_method(self) -> Optional[AuthMethod]:
        """Determine authentication method based on auth type"""
        if self.auth is None:
            return None
        elif isinstance(self.auth, tuple):
            return AuthMethod.BASIC
        else:
            return AuthMethod.TOKEN

    class Config:
        frozen = True
        use_enum_values = True


class PaginationConfig(BaseModel):
    """Pagination configuration"""

    page_size: int = Field(200, description="Default page size", gt=0, le=10000)
    max_pages: Optional[int] = Field(None, description="Maximum page limit")
    use_paging: bool = Field(True, description="Whether to enable paging")


class AnalyticsQuery(BaseModel):
    """Analytics query configuration"""

    dx: Union[str, list[str]] = Field(..., description="Data dimension (indicators/data elements)")
    ou: Union[str, list[str]] = Field(..., description="Organization units")
    pe: Union[str, list[str]] = Field(..., description="Period dimension")
    co: Optional[Union[str, list[str]]] = Field(None, description="Category option combinations")
    ao: Optional[Union[str, list[str]]] = Field(None, description="Attribute option combinations")

    output_id_scheme: str = Field("UID", description="Output ID scheme")
    display_property: str = Field("NAME", description="Display property")
    skip_meta: bool = Field(False, description="Skip metadata")
    skip_data: bool = Field(False, description="Skip data")
    skip_rounding: bool = Field(False, description="Skip rounding")

    def to_params(self) -> dict[str, Any]:
        """Convert to request parameters"""
        params = {}

        # Process dimensions
        for dim in ['dx', 'ou', 'pe', 'co', 'ao']:
            value = getattr(self, dim)
            if value is not None:
                if isinstance(value, list):
                    params[f'dimension={dim}'] = ';'.join(value)
                else:
                    params[f'dimension={dim}'] = value

        # Other parameters
        params.update({
            'outputIdScheme': self.output_id_scheme,
            'displayProperty': self.display_property,
            'skipMeta': str(self.skip_meta).lower(),
            'skipData': str(self.skip_data).lower(),
            'skipRounding': str(self.skip_rounding).lower(),
        })

        return params


class ImportStrategy(str, Enum):
    """Import strategy enumeration"""
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    CREATE_AND_UPDATE = "CREATE_AND_UPDATE"
    DELETE = "DELETE"


class ImportMode(str, Enum):
    """Import mode enumeration"""
    COMMIT = "COMMIT"
    VALIDATE = "VALIDATE"


class ImportConfig(BaseModel):
    """Import configuration"""

    strategy: ImportStrategy = Field(
        ImportStrategy.CREATE_AND_UPDATE, description="Import strategy"
    )
    import_mode: ImportMode = Field(ImportMode.COMMIT, description="Import mode")
    atomic: bool = Field(True, description="Whether to perform atomic import")
    dry_run: bool = Field(False, description="Whether this is a dry run")
    chunk_size: int = Field(5000, description="Chunk size", gt=0)
    max_chunks: Optional[int] = Field(None, description="Maximum number of chunks")

    # Conflict handling
    skip_existing_check: bool = Field(False, description="Skip existing check")
    skip_audit: bool = Field(False, description="Skip audit")

    # Performance options
    async_import: bool = Field(False, description="Whether to perform async import")
    force: bool = Field(False, description="Force import")


class DataFrameFormat(str, Enum):
    """DataFrame output format"""
    PANDAS = "pandas"
    ARROW = "arrow"
    POLARS = "polars"


class ExportFormat(str, Enum):
    """Export format"""
    JSON = "json"
    CSV = "csv"
    PARQUET = "parquet"
    EXCEL = "excel"
    FEATHER = "feather"
