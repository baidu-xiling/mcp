"""MCP server module for the Xiling API."""

import os
import sys

from typing import Annotated, Literal, Optional
from pydantic import Field
from mcp.server.fastmcp import FastMCP

from mcp_server_baidu_digitalhuman.dhapi import (
    TtsParams,
    VideoParams,
    DHApiClient,
    MCPVideoGenerateResponse,
    MCPVideoStatusResponse,
    MCPVoicesResponse,
    Generate123VideoRequest,
    MCPText2AudioStatusResponse,
    Text2AudioGenerateRequest,
    VideoGenerateRequest,
    DHParams,
    SubtitleParams,
    MCPFiguresResponse,
    MCPUploadResponse,
    MCPLite2DGenerateResponse,
    Lite2dGenerateRequest,
    MCPLite2DStatusResponse,
    MCPVoiceCloneResponse,
    VoiceCloneRequest,
    MCPVoiceCloneStatusResponse,
)

# mcp服务器实例
mcp = FastMCP(name="DH MCP", log_level="ERROR")

# 数字人客户端
dhClient = None

async def getDhClient() -> DHApiClient:
    """Get the API client, creating it if necessary."""
    global dhClient

    if dhClient is not None:
        return dhClient

    ak = os.getenv("DH_API_AK")
    sk = os.getenv("DH_API_SK")

    if not ak or not sk:
        raise ValueError("DH_API_KEY  DH_API_SK environment variable not set.")

    dhClient = DHApiClient._stdio(ak, sk)
    return dhClient

@mcp.tool(
    name="getVoices",
    description=(
    """
#工具说明：查询可用的发音人ID。
# 样例1：
用户输入：我之前克隆过哪些声音？
思考过程:
1.用户想要查询可用的发音人ID，需要使用“getVoices”工具。
2.工具需要参数，isSystem，一个参数。
3.从“克隆过的”可以推测希望查询克隆发音人ID，因此参数的值为“false”
# 样例2：
用户输入：我想用一个二十岁左右温柔小姐姐的声音。
思考过程:
1.用户想要查询可用的发音人ID，需要使用“getVoices”工具。
2.工具需要参数，isSystem，一个参数。
3.用户未明确指出发音人ID的来源，因此不传任何值。
4.从接口返回的内容中寻找describe中“二十岁”左右，gender中为“female”的音色，优先推荐给用户
    """)
)
async def getVoices(
        isSys: Annotated[Optional[bool],
            Field(description="是否是系统音色，true获取系统音色，false获取克隆音色, 空查询所有音色", default=None)]
) -> MCPVoicesResponse:
    """
    Get the list of available voices via DH API.

    Args:
        isSys: 是否是系统音色: true获取系统音色, false获取克隆音色, 空查询所有音色

    """
    try:
        client = await getDhClient()
        ret = await client.get_voices(isSys)
        return ret
    except Exception as e:
        return MCPVoicesResponse(error=str(e))


@mcp.tool(
    name="getFigures",
    description=(
    """
#工具说明：查询可用的人像ID
    """)
)
async def getFigures(
        systemFigure: Annotated[Optional[bool],
            Field(description="是否是平台公共人像，true返回平台公共人像，false返回定制人像，空查询全部", default=None)]
) -> MCPFiguresResponse:
    """
    Get the list of available figures via DH API.

    Args:
        systemFigure: 是否是平台公共人像，true返回平台公共人像，false返回定制人像，空查询全部
    """
    try:
        client = await getDhClient()
        ret = await client.get_figures(systemFigure)
        return ret
    except Exception as e:
        return MCPFiguresResponse(error=str(e))

