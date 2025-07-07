"""MCP server module client tools and utils"""

import hmac
import hashlib
import datetime
import httpx
import importlib.metadata

from typing import Any, Dict, List, Optional, Annotated
from pydantic import BaseModel, Field, ValidationError

def hmac_sha256(key, data):
    """ hmac with sha256 """
    return hmac.new(key.encode(), data.encode(), hashlib.sha256).hexdigest()

def genKey(ak: str, sk: str):
    """ generate api key by ak and sk"""
    appId = ak
    appKey = sk
    expired_time = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)).isoformat()
    authorization = f"{appId}/{hmac_sha256(appKey, appId + expired_time)}/{expired_time}"
    return authorization

# Common base response model
class BaseDHResponse(BaseModel):
    """ 接口响应基类 """
    error: Optional[str] = None

# Voice information models
class VoiceInfo(BaseModel):
    """ 音色数据 """
    perId: str
    name: str
    gender: Annotated[Optional[str], Field(description="性别", default=None)]
    
class FigureInfo(BaseModel):
    """
    人像数据

    Attributes:
        figureId: 人像ID
        name: 人像名称
        gender: 性别
        status: 状态
    """
    figureId: str
    name: str
    gender: str
    status: str

class VideoParams(BaseModel):
    """视频请求参数"""
    width: int = 720
    height: int = 1280
    transparent: bool = False

class DHParams(BaseModel):
    """ 数字人参数

    Attributes:
        cameraId: 数字人机位
    """
    cameraId: int = 0

class SubtitleParams(BaseModel):
    """ 字幕参数 """
    subtitlePolicy: str = "SRT"
    enabled: bool = False

class TtsParams(BaseModel):
    """ TTS 参数 """
    person: str = "20000000"
    speed: str = "5"
    volume: str = "5"
    pitch: str = "5"

class Generate123VideoRequest(BaseModel):
    """ 生成123数字人请求参数 """
    templateVideoId: str = ""
    text: str = "百度数字人MCP SERVER"
    ttsParams: TtsParams = Field(default_factory=lambda: TtsParams())
    videoParams: VideoParams = Field(default_factory=lambda: VideoParams())

class VideoGenerateRequest(BaseModel):
    """ 视频生成请求 """
    figureId: str = ""
    driveType: str = "TEXT"
    text: str = ""
    ttsParams: TtsParams = Field(default_factory=lambda: TtsParams())
    videoParams: VideoParams = Field(default_factory=lambda: VideoParams())

class Text2AudioGenerateRequest(BaseModel):
    """ 文本转语音请求 """
    text: str = ""
    person: str = ""
    speed: int = 5
    volume: int = 5
    pitch: int = 5
    outputFormat: str = "mp3"
    sampleRate: int = 16000

class Message(BaseModel):
    """ 基础响应消息 """
    global_field: Optional[str] = Field(..., alias="global")

class VideoStatusData(BaseModel):
    """ 视频状态 """
    taskId: Optional[str] = None 
    status: Optional[str] = None 
    failedCode: Optional[int] = None
    failedMessage: Optional[str] = None 
    videoUrl: Optional[str] = None
    duration: Optional[int] = None
    createTime: Optional[str] = None 
    updateTime: Optional[str] = None 
    startTrainTime: Optional[str] = None

class VideoGenerateResponse(BaseDHResponse):
    """ 视频生成响应 """
    code: int
    message: Message
    result: Optional[VideoStatusData] = None
    requestId: str
    success: bool

class VoicesResponse(BaseDHResponse):
    """ 音色响应 """
    code: int
    message: Message
    result: Optional[List[VoiceInfo]] = None
    requestId: str
    success: bool

class VideoStatusResponse(BaseModel):
    """ 音色状态响应 """
    code: int
    message: Message
    result:  VideoStatusData
    requestId: str
    success: bool

class Text2AudioGenerateResponse(BaseDHResponse):
    """ 文本转语音响应 """
    code: int
    message: Message
    result: Dict[str, Any] = {}
    requestId: str
    success: bool

class TextTimeStampInfo(BaseModel):
    """ 文本及对应时间戳 """
    content: Optional[str] = None
    startTimestamp: Optional[int] = None
    endTimestamp: Optional[int] = None

