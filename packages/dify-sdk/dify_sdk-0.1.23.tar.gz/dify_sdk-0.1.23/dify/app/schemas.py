from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Literal, Optional, List, Annotated, Union

from pydantic import BaseModel, Field, model_validator


class AppMode(str, Enum):
    CHAT = "chat"
    AGENT_CHAT = "agent-chat"
    WORKFLOW = "workflow"
    COMPLETION = "completion"
    BUNDLE = "bundle"

class Tag(BaseModel):
    """标签模型

    Attributes:
        id: 标签ID
        name: 标签名称
        type: 标签类型
    """

    id: str = Field(description="标签ID")
    name: str = Field(description="标签名称")
    type: str = Field(description="标签类型")


class MoreLikeThis(BaseModel):
    """相似推荐配置模型

    Attributes:
        enabled: 是否启用相似推荐功能
    """

    enabled: bool = Field(default=False, description="是否启用相似推荐功能")


class SuggestedQuestionsAfterAnswer(BaseModel):
    """回答后的建议问题配置模型"""

    enabled: bool = Field(default=False, description="是否启用回答后的建议问题功能")


class SpeechToText(BaseModel):
    """语音转文本配置

    Attributes:
        enabled: 是否开启语音转文本功能
    """

    enabled: bool = Field(default=False, description="是否开启语音转文本功能")


class TextToSpeech(BaseModel):
    """文字转语音配置

    Attributes:
        enabled: 是否开启文字转语音功能
        language: 语音语言
        voice: 语音类型
    """

    enabled: bool = Field(default=False, description="是否开启文字转语音功能")
    language: str = Field(default="", description="语音语言")
    voice: str = Field(default="", description="语音类型")


class RetrieverResource(BaseModel):
    """检索资源Schema

    Attributes:
        enabled: 是否开启检索资源功能
        position: 段落位置
        document_id: 文档ID
        content: 内容摘要
    """

    enabled: bool = Field(default=False, description="是否开启检索资源功能")
    position: Optional[int] = Field(default=None, description="段落位置")
    document_id: Optional[str] = Field(default=None, description="文档ID")
    content: Optional[str] = Field(default=None, description="内容摘要")


class SensitiveWordAvoidance(BaseModel):
    """敏感词规避配置

    Attributes:
        enabled: 是否开启敏感词规避功能
        type: 敏感词规避类型
    """

    enabled: bool = Field(default=False, description="是否开启敏感词规避功能")
    type: str = Field(default="", description="敏感词规避类型")
    configs: Optional[list] = Field(default=None, description="敏感词规避配置")


class Tool(BaseModel):
    """工具配置

    Attributes:
        provider_id: 提供者ID
        provider_type: 提供者类型
        provider_name: 提供者名称
        tool_name: 工具名称
        tool_label: 工具标签
        tool_parameters: 工具参数配置
        notAuthor: 是否非作者
        enabled: 是否启用
    """

    provider_id: Optional[str] = Field(default=None, description="提供者ID")
    provider_type: Optional[str] = Field(default=None, description="提供者类型")
    provider_name: Optional[str] = Field(default=None, description="提供者名称")
    tool_name: Optional[str] = Field(default=None, description="工具名称")
    tool_label: Optional[str] = Field(default=None, description="工具标签")
    tool_parameters: Optional[dict] = Field(default=None, description="工具参数配置")
    notAuthor: Optional[bool] = Field(default=False, description="是否非作者")
    enabled: Optional[bool] = Field(default=True, description="是否启用")


class AgentMode(BaseModel):
    """代理模式配置

    Attributes:
        max_iteration: 最大迭代次数
        enabled: 是否启用
        tools: 工具列表
        strategy: 策略类型
    """

    max_iteration: Optional[int] = Field(default=5, description="最大迭代次数")
    enabled: Optional[bool] = Field(default=True, description="是否启用")
    tools: Optional[List[Tool]] = Field(default_factory=list, description="工具列表")
    strategy: Optional[str] = Field(default="react", description="策略类型")


class DatasetConfigs(BaseModel):
    """数据集配置"""

    retrieval_model: str = Field(default="multiple", description="检索模型类型")
    datasets: dict = Field(
        default_factory=lambda: {"datasets": []},
        description="数据集配置，包含数据集列表",
    )
    reranking_enable: bool = Field(default=False, description="是否启用重排序")
    top_k: int = Field(default=4, description="返回结果数量")


class FileUploadConfig(BaseModel):
    """文件上传配置

    Attributes:
        file_size_limit: 文件大小限制（MB）
        batch_count_limit: 批量上传数量限制
        image_file_size_limit: 图片文件大小限制（MB）
        video_file_size_limit: 视频文件大小限制（MB）
        audio_file_size_limit: 音频文件大小限制（MB）
        workflow_file_upload_limit: 工作流文件上传限制（MB）
    """

    file_size_limit: int = Field(default=15, description="文件大小限制（MB）")
    batch_count_limit: int = Field(default=5, description="批量上传数量限制")
    image_file_size_limit: int = Field(default=10, description="图片文件大小限制（MB）")
    video_file_size_limit: int = Field(
        default=100, description="视频文件大小限制（MB）"
    )
    audio_file_size_limit: int = Field(default=50, description="音频文件大小限制（MB）")
    workflow_file_upload_limit: int = Field(
        default=10, description="工作流文件上传限制（MB）"
    )