@mcp.tool(
    name="uploadFiles",
    description=(
        """
#工具说明：根据业务类型上传所需要的文件。
# 样例：
用户输入：上传test.mp3这个文件用于声音克隆，文件在C：/Users/username/Desktop/test.mp3。
思考过程:
1.用户想要上传文件，需要使用“uploadFiles”工具。
2.工具需要参数，file，providerType，sourceFileName三个参数。
3.file：在C：/Users/username/Desktop/test.mp3路径下，名称为test.mp3的文件；\
providerType：声音克隆对应的值OPEN_TTS_CLONE_LITE；sourceFileName：test.mp3
        """
    )
)
async def uploadFiles(
        localFilePath: Annotated[str, Field(description="本地文件路径")],
        providerType: Annotated[Literal["OPEN_CUSTOMIZATION_2D_GENERAL", "OPEN_TTS_CLONE_LITE"],
        Field(description="上传文件的业务类型, OPEN_CUSTOMIZATION_2D_GENERAL：通用口型，OPEN_TTS_CLONE_LITE：音色克隆")],
        fileName: Annotated[str, Field(description="文件名")]
) -> MCPUploadResponse:
    """
    Upload Media file to DH using DH API

    Args:
        localFilePath: 本地文件路径
        providerType: 业务类型
        fileName: 文件名

    Return:
        fileID: 文件ID
    """
    try:
        client = await getDhClient()
        ret = await client.upload_file(localFilePath, providerType, fileName)
        return ret
    except Exception as e:
        return MCPFiguresResponse(error=str(e))

@mcp.tool(
    name="generateDh123Video",
    description=(
    """
#工具说明：简单便捷的生成数字人视频，根据真人录制的视频及选定音色，对视频分辨率等没有要求，无需人像生成，直接生产对应的数字人视频。
# 样例1：
用户输入：用fileid为xxx的视频文件，发音人ID为yyy的音色，视频的内容是“大家好，我是数字人播报的内容”，生成一个数字人视频。
思考过程:
1.用户想要用视频文件来直接生成一个视频，用户只提供了视频文件ID，发音人ID，以及内容，是一个简单的视频合成需求，需要使用“generateDh123Video”工具。
2.工具需要templateVideoId，driveType，text，person，inputAudioUrl这几个参数。
3.templateVideoId是需要使用的视频文件的ID，所以值为xxx。给的播报内容是文本，所以driveType是文本驱动，text为“大家好，我是数字人播报的内容”。\
发音人已经提供了ID，所以person的值是yyy
# 样例2：
用户输入：视频的地址是https://open-api-test.bj.bcebos.com/ae870923-2a3b-4d5e-b6a2-e44b4025647220250417_163529_trim.mp4，\
用发音人ID为yyy的音色，视频的内容是“大家好，我是数字人播报的内容”，生成一个数字人视频。
思考过程:
1.用户想要用视频地址的文件来直接生成一个视频，用户只提供了视频文件链接URL，发音人ID，以及内容，是一个简单的视频合成需求用户没有提到，\
需要使用“generateDh123Video”工具。
2.工具需要templateVideoId，driveType，text，person，inputAudioUrl这几个参数。
3.templateVideoId是需要使用的视频文件的ID，所以值为xxx。给的播报内容是文本，所以driveType是文本驱动，text为“大家好，我是数字人播报的内容”。\
发音人已经提供了ID，所以person的值是yyy
    """)
)
async def generateDh123Video(
        inputText: Annotated[str, Field(description="文本内容", default=None)],
        voiceId: Annotated[str, Field(description="音色Id,来自getVoices", default=None)],
        videoUrl: Annotated[str, Field(description="视频文件id或URL", default=None)],
        title: Annotated[str, Field(description="标题", default=None)],
) -> MCPVideoGenerateResponse:
    """
    Generate a new 123 digital human video using the DH API.

    Args:
        inputText: 文本内容
        voiceId: 音色
        videoUrl: 视频信息
        title: 标题
    """
    try:
        request = Generate123VideoRequest(
            title=title,
            text=inputText,
            templateVideoId=videoUrl,
            ttsParams=TtsParams(person=voiceId)
        )

        client = await getDhClient()
        ret = await client.generate_123avatar_video(request)
        return ret
    except Exception as e:
        return MCPVideoGenerateResponse(error=str(e))


