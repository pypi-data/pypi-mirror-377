from typing import Any

from pydantic import BaseModel, EmailStr

from ncmi_idc_extract_interfaces.models import ParameterCodes, SurveyNames
from ncmi_idc_extract_interfaces.query_models import CTDExportQuery

###########################################
# REQUESTS
###########################################


class CTDExportRequest(BaseModel):

    """Request model for exporting CTD data.

    Parameters
    ----------
    email : EmailStr
        Email address to send the export to (the requesting user too)

    query : CTDExportQuery
        Query parameters for filtering the CTD data

    """

    email: EmailStr
    query: CTDExportQuery

    class Config:
        extra = "forbid"


###########################################
# RESPONSES
###########################################


class BaseResponse(BaseModel):

    """Base response model that defines common fields for API responses.

    Parameters
    ----------
    detail : str
        Description or detail about the response

    """

    detail: str


class HealthCheckResponse(BaseResponse):

    """Response model for health check endpoints.

    Inherits all fields from BaseResponse.
    """



class TaskStatusResponseBaseModel:

    """Response model for checking the status of an asynchronous task.

    Parameters
    ----------
    task_id : str
        Unique identifier for the task
    status : str
        Current status of the task (e.g., "pending", "processing", "completed", "failed")
    result : Optional[Any]
        Result of the task, if completed

    """

    task_id: str
    status: str
    result: Any = None


class CreateTaskResponse(BaseResponse):

    """Response model for creating a new asynchronous task.

    Parameters
    ----------
    detail : str
        Description or detail about the task creation
    task_id : str
        Unique identifier for the newly created task

    """

    task_id: str



class DownloadResponse(BaseModel):

    """Response model for file download operations.

    Parameters
    ----------
    file_path : str
        Path to the file on the server
    filename : str
        Name of the file to be downloaded
    headers : dict
        HTTP headers for the download response

    """

    file_path: str
    filename: str
    headers: dict


class PresignedURLResponse(BaseResponse):

    """Response model for providing a pre-signed URL.

    Parameters
    ----------
    signed_url : str
        The pre-signed URL for accessing a resource

    Notes
    -----
    Inherits detail from BaseResponse.

    """

    signed_url: str


class CreateExportTaskResponse(CreateTaskResponse, PresignedURLResponse):
    pass


class ParameterCodesResponse(BaseResponse, ParameterCodes):

    """Response model for providing valid parameter codes.

    Parameters
    ----------
    parameter_codes : list[str]
        List of valid parameter codes

    Notes
    -----
    Inherits detail from BaseResponse and adds parameter_codes.

    """


class SurveyNamesResponse(BaseResponse, SurveyNames):

    """Response model for providing valid survey names.

    Parameters
    ----------
    survey_names : list[str]
        List of valid survey names

    Notes
    -----
    Inherits detail from BaseResponse and adds survey_names.

    """


class ParameterCodesAndSurveyNamesResponse(BaseResponse, SurveyNames, ParameterCodes):
    #! class methods are also inherited and can overwrite each other if named the same.
    """Response model for providing both valid parameter codes and survey names.

    Parameters
    ----------
    parameter_codes : list[str]
        List of valid parameter codes
    survey_names : list[str]
        List of valid survey names

    Notes
    -----
    Inherits.
    """