class Image(BaseModel):
    """图片设置

    Attributes:
        enabled: 是否开启
        number_limits: 图片数量限制，默认3
        transfer_methods: 传递方式列表，remote_url, local_file，必选一个
    """

    enabled: bool = Field(default=False, description="是否开启")
    number_limits: int = Field(default=3, description="图片数量限制，默认3")
    transfer_methods: List[str] = Field(
        default_factory=list,
        description="传递方式列表，remote_url, local_file，必选一个",
    )
    detail: Optional[str] = Field(default="high", description="图片详情")


class FileUpload(BaseModel):
    """文件上传配置

    Attributes:
        image: 图片上传配置，包含细节、启用状态、数量限制和传输方式
        enabled: 是否启用文件上传功能
        allowed_file_types: 允许上传的文件类型
        allowed_file_extensions: 允许上传的文件扩展名
        allowed_file_upload_methods: 允许的文件上传方式
        number_limits: 文件上传数量限制
        fileUploadConfig: 文件上传配置
    """

    image: Image = Field(
        default=Image(),
        description="图片上传配置，包含细节、启用状态、数量限制和传输方式",
    )
    enabled: bool = Field(default=False, description="是否启用文件上传功能")
    allowed_file_types: List[str] = Field(
        default_factory=list, description="允许上传的文件类型"
    )
    allowed_file_extensions: List[str] = Field(
        default_factory=list, description="允许上传的文件扩展名"
    )
    allowed_file_upload_methods: List[str] = Field(
        default_factory=list, description="允许的文件上传方式"
    )
    number_limits: int = Field(default=3, description="文件上传数量限制")
    fileUploadConfig: FileUploadConfig = Field(
        default=FileUploadConfig(), description="文件上传配置"
    )


class AnnotationReply(BaseModel):
    """标记回复配置

    Attributes:
        enabled: 是否开启标记回复功能
    """

    enabled: bool = Field(default=False, description="是否开启标记回复功能")


class ModelProviderConfig(BaseModel):
    """模型提供者配置

    Attributes:
        provider: 模型提供者名称
        name: 模型名称
        mode: 模型模式
        completion_params: 完成参数配置
    """

    provider: str = Field(description="模型提供者名称")
    name: str = Field(description="模型名称")
    mode: str = Field(description="模型模式")
    completion_params: dict = Field(default_factory=dict, description="完成参数配置")


class ModelConfig(BaseModel):
    """AI应用配置模型"""

    pre_prompt: Optional[str] = Field(default=None, description="提示词")
    prompt_type: Optional[str] = Field(default=None, description="提示词类型")
    chat_prompt_config: Optional[dict] = Field(default=None, description="对话提示配置")
    completion_prompt_config: Optional[dict] = Field(
        default=None, description="补全提示配置"
    )
    user_input_form: Optional[List["UserInputItem"]] = Field(
        default=None, description="用户输入表单配置"
    )
    dataset_query_variable: Optional[str] = Field(
        default=None, description="数据集查询变量"
    )
    opening_statement: Optional[str] = Field(default=None, description="开场白文本")
    more_like_this: Optional[MoreLikeThis] = Field(
        default=None, description="相似推荐配置"
    )
    suggested_questions: Optional[List[str]] = Field(
        default=None, description="建议问题列表"
    )
    suggested_questions_after_answer: Optional[SuggestedQuestionsAfterAnswer] = Field(
        default=None, description="回答后的建议问题配置"
    )
    text_to_speech: Optional[TextToSpeech] = Field(
        default=None, description="文字转语音配置"
    )
    speech_to_text: Optional[SpeechToText] = Field(
        default=None, description="语音转文字配置"
    )
    retriever_resource: Optional[RetrieverResource] = Field(
        default=None, description="检索资源配置"
    )
    sensitive_word_avoidance: Optional[SensitiveWordAvoidance] = Field(
        default=None, description="敏感词规避配置"
    )
    agent_mode: Optional[AgentMode] = Field(default=None, description="代理模式配置")
    dataset_configs: Optional[DatasetConfigs] = Field(
        default=None, description="数据集配置"
    )
    file_upload: Optional[FileUpload] = Field(default=None, description="文件上传配置")
    annotation_reply: Optional[AnnotationReply] = Field(
        default=None, description="注释回复配置"
    )
    supportAnnotation: Optional[bool] = Field(
        default=True, description="是否支持注释功能"
    )
    appId: Optional[str] = Field(default=None, description="应用ID")
    supportCitationHitInfo: Optional[bool] = Field(
        default=True, description="是否支持引用命中信息"
    )
    model: Optional[ModelProviderConfig] = Field(default=None, description="模型配置")


class App(BaseModel):
    """Dify应用模型

    Attributes:
        id: 应用ID
        name: 应用名称
        max_active_requests: 最大活跃请求数
        description: 应用描述
        mode: 应用模式
        icon_type: 图标类型
        icon: 图标
        icon_background: 图标背景
        icon_url: 图标URL
        app_config: 模型配置
        workflow: 工作流
        use_icon_as_answer_icon: 是否使用图标作为回答图标
        created_by: 创建者
        created_at: 创建时间
        updated_by: 更新者
        updated_at: 更新时间
        tags: 标签
    """

    id: Optional[str] = Field(default=None, description="应用ID")
    name: Optional[str] = Field(default=None, description="应用名称")
    max_active_requests: Optional[int] = Field(
        default=None, description="最大活跃请求数"
    )
    description: Optional[str] = Field(default=None, description="应用描述")
    mode: Optional[AppMode] = Field(default=None, description="应用模式")
    icon_type: Optional[str] = Field(default=None, description="图标类型")
    icon: Optional[str] = Field(default=None, description="图标")
    icon_background: Optional[str] = Field(default=None, description="图标背景")
    icon_url: Optional[str] = Field(default=None, description="图标URL")
    app_config: Optional[ModelConfig] = Field(
        default_factory=ModelConfig, alias="model_config", description="模型配置"
    )
    workflow: Optional[dict] = Field(default=None, description="工作流")
    use_icon_as_answer_icon: Optional[bool] = Field(
        default=None, description="是否使用图标作为回答图标"
    )
    created_by: Optional[str] = Field(default=None, description="创建者")
    created_at: Optional[datetime] = Field(default=None, description="创建时间")
    updated_by: Optional[str] = Field(default=None, description="更新者")
    updated_at: Optional[datetime] = Field(default=None, description="更新时间")
    tags: Optional[List[Tag]] = Field(default_factory=list, description="标签")
    # Pydantic V2 配置方式
    model_config = {
        "populate_by_name": True,
        "protected_namespaces": (),  # 可选，解决 Pydantic 保留名称冲突
    }