@mcp.tool(
    name="getDh123VideoStatus",
    description=(
    """
#工具说明：查询123数字人视频合成进度。
# 样例1：
用户输入：查一下taskid为xxx的123数字人视频好了没有
思考过程:
1.用户想要查询taskid为xxx的123数字人视频，需要使用“getDh123VideoStatus”工具。
2.工具需要task ID这些参数。
3.task ID的值为xxx
    """)
)
async def getDh123VideoStatus(
        taskId: Annotated[str, Field(description="视频任务ID", default=None)],
) -> MCPVideoStatusResponse:
    """
    Retrieve the status of a 123 video generated via the DH API.

    Args:
        taskId: 视频任务ID
    """
    try:
        client = await getDhClient()
        ret = await client.get_video_status(taskId)
        return ret
    except Exception as e:
        return MCPVideoStatusResponse(error=str(e))

@mcp.tool(
    name="generateDhVideo",
    description=(
    """
#工具说明：根据所选数字人像ID及发音人ID，生成数字人视频。
# 样例1：
用户输入：用数字人像ID为xxx，发音人ID为yyy的音色，视频的内容是“大家好，我是数字人播报的内容”，使用横屏全身的机位，视频背景用\
“https://digital-human-material.bj.bcebos.com/-%5BLjava.lang.String%3B%4046f6cc1e.png”，\
开启自动添加动作，开启字幕，生成一个1080P的数字人视频。
思考过程:
1.用户想要用人像ID生成一个数字人视频，对声音，背景，字幕，分辨率等有要求，不是一个简单的数字人视频，需要使用“generateDhVideo”工具。
2.工具需要FigureId，driveType，text，person，inputAudioUrl，width，hight，cameraID，enable，backgroundimageUrl，\
autoAnimoji这些参数。
3.FigureId是需要使用的人像ID，所以值为xxx。给的播报内容是文本，所以driveType是文本驱动，text为“大家好，我是数字人播报的内容”。\
发音人已经提供了ID，所以person的值是yyy，开启自动动作，所以autoAnimoji的值为true，开启字幕，所以enabled的值为true，分辨率为1080P，\
拆分为width的值为1920，hight的值为1080，backgroundimageUrl的值是\
“https://digital-human-material.bj.bcebos.com/-%5BLjava.lang.String%3B%4046f6cc1e.png”
    """)
)
async def generateDhVideo(
        figureId: Annotated[str, Field(description="人像ID", default=None)],
        voiceId: Annotated[str, Field(description="音色ID", default=None)],
        text: Annotated[str, Field(description="播报内容", default=None)],
        inputAudioUrl: Annotated[str, Field(description="驱动音频URL", default=None)],
        resolutionWidth: Annotated[int, Field(description="分辨率:宽", default=768)],
        resolutionHeight: Annotated[int, Field(description="分辨率:高", default=1280)],
        backgroundTransparent: Annotated[bool, Field(description="背景是否透明", default=False)],
        cameraId: Annotated[int,
            Field(description="数字人相机机位，0:横屏半身, 1:竖屏半身, 2: 横屏全身, 3: 竖屏全身", default=3)],
        backgroundImageUrl: Annotated[str, Field(description="背景图片", default=None)],
        callbackUrl: Annotated[str, Field(description="回调地址", default=None)],
        driveType: Annotated[Literal["TEXT", "VOICE"],
            Field(description="驱动类型, TEXT:文本驱动, VOICE: 音频驱动", default="TEXT")],
        subtitleEnable: Annotated[bool, Field(description="是否启用字幕", default=False)],
        autoAnimoji: Annotated[bool, Field(description="自动添加数字人动作", default=False)]
) -> MCPVideoGenerateResponse:
    """
    Generate a new digital human video using the DH API.

    Args:
        figureId: 人像ID
        driveType: 驱动类型, TEXT:文本驱动, VOICE: 音频驱动
        text: 文本内容，播报内容
        voiceId: 音色id,
        inputAudioUrl: 驱动音频URL
        resolutionWidth: 分辨率宽
        resolutionHeight: 分辨率高
        backgroundTransparent: 背景透明
        cameraId: 0:横屏半身, 1:竖屏半身, 2: 横屏全身, 3: 竖屏全身
        subtitleEnable: 字幕
        backgroundImageUrl: 背景图片
        autoAnimoji: 自动添加数字人动作
        callbackUrl: 回调地址

    Returns:
        taskId: 任务ID
    """
    try:
        request = VideoGenerateRequest(
            figureId=figureId,
            driveType=driveType,
            text=text,
            ttsParams=TtsParams(person=str(voiceId), speed="5", volume="5", pitch="5"),
            inputAudioUrl=inputAudioUrl,
            videoParams=VideoParams(width=resolutionWidth, height=resolutionHeight, transparent=backgroundTransparent),
            dhParams=DHParams(cameraId=cameraId),
            subtitleParams=SubtitleParams(subtitlePolicy="SRT", enabled=True) if subtitleEnable else None,
            backgroundImageUrl=backgroundImageUrl,
            callbackUrl=callbackUrl,
            autoAnimoji=autoAnimoji,
        )

        client = await getDhClient()
        ret = await client.generate_avatar_video(request)
        return ret
    except Exception as e:
        return MCPVideoGenerateResponse(error=str(e))


