import io
import base64
import tempfile
from pathlib import Path
import requests
from datetime import datetime
from typing import Any, List, Dict, Tuple, Optional
from PIL import Image

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from app.plugins import _PluginBase
from app.log import logger
from app.db.site_oper import SiteOper
from app.schemas import NotificationType
from app.utils.http import RequestUtils
from app.core.config import settings
from app.core.cache import cache_backend, cached
from app.utils.security import SecurityUtils

class ZmMedal(_PluginBase):
    # 插件名称
    plugin_name = "织梦勋章购买提醒"
    # 插件描述
    plugin_desc = "织梦勋章购买提醒"
    # 插件图标
    plugin_icon = "https://raw.githubusercontent.com/smallMing120/MoviePilot-Plugins/main/icons/zm.png"
    # 插件版本
    plugin_version = "1.0.5"
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
    _onlyonce: bool = False
    _notify: bool = False

    # 定时器
    _scheduler: Optional[BackgroundScheduler] = None
    _siteoper = None

    def init_plugin(self, config: Optional[dict] = None) -> None:
        """
            初始化插件
        """
        # 停止现有任务
        self.stop_service()
        self._siteoper =  SiteOper()
        if config:
            self._enabled = config.get("enabled", False)
            self._cron = config.get("cron")
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
                    "func": self.__start,
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

            site = self._siteoper.get_by_domain('zmpt.cc')
            if not site :
                logger.info(f"未添加织梦站点！")
                return

            res = RequestUtils(cookies=site.cookie).get_res(url="https://zmpt.cc/javaapi/user/queryAllMedals")
            if not res or res.status_code != 200:
                logger.error("请求勋章接口失败！状态码：%s", res.status_code if res else "无响应")
                return
            data = res.json().get('result',{})
            medalGroups = data.get('medalGroups')
            medals = data.get('medals')
            for medal in medals:
                hasMedal = medal.get('hasMedal')
                imageSmall = medal.get('imageSmall')
                price = medal.get('price')
                name = medal.get('name')
                logger.info(f"开始检查：《{name}》勋章....")
                if hasMedal:
                    #已拥有勋章跳过
                    logger.info(f"《{name}》:已拥有,跳过")
                    continue

                saleBeginTime = medal.get('saleBeginTime')
                saleEndTime = medal.get('saleEndTime')

                if self.is_current_time_in_range(saleBeginTime,saleEndTime):
                    logger.info(f"《{name}》:可购买！")
                    unhasMedal.append({
                        'name':name,
                        'imageSmall':imageSmall,
                        'saleBeginTime':saleBeginTime,
                        'saleEndTime':saleEndTime,
                        'price':price
                    })
                else:
                    logger.info(f"《{name}》:未到开售时间")

            for medalGroup in medalGroups:
                medalList = medalGroup.get('medalList')
                for medal in medalList:
                    hasMedal = medal.get('hasMedal')
                    imageSmall = medal.get('imageSmall')
                    price = medal.get('price')
                    name = medal.get('name')
                    logger.info(f"开始检查：《{name}》勋章....")
                    if hasMedal:
                        #已拥有勋章跳过
                        logger.info(f"《{name}》:已拥有,跳过")
                        continue

                    saleBeginTime = medal.get('saleBeginTime')
                    saleEndTime = medal.get('saleEndTime')

                    if self.is_current_time_in_range(saleBeginTime,saleEndTime):
                        logger.info(f"《{name}》:可购买！")

                        # 缓存收集到的圖片
                        self.__cache_img(imageSmall)

                        unhasMedal.append({
                            'name':name,
                            'imageSmall':imageSmall,
                            'saleBeginTime':saleBeginTime,
                            'saleEndTime':saleEndTime,
                            'price':price
                        })
                    else:
                        logger.info(f"《{name}》:未到开售时间")

            if self._notify and unhasMedal:
                # 发送通知
                text_message = "织梦勋章购买提醒 \n"
                for medal in unhasMedal:
                    text_message += self.generate_text_report(medal)
                self.post_message(
                    mtype=NotificationType.SiteMessage,
                    title="【任务执行完成】",
                    text=f"{text_message}")
            if unhasMedal:
                self.save_data('medals',unhasMedal,'zmmedal')

        except requests.exceptions.RequestException as e:
            logger.error(f"请求勋章页面时发生异常: {e}")

    def __cache_img(self,url):
        if not settings.GLOBAL_IMAGE_CACHE or not url:
            return
        # 生成缓存路径
        sanitized_path = SecurityUtils.sanitize_url_path(url)
        cache_path = settings.CACHE_PATH / "images" / sanitized_path
        # 没有文件类型，则添加后缀，在恶意文件类型和实际需求下的折衷选择
        if not cache_path.suffix:
            cache_path = cache_path.with_suffix(".jpg")
        # 确保缓存路径和文件类型合法
        if not SecurityUtils.is_safe_path(settings.CACHE_PATH, cache_path, settings.SECURITY_IMAGE_SUFFIXES):
            logger.debug(f"Invalid cache path or file type for URL: {url}, sanitized path: {sanitized_path}")
            return
        # 本地存在缓存图片，则直接跳过
        if cache_path.exists():
            logger.debug(f"Cache hit: Image already exists at {cache_path}")
            return

        # 请求远程图片
        response = RequestUtils(ua=settings.USER_AGENT).get_res(url=url)
        if not response:
            logger.debug(f"Empty response for URL: {url}")
            return
        # 验证下载的内容是否为有效图片
        try:
            Image.open(io.BytesIO(response.content)).verify()
        except Exception as e:
            logger.debug(f"Invalid image format for URL {url}: {e}")
            return

        if not cache_path:
            return

        try:
            if not cache_path.parent.exists():
                cache_path.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(dir=cache_path.parent, delete=False) as tmp_file:
                tmp_file.write(response.content)
                temp_path = Path(tmp_file.name)
            temp_path.replace(cache_path)
            logger.debug(f"Successfully cached image at {cache_path} for URL: {url}")

        except Exception as e:
            logger.debug(f"Failed to write cache file {cache_path} for URL {url}: {e}")
            return

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
            report += f"《{medal.get('name')}》\n 购买时间：{medal.get('saleBeginTime')} - {medal.get('saleEndTime')}\n"
            report += f" 所需积分: {medal.get('price'):,} \n ---------- \n"
            return report
        except Exception as e:
            logger.error(f"生成报告时发生异常: {e}")
            return "🌟 织梦勋章购买提醒 🌟\n生成报告时发生错误，请检查日志以获取更多信息。"

    def get_dashboard(self, key: str, **kwargs) -> Optional[Tuple[Dict[str, Any], Dict[str, Any], List[dict]]]:
        medals = self.get_data('medals','zmmedal')
        if not medals:
            pass
        else:
            # 列配置
            cols = {
                "cols": 12
            }
            # 全局配置
            attrs = {}

            elements = [
                {
                    'component': 'VRow',
                    'content': self.__get_medal_elements(medals)
                }
            ]
            return cols,attrs,elements

    def __get_medal_elements(self,medals):
        medal_html = []
        for medal in medals:
            url = medal.get('imageSmall')
            sanitized_path = SecurityUtils.sanitize_url_path(url)
            cache_path = settings.CACHE_PATH / "images" / sanitized_path
            if cache_path.exists():
                content = cache_path.read_bytes()
                url = f'data:image/{cache_path.suffix.lower().replace(".", "")};base64,' + base64.b64encode(content).decode('utf-8')

            medal_html.append(
                {
                    'component':'VCol',
                    'props':{
                        'cols': 3,
                        'md': 3,
                        'style':"border:1px;"
                    },
                    'content':[
                        {
                          'component':'VTable',
                          'props': {
                            'hover': True,
                            'fixed-header': True,
                          },
                          'content':[
                              {
                                  'component': 'thead',
                                  'content': [
                                      {
                                          'component': 'tr',
                                          'content': [
                                              {
                                                  'component': 'th',
                                                  'props': {
                                                      'class': 'text-center',
                                                      'colspan': 2
                                                  },
                                                  'content': [
                                                      {
                                                          'component': 'H1',
                                                          'props': {
                                                              'class': 'mr-2 min-w-0 text-lg font-bold'
                                                          },
                                                          'text': f"《{medal.get('name')}》"
                                                      }
                                                  ]
                                              }
                                          ]
                                      }
                                  ]
                              },
                              {
                                  'component': 'tbody',
                                  'content':[
                                      {
                                          'component': 'tr',
                                          'content': [
                                              {
                                                   'component': 'td',
                                                   'props': {
                                                      'class': 'text-right',
                                                       'rowspan': 2
                                                   },
                                                   'content':[
                                                       {
                                                           'component': 'VImg',
                                                           'props': {
                                                               'src': url,
                                                               'height': '100',
                                                               'width': '100',
                                                           }
                                                       }
                                                   ]
                                              },
                                              {
                                                  'component': 'td',
                                                  'props': {
                                                      'class': 'text-start'
                                                  },
                                                  'text':f"开始时间 : {medal.get('saleBeginTime')}"
                                              }
                                          ]
                                      },
                                      {
                                          'component': 'tr',
                                          'content': [
                                              {
                                                  'component': 'td',
                                                  'props': {
                                                      'class': 'text-start'
                                                  },
                                                  'text':f"結束時間 : {medal.get('saleEndTime')}"
                                              }
                                          ]
                                      },
                                      {
                                          'component': 'tr',
                                          'content': [
                                              {
                                                  'component': 'td',
                                                  'props': {
                                                      'class': 'text-center',
                                                      'colspan': 2
                                                  },
                                                  'text': f"價格 : {medal.get('price'):,}"
                                              }
                                          ]
                                      }
                                  ]
                              }
                          ]
                        },
                    ]
                }
            )
        return medal_html