class ChatCompletionResponse(BaseModel):
    """聊天完成响应"""

    message_id: str = Field(..., description="消息ID")
    conversation_id: Optional[str] = Field(default=None, description="会话ID")
    answer: str = Field(..., description="回答")
    metadata: Optional['Metadata'] = Field(default=None, description="元数据")
    created_at: Optional[int] = Field(default=None, description="消息创建时间戳，如：1705395332")

class TransferMethod(str, Enum):
    """图片上传方式


    Attributes:
        REMOTE_URL: 远程URL
        LOCAL_FILE: 本地文件
    """

    REMOTE_URL = "remote_url"
    LOCAL_FILE = "local_file"


class FileType(str, Enum):
    """文件类型枚举

    Attributes:
        DOCUMENT: 文档类型,具体类型包含：'TXT', 'MD', 'MARKDOWN', 'PDF', 'HTML', 'XLSX', 'XLS', 'DOCX', 'CSV', 'EML', 'MSG', 'PPTX', 'PPT', 'XML', 'EPUB'
        IMAGE: 图片类型,具体类型包含：'JPG', 'JPEG', 'PNG', 'GIF', 'WEBP', 'SVG'
        AUDIO: 音频类型,具体类型包含：'MP3', 'M4A', 'WAV', 'WEBM', 'AMR'
        VIDEO: 视频类型,具体类型包含：'MP4', 'MOV', 'MPEG', 'MPGA'
        CUSTOM: 自定义类型
    """

    DOCUMENT = "document"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    CUSTOM = "custom"


class File(BaseModel):
    """用户上传的文件对象

    Attributes:
        type: 文件类型，`chat`模式仅支持图片格式
        transfer_method: 文件传递方式
        url: 图片地址（仅当传递方式为remote_url时）
        upload_file_id: 上传文件ID（仅当传递方式为local_file时）
    """

    type: FileType = Field(default=FileType.IMAGE, description="文件类型")
    transfer_method: TransferMethod = Field(description="文件传递方式")
    url: Optional[str] = Field(
        default=None, description="图片地址，仅当传递方式为remote_url时有效"
    )
    upload_file_id: Optional[str] = Field(
        default=None, description="上传文件ID，仅当传递方式为local_file时有效"
    )

    @model_validator(mode="after")
    def validate_file_info(self) -> "File":
        """验证文件信息是否有效"""
        if self.transfer_method == TransferMethod.REMOTE_URL and not self.url:
            raise ValueError("当传递方式为remote_url时，必须提供url")
        if (
            self.transfer_method == TransferMethod.LOCAL_FILE
            and not self.upload_file_id
        ):
            raise ValueError("当传递方式为local_file时，必须提供upload_file_id")
        return self

    # Pydantic V2 配置方式
    model_config = {
        "populate_by_name": True,
        "protected_namespaces": (),  # 可选，解决 Pydantic 保留名称冲突
    }


class ChatPayloads(BaseModel):
    """聊天请求配置

    Attributes:
        query (str): 用户输入/提问内容
        inputs (dict): 允许传入 App 定义的各变量值。inputs 参数包含了多组键值对（Key/Value pairs），每组的键对应一个特定变量，每组的值则是该变量的具体值。默认 {}
        response_mode (str): 响应模式。streaming 流式模式（推荐）。基于 SSE（Server-Sent Events）实现类似打字机输出方式的流式返回。blocking 阻塞模式，等待执行完毕后返回结果。（请求若流程较长可能会被中断）。由于 Cloudflare 限制，请求会在 100 秒超时无返回后中断。注：Agent模式下不允许blocking
        user (str): 用户标识，用于定义终端用户的身份，方便检索、统计。由开发者定义规则，需保证用户标识在应用内唯一
        conversation_id (str): （选填）会话 ID，需要基于之前的聊天记录继续对话，必须传之前消息的 conversation_id
        files (list[UploadFile]): 上传的文件。
        auto_generate_name (bool): （选填）自动生成标题，默认 true。若设置为 false，则可通过调用会话重命名接口并设置 auto_generate 为 true 实现异步生成标题
    """

    query: str = Field(..., description="用户输入/提问内容")
    inputs: Optional[dict] = Field(
        default_factory=dict, description="额外的输入参数配置"
    )
    response_mode: Literal["streaming", "blocking"] = Field(
        default="streaming", description="响应模式"
    )
    user: str = Field(..., description="用户标识")
    conversation_id: Optional[str] = Field(default=None, description="对话ID")
    files: Optional[List[File]] = Field(
        default_factory=list, description="上传的文件列表"
    )
    auto_generate_name: Optional[bool] = Field(default=True, description="自动生成标题")
    parent_message_id: Optional[str] = Field(default=None, description="父消息ID")
    app_config: Optional[ModelConfig] = Field(
        default_factory=ModelConfig, alias="model_config", description="模型配置"
    )