@mcp.tool(
    name="getDhVideoStatus",
    description=(
    """
#工具说明：查询基础数字人视频合成进度。
# 样例1：
用户输入：查一下taskid为xxx的数字人视频好了没有
思考过程:
1.用户想要查询taskid为xxx的数字人视频好了没有，需要根据context来做判断，最近调用了“generateDhVideo”工具，\
需要使用“getDhVideoStatus”工具，如果没有查询到，则需要使用“getDh123VideoStatus”工具继续查询。
2.工具需要task ID这些参数。
3.task ID的值为xxx
    """)
)
async def getDhVideoStatus(
        taskId: Annotated[str, Field(description="基础数字人视频任务ID", default=None)],
) -> MCPVideoStatusResponse:
    """
    Retrieve the status of a video generated via the DH API.

    Args:
        taskId: 任务ID

    Returns:
        任务状态
    """
    try:
        client = await getDhClient()
        ret = await client.get_video_status(taskId)
        return ret
    except Exception as e:
        return MCPVideoStatusResponse(error=str(e))

@mcp.tool(
    name="generateText2Audio",
    description=(
    """
#工具说明：根据提供的文本内容及选定音色，无需生成视频，生产对应的音频。
# 样例1：
用户输入：用发音人ID为xxx的音色，内容是“大家好，我是数字人播报的内容”，生成音频。
思考过程:
1.用户想生成一个音频，需要使用“generateText2Audio”工具。
2.工具需要text，person这几个参数。
3.text为“大家好，我是数字人播报的内容”。发音人已经提供了ID，所以person的值是yyy
    """)
)
async def generateText2Audio(
        text: Annotated[str, Field(description="文本内容", default=None)],
        voiceId: Annotated[str, Field(description="音色ID，来自getVoices的返回值", default=None)],
) -> MCPVideoGenerateResponse:
    """
    Generate new audio by inputText using the DH API.
    # outputFormat: str = "mp3"
    Args:
        text: 文本内容
        voiceId: 音色id

    """
    try:
        request = Text2AudioGenerateRequest(
            text=text,
            person=voiceId,
        )

        client = await getDhClient()
        ret = await client.generate_text2audio(request)
        return ret
    except Exception as e:
        return MCPVideoGenerateResponse(error=str(e))

@mcp.tool(
    name="getText2AudioStatus",
    description=(
    """
#工具说明：查询音频合成进度。
# 样例1：
用户输入：查一下taskid为xxx的语音合成好了没有。
思考过程:
1.用户想要查询taskid为xxx的音频好了没有，需要使用“getText2AudioStatus”工具查询。
2.工具需要task ID这些参数。
3.task ID的值为xxx
    """)
)
async def getText2AudioStatus(
        taskId: Annotated[str, Field(description="语音合成任务ID", default=None)]
) -> MCPText2AudioStatusResponse:
    """
    Retrieve the status of generated audio via the DH API.

    Args:
        taskId: 任务ID
    """
    try:
        client = await getDhClient()
        ret = await client.get_text2audio_status(taskId)
        return ret
    except Exception as e:
        return MCPText2AudioStatusResponse(error=str(e))