class Text2AudioStatusData(BaseModel):
    """ 文本转语音状态数据 """
    taskId: Optional[str] = None
    status: Optional[str] = None
    failedCode: Optional[int] = None
    failedMessage: Optional[str] = None
    audioUrl: Optional[str] = None
    duration: Optional[int] = None
    textTimestamp: Optional[List[TextTimeStampInfo]] = None
    createTime: Optional[str] = None
    updateTime: Optional[str] = None

class Text2AudioStatusResponse(BaseModel):
    """ 文本转语音状态结果 """
    code: int
    message: Message
    result:  Text2AudioStatusData
    requestId: str
    success: bool

class BgmParams(BaseModel):
    """ 背景音参数 """
    bgmUrl: str

class BGMaterial(BaseModel):
    """ 背景材质 """
    fileUrl: str
    mediaType: str

class FissionParam(BaseModel):
    """ 裂变参数 """
    figureIds: list[str]
    ttsPersons: list[str]

class FigureResult(BaseModel):
    """ 人像数据 """
    pageNo: int
    pageSize: int
    totalCount: int
    result: List[FigureInfo]

class FigureResponse(BaseDHResponse):
    """ 人像结果响应 """
    code: int
    message: Message
    result: FigureResult
    requestId: str
    success: bool

class UploadFileResponse(BaseDHResponse):
    """ 上传文件响应 """
    code: int
    message: Message
    result: Optional[Dict[str, Any]] = {}
    requestId: str
    success: bool

class Lite2dGenerateRequest(BaseModel):
    """ 通用口型驱动请求 """
    name: str
    customizeType: str
    gender: str
    keepBackground: bool = True
    templateVideoId: str
    lipVideoId: Optional[str] = None
    maskVideoId: Optional[str] = None
    callbackUrl: Optional[str] = None

class CommonDHResponse(BaseDHResponse):
    """ 通用数字人响应 """
    code: int
    message: Message
    result: Optional[Dict[str, Any]] = None
    requestId: str
    success: bool

class CommonDHListResponse(BaseDHResponse):
    """ 通用数字人列表响应 """
    code: int
    message: Message
    result: List[Dict[str, Any]] = []
    requestId: str
    success: bool

class Lite2dStatus(BaseModel):
    """ 2D小样本数字人状态 """
    figureId: Optional[str] = None
    name: Optional[str] = None
    customizeType: Optional[str] = None
    systemFigure: Optional[bool] = None
    keepBackground: Optional[bool] = None
    gender: Optional[str] = None
    resolutionWidth: Optional[int] = None
    resolutionHeight: Optional[int] = None
    templateVideoUrl: Optional[str] = None
    maskVideoUrl: Optional[str] = None
    status: Optional[str] = None
    failedMessage: Optional[str] = None

class Lite2DResult(BaseModel):
    """ 2D小样本数字人结果 """
    pageNo: int
    pageSize: int
    totalCount: int
    result: List[Lite2dStatus]

class Lite2dStatusResponse(BaseDHResponse):
    """ 2D小样本数字人生成状态 """
    code: int
    message: Message
    result: Optional[Lite2DResult] = None
    requestId: str
    success: bool

class VoiceCloneRequest(BaseModel):
    """ 音色克隆请求 """
    name: Optional[str]
    describe: Optional[str]
    gender: Optional[str]
    uploadAudioId: Optional[str]
    exampleText: Optional[str]

########################
# MCP Response Models #
########################

class MCPVoicesResponse(BaseDHResponse):
    """ MCP 音色列表响应 """
    voices: Optional[List[VoiceInfo]] = None

class MCPFiguresResponse(BaseDHResponse):
    """ MCP 人像列表响应 """
    figures: Optional[List[FigureInfo]] = None

class MCPUploadResponse(BaseDHResponse):
    """ MCP 上传文件响应 """
    fileId: Optional[str] = None
    fileName: Optional[str] = None
    message: Optional[str] = None

class MCPVideoGenerateResponse(BaseDHResponse):
    """ MCP 视频生成响应 """
    videoId: Optional[str] = None
    taskId: Optional[str] = None
    videoUrl: Optional[str] = None
    status: Optional[str] = None

class MCPVideoStatusResponse(BaseDHResponse):
    """ MCP 视频状态响应 """
    taskId: Optional[str] = None
    status: Optional[str] = None
    duration: Optional[float] = None
    videoUrl: Optional[str] = None
    requestId: Optional[str] = None
    failedCode: Optional[int] = None
    createTime: Optional[str] = None
    failedMessage: Optional[Dict[str, Any]] = None