class RunWorkflowPayloads(BaseModel):
    """运行工作流请求配置

    Attributes:
        inputs (dict): 允许传入 App 定义的各变量值。inputs 参数包含了多组键值对（Key/Value pairs），每组的键对应一个特定变量，每组的值则是该变量的具体值。默认 {}
        response_mode (str): 响应模式。streaming 流式模式（推荐）。基于 SSE（Server-Sent Events）实现类似打字机输出方式的流式返回。blocking 阻塞模式，等待执行完毕后返回结果。（请求若流程较长可能会被中断）。由于 Cloudflare 限制，请求会在 100 秒超时无返回后中断。注：Agent模式下不允许blocking
        user (str): 用户标识，用于定义终端用户的身份，方便检索、统计。由开发者定义规则，需保证用户标识在应用内唯一
        files (list[UploadFile]): 上传的文件。
    """

    inputs: Optional[dict] = Field(
        default_factory=dict, description="额外的输入参数配置"
    )
    response_mode: Optional[str] = Field(default="streaming", description="响应模式")
    user: Optional[str] = Field(default=None, description="用户标识")
    files: Optional[List[File]] = Field(
        default_factory=list, description="上传的文件列表"
    )

class ConversationEventType(str, Enum):
    """对话事件类型枚举

    Attributes:
        MESSAGE: LLM返回文本块事件，即完整的文本以分块的方式输出
        AGENT_MESSAGE: Agent模式下返回文本块事件，即文章的文本以分块的方式输出（仅Agent模式下使用）
        AGENT_THOUGHT: Agent模式下有关Agent思考步骤的相关内容，涉及到工具调用（仅Agent模式下使用）
        MESSAGE_FILE: 表示有新文件需要展示
        MESSAGE_END: 消息结束事件，收到此事件则代表流式返回结束
        TTS_MESSAGE: TTS消息
        TTS_MESSAGE_END: TTS消息结束
        MESSAGE_REPLACE: 消息替换
        ERROR: 错误
        PING: 心跳检测
        WORKFLOW_STARTED: 工作流开始
        WORKFLOW_FINISHED: 工作流结束
        NODE_STARTED: 节点开始
        NODE_FINISHED: 节点结束
        TEXT_CHUNK: 文本片段
    """

    MESSAGE = "message"
    AGENT_MESSAGE = "agent_message"
    AGENT_THOUGHT = "agent_thought"
    MESSAGE_FILE = "message_file"
    MESSAGE_END = "message_end"
    TTS_MESSAGE = "tts_message"
    TTS_MESSAGE_END = "tts_message_end"
    MESSAGE_REPLACE = "message_replace"
    ERROR = "error"
    PING = "ping"
    WORKFLOW_STARTED = "workflow_started"
    WORKFLOW_FINISHED = "workflow_finished"
    NODE_STARTED = "node_started"
    NODE_FINISHED = "node_finished"
    TEXT_CHUNK = "text_chunk"


class ChatMessageEvent(BaseModel):
    """聊天消息事件模型

    Attributes:
        event (str): 事件类型，固定为'message'
        task_id (str, optional): 任务ID
        message_id (str): 消息ID
        conversation_id (str, optional): 会话ID
        answer (str): 回答内容
        created_at (int): 创建时间戳
    """

    event: Literal[ConversationEventType.MESSAGE] = Field(
        default=ConversationEventType.MESSAGE, description="事件类型"
    )
    task_id: Optional[str] = Field(default=None, description="任务ID")
    message_id: str = Field(..., description="消息ID")
    conversation_id: Optional[str] = Field(default=None, description="会话ID")
    answer: str = Field(..., description="回答内容")
    created_at: int = Field(..., description="创建时间戳")

    # Pydantic V2 配置方式
    model_config = {
        "populate_by_name": True,
        "protected_namespaces": (),
    }


class ErrorEvent(BaseModel):
    """流式输出过程中出现的异常会以 stream event 形式输出，收到异常事件后即结束。

    Attributes:
        event (str): 事件类型，固定为'error'
        task_id (str): 任务ID
        message_id (str): 消息ID
        status (int): HTTP状态码
        code (str): 错误代码
        message (str): 错误信息
    """

    event: Literal[ConversationEventType.ERROR] = Field(
        default=ConversationEventType.ERROR, description="事件类型"
    )
    task_id: Optional[str] = Field(default=None, description="任务ID")
    message_id: Optional[str] = Field(default=None, description="消息ID")
    status: Optional[int] = Field(default=None, description="HTTP状态码")
    code: Optional[str] = Field(default=None, description="错误代码")
    message: Optional[str] = Field(default=None, description="错误信息")


class AgentMessageEvent(BaseModel):
    """Agent模式下返回文本块事件，即：在Agent模式下，文章的文本以分块的方式输出（仅Agent模式下使用）

    Attributes:
        event (str): 事件类型，固定为'agent_message'
        task_id (str): 任务ID
        message_id (str): 消息ID
        conversation_id (str): 会话ID
        id (str): 消息ID
        answer (str): 回答内容
        created_at (int): 创建时间戳
    """

    event: Literal[ConversationEventType.AGENT_MESSAGE] = Field(
        default=ConversationEventType.AGENT_MESSAGE, description="事件类型"
    )
    task_id: str = Field(..., description="任务ID")
    message_id: str = Field(..., description="消息ID")
    conversation_id: str = Field(..., description="会话ID")
    id: str = Field(..., description="消息ID")
    answer: str = Field(..., description="回答内容")
    created_at: int = Field(..., description="创建时间戳")


