import time
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from funtts.models import VoiceInfo, TTSRequest, TTSResponse, SubtitleMaker
from funutil import getLogger


logger = getLogger("funtts")


class BaseTTS(ABC):
    # ==================== 类变量 ====================
    supported_formats: List[str] = ["wav"]  # 子类可以重写
    supports_subtitles: bool = True  # 子类可以重写

    def __init__(self, *args, **kwargs):
        """初始化TTS基类

        子类可以根据需要重写此方法来处理特定的初始化参数
        """
        pass

    # ==================== 核心抽象方法 ====================

    @abstractmethod
    def _synthesize(self, request: TTSRequest) -> TTSResponse:
        """语音合成核心方法，子类必须实现（内部方法）

        这是纯粹的合成逻辑，子类只需要实现核心功能。
        返回的TTSResponse对象必须设置以下字段：
        - success: bool - 是否成功
        - audio_file: Optional[str] - 音频文件路径
        - error_message: Optional[str] - 错误信息（失败时）
        - error_code: Optional[str] - 错误代码（失败时）

        可选字段：
        - subtitle_maker: Optional[SubtitleMaker] - 字幕生成器
        - duration: float - 音频时长
        - voice_used: str - 实际使用的语音名称
        - processing_time: float - 处理时间（会被外层重新设置）
        - engine_info: Dict[str, Any] - 引擎信息（会被外层重新设置）

        Args:
            request: TTS请求对象

        Returns:
            TTS响应对象
        """
        raise NotImplementedError("子类必须实现_synthesize方法")

    @abstractmethod
    def list_voices(self, language: Optional[str] = None) -> List[VoiceInfo]:
        """获取可用语音列表，子类必须实现

        Args:
            language: 可选的语言过滤条件（如: "zh-CN", "en-US"）

        Returns:
            VoiceInfo对象列表
        """
        raise NotImplementedError("子类必须实现list_voices方法")

    # ==================== 工具方法 ====================

    def get_default_voice(self) -> Optional[str]:
        """获取默认语音名称

        默认实现返回语音列表的第一个，子类可以重写此方法自定义默认语音

        Returns:
            默认语音名称，如果没有可用语音则返回None
        """
        try:
            voices = self.list_voices()
            return voices[0].name if voices else None
        except Exception as e:
            logger.error(f"获取默认语音失败: {str(e)}")
            return None

    # ==================== 公共方法 ====================

    # ==================== 可重写的方法 ====================

    def get_engine_info(self) -> Dict[str, Any]:
        """获取引擎信息"""
        return {
            "engine_name": self.__class__.__name__,
            "default_voice": self.get_default_voice(),
            "supported_formats": self.supported_formats,
            "supports_subtitles": self.supports_subtitles,
        }

    # ==================== 便捷方法 ====================

    def find_voice(self, **criteria) -> Optional[VoiceInfo]:
        """按条件查找语音

        Args:
            **criteria: 查找条件

        Returns:
            匹配的语音信息
        """
        try:
            voices = self.list_voices()
            for voice in voices:
                if voice.matches(**criteria):
                    return voice
            return None
        except Exception as e:
            logger.error(f"查找语音失败: {str(e)}")
            return None

    def is_voice_available(self, voice_name: str) -> bool:
        """检查语音是否可用

        Args:
            voice_name: 语音名称

        Returns:
            是否可用
        """
        try:
            voices = self.list_voices()
            return any(voice.name == voice_name for voice in voices)
        except Exception as e:
            logger.error(f"检查语音可用性失败: {str(e)}")
            return False

    # ==================== 流式接口（预留） ====================

    def synthesize_stream(self, request: TTSRequest):
        """流式语音合成接口（预留，暂不实现）

        未来实现时将调用_synthesize方法进行流式处理
        """
        raise NotImplementedError("流式接口暂未实现")

    # ==================== 对外接口方法 ====================
    def synthesize(self, request: TTSRequest) -> TTSResponse:
        """处理TTS请求的主入口方法（对外接口）

        这是完整的请求处理流程，包括：
        1. 参数验证
        2. 调用核心合成方法(_synthesize)
        3. 设置公共信息（processing_time, engine_info等）
        4. 处理输出文件保存
        5. 处理字幕文件生成
        6. 异常处理和错误响应

        Args:
            request: TTS请求对象

        Returns:
            完整的TTS响应对象
        """
        start_time = time.time()

        try:
            # 验证请求
            if not request.validate():
                return TTSResponse(
                    success=False,
                    request=request,
                    error_message="请求参数验证失败",
                    error_code="INVALID_REQUEST",
                    processing_time=time.time() - start_time,
                )

            # 调用子类实现的核心合成方法
            response = self._synthesize(request)

            # 设置公共信息
            response.request = request
            response.processing_time = time.time() - start_time
            response.engine_info.update(self.get_engine_info())

            # 处理输出文件
            if response.success and request.output_file and response.audio_file:
                if response.audio_file != request.output_file:
                    # 复制文件到指定位置
                    import shutil

                    shutil.copy2(response.audio_file, request.output_file)
                    response.audio_file = request.output_file

            # 处理字幕文件
            if (
                response.success
                and request.generate_subtitles
                and response.subtitle_maker
                and response.audio_file
            ):
                # 使用SubtitleMaker的统一文件命名策略
                # 1. 保存FRT格式（完整数据）
                frt_file = SubtitleMaker.generate_subtitle_filename(
                    response.audio_file, "frt"
                )
                response.subtitle_maker.save_to_file(frt_file, "frt")
                response.frt_subtitle_file = frt_file
                logger.success(f"FRT字幕文件已保存: {frt_file}")

                # 2. 保存标准格式（兼容性）
                standard_file = SubtitleMaker.generate_subtitle_filename(
                    response.audio_file, request.subtitle_format
                )
                response.subtitle_maker.save_to_file(
                    standard_file, request.subtitle_format
                )
                response.subtitle_file = standard_file
                logger.success(
                    f"{request.subtitle_format.upper()}字幕文件已保存: {standard_file}"
                )

                logger.success(
                    f"字幕文件生成完成: FRT格式({frt_file}) + {request.subtitle_format.upper()}格式({standard_file})"
                )

            return response

        except Exception as e:
            logger.error(f"TTS处理失败: {str(e)}")
            return TTSResponse(
                success=False,
                request=request,
                error_message=str(e),
                error_code="PROCESSING_ERROR",
                processing_time=time.time() - start_time,
                engine_info=self.get_engine_info(),
            )

    def synthesize_text(
        self,
        text: str,
        voice_name: Optional[str] = None,
        output_file: Optional[str] = None,
        **kwargs,
    ) -> TTSResponse:
        """文本语音合成的便捷方法

        Args:
            text: 要转换的文本
            voice_name: 语音名称
            output_file: 输出文件路径
            **kwargs: 其他参数

        Returns:
            TTS响应对象
        """
        # 使用默认语音如果没有指定
        if voice_name is None:
            voice_name = self.get_default_voice()

        # 创建请求对象
        request = TTSRequest(
            text=text, voice_name=voice_name, output_file=output_file, **kwargs
        )
        return self.synthesize(request)
