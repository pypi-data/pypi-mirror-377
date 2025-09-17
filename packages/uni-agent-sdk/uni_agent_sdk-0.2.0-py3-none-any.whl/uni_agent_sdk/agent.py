"""Agent基类 - 智能体开发框架核心抽象

基于ultra-analysis深度分析结果设计的革命性智能体基类。
将400+行基础设施代码简化为3行业务逻辑。

设计原则：
- KISS: 极致简洁的开发体验
- SOLID: 科学的架构设计原则
- DRY: 统一的基础设施管理
- YAGNI: 专注当前需求实现
"""

import asyncio
import logging
import signal
import sys
from abc import ABC, abstractmethod
from typing import Optional, Any, Dict

from .models.message import Message, Response
from .services.platform import PlatformAPI
from .services.llm import LLMService
from .services.file import FileService
from .utils.config import Config
from .utils.logger import get_logger, AgentLogger
from .core.message_broker import MessageBroker
from .core.context import MessageContext
from .core.lifecycle import LifecycleManager


class Agent(ABC):
    """智能体基类

    提供极简的智能体开发体验：

    示例：
        from uni_agent_sdk import Agent, Response

        class MyAgent(Agent):
            async def handle_message(self, message, context):
                return Response.text("你好！")

        MyAgent("api_key", "api_secret").run()
    """

    def __init__(self, api_key: str, api_secret: str, **config_kwargs):
        """初始化智能体

        Args:
            api_key: 智能体API密钥
            api_secret: 智能体API秘钥
            **config_kwargs: 额外配置参数
        """
        self.api_key = api_key
        self.api_secret = api_secret

        # 初始化配置
        self.config = Config(**config_kwargs)

        # 使用新的日志模块 - 为每个智能体类创建专用日志器
        self.logger = get_logger(f"{self.__class__.__name__}-{api_key[:8]}")

        # 初始化状态
        self._running = False
        self._robot_info = None

        # 认证信息（通过register_robot获取）
        self._developer_userid = None
        self._jwt_token = None
        self._token_expires_at = None
        self._rabbitmq_config = None

        # 延迟加载的服务（依赖注入）
        self._platform: Optional[PlatformAPI] = None
        self._llm: Optional[LLMService] = None
        self._files: Optional[FileService] = None
        self._message_broker: Optional[MessageBroker] = None
        self._lifecycle: Optional[LifecycleManager] = None

    # === 服务依赖注入（延迟加载） ===

    @property
    def platform(self) -> PlatformAPI:
        """平台API服务"""
        if self._platform is None:
            self._platform = PlatformAPI(self.api_key, self.api_secret, self.config)
            # 如果已有认证信息，立即设置
            if self._developer_userid and self._jwt_token:
                self._platform.set_auth_info(self._developer_userid, self._jwt_token)
        return self._platform

    @property
    def llm(self) -> LLMService:
        """LLM推理服务"""
        if self._llm is None:
            self._llm = LLMService(self.config)
        return self._llm

    @property
    def files(self) -> FileService:
        """文件处理服务"""
        if self._files is None:
            self._files = FileService(self.config)
        return self._files

    @property
    def message_broker(self) -> MessageBroker:
        """消息代理服务"""
        if self._message_broker is None:
            self._message_broker = MessageBroker(
                self.api_key,
                self.api_secret,
                self.config,
                self._on_message_received
            )
        return self._message_broker

    @property
    def lifecycle(self) -> LifecycleManager:
        """生命周期管理器"""
        if self._lifecycle is None:
            self._lifecycle = LifecycleManager(self)
        return self._lifecycle

    # === 核心抽象方法 ===

    @abstractmethod
    async def handle_message(self, message: Message, context: MessageContext) -> Optional[Response]:
        """处理接收到的消息（子类必须实现）

        Args:
            message: 接收到的消息对象
            context: 消息上下文（包含用户信息、会话状态等）

        Returns:
            响应对象，None表示不响应
        """
        pass

    # === 生命周期钩子（可选覆盖） ===

    async def on_startup(self):
        """启动钩子 - 智能体启动完成后调用"""
        self.logger.info(f"🚀 智能体 {self.api_key[:8]} 启动完成")

    async def on_shutdown(self):
        """关闭钩子 - 智能体停止前调用"""
        self.logger.info(f"📴 智能体 {self.api_key[:8]} 正在停止")

    async def on_error(self, error: Exception, context: Optional[MessageContext] = None):
        """错误处理钩子 - 发生异常时调用"""
        self.logger.error(f"❌ 智能体错误: {error}")
        if context:
            self.logger.error(f"   上下文: {context.conversation_id}")

    # === 内部消息处理机制 ===

    async def _on_message_received(self, raw_message: Dict[str, Any]):
        """内部消息接收处理器"""
        try:
            # 添加调试信息
            self.logger.debug(f"🔍 原始消息: {raw_message}")

            # 解析消息
            message = Message.from_dict(raw_message)

            self.logger.debug(f"📝 解析后消息: id={message.id}, conversation_id={message.conversation_id}, from_uid={message.from_uid}")

            # 创建上下文
            context = await MessageContext.create(
                message=message,
                platform_api=self.platform,
                config=self.config
            )

            self.logger.info(f"📩 收到消息: {message.content[:50]}...")
            self.logger.debug(f"   发送者: {context.user_nickname}")
            self.logger.debug(f"   会话: {message.conversation_id}")

            # 调用用户处理逻辑
            response = await self.handle_message(message, context)

            # 发送响应
            if response is not None:
                await self.platform.send_response(
                    conversation_id=message.conversation_id,
                    response=response,
                    to_uid=message.from_uid
                )
                self.logger.info(f"✅ 响应已发送: {response.content[:50]}...")
            else:
                self.logger.debug("⏭️ 无需响应")

        except Exception as e:
            await self.on_error(e, context if 'context' in locals() else None)

    # === 智能体运行控制 ===

    def run(self):
        """启动智能体（阻塞运行）

        这是主要的入口方法，设置信号处理并启动异步事件循环。
        """
        try:
            # 设置信号处理
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)

            self.logger.info(f"🎯 启动智能体 {self.api_key[:8]}")
            self.logger.info("=" * 60)

            # 启动异步事件循环
            asyncio.run(self._run_async())

        except KeyboardInterrupt:
            self.logger.info("👋 用户手动停止")
        except Exception as e:
            self.logger.error(f"❌ 智能体运行错误: {e}")
        finally:
            self.logger.info("🏁 智能体已停止")

    async def _run_async(self):
        """异步运行逻辑"""
        try:
            self._running = True

            # 启动生命周期管理
            await self.lifecycle.startup()

            # 第一步：注册机器人并获取完整认证信息
            self.logger.info("🔐 执行机器人注册和认证...")
            registration_result = await self.platform.register_robot()
            if registration_result.get('errCode') != 0:
                raise Exception(f"机器人注册失败: {registration_result.get('errMsg')}")

            # 保存注册信息
            reg_data = registration_result['data']
            self._developer_userid = reg_data.get('developer_userid')
            self._jwt_token = reg_data.get('jwt_token')
            self._token_expires_at = reg_data.get('token_expires_at')
            self._rabbitmq_config = reg_data.get('rabbitmq_config')

            # 更新PlatformAPI的认证信息
            self.platform.set_auth_info(self._developer_userid, self._jwt_token)

            # 如果注册直接返回了robot_info，使用它；否则调用get_robot_info
            if 'robot_info' in reg_data:
                self._robot_info = reg_data['robot_info']
                self.logger.info("🎉 机器人注册成功！")
                self.logger.info(f"👤 开发者ID: {self._developer_userid}")
                self.logger.info(f"🤖 智能体: {self._robot_info.get('name', 'Unknown')}")
                self.logger.info(f"🔑 JWT令牌已获取")
            else:
                # 第二步：使用JWT令牌获取详细的机器人信息（如果需要）
                self.logger.info("🔍 获取详细机器人信息...")
                robot_info = await self.platform.get_robot_info()
                if robot_info.get('errCode') != 0:
                    raise Exception(f"获取智能体信息失败: {robot_info.get('errMsg')}")

                self._robot_info = robot_info['data']
                self.logger.info(f"🤖 智能体: {self._robot_info.get('name', 'Unknown')}")

            # 启动消息代理
            await self.message_broker.start()

            # 调用用户启动钩子
            await self.on_startup()

            # 保持运行
            while self._running:
                await asyncio.sleep(1)

        except Exception as e:
            await self.on_error(e)
            raise
        finally:
            await self._cleanup()

    async def _cleanup(self):
        """清理资源"""
        try:
            # 调用用户关闭钩子
            await self.on_shutdown()

            # 停止消息代理
            if self._message_broker:
                await self.message_broker.stop()

            # 关闭服务连接
            if self._platform:
                await self.platform.close()

            # 停止生命周期管理
            if self._lifecycle:
                await self.lifecycle.shutdown()

        except Exception as e:
            self.logger.error(f"清理资源时出错: {e}")

    def _signal_handler(self, signum, frame):
        """信号处理器"""
        self.logger.info(f"收到信号 {signum}")
        self.stop()

    def stop(self):
        """停止智能体"""
        self._running = False
        self.logger.info("⏹️ 收到停止信号")

    # === 便捷方法 ===

    def is_running(self) -> bool:
        """检查智能体是否运行中"""
        return self._running

    def get_robot_info(self) -> Optional[Dict[str, Any]]:
        """获取智能体信息"""
        return self._robot_info

    def __repr__(self) -> str:
        """字符串表示"""
        status = "运行中" if self._running else "已停止"
        return f"Agent({self.api_key[:8]}..., {status})"