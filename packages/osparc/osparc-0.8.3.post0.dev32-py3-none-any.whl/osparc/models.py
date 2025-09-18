# wraps osparc_client.models
#
# TIP:
#  search  "import (\w+)"
#  replace "import $1 as $1"
#
# NOTE: this is an interface. Keep it clean!

from osparc_client.models.body_abort_multipart_upload_v0_files_file_id_abort_post import (
    BodyAbortMultipartUploadV0FilesFileIdAbortPost as BodyAbortMultipartUploadV0FilesFileIdAbortPost,
)
from osparc_client.models.body_complete_multipart_upload_v0_files_file_id_complete_post import (
    BodyCompleteMultipartUploadV0FilesFileIdCompletePost as BodyCompleteMultipartUploadV0FilesFileIdCompletePost,
)
from osparc_client.models.client_file import ClientFile as ClientFile
from osparc_client.models.client_file_upload_data import (
    ClientFileUploadData as ClientFileUploadData,
)
from osparc_client.models.error_get import ErrorGet as ErrorGet
from osparc_client.models.file import File as File
from osparc_client.models.file_upload_completion_body import (
    FileUploadCompletionBody as FileUploadCompletionBody,
)
from osparc_client.models.file_upload_data import FileUploadData as FileUploadData
from osparc_client.models.groups import Groups as Groups
from osparc_client.models.http_validation_error import (
    HTTPValidationError as HTTPValidationError,
)
from osparc_client.models.job import Job as Job
from osparc_client.models.job_logs_map import JobLogsMap as JobLogsMap
from osparc_client.models.values_value import ValuesValue as ValuesValue
from osparc_client.models.job_status import JobStatus as JobStatus
from osparc_client.models.links import Links as Links
from osparc_client.models.log_link import LogLink as LogLink
from osparc_client.models.meta import Meta as Meta
from osparc_client.models.one_page_solver_port import (
    OnePageSolverPort as OnePageSolverPort,
)
from osparc_client.models.one_page_study_port import (
    OnePageStudyPort as OnePageStudyPort,
)
from osparc_client import MetadataValue as MetadataValue
from osparc_client.models.page_file import PageFile as PageFile
from osparc_client.models.page_job import PageJob as PageJob
from osparc_client.models.page_study import PageStudy as PageStudy
from osparc_client.models.pricing_plan_classification import (
    PricingPlanClassification as PricingPlanClassification,
)
from osparc_client.models.profile import Profile as Profile
from osparc_client.models.profile_update import ProfileUpdate as ProfileUpdate
from osparc_client.models.running_state import RunningState as _RunningState
from osparc_client.models.solver import Solver as Solver
from osparc_client.models.solver_port import SolverPort as SolverPort
from osparc_client.models.study import Study as Study
from osparc_client.models.study_port import StudyPort as StudyPort
from osparc_client.models.upload_links import UploadLinks as UploadLinks
from osparc_client.models.uploaded_part import UploadedPart as UploadedPart
from osparc_client.models.user_role_enum import UserRoleEnum as UserRoleEnum
from osparc_client.models.users_group import UsersGroup as UsersGroup
from osparc_client.models.validation_error import ValidationError as ValidationError
from osparc_client.models.wallet_status import WalletStatus as WalletStatus
from osparc_client.models.user_file import UserFile as UserFile
from ._models import JobInputs as JobInputs
from ._models import JobOutputs as JobOutputs
from ._models import JobMetadata as JobMetadata
from ._models import JobMetadataUpdate as JobMetadataUpdate

# renames
TaskStates = _RunningState