class MCPLite2DStatusResponse(BaseDHResponse):
    """ MCP 2D小样本数字人状态响应 """
    figureId: Optional[str] = None
    name: Optional[str] = None
    customizeType: Optional[str] = None
    systemFigure: Optional[bool] = None
    keepBackground: Optional[bool] = None
    gender: Optional[str] = None
    resolutionWidth: Optional[int] = None
    resolutionHeight: Optional[int] = None
    templateVideoUrl: Optional[str] = None
    maskVideoUrl: Optional[str] = None
    status: Optional[str] = None
    failedMessage: Optional[str] = None


class MCPText2AudioGenerateResponse(BaseDHResponse):
    """ MCP 文本转语音结果响应 """
    taskId: Optional[str] = None

class MCPText2AudioStatusResponse(BaseDHResponse):
    """ MCP 文本转语音状态响应 """
    taskId: Optional[str] = None
    status: Optional[str] = None
    failedCode: Optional[int] = None
    failedMessage: Optional[str] = None
    audioUrl: Optional[str] = None
    duration: Optional[int] = None
    textTimestamp: List[TextTimeStampInfo]
    createTime: Optional[str] = None
    updateTime: Optional[str] = None

class MCPLite2DGenerateResponse(BaseDHResponse):
    """ MCP 2D小样本数字人响应 """
    figureId: Optional[str] = None

class MCPVoiceCloneResponse(BaseDHResponse):
    """ MCP 音色克隆响应 """
    perId: Optional[str] = None

class MCPVoiceCloneStatusResponse(BaseDHResponse):
    """ MCP 音色克隆状态响应 """
    perId: Optional[str] = None
    name: Optional[str]
    status: Optional[str]
    description: Optional[str]
    exampleText: Optional[str]
    exampleAudioUrl: Optional[str]
    reason: Optional[str]
    version: Optional[str]
    gender: Optional[str]