@mcp.tool(
    name="generateLite2dGeneralVideo",
    description=(
    """
#工具说明：根据上传真人录制的视频生成数字人像，仅可用于基础视频制作，数字人使用通用口型驱动。
# 样例1：
用户输入：用fileid为xxx的视频文件，生成数字人，命名为“zhangsan”，是个男生的形象。
思考过程:
1.用户想要生成数字人像，需要使用“generateLite2dGeneralVideo”工具。
2.工具需要参数，name，gender，keepBackground，templateVideoId四个参数。
3.用户提到了fileID为xxx，所以templateVideoid的值为xxx，name为zhangsan，男生的形象，gender的值为male，未提到是否保留背景所以keepBackground默认为false。
    """)
)
async def generateLite2dGeneralVideo(
        name: Annotated[str, Field(description="名称", default=None)],
        gender: Annotated[Literal["MALE", "FEMALE"], Field(description="性别", default="FEMALE")],
        templateVideoId: Annotated[str, Field(description="视频：视频文件/底板视频，来自 uploadFiles 返回的fileId", default=None)],
        keepBackground: Annotated[bool, Field(description="是否保留背景", default=False)],
        maskVideoId: Annotated[str, Field(description="遮罩，底板视频对应的mask视频", default=None)]
) -> MCPLite2DGenerateResponse:
    """
    Generate a lite 2d general avatar video from template video file via the DH API.

    Args:
        name (str): 数字人名称
        gender (str): 性别，MALE 或 FEMALE，来自 getGender
        keepBackground (bool): 是否保留背景
        templateVideoId (str): 视频，视频文件，底板视频，来自 uploadFiles 返回的fileId
        maskVideoId (str): 遮罩，底板视频对应的mask视频，可选，来自 uploadFiles 返回的fileId
    """
    try:
        client = await getDhClient()
        req = Lite2dGenerateRequest(
            name=name,
            customizeType="LITE_2D_GENERAL",
            gender=gender,
            keepBackground=keepBackground,
            templateVideoId=templateVideoId,
            maskVideoId=maskVideoId if maskVideoId != "" else None,
        )

        ret = await client.generate_lite2d_video(req)
        return ret
    except Exception as e:
        return MCPLite2DGenerateResponse(error=str(e))

@mcp.tool(
    name="getLite2dGeneralStatus",
    description=(
    """
#工具说明：根据2D小样本数字人对应的人像ID，查询该任务目前的状态，也可以用于查询有哪些可用的2D人像。
# 样例1：
用户输入：查一下id为xxx的数字人好了没有。
思考过程:
1.用户想要查询人像生成任务的状态，需要使用“getLite2dGeneralStatus”工具。
2.工具需要，figureId，systemFigure，trainSuccess，pageNo，ppageSize这些参数。
3.用户提到了ID为xxx，所以figureId的值为xxx，现在不清楚这个任务的状态，所以trainSuccess的值不需要填，系统人像不需要生成过程，所以systemFigure值为false，其他为默认值。
# 样例2：
用户输入：我可以用哪些人像
思考过程:
1.用户想要查询哪些人像ID可以使用，需要使用“getLite2dGeneralStatus”工具。
2.工具需要，figureId，systemFigure，trainSuccess，pageNo，ppageSize这些参数。
3.查询可用人像，所以figureId为空，syste
Figure为空，trainSuccess为ture，pageNo默认为1，避免漏查pageSize为最大值100。
    """)
)
async def getLite2dGeneralStatus(
        figureId: Annotated[str, Field(description="人像ID", default=None)],
        systemFigure: Annotated[Optional[bool], \
                Field(description="是否是平台公共人像，true返回平台公共人像，false返回定制人像，空查询全部", default=None)],
        trainSuccess: Annotated[bool, \
                Field(description="是否查询训练完成:true：只返回可用人像,false：只返回排队中、训练中或训练失败的定制人像,为空不进行过滤",
                      default=None)]) \
        -> MCPLite2DStatusResponse:
    """
    Retrieve the status of a lite2d General video via the DH API.

    Args:
        figureId: 人像ID

    Returns:
        任务状态
    """
    try:
        client = await getDhClient()
        ret = await client.get_lite2d_general_status(figureId, systemFigure, trainSuccess)
        return ret
    except Exception as e:
        return MCPVideoStatusResponse(error=str(e))

