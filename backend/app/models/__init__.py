"""
Import all models here so Base.metadata is fully populated for
Alembic autogenerate and for Base.metadata.create_all().
"""
from app.models.endpoint import Endpoint  # noqa: F401
from app.models.evidence import Evidence  # noqa: F401
from app.models.finding import Finding, FindingStatus, Severity  # noqa: F401
from app.models.observation import Observation  # noqa: F401
from app.models.project import Project, TargetType  # noqa: F401
from app.models.report import Report  # noqa: F401
from app.models.scan import Scan, ScanStage, ScanStatus, ScanType  # noqa: F401
from app.models.source_file import SourceFile  # noqa: F401
from app.models.user import AuthProvider, User  # noqa: F401
from app.models.web_page import WebPage  # noqa: F401