class AgentThoughtEvent(BaseModel):
    """Agent模式下有关Agent思考步骤的相关内容，涉及到工具调用（仅Agent模式下使用）

    Attributes:
        event (str): 事件类型，固定为'agent_thought'
        conversation_id (str): 会话ID
        message_id (str): 消息ID
        created_at (int): 创建时间戳
        task_id (str): 任务ID
        id (str): 思考ID
        position (int): 思考位置
        thought (str, optional): 思考内容
        observation (str, optional): 工具返回结果
        tool (str, optional): 使用工具
        tool_labels (dict, optional): 工具标签
        tool_input (str, optional): 工具输入参数
        message_files (list[str], optional): 关联文件ID列表
    """

    event: Literal[ConversationEventType.AGENT_THOUGHT] = Field(
        default=ConversationEventType.AGENT_THOUGHT, description="事件类型"
    )
    conversation_id: str = Field(..., description="会话ID")
    message_id: str = Field(..., description="消息ID")
    created_at: int = Field(..., description="创建时间戳")
    task_id: str = Field(..., description="任务ID")
    id: str = Field(..., description="思考ID")
    position: int = Field(..., description="思考位置")
    thought: Optional[str] = Field(None, description="思考内容")
    observation: Optional[str] = Field(None, description="工具返回结果")
    tool: Optional[str] = Field(None, description="使用工具")
    tool_labels: Optional[dict] = Field(None, description="工具标签")
    tool_input: Optional[str] = Field(None, description="工具输入参数")
    message_files: Optional[List[str]] = Field(None, description="关联文件ID列表")


class MessageFileEvent(BaseModel):
    """消息文件事件Schema

    Attributes:
        event (str): 事件类型，固定为'message_file'
        conversation_id (str): 会话ID
        message_id (str): 消息ID
        created_at (int): 创建时间戳
        task_id (str): 任务ID
        id (str): 文件唯一ID
        type (str): 文件类型，目前仅为image
        belongs_to (str): 文件归属，user或assistant，该接口返回仅为 assistant
        url (str): 文件访问地址
    """

    event: Literal[ConversationEventType.MESSAGE_FILE] = Field(
        default=ConversationEventType.MESSAGE_FILE, description="事件类型"
    )
    conversation_id: str = Field(..., description="会话ID")
    message_id: str = Field(..., description="消息ID")
    created_at: int = Field(..., description="创建时间戳")
    task_id: str = Field(..., description="任务ID")
    id: str = Field(..., description="文件唯一ID")
    type: str = Field(..., description="文件类型，目前仅为image")
    belongs_to: str = Field(
        ..., description="文件归属，user或assistant，该接口返回仅为 assistant"
    )
    url: str = Field(..., description="文件访问地址")


class Usage(BaseModel):
    """使用情况统计Schema

    Attributes:
        prompt_tokens: 提示词消耗的token数量
        prompt_unit_price: 提示词单价
        prompt_price_unit: 提示词价格单位
        prompt_price: 提示词总价
        completion_tokens: 补全消耗的token数量
        completion_unit_price: 补全单价
        completion_price_unit: 补全价格单位
        completion_price: 补全总价
        total_tokens: 总token数量
        total_price: 总价格
        currency: 货币单位
        latency: 请求延迟时间（秒）
    """

    prompt_tokens: Optional[int] = Field(
        default=None, description="提示词消耗的token数量"
    )
    prompt_unit_price: Optional[str] = Field(default=None, description="提示词单价")
    prompt_price_unit: Optional[str] = Field(default=None, description="提示词价格单位")
    prompt_price: Optional[str] = Field(default=None, description="提示词总价")
    completion_tokens: Optional[int] = Field(
        default=None, description="补全消耗的token数量"
    )
    completion_unit_price: Optional[str] = Field(default=None, description="补全单价")
    completion_price_unit: Optional[str] = Field(
        default=None, description="补全价格单位"
    )
    completion_price: Optional[str] = Field(default=None, description="补全总价")
    total_tokens: Optional[int] = Field(default=None, description="总token数量")
    total_price: Optional[str] = Field(default=None, description="总价格")
    currency: Optional[str] = Field(default=None, description="货币单位")
    latency: Optional[float] = Field(default=None, description="请求延迟时间（秒）")


class Metadata(BaseModel):
    """元数据信息Schema

    Attributes:
        usage: 使用情况统计
        retriever_resources: 检索资源列表
    """

    usage: Optional[Usage] = Field(default=None, description="使用情况统计")
    retriever_resources: Optional[List[RetrieverResource]] = Field(
        default_factory=list, description="检索资源列表"
    )


class MessageEndEvent(BaseModel):
    """消息结束事件Schema

    Attributes:
        event (str): 事件类型，固定为'message_end'
        task_id (str): 任务ID，用于请求跟踪和停止响应接口
        message_id (str): 消息唯一ID
        conversation_id (Optional[str]): 会话ID
        created_at (int): 创建时间戳
        id (str): 消息ID
        metadata (dict): 元数据信息，包含usage和retriever_resources
        files (list, optional): 关联文件列表
    """

    event: Literal[ConversationEventType.MESSAGE_END] = Field(
        default=ConversationEventType.MESSAGE_END, description="事件类型"
    )
    task_id: str = Field(..., description="任务ID，用于请求跟踪和停止响应接口")
    message_id: str = Field(..., description="消息唯一ID")
    conversation_id: Optional[str] = Field(None, description="会话ID")
    created_at: int = Field(..., description="创建时间戳")
    id: str = Field(..., description="消息ID")
    metadata: Metadata = Field(
        default_factory=Metadata,
        description="元数据信息，包含usage和retriever_resources",
    )
    files: Optional[List] = Field(None, description="关联文件列表")


