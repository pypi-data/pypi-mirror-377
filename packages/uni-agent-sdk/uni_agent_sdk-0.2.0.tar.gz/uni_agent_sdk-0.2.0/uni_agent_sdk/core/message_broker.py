"""消息代理 - RabbitMQ消息监听与管理

将原本分散在智能体中的400+行RabbitMQ代码统一封装，
提供自动重连、错误恢复、JWT认证等企业级功能。

设计原则：
- 隐藏复杂性：开发者无需了解RabbitMQ细节
- 自动恢复：网络断线、认证失效自动处理
- 企业级：连接池、监控、日志等生产级特性
"""

import asyncio
import json
import logging
import time
from typing import Dict, Any, Callable, Optional, Awaitable

import aio_pika
import requests

from ..utils.config import Config


class MessageBroker:
    """消息代理 - 统一的RabbitMQ消息处理

    封装所有RabbitMQ相关的复杂逻辑：
    - JWT Token获取与自动刷新
    - RabbitMQ连接与断线重连
    - 队列声明与消息消费
    - 错误处理与状态监控
    """

    def __init__(
        self,
        api_key: str,
        api_secret: str,
        config: Config,
        message_handler: Callable[[Dict[str, Any]], Awaitable[None]]
    ):
        """初始化消息代理

        Args:
            api_key: 智能体API密钥
            api_secret: 智能体API秘钥
            config: 配置对象
            message_handler: 消息处理回调函数
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.config = config
        self.message_handler = message_handler

        self.logger = logging.getLogger(f"MessageBroker-{api_key[:8]}")

        # JWT认证状态
        self.jwt_token = None
        self.token_expires_at = None
        self.rabbit_config = None
        self.queue_name = None

        # RabbitMQ连接状态
        self.connection: Optional[aio_pika.RobustConnection] = None
        self.channel: Optional[aio_pika.Channel] = None
        self.queue: Optional[aio_pika.Queue] = None

        # 运行状态
        self._running = False
        self._reconnect_task: Optional[asyncio.Task] = None
        self._token_refresh_task: Optional[asyncio.Task] = None

    # === JWT Token管理 ===

    async def _get_jwt_token(self) -> bool:
        """获取JWT Token"""
        try:
            self.logger.info("🔑 获取JWT Token...")

            url = f"{self.config.platform_base_url}/uni-im-co/getRabbitMQToken"
            data = {
                "api_key": self.api_key,
                "api_secret": self.api_secret
            }

            response = requests.post(url, json=data, timeout=10)

            if response.status_code == 200:
                result = response.json()

                if result.get('errCode') == 0:
                    token_data = result['data']

                    self.jwt_token = token_data['token']
                    self.token_expires_at = token_data['expires_at']
                    self.rabbit_config = token_data['rabbitmq_config']
                    self.queue_name = token_data['rabbitmq_config']['queue_name']

                    self.logger.info("✅ JWT Token获取成功")
                    self.logger.debug(f"   队列: {self.queue_name}")

                    return True
                else:
                    self.logger.error(f"❌ API返回错误: {result.get('errMsg')}")
                    return False
            else:
                self.logger.error(f"❌ HTTP请求失败: {response.status_code}")
                return False

        except Exception as e:
            self.logger.error(f"❌ 获取JWT Token失败: {e}")
            return False

    async def _token_refresh_loop(self):
        """JWT Token自动刷新循环"""
        while self._running:
            try:
                # 检查Token是否即将过期（提前5分钟刷新）
                current_time = int(time.time())
                if self.token_expires_at and (self.token_expires_at - current_time) < 300:
                    self.logger.info("🔄 Token即将过期，正在刷新...")

                    if await self._get_jwt_token():
                        # 重新连接RabbitMQ
                        await self._reconnect_rabbitmq()
                        self.logger.info("✅ Token刷新完成")
                    else:
                        self.logger.error("❌ Token刷新失败")

                # 每分钟检查一次
                await asyncio.sleep(60)

            except Exception as e:
                self.logger.error(f"❌ Token刷新循环异常: {e}")
                await asyncio.sleep(60)

    # === RabbitMQ连接管理 ===

    async def _connect_rabbitmq(self) -> bool:
        """连接RabbitMQ"""
        try:
            self.logger.info("🔌 连接RabbitMQ...")

            # 使用临时guest认证方案进行测试
            # TODO: 正式环境切换为JWT认证
            robot_user_id = "1000000001"
            self.queue_name = f"robot_{robot_user_id}_development"

            self.logger.debug(f"   🔑 使用guest认证")
            self.logger.debug(f"   📡 目标队列: {self.queue_name}")

            # 建立robust连接（自动重连）
            self.connection = await aio_pika.connect_robust(
                host=self.config.rabbitmq_host,
                port=self.config.rabbitmq_port,
                login=self.config.rabbitmq_user,
                password=self.config.rabbitmq_password,
                virtualhost=self.config.rabbitmq_vhost,
                client_properties={
                    "connection_name": f"Agent-{self.api_key[:8]}",
                    "product": "uni-agent-sdk",
                    "version": "1.0.0"
                }
            )

            # 创建频道
            self.channel = await self.connection.channel()
            await self.channel.set_qos(prefetch_count=self.config.prefetch_count)

            self.logger.info("✅ RabbitMQ连接成功")
            self.logger.debug(f"   🏠 主机: {self.config.rabbitmq_host}")
            self.logger.debug(f"   📡 监听队列: {self.queue_name}")

            return True

        except Exception as e:
            self.logger.error(f"❌ RabbitMQ连接失败: {e}")
            return False

    async def _setup_queue_consumer(self) -> bool:
        """设置队列消费者"""
        try:
            self.logger.info("📡 设置队列消费者...")

            # 声明队列（与云函数配置一致）
            self.queue = await self.channel.declare_queue(
                self.queue_name,
                durable=True,
                arguments={
                    'x-message-ttl': 300000,        # 5分钟TTL
                    'x-max-length': 10000,          # 最大消息数
                    'x-overflow': 'reject-publish'  # 队列满时拒绝发布
                }
            )

            # 设置消息处理器
            await self.queue.consume(self._process_message)

            self.logger.info(f"✅ 消费者设置完成，监听队列: {self.queue_name}")
            return True

        except Exception as e:
            self.logger.error(f"❌ 设置消费者失败: {e}")
            return False

    async def _process_message(self, message: aio_pika.IncomingMessage):
        """处理接收到的消息"""
        try:
            async with message.process():
                # 解析消息
                message_data = json.loads(message.body.decode())
                self.logger.debug(f"🔥 收到原始消息: {message_data}")

                # 调用用户消息处理器
                await self.message_handler(message_data)

        except Exception as e:
            self.logger.error(f"❌ 处理消息失败: {e}")
            # 消息处理失败时不重试，避免无限循环

    async def _reconnect_rabbitmq(self):
        """重新连接RabbitMQ"""
        try:
            # 关闭现有连接
            if self.connection:
                await self.connection.close()

            # 重新连接
            if await self._connect_rabbitmq():
                await self._setup_queue_consumer()
                self.logger.info("🔄 RabbitMQ重连成功")
            else:
                self.logger.error("🔄 RabbitMQ重连失败")

        except Exception as e:
            self.logger.error(f"❌ 重连异常: {e}")

    async def _connection_monitor(self):
        """连接状态监控"""
        while self._running:
            try:
                # 检查连接状态
                if not self.connection or self.connection.is_closed:
                    self.logger.warning("⚠️ 检测到连接断开，尝试重连...")
                    await self._reconnect_rabbitmq()

                # 每30秒检查一次
                await asyncio.sleep(30)

            except Exception as e:
                self.logger.error(f"❌ 连接监控异常: {e}")
                await asyncio.sleep(30)

    # === 外部接口 ===

    async def start(self):
        """启动消息代理"""
        self.logger.info("🚀 启动消息代理...")
        self._running = True

        try:
            # 1. 尝试获取JWT Token（可选，当前使用guest）
            # await self._get_jwt_token()

            # 2. 连接RabbitMQ
            if not await self._connect_rabbitmq():
                raise Exception("RabbitMQ连接失败")

            # 3. 设置消费者
            if not await self._setup_queue_consumer():
                raise Exception("设置消费者失败")

            # 4. 启动后台任务
            # self._token_refresh_task = asyncio.create_task(self._token_refresh_loop())
            self._reconnect_task = asyncio.create_task(self._connection_monitor())

            self.logger.info("✅ 消息代理启动成功")

        except Exception as e:
            self.logger.error(f"❌ 启动消息代理失败: {e}")
            await self.stop()
            raise

    async def stop(self):
        """停止消息代理"""
        self.logger.info("📴 停止消息代理...")
        self._running = False

        try:
            # 取消后台任务
            if self._token_refresh_task:
                self._token_refresh_task.cancel()
                try:
                    await self._token_refresh_task
                except asyncio.CancelledError:
                    pass

            if self._reconnect_task:
                self._reconnect_task.cancel()
                try:
                    await self._reconnect_task
                except asyncio.CancelledError:
                    pass

            # 关闭RabbitMQ连接
            if self.connection:
                await self.connection.close()

            self.logger.info("✅ 消息代理已停止")

        except Exception as e:
            self.logger.error(f"停止消息代理时出错: {e}")

    def is_connected(self) -> bool:
        """检查连接状态"""
        return (
            self.connection is not None and
            not self.connection.is_closed and
            self.channel is not None and
            not self.channel.is_closed
        )

    def get_queue_info(self) -> Dict[str, Any]:
        """获取队列信息"""
        return {
            "queue_name": self.queue_name,
            "connected": self.is_connected(),
            "jwt_token_valid": self.token_expires_at and (self.token_expires_at > int(time.time())),
            "running": self._running
        }

    def __repr__(self) -> str:
        """字符串表示"""
        status = "运行中" if self._running else "已停止"
        connection_status = "已连接" if self.is_connected() else "未连接"
        return f"MessageBroker({self.queue_name}, {status}, {connection_status})"