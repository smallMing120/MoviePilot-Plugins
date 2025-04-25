import re
import requests
import time
from datetime import datetime
from typing import Any, List, Dict, Tuple, Optional

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from app.plugins import _PluginBase
from app.log import logger
from app.scheduler import Scheduler
from app.schemas import NotificationType
from app.utils.http import RequestUtils

class ZmMedal(_PluginBase):
    # 插件名称
    plugin_name = "织梦勋章购买提醒"
    # 插件描述
    plugin_desc = "织梦勋章购买提醒"
    # 插件图标
    plugin_icon = "https://raw.githubusercontent.com/smallMing120/MoviePilot-Plugins/main/icons/zm.png"
    # 插件版本
    plugin_version = "1.0.0"
    # 插件作者
    plugin_author = "smallMing"
    # 作者主页
    author_url = "https://github.com/smallMing120/MoviePilot-Plugins"
    # 插件配置项ID前缀
    plugin_config_prefix = "zmmedal_"
    # 加载顺序
    plugin_order = 24
    # 可使用的用户级别
    auth_level = 2

    # 私有属性
    _enabled: bool = False
    # 任务执行间隔
    _cron: Optional[str] = None
    _cookie: Optional[str] = None
    _onlyonce: bool = False
    _notify: bool = False

    # 定时器
    _scheduler: Optional[BackgroundScheduler] = None

    def init_plugin(self, config: Optional[dict] = None) -> None:
        """
                初始化插件
                """
        # 停止现有任务
        self.stop_service()
        if config:
            self._enabled = config.get("enabled", False)
            self._cron = config.get("cron")
            self._cookie = config.get("cookie")
            self._notify = config.get("notify", False)
            self._onlyonce = config.get("onlyonce", False)

        if self._onlyonce:
            try:
                logger.info("织梦勋章购买提醒，立即运行一次")
                # 关闭一次性开关
                self._onlyonce = False
                self.update_config({
                    "onlyonce": False,
                    "cron": self._cron,
                    "enabled": self._enabled,
                    "cookie": self._cookie,
                    "notify": self._notify,
                })
                # 启动任务
                self.__start()
            except Exception as e:
                logger.error(f"织梦勋章购买提醒服务启动失败: {str(e)}")

    def get_state(self) ->bool:
        return bool(self._enabled)

    @staticmethod
    def get_command() -> List[Dict[str, Any]]:
        """获取命令"""
        pass

    def get_api(self) -> List[Dict[str, Any]]:
        """获取API"""
        pass

    def get_service(self) -> List[Dict[str, Any]]:
        """
            注册插件公共服务
        """
        if self._enabled and self._cron:
            return [
                {
                    "id": "ZmMedal",
                    "name": "织梦勋章购买提醒",
                    "trigger": CronTrigger.from_crontab(self._cron),
                    "func": self.__start(),
                    "kwargs": {}
                }
            ]
        return []


    def get_form(self) -> Tuple[List[dict], Dict[str, Any]]:
        """
            拼装插件配置页面，需要返回两块数据：1、页面配置；2、数据结构
        """
        return [
            {
                'component': 'VForm',
                'content': [
                    {
                        'component': 'VCard',
                        'props': {
                            'variant': 'outlined',
                            'class': 'mt-0'
                        },
                        'content': [
                            {
                                'component': 'VCardTitle',
                                'props': {
                                    'class': 'd-flex align-center'
                                },
                                'content': [
                                    {
                                        'component': 'VIcon',
                                        'props': {
                                            'style': 'color: #1976D2;',
                                            'class': 'mr-2'
                                        },
                                        'text': 'mdi-cog'
                                    },
                                    {
                                        'component': 'span',
                                        'text': '基本设置'
                                    }
                                ]
                            },
                            {
                                'component': 'VDivider'
                            },
                            {
                                'component': 'VCardText',
                                'content': [
                                    {
                                        'component': 'VRow',
                                        'content': [
                                            {
                                                'component': 'VCol',
                                                'props': {
                                                    'cols': 12,
                                                    'md': 4
                                                },
                                                'content': [
                                                    {
                                                        'component': 'VSwitch',
                                                        'props': {
                                                            'model': 'enabled',
                                                            'label': '启用插件',
                                                        }
                                                    }
                                                ]
                                            },
                                            {
                                                'component': 'VCol',
                                                'props': {
                                                    'cols': 12,
                                                    'md': 4
                                                },
                                                'content': [
                                                    {
                                                        'component': 'VSwitch',
                                                        'props': {
                                                            'model': 'notify',
                                                            'label': '开启通知',
                                                        }
                                                    }
                                                ]
                                            },
                                            {
                                                'component': 'VCol',
                                                'props': {
                                                    'cols': 12,
                                                    'md': 4
                                                },
                                                'content': [
                                                    {
                                                        'component': 'VSwitch',
                                                        'props': {
                                                            'model': 'onlyonce',
                                                            'label': '立即运行一次',
                                                        }
                                                    }
                                                ]
                                            }
                                        ]
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        'component': 'VCard',
                        'props': {
                            'variant': 'outlined',
                            'class': 'mt-3'
                        },
                        'content': [
                            {
                                'component': 'VCardTitle',
                                'props': {
                                    'class': 'd-flex align-center'
                                },
                                'content': [
                                    {
                                        'component': 'VIcon',
                                        'props': {
                                            'style': 'color: #1976D2;',
                                            'class': 'mr-2'
                                        },
                                        'text': 'mdi-cog-sync'
                                    },
                                    {
                                        'component': 'span',
                                        'text': 'cookie设置'
                                    }
                                ]
                            },
                            {
                                'component': 'VDivider'
                            },
                            {
                                'component': 'VCardText',
                                'content': [
                                    {
                                        'component': 'VRow',
                                        'content': [
                                            {
                                                'component': 'VCol',
                                                'props': {
                                                    'cols': 12,
                                                    'md': 12
                                                },
                                                'content': [
                                                    {
                                                        'component': 'VTextField',
                                                        'props': {
                                                            'model': 'cookie',
                                                            'label': '站点cookie',
                                                            'hint': '用于登录站点的cookie信息'
                                                        }
                                                    }
                                                ]
                                            }
                                        ]
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        'component': 'VCard',
                        'props': {
                            'variant': 'outlined',
                            'class': 'mt-3'
                        },
                        'content': [
                            {
                                'component': 'VCardTitle',
                                'props': {
                                    'class': 'd-flex align-center'
                                },
                                'content': [
                                    {
                                        'component': 'VIcon',
                                        'props': {
                                            'style': 'color: #1976D2;',
                                            'class': 'mr-2'
                                        },
                                        'text': 'mdi-clock-outline'
                                    },
                                    {
                                        'component': 'span',
                                        'text': '定时设置'
                                    }
                                ]
                            },
                            {
                                'component': 'VDivider'
                            },
                            {
                                'component': 'VCardText',
                                'content': [
                                    {
                                        'component': 'VRow',
                                        'content': [
                                            {
                                                'component': 'VCol',
                                                'props': {
                                                    'cols': 12,
                                                    'md': 6
                                                },
                                                'content': [
                                                    {
                                                        'component': 'VTextField',
                                                        'props': {
                                                            'model': 'cron',
                                                            'label': '签到周期',
                                                            'hint': '5位cron表达式，默认每天9点执行'
                                                        }
                                                    }
                                                ]
                                            }
                                        ]
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        ],{
            "enabled": False,
            "onlyonce": False,
            "notify": False,
            "cookie": "",
            "cron": "0 9 * * *",
        }

    def get_page(self) -> List[dict]:
        pass

    def stop_service(self) -> None:
        try:
            if self._scheduler:
                self._scheduler.remove_all_jobs()
                if self._scheduler.running:
                    self._scheduler.shutdown()
                self._scheduler = None
        except Exception as e:
            logger.error("退出插件失败：%s" % str(e))

    def __start(self):
        """
            执行请求任务
        """
        logger.info("织梦勋章购买提醒，开始执行")
        try:
            unhasMedal = []

            res = RequestUtils(cookies=self._cookie).get_res(url="https://zmpt.cc/javaapi/user/queryAllMedals")
            if not res or res.status_code != 200:
                logger.error("请求首页失败！状态码：%s", res.status_code if res else "无响应")
                return
            data = res.json().get('result',{})
            medalGroups = data.get('medalGroups')
            medals = data.get('medals')
            for medal in medals:
                hasMedal = medal.get('hasMedal')
                imageSmall = medal.get('imageSmall')
                price = medal.get('price')
                name = medal.get('name')
                logger.info(f"开始检查：{name}勋章....")
                if hasMedal:
                    #已拥有勋章跳过
                    logger.info(f"{name}:已拥有,跳过...")
                    continue

                saleBeginTime = medal.get('saleBeginTime')
                saleEndTime = medal.get('saleEndTime')

                if self.is_current_time_in_range(saleBeginTime,saleEndTime):
                    unhasMedal.append({
                        'name':name,
                        'imageSmall':imageSmall,
                        'saleBeginTime':saleBeginTime,
                        'saleEndTime':saleEndTime,
                        'price':price
                    })
                else:
                    logger.info(f"{name}:未到开售时间...")

            for medalGroup in medalGroups:
                medalList = medalGroup.get('medalList')
                for medal in medalList:
                    hasMedal = medal.get('hasMedal')
                    price = medal.get('price')
                    name = medal.get('name')
                    imageSmall = medal.get('imageSmall')
                    logger.info(f"开始检查：{name}勋章....")
                    if hasMedal:
                        # 已拥有勋章跳过
                        logger.info(f"{name}:已拥有,跳过...")
                        continue

                    saleBeginTime = medal.get('saleBeginTime')
                    saleEndTime = medal.get('saleEndTime')

                    if self.is_current_time_in_range(saleBeginTime, saleEndTime):
                        unhasMedal.append({
                            'name': name,
                            'imageSmall': imageSmall,
                            'saleBeginTime': saleBeginTime,
                            'saleEndTime': saleEndTime,
                            'price': price
                        })
                    else:
                        logger.info(f"{name}:未到开售时间...")

            if self._notify and unhasMedal:
                # 发送通知
                text_message = "织梦勋章购买提醒 \n"
                for medal in unhasMedal:
                    text_message += self.generate_text_report(medal)
                self.post_message(
                    mtype=NotificationType.SiteMessage,
                    title="【任务执行完成】",
                    text=f"{text_message}")

        except requests.exceptions.RequestException as e:
            logger.error(f"请求勋章页面时发生异常: {e}")

    def is_current_time_in_range(self,start_time,end_time):
        """
            判断当前时间是否在给定的时间范围内。
        """
        try:
            current_time = datetime.now()
            start_datetime = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
            end_datetime = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
            return start_datetime <= current_time <= end_datetime
        except Exception as e:
            logger.error(f"解析时间范围时发生错误: {e}")
            return False

    def generate_text_report(self,medal) -> str:
        """生成报告"""
        try:
            report = ""
            report += f"《{medal.get('name')}》可购买！（{medal.get('saleBeginTime')} - {medal.get('saleEndTime')}）\n"
            report += f" 所需积分: {medal.get('name')} \n"
            return report
        except Exception as e:
            logger.error(f"生成报告时发生异常: {e}")
            return "🌟 织梦勋章购买提醒 🌟\n生成报告时发生错误，请检查日志以获取更多信息。"