class MessageReplaceEvent(BaseModel):
    """消息替换事件Schema

    Attributes:
        event: 事件类型，固定为'message_replace'
        task_id: 任务ID，用于请求跟踪和停止响应接口
        message_id: 消息唯一ID
        conversation_id: 会话ID
        answer: 替换内容（直接替换LLM所有回复文本）
        created_at: 创建时间戳
    """

    event: Literal[ConversationEventType.MESSAGE_REPLACE] = Field(
        default=ConversationEventType.MESSAGE_REPLACE, description="事件类型"
    )
    task_id: str = Field(..., description="任务ID，用于请求跟踪和停止响应接口")
    message_id: str = Field(..., description="消息唯一ID")
    conversation_id: str = Field(..., description="会话ID")
    answer: str = Field(..., description="替换内容（直接替换LLM所有回复文本）")
    created_at: int = Field(..., description="创建时间戳")


class TTSMessageEndEvent(BaseModel):
    """TTS音频流结束事件Schema

    Attributes:
        event: 事件类型，固定为'tts_message_end'
        task_id: 任务ID，用于请求跟踪和停止响应接口
        message_id: 消息唯一ID
        audio: 音频内容（结束事件为空字符串）
        created_at: 创建时间戳
    """

    event: Literal[ConversationEventType.TTS_MESSAGE_END] = Field(
        default=ConversationEventType.TTS_MESSAGE_END, description="事件类型"
    )
    task_id: Optional[str] = Field(
        default=None, description="任务ID，用于请求跟踪和停止响应接口"
    )
    message_id: Optional[str] = Field(default=None, description="消息唯一ID")
    audio: Optional[str] = Field(
        default="", description="音频内容（结束事件为空字符串）"
    )
    created_at: Optional[int] = Field(default=None, description="创建时间戳")


class TTSMessageEvent(BaseModel):
    """TTS音频流事件Schema

    Attributes:
        event: 事件类型，固定为'tts_message'
        task_id: 任务ID，用于请求跟踪和停止响应接口
        message_id: 消息唯一ID
        audio: 语音合成音频块（Base64编码的Mp3格式）
        created_at: 创建时间戳
    """

    event: Literal[ConversationEventType.TTS_MESSAGE] = Field(
        default=ConversationEventType.TTS_MESSAGE, description="事件类型"
    )
    task_id: Optional[str] = Field(
        default=None, description="任务ID，用于请求跟踪和停止响应接口"
    )
    message_id: Optional[str] = Field(default=None, description="消息唯一ID")
    audio: Optional[str] = Field(
        default=None, description="语音合成音频块（Base64编码的Mp3格式）"
    )
    created_at: Optional[int] = Field(default=None, description="创建时间戳")


class WorkflowStartedData(BaseModel):
    """工作流开始事件数据模型

    Attributes:
        id: 工作流执行ID
        workflow_id: 关联工作流ID
        sequence_number: 自增序号，从1开始
        created_at: 开始时间戳
    """

    id: Optional[str] = Field(default=None, description="工作流执行ID")
    workflow_id: Optional[str] = Field(default=None, description="关联工作流ID")
    sequence_number: Optional[int] = Field(
        default=None, description="自增序号，从1开始"
    )
    created_at: Optional[int] = Field(default=None, description="开始时间戳")


class WorkflowStartedEvent(BaseModel):
    """工作流开始事件Schema

    Attributes:
        event: 事件类型，固定为'workflow_started'
        task_id: 任务ID，用于请求跟踪和停止响应接口
        workflow_run_id: workflow执行ID
        data: 详细内容，包含工作流执行信息
    """

    event: Literal[ConversationEventType.WORKFLOW_STARTED] = Field(
        default=ConversationEventType.WORKFLOW_STARTED, description="事件类型"
    )
    task_id: Optional[str] = Field(
        default=None, description="任务ID，用于请求跟踪和停止响应接口"
    )
    workflow_run_id: Optional[str] = Field(default=None, description="workflow执行ID")
    data: Optional[WorkflowStartedData] = Field(
        default=None, description="详细内容，包含工作流执行信息"
    )


class NodeStartedData(BaseModel):
    """节点开始事件数据模型

    Attributes:
        id: workflow 执行 ID
        node_id: 节点 ID
        node_type: 节点类型
        title: 节点名称
        index: 执行序号，用于展示 Tracing Node 顺序
        predecessor_node_id: 前置节点 ID，用于画布展示执行路径
        inputs: 节点中所有使用到的前置节点变量内容
        created_at: 开始时间戳
    """

    id: Optional[str] = Field(default=None, description="workflow 执行 ID")
    node_id: Optional[str] = Field(default=None, description="节点 ID")
    node_type: Optional[str] = Field(default=None, description="节点类型")
    title: Optional[str] = Field(default=None, description="节点名称")
    index: Optional[int] = Field(
        default=None, description="执行序号，用于展示 Tracing Node 顺序"
    )
    predecessor_node_id: Optional[str] = Field(
        default=None, description="前置节点 ID，用于画布展示执行路径"
    )
    inputs: Optional[dict] = Field(
        default_factory=dict, description="节点中所有使用到的前置节点变量内容"
    )
    created_at: Optional[int] = Field(default=None, description="开始时间戳")