@mcp.tool(
    name="generateVoiceCloneLite",
    description=(
    """
#工具说明：根据上传音频生成音色，可用于语音合成及视频制作.
# 样例1：
用户输入：用文件id为xxx的音频文件克隆声音。命名为“zhangsan”，是一个三十岁左右中年男性的音色，用“这个是我克隆的声音”这段文本试听一下
思考过程:
1.用户想要克隆一个声音，需要使用“generateVoiceCloneLite”工具。
2.工具需要参数，name,gender,describe,uploadAudioId,example，五个参数。
3.uploadAudioId的值为文件ID，name的值为zhangsan，describe的值为“一个三十岁左右中年男性的音色”，gender的值为male，example为“这个是我克隆的声音”
    """)
)
async def generateVoiceCloneLite(
        name: Annotated[str, Field(description="音色名称")],
        describe: Annotated[str, Field(description="音色描述")],
        uploadAudioId: Annotated[str, Field(description="音频文件id")],
        exampleText: Annotated[str, Field(description="音频文本")],
        gender: Annotated[Literal["male", "female", "unknown"], Field(description="性别", default="unknown")]
) -> MCPVoiceCloneResponse:
    """
    create a lite task of Clone a voice with upload audio file via the DH API.

    Args:
        name: 音色名称
        describe: 音色描述
        gender: 性别
        uploadAudioId: 音频文件id
        exampleText: 音频文本
        callbackUrl: 回调地址

    Return:
        perId: 音色克隆任务的ID
    """
    try:
        client = await getDhClient()
        req = VoiceCloneRequest(
            name=name,
            describe=describe,
            uploadAudioId=uploadAudioId,
            exampleText=exampleText,
            gender=gender.lower(),
        )

        ret = await client.voice_clone(req, True)
        return ret
    except Exception as e:
        return MCPVoiceCloneResponse(error=str(e))

@mcp.tool(
    name="getVoiceCloneStatus",
    description=(
    """
#工具说明：根据声音克隆任务的发音人ID，查询该任务目前的状态。
# 样例1：
用户输入：查一下id为xxx的声音克隆好了没有。
思考过程:
1.用户想要查询声音克隆任务的状态，需要使用“getVoiceCloneStatus”工具。
2.工具需要参数，isSuccess，perId两个参数。
3.用户提到了ID为xxx，所以perid的值为xxx，现在不清楚这个任务的状态，所以isSuccess的值为false。
    """)
)
async def getVoiceCloneStatus(
    perId: Annotated[str, Field(description="音色克隆任务的ID", default=None)]
) -> MCPVoiceCloneStatusResponse:
    """
    Retrieve the status of a voice clone task via the DH API.

    Args:
        perId: 音色克隆任务的ID

    Returns:
        任务状态
    """
    try:
        client = await getDhClient()
        ret = await client.voice_clone_status(perId)
        return ret
    except Exception as e:
        return MCPVoiceCloneStatusResponse(error=str(e))


def main():
    """Start the DH MCP """
    print("Start DH MCP")
    try:
        mcp.run()
    except KeyboardInterrupt:
        print(f"Keyboard Interrupt")
        sys.exit()
    except BaseException as e:
        print("unhandled exception", e)
        sys.exit()

if __name__ == "__main__":
    main()