class DHApiClient:
    """Client for interacting with the DH API."""

    def __init__(self, api_key: str):
        """Initialize the API client with the API key."""
        self.api_key = api_key

        try:
            self.version = importlib.metadata.version("mcp_server_baidu_digitalhuman")
        except importlib.metadata.PackageNotFoundError:
            self.version = "unknown"

        self.user_agent = f"dh-mcp/{self.version}"
        self.base_url = "https://open.xiling.baidu.com"
        self._client = httpx.AsyncClient()


    @classmethod
    def _stdio(cls, ak: str, sk: str):
        """
            通过标准输入获取API Key，并返回一个实例。
        如果标准输入中没有提供API Key，则抛出ValueError异常。

        Args:
            ak (str, optional): API Key. Defaults to None.
            sk (str, optional): Secret Key. Defaults to None.

        Raises:
            ValueError: 如果标准输入中没有提供API Key。

        Returns:
            InstanceType: 返回一个类的实例。
        """
        api_key = genKey(ak, sk)
        return cls(api_key)

    async def close(self):
        """Close the underlying HTTP client."""
        await self._client.aclose()

    def _get_headers(self) -> Dict[str, str]:
        """Return the headers needed for API requests."""
        return {
            "Accept": "application/json",
            "Authorization": self.api_key,
            "User-Agent": self.user_agent,
        }

    async def _make_request(
        self, endpoint: str, method: str = "GET", data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make a request to the specified API endpoint.

        Args:
            endpoint: The API endpoint to call (without the base URL)
            method: HTTP method to use (GET or POST)
            data: JSON payload for POST requests

        Returns:
            The JSON response from the API

        Raises:
            httpx.RequestError: If there's a network-related error
            httpx.HTTPStatusError: If the API returns an error status code
            Exception: For any other unexpected errors
        """
        url = f"{self.base_url}/{endpoint}"
        headers = self._get_headers()
        if method.upper() == "GET":
            response = await self._client.get(url, headers=headers)
        elif method.upper() == "POST":
            headers["Content-Type"] = "application/json;charset=utf-8"
            response = await self._client.post(url, headers=headers, json=data)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

        response.raise_for_status()  # Raises if status code is 4xx or 5xx
        return response.json()

    async def _upload_file(
        self, endpoint: str, data: Optional[Dict[str, Any]] = None, file: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Make a request to the specified API endpoint.

        Args:
            endpoint: The API endpoint to call (without the base URL)
            method: HTTP method to use (GET or POST)
            data: JSON payload for POST requests

        Returns:
            The JSON response from the API

        Raises:
            httpx.RequestError: If there's a network-related error
            httpx.HTTPStatusError: If the API returns an error status code
            Exception: For any other unexpected errors
        """
        url = f"{self.base_url}/{endpoint}"
        headers = self._get_headers()
        response = await self._client.post(url, headers=headers, data=data, files=file)

        response.raise_for_status()  # Raises if status code is 4xx or 5xx
        return response.json()

    async def _handle_api_request(
        self,
        api_call,
        response_model_class,
        mcp_response_class,
        error_msg: str,
        **kwargs,
    ):
        """Generic handler for API requests to reduce code duplication.

        Args:
            api_call: Async function to call the API
            response_model_class: Pydantic model class for validating the API response
            mcp_response_class: Pydantic model class for the MCP response
            error_msg: Error message to return if the validation fails
            **kwargs: Additional arguments for the response transformation

        Returns:
            An MCP response object
        """
        try:
            result = await api_call()
            validated_response = response_model_class.model_validate(result)

            # Return the appropriate response based on the validation result
            if hasattr(validated_response, "result") and validated_response.result:
                return self._transform_to_mcp_response(
                    validated_response.result, mcp_response_class, **kwargs
                )
            elif validated_response.error:
                return mcp_response_class(error=validated_response.error)
            else:
                errmsg = validated_response.message.global_field
                return mcp_response_class(error=errmsg if errmsg is not None else error_msg)

        except httpx.RequestError as exc:
            return mcp_response_class(error=f"HTTP Request failed: {exc}")
        except httpx.HTTPStatusError as exc:
            return mcp_response_class(
                error=f"HTTP Error: {exc.response.status_code} - {exc.response.text}"
            )
        except Exception as e:
            return mcp_response_class(error=f"An unexpected error occurred: {e}")

    def _transform_to_mcp_response(self, data, mcp_response_class, **kwargs):
        """Transform API response data to MCP response format.

        Args:
            data: The API response data
            mcp_response_class: The MCP response class to instantiate
            **kwargs: Additional parameters for the response

        Returns:
            An instance of the MCP response class
        """
        if "transform_func" in kwargs:
            transform_func = kwargs.pop("transform_func")
            return transform_func(data, mcp_response_class)

        # Apply lambda functions to data if provided or use direct values
        processed_kwargs = {}
        for key, value in kwargs.items():
            if callable(value):
                processed_kwargs[key] = value(data)
            else:
                processed_kwargs[key] = value

        return mcp_response_class(**processed_kwargs)

    async def get_voices(self, isSys: Optional[bool] = None) -> MCPVoicesResponse:
        """Get the list of available voices from the API."""
        async def api_call():
            param = ""
            if isSys == True:
                param = "true"
            elif isSys == False:
                param = "false"
            return await self._make_request(f"api/digitalhuman/open/v1/tts/persons?isSystem={param}")

        def transform_data(data, mcp_class):
            return mcp_class(voices=data if len(data) > 0 else None)

        return await self._handle_api_request(
            api_call=api_call,
            response_model_class=VoicesResponse,
            mcp_response_class=MCPVoicesResponse,
            error_msg="No voices found.",
            transform_func=transform_data,
        )

    async def get_figures(self, isSys: Annotated[Optional[bool], Field(default=None)],
                          trainSuccess: bool = True) -> MCPFiguresResponse:
        """Get the list of available voices from the API."""

        async def api_call():
            param = "" if isSys is None else "true" if isSys else "false"
            param2 = "true" if trainSuccess else "false"
            return await self._make_request(f"api/digitalhuman/open/v1/figure/lite2d/query?\
pageNo=1&pageSize=100&systemFigure={param}&trainSuccess={param2}")

        def transform_data(data, mcp_class):
            return mcp_class(figures=data.result if len(data.result) > 0 else None)

        return await self._handle_api_request(
            api_call=api_call,
            response_model_class=FigureResponse,
            mcp_response_class=MCPFiguresResponse,
            error_msg="No voices found.",
            transform_func=transform_data,
        )

    async def upload_file(self, localFilePath: str, providerType: str = "OPEN_CUSTOMIZATION_2D_GENERAL",
                          fileName: str = "") -> MCPUploadResponse:
        """ upload a file to DH server"""
        async def api_call():
            with open(localFilePath, 'rb') as f:
                data = {"providerType": providerType, "sourceFileName": fileName}
                file = {"file": f}
                return await self._upload_file(
                    "api/digitalhuman/open/v1/file/upload", file=file, data=data
                )
        return await self._handle_api_request(
            api_call=api_call,
            response_model_class=UploadFileResponse,
            mcp_response_class=MCPUploadResponse,
            error_msg="upload failed",
            fileId=lambda d: d.get("fileId"),
            fileName=lambda d: d.get("fileName"),
        )

    async def generate_123avatar_video(
        self, video_request: Generate123VideoRequest
    ) -> MCPVideoGenerateResponse:
        """ Generate an avatar video """
        
        async def api_call():
            return await self._make_request(
                "api/digitalhuman/open/v1/video/submit/fast", method="POST", data=video_request.model_dump()
            )

        ret = await self._handle_api_request(
            api_call=api_call,
            response_model_class=VideoGenerateResponse,
            mcp_response_class=MCPVideoGenerateResponse,
            error_msg="No video generation data returned.",
            taskId=lambda d: d.taskId,
        )
        return ret

    async def generate_avatar_video(
            self, video_request: VideoGenerateRequest
    ) -> MCPVideoGenerateResponse:
        """ Generate an avatar video """

        async def api_call():
            return await self._make_request(
                "api/digitalhuman/open/v1/video/submit", method="POST", data=video_request.model_dump()
            )

        ret = await self._handle_api_request(
            api_call=api_call,
            response_model_class=VideoGenerateResponse,
            mcp_response_class=MCPVideoGenerateResponse,
            error_msg="No video generation data returned.",
            taskId=lambda d: d.taskId,
            videoUrl=lambda d: d.videoUrl,
            status=lambda d: d.status,
        )
        return ret

    async def get_video_status(self, taskId: str, isAdvanced: bool = False) -> MCPVideoStatusResponse:
        """Get the status of a generated video from the API."""

        async def api_call():
            endpoint = f"api/digitalhuman/open/v1/video/advanced/task?taskId={taskId}" \
                if isAdvanced else f"api/digitalhuman/open/v1/video/task?taskId={taskId}"
            return await self._make_request(endpoint)

        try:
            result = await api_call()

            validated_response = VideoStatusResponse.model_validate(result)

            data = validated_response.result

            error_details = None
            if validated_response.code != 0 :
                error_details = {
                    "code": validated_response.code,
                    "message": validated_response.message.global_field,
                }

            return MCPVideoStatusResponse(
                taskId=data.taskId,
                status=data.status,
                duration=data.duration,
                videoUrl=data.videoUrl,
                createTime=data.createTime,
                failedMessage=error_details,
            )
        except httpx.RequestError as exc:
            return MCPVideoStatusResponse(
                error=f"HTTP Request failed: {exc}"
            )
        except httpx.HTTPStatusError as exc:
            return MCPVideoStatusResponse(
                error=f"HTTP Error: {exc.response.status_code} - {exc.response.text}"
            )
        except ValidationError as ve:
            return MCPVideoStatusResponse(
                error=f"ValidationError: {ve}"
            )
        except Exception as e:
            return MCPVideoStatusResponse(
                error=f"An unexpected error occurred: {e}"
            )

    async def generate_text2audio(
            self, text2audio_request: Text2AudioGenerateRequest
    ) -> MCPVideoGenerateResponse:
        """Generate new audio by inputText using the DH API."""

        async def api_call():
            return await self._make_request(
                "api/digitalhuman/open/v1/tts/text2audio/submit", method="POST",
                data=text2audio_request.model_dump()
            )

        ret = await self._handle_api_request(
            api_call=api_call,
            response_model_class=Text2AudioGenerateResponse,
            mcp_response_class=MCPText2AudioGenerateResponse,
            error_msg="No text2audio generation data returned.",
            taskId=lambda d: d.get("taskId"),
        )
        return ret

    async def get_text2audio_status(self, taskId: str) -> MCPText2AudioStatusResponse:
        """Get the status of a generated video from the API."""

        async def api_call():
            endpoint = f"api/digitalhuman/open/v1/tts/text2audio/task?taskId={taskId}"
            return await self._make_request(endpoint)

        try:
            result = await api_call()

            validated_response = Text2AudioStatusResponse.model_validate(result)
            data = validated_response.result

            return MCPText2AudioStatusResponse(
                taskId=data.taskId,
                status=data.status,
                audioUrl=data.audioUrl,
                duration=data.duration,
                textTimestamp=data.textTimestamp,
                createTime=data.createTime,
                updateTime=data.updateTime,
                failedCode=validated_response.code,
                failedMessage="" if validated_response.message is None else validated_response.message.global_field,
            )
        except httpx.RequestError as exc:
            return MCPText2AudioStatusResponse(error=f"HTTP Request failed: {exc}")
        except httpx.HTTPStatusError as exc:
            return MCPText2AudioStatusResponse(
                error=f"HTTP Error: {exc.response.status_code} - {exc.response.text}"
            )
        except ValidationError as ve:
            return MCPText2AudioStatusResponse(error=f"ValidationError")
        except Exception as e:
            return MCPText2AudioStatusResponse(error=f"An unexpected error occurred: {e}")

    async def generate_lite2d_video(self, video_request: Lite2dGenerateRequest) -> MCPLite2DGenerateResponse:
        """Generate a lite 2d avatar video from template video file via the DH API."""
        async def api_call():
            return await self._make_request(
                "api/digitalhuman/open/v1/figure/lite2d/train", method="POST", data=video_request.model_dump()
            )

        ret = await self._handle_api_request(
            api_call=api_call,
            response_model_class=CommonDHResponse,
            mcp_response_class=MCPLite2DGenerateResponse,
            error_msg="No video generation data returned.",
            figureId=lambda d: d.get("figureId"),
        )
        return ret

    async def get_lite2d_general_status(self, figureId: str, systemFigure: bool = None, trainSuccess: bool = None) \
            -> MCPLite2DStatusResponse:
        """ 2D 小样本数字人生成状态 """
        async def api_call():
            # fix in the future: systemFigure, trainSuccess
            endpoint = f"api/digitalhuman/open/v1/figure/lite2d/query?figureId={figureId}"
            return await self._make_request(endpoint)

        ret = await self._handle_api_request(
            api_call=api_call,
            response_model_class=Lite2dStatusResponse,
            mcp_response_class=MCPLite2DStatusResponse,
            error_msg="No video generation data returned.",
            figureId=lambda d: d.result[0].figureId,
            name=lambda d: d.result[0].name,
            status=lambda d: d.result[0].status,
            templateVideoUrl=lambda d: d.result[0].templateVideoUrl,
            failedMessage=lambda d: d.result[0].failedMessage,
            systemFigure=lambda d: d.result[0].systemFigure,
            gender=lambda d: d.result[0].gender,
        )
        return ret

    async def voice_clone(self, req: VoiceCloneRequest, isLite: bool = True) -> MCPVoiceCloneResponse:
        """ clone voice """
        async def api_call():
            endpoint = "api/digitalhuman/open/v1/tts/clone/lite" if isLite else "api/digitalhuman/open/v1/tts/clone/v2"
            return await self._make_request(
                endpoint=endpoint, method="POST", data=req.model_dump()
            )

        ret = await self._handle_api_request(
            api_call=api_call,
            response_model_class=CommonDHResponse,
            mcp_response_class=MCPVoiceCloneResponse,
            error_msg="voice clone failed.",
            perId=lambda d: d.get("perId"),
        )
        return ret

    async def voice_clone_status(self, perId: str) -> MCPVoiceCloneStatusResponse:
        """Get the status of a generated voice clone task from the API."""

        async def api_call():
            endpoint = f"api/digitalhuman/open/v1/tts/clone?isSuccess=false&perId={perId}"
            return await self._make_request(endpoint)

        ret = await self._handle_api_request(
            api_call=api_call,
            response_model_class=CommonDHListResponse,
            mcp_response_class=MCPVoiceCloneStatusResponse,
            error_msg="voice clone failed.",
            perId=lambda d: d[0].get("perId"),
            description=lambda d: d[0].get("description"),
            name=lambda d: d[0].get("name"),
            status=lambda d: d[0].get("status"),
            exampleText=lambda d: d[0].get("exampleText"),
            exampleAudioUrl=lambda d: d[0].get("exampleAudioUrl"),
            reason=lambda d: d[0].get("reason"),
            version=lambda d: d[0].get("version"),
            gender=lambda d: d[0].get("gender"),

        )
        return ret