class NodeStartedEvent(BaseModel):
    """节点开始事件Schema

    Attributes:
        event: 事件类型，固定为'node_started'
        task_id: 任务ID，用于请求跟踪和停止响应接口
        workflow_run_id: workflow执行ID
        data: 详细内容，包含节点执行信息
    """

    event: Literal[ConversationEventType.NODE_STARTED] = Field(
        default=ConversationEventType.NODE_STARTED, description="事件类型"
    )
    task_id: Optional[str] = Field(
        default=None, description="任务ID，用于请求跟踪和停止响应接口"
    )
    workflow_run_id: Optional[str] = Field(default=None, description="workflow执行ID")
    data: Optional[NodeStartedData] = Field(
        default=None, description="详细内容，包含节点执行信息"
    )


class NodeExecutionMeta(BaseModel):
    """节点执行元数据Schema

    Attributes:
        total_tokens: 总使用tokens数量
        total_price: 总费用
        currency: 货币单位，如USD/RMB
    """

    total_tokens: Optional[int] = Field(default=None, description="总使用tokens数量")
    total_price: Optional[Decimal] = Field(default=None, description="总费用")
    currency: Optional[str] = Field(default=None, description="货币单位，如USD/RMB")


class NodeFinishedData(BaseModel):
    """节点完成数据Schema

    Attributes:
        id: 节点执行ID
        node_id: 节点ID
        index: 执行序号，用于展示Tracing Node顺序
        predecessor_node_id: 前置节点ID，用于画布展示执行路径
        inputs: 节点中所有使用到的前置节点变量内容
        process_data: 节点过程数据
        outputs: 输出内容
        status: 执行状态，包括running/succeeded/failed/stopped
        error: 错误原因
        elapsed_time: 耗时（秒）
        execution_metadata: 元数据
        created_at: 开始时间戳
    """

    id: Optional[str] = Field(default=None, description="节点执行ID")
    node_id: Optional[str] = Field(default=None, description="节点ID")
    index: Optional[int] = Field(
        default=None, description="执行序号，用于展示Tracing Node顺序"
    )
    predecessor_node_id: Optional[str] = Field(
        default=None, description="前置节点ID，用于画布展示执行路径"
    )
    inputs: Optional[dict] = Field(
        default=None, description="节点中所有使用到的前置节点变量内容"
    )
    process_data: Optional[dict] = Field(default=None, description="节点过程数据")
    outputs: Optional[dict] = Field(default=None, description="输出内容")
    status: Optional[str] = Field(
        default=None, description="执行状态，包括running/succeeded/failed/stopped"
    )
    error: Optional[str] = Field(default=None, description="错误原因")
    elapsed_time: Optional[float] = Field(default=None, description="耗时（秒）")
    execution_metadata: Optional[NodeExecutionMeta] = Field(
        default=None, description="元数据"
    )
    created_at: Optional[int] = Field(default=None, description="开始时间戳")


class NodeFinishedEvent(BaseModel):
    """节点完成事件Schema

    Attributes:
        event: 事件类型，固定为'node_finished'
        task_id: 任务ID，用于请求跟踪和停止响应接口
        workflow_run_id: workflow执行ID
        data: 详细内容，包含节点执行信息
    """

    event: Literal[ConversationEventType.NODE_FINISHED] = Field(
        default=ConversationEventType.NODE_FINISHED, description="事件类型"
    )
    task_id: Optional[str] = Field(
        default=None, description="任务ID，用于请求跟踪和停止响应接口"
    )
    workflow_run_id: Optional[str] = Field(default=None, description="workflow执行ID")
    data: Optional[NodeFinishedData] = Field(
        default=None, description="详细内容，包含节点执行信息"
    )


class WorkflowStatus(str, Enum):
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    STOPPED = "stopped"


class WorkflowFinishedData(BaseModel):
    """工作流完成数据Schema

    Attributes:
        id: workflow执行ID
        workflow_id: 关联Workflow ID
        status: 执行状态，包括running/succeeded/failed/stopped
        outputs: 输出内容
        error: 错误原因
        elapsed_time: 耗时（秒）
        total_tokens: 总使用tokens
        total_steps: 总步数
        created_at: 开始时间戳
        finished_at: 结束时间戳
    """

    id: Optional[str] = Field(default=None, description="workflow执行ID")
    workflow_id: Optional[str] = Field(default=None, description="关联Workflow ID")
    status: Optional[WorkflowStatus] = Field(
        default=None, description="执行状态，包括running/succeeded/failed/stopped"
    )
    outputs: Optional[dict] = Field(default=None, description="输出内容")
    error: Optional[str] = Field(default=None, description="错误原因")
    elapsed_time: Optional[float] = Field(default=None, description="耗时（秒）")
    total_tokens: Optional[int] = Field(default=None, description="总使用tokens")
    total_steps: Optional[int] = Field(default=None, description="总步数")
    created_at: Optional[int] = Field(default=None, description="开始时间戳")
    finished_at: Optional[int] = Field(default=None, description="结束时间戳")


class WorkflowFinishedEvent(BaseModel):
    """工作流完成事件Schema

    Attributes:
        event (str): 事件类型，固定为'workflow_finished'
        task_id (str): 任务ID，用于请求跟踪和停止响应接口
        workflow_run_id (str): workflow执行ID
        data (WorkflowFinishedData): 工作流完成数据
    """

    event: Literal[ConversationEventType.WORKFLOW_FINISHED] = Field(
        default=ConversationEventType.WORKFLOW_FINISHED, description="事件类型"
    )
    task_id: Optional[str] = Field(
        default=None, description="任务ID，用于请求跟踪和停止响应接口"
    )
    workflow_run_id: Optional[str] = Field(default=None, description="workflow执行ID")
    data: Optional[WorkflowFinishedData] = Field(
        default=None, description="工作流完成数据"
    )


class TextChunkData(BaseModel):
    """文本片段数据Schema

    Attributes:
        text: 文本内容
        from_variable_selector: 变量选择器来源
    """

    text: Optional[str] = Field(default=None, description="文本内容")
    from_variable_selector: Optional[List[str]] = Field(
        default=None, description="变量选择器来源"
    )


class TextChunkEvent(BaseModel):
    """文本片段事件Schema

    Attributes:
        event (str): 事件类型，固定为'text_chunk'
        task_id (str): 任务ID，用于请求跟踪和停止响应接口
        workflow_run_id (str): workflow执行ID
        data (TextChunkData): 文本片段数据
    """

    event: Literal[ConversationEventType.TEXT_CHUNK] = Field(
        default=ConversationEventType.TEXT_CHUNK, description="事件类型"
    )
    task_id: Optional[str] = Field(
        default=None, description="任务ID，用于请求跟踪和停止响应接口"
    )
    workflow_run_id: Optional[str] = Field(default=None, description="workflow执行ID")
    data: Optional[TextChunkData] = Field(default=None, description="文本片段数据")


# 创建联合类型
ConversationEvent = Annotated[
    Union[
        ChatMessageEvent,
        AgentMessageEvent,
        AgentThoughtEvent,
        MessageFileEvent,
        MessageEndEvent,
        TTSMessageEvent,
        TTSMessageEndEvent,
        MessageReplaceEvent,
        ErrorEvent,
        WorkflowStartedEvent,
        NodeStartedEvent,
        NodeFinishedEvent,
        WorkflowFinishedEvent,
        TextChunkEvent,
    ],
    Field(discriminator="event"),
]


# 示例用法
class EventContainer(BaseModel):
    """
    事件容器，用于处理多种类型的事件

    Attributes:
        events: 事件列表
    """

    events: List[ConversationEvent] = Field(
        default_factory=list, description="事件列表"
    )


class ApiKey(BaseModel):
    """API密钥模型

    Attributes:
        id: API密钥ID
        type: 密钥类型
        token: API令牌
        last_used_at: 最后使用时间戳
        created_at: 创建时间戳
    """

    id: str = Field(description="API密钥ID")
    type: str = Field(description="密钥类型")
    token: str = Field(description="API令牌")
    last_used_at: Optional[int] = Field(default=None, description="最后使用时间戳")
    created_at: Optional[int] = Field(default=None, description="创建时间戳")


class OperationResult(BaseModel):
    """操作结果模型"""

    result: str = Field(default="success", description="操作结果")


class RetrieverResourceConfig(BaseModel):
    """引用和归属配置

    Attributes:
        enabled: 是否开启引用和归属功能
    """

    enabled: bool = Field(default=False, description="是否开启引用和归属功能")


class BaseInput(BaseModel):
    """基础输入控件配置

    Attributes:
        label: 控件展示标签名
        variable: 控件ID
    """

    label: str = Field(description="控件展示标签名")
    variable: str = Field(description="控件ID")
    type: Optional[str] = Field(default=None, description="控件类型")
    max_length: Optional[int] = Field(default=None, description="最大长度")
    required: Optional[bool] = Field(default=None, description="是否必填")


class TextInput(BaseInput):
    pass


class NumberInput(BaseInput):
    pass


class ParagraphInput(BaseInput):
    pass


class SelectInput(BaseInput):
    options: List[str] = Field(default_factory=list, description="选项值列表")


class UserInputItem(BaseModel):
    """用户输入项

    Attributes:
        text_input: 文本输入项
        paragraph_input: 段落输入项
        select_input: 下拉输入项
    """

    text_input: Optional[TextInput] = Field(default=None, alias="text-input")
    number_input: Optional[NumberInput] = Field(default=None, alias="number")
    paragraph: Optional[ParagraphInput] = Field(default=None, alias="paragraph")
    select_input: Optional[SelectInput] = Field(default=None, alias="select-input")


class AppParameters(BaseModel):
    """应用参数模型

    Attributes:
        opening_statement: 开场白
        suggested_questions: 开场推荐问题列表，用于引导用户进行对话
        suggested_questions_after_answer: 回答后推荐问题配置
        speech_to_text: 语音转文本配置
        retriever_resource: 引用和归属配置
        annotation_reply: 标记回复配置
        user_input_form: 用户输入项
        file_upload: 文件上传配置
    """

    opening_statement: str = Field(default="", description="开场白")
    suggested_questions: List[str] = Field(
        default_factory=list, description="开场推荐问题列表，用于引导用户进行对话"
    )
    suggested_questions_after_answer: SuggestedQuestionsAfterAnswer = Field(
        default=SuggestedQuestionsAfterAnswer(), description="回答后推荐问题配置"
    )
    speech_to_text: SpeechToText = Field(
        default=SpeechToText(), description="语音转文本配置"
    )
    retriever_resource: RetrieverResourceConfig = Field(
        default=RetrieverResourceConfig(), description="引用和归属配置"
    )
    annotation_reply: AnnotationReply = Field(
        default=AnnotationReply(), description="标记回复配置"
    )
    user_input_form: List[UserInputItem] = Field(
        default_factory=list, description="用户输入项"
    )
    file_upload: FileUploadConfig = Field(
        default=FileUploadConfig(), description="文件上传配置"
    )
