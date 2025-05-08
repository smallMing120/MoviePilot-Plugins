from typing import Any, List, Dict, Tuple
from app.log import logger
from app.plugins import _PluginBase
from app.core.metainfo import MetaInfo
from app.schemas.types import MediaType, SystemConfigKey
from app.chain.search import SearchChain
from app.db.systemconfig_oper import SystemConfigOper
from app.chain.site import SiteChain
from app.db.site_oper import SiteOper
from app.helper.sites import SitesHelper
from app.core.config import settings
from app.db.models.subscribe import Subscribe
from app.helper.subscribe import SubscribeHelper
from app.chain.subscribe import SubscribeChain
from app.db.subscribe_oper import SubscribeOper
from app.utils.string import StringUtils

class SubscriptionQuery(_PluginBase):
    # 插件名称
    plugin_name = "订阅结果查询"
    # 插件描述
    plugin_desc = "用于调试订阅"
    # 插件图标
    plugin_icon = "Calibreweb_A.png"
    # 插件版本
    plugin_version = "1.2.5"
    # 插件作者
    plugin_author = "smallMing"
    # 作者主页
    author_url = "https://github.com/smallMing120/MoviePilot-Plugins/"
    # 插件配置项ID前缀
    plugin_config_prefix = "subscription_query_"
    # 加载顺序
    plugin_order = 100
    # 可使用的用户级别
    auth_level = 2

    # 私有属性
    sites: SitesHelper = None
    siteoper: SiteOper = None
    sitechain: SiteChain = None
    subscribe: Subscribe = None
    subscribehelper: SubscribeHelper = None
    subscribeoper: SubscribeOper = None
    searchchain:SearchChain = None
    systemconfigoper:SystemConfigOper = None

    # 配置属性
    _subscribe_id :int = None
    _keyword:str = ""
    _quality:str = ""
    _resolution:str = ""
    _effect:str = ""
    _sites:list = []
    _include:str = ""
    _exclude:str = ""
    _custom_words:str=""
    _search:bool=False
    _start_episode:str = ""
    _best_version:bool = False
    _search_imdbid:bool = False
    _media_category:str = ""
    _filter_groups:list = []
    _update:bool = False


    def init_plugin(self, config: dict = None):
        # 停止现有任务
        self.stop_service()
        #站点
        self.sites = SitesHelper()
        self.siteoper = SiteOper()
        self.sitechain = SiteChain()
        #订阅
        self.subscribe = Subscribe()
        self.siteshelper = SubscribeHelper()
        self.subscribeoper = SubscribeOper()
        self.subscribechain = SubscribeChain()
        self.searchchain = SearchChain()
        self.systemconfigoper = SystemConfigOper()

        # 获取所有订阅
        self._subscribe_option = [
            {
                'text': f"{subscribe.name} S{int(subscribe.season):02d}",
                'value': subscribe.id,
            }
            for subscribe in self.subscribeoper.list()
            if isinstance(subscribe.season, (int, float, str)) and str(subscribe.season).isdigit()
        ]
        # 用户自定义规则组
        if self.systemconfigoper.get('UserFilterRuleGroups'):
            self._filter_rule_groups = [{"text": group.get('name'), "value": group.get('name')} for group in
                                         self.systemconfigoper.get('UserFilterRuleGroups')]
        #配置
        if config:
            self._subscribe_id = config.get('subscribe_id')
            self._keyword = config.get('keyword')
            self._quality = config.get('quality')
            self._resolution = config.get('resolution')
            self._effect = config.get('effect')
            self._include = config.get('include')
            self._exclude = config.get('exclude')
            self._custom_words = config.get('custom_words')
            self._sites = config.get('sites')
            self._search = config.get('search')
            self._start_episode = config.get('start_episode')
            self._best_version = config.get('best_version')
            self._search_imdbid = config.get('search_imdbid')
            self._media_category = config.get('media_category')
            self._filter_groups = config.get('filter_groups')
            self._update = config.get('update')

            # 过滤掉已删除的站点
            all_sites = [site.id for site in self.siteoper.list_order_by_pri()]
            self._sites = [site_id for site_id in all_sites if site_id in self._sites]
            # 保存配置
            self.__update_config()
        else:
            self.update_config(
                {
                    "subscribe_id": self._subscribe_id,
                    'keyword': self._keyword,
                    'quality': self._quality,
                    'resolution': self._resolution,
                    'effect': self._effect,
                    'sites': self._sites,
                    'include': self._include,
                    'exclude': self._exclude,
                    'custom_words': self._custom_words,
                    'search': self._search,
                    'start_episode': self._start_episode,
                    'best_version': self._best_version,
                    'search_imdbid': self._search_imdbid,
                    'media_category': self._media_category,
                    'filter_groups': self._filter_groups,
                    'update': self._update,
                    'apikey':settings.API_TOKEN
                }
            )

    def __update_config(self):
        if self._search:
            res = self.check()
            self.save_data('history',res)
        self._search = False

        if self._update:
            self.subscribeoper.update(self._subscribe_id,{
                'keyword': self._keyword,
                'quality': self._quality,
                'resolution': self._resolution,
                'effect': self._effect,
                'sites': self._sites,
                'include': self._include,
                'exclude': self._exclude,
                'custom_words': self._custom_words,
                'best_version': self._best_version,
                'search_imdbid': self._search_imdbid,
                'media_category': self._media_category,
                'filter_groups': self._filter_groups,
            })
            # 保存配置
            self.update_config(
                {
                    "subscribe_id": None,
                    'keyword': "",
                    'quality': "",
                    'resolution': "",
                    'effect': "",
                    'sites': [],
                    'include': "",
                    'exclude': "",
                    'custom_words': '',
                    'search': False,
                    'start_episode': '',
                    'best_version': False,
                    'search_imdbid': False,
                    'media_category': '',
                    'filter_groups': [],
                    'update': False,
                    'apikey': settings.API_TOKEN
                }
            )
        else:
            # 保存配置
            self.update_config(
                {
                    "subscribe_id": self._subscribe_id,
                    'keyword': self._keyword,
                    'quality': self._quality,
                    'resolution': self._resolution,
                    'effect': self._effect,
                    'sites': self._sites,
                    'include': self._include,
                    'exclude': self._exclude,
                    'custom_words': self._custom_words,
                    'search': self._search,
                    'start_episode': self._start_episode,
                    'best_version': self._best_version,
                    'search_imdbid': self._search_imdbid,
                    'media_category': self._media_category,
                    'filter_groups': self._filter_groups,
                    'update': self._update,
                    'apikey': settings.API_TOKEN
                }
            )

    def get_state(self) -> bool:
        return True

    @staticmethod
    def get_command() -> List[Dict[str, Any]]:
        """
        定义远程控制命令
        :return: 命令关键字、事件、描述、附带数据
        """
        pass

    def get_api(self) -> List[Dict[str, Any]]:
        """
        获取插件API
        [{
            "path": "/xx",
            "endpoint": self.xxx,
            "methods": ["GET", "POST"],
            "summary": "API说明"
        }]
        """
        return [
            {
                "path": '/getSiteList',
                "endpoint": self.get_site_list,
                "methods": ["GET"],
                "summary": ""
            },
            {
                "path": '/getSubscribeList',
                "endpoint": self.get_subscribe_list,
                "methods": ["GET"],
                "summary": ""
            },
            {
                "path": '/getFilterRuleGroupsList',
                "endpoint": self.get_filter_rule_groups_list,
                "methods": ["GET"],
                "summary": ""
            },
            {
                "path": '/getSubscribe',
                "endpoint": self.get_subscribe,
                "methods": ["GET"],
                "summary": ""
            },
            {
                "path": '/getHistory',
                "endpoint": self.get_history,
                "methods": ["GET"],
                "auth":"bear",
                "summary": ""
            }
        ]

    def get_subscribe(self,subscribe_id):
        subscribe:{}=None
        if(subscribe_id):
            subscribe = self.subscribeoper.get(subscribe_id)
        return subscribe


    def get_site_list(self):
        """
        获取所有站点
        """
        return [{"text": site.name, "value": site.id} for site in self.siteoper.list_order_by_pri()]

    def get_history(self):
        histories = self.get_data('history')
        subscribe_search = self.get_data('subscribe_search')
        if not histories:
            return {
                "subscribe_search": subscribe_search,
                "histories": []
            }
        # 数据按时间降序排序
        histories = sorted(histories, key=lambda x: x.get('pubdate'), reverse=True)
        return {
            "subscribe_search": subscribe_search,
            "histories": [{
                "site_icon" : history.get('site_icon'),
                "title" : history.get('title'),
                "site_name" : history.get('site_name'),
                "description" : history.get('description'),
                "labels" : history.get('labels'),
                "seeders" : '↑' + str(history.get('seeders')),
                "peers" : '↓' + str(history.get('peers')),
                "date_elapsed" : history.get('date_elapsed'),
                "size" : StringUtils.str_filesize(history.get("size")),
                "pubdate" : history.get('pubdate'),
                "page_url" : history.get('page_url'),
                "hit_and_run" : history.get('hit_and_run'),
                "freedate_diff" : history.get('freedate_diff')
            } for history in histories]
        }

    def get_subscribe_list(self):
        """
        获取所有订阅
        """
        return  [
            {
                'text': f"{subscribe.name} S{int(subscribe.season):02d}",
                'value': subscribe.id,
            }
            for subscribe in self.subscribeoper.list()
            if isinstance(subscribe.season, (int, float, str)) and str(subscribe.season).isdigit()
        ]

    def get_filter_rule_groups_list(self):
        """
        获取规则组
        """
        if self.systemconfigoper.get('UserFilterRuleGroups'):
            return [{"text": group.get('name'), "value": group.get('name')} for group in
                                         self.systemconfigoper.get('UserFilterRuleGroups')]
        return []

    def get_service(self) -> List[Dict[str, Any]]:
        """
        注册插件公共服务
        [{
            "id": "服务ID",
            "name": "服务名称",
            "trigger": "触发器：cron/interval/date/CronTrigger.from_crontab()",
            "func": self.xxx,
            "kwargs": {} # 定时器参数
        }]
        """
        return []

    def get_form(self) -> Tuple[List[dict], Dict[str, Any]]:
        """
        拼装插件配置页面，需要返回两块数据：1、页面配置；2、数据结构
        """
        #获取所有站点
        site_options = ([{"title": site.name, "value": site.id} for site in self.siteoper.list_order_by_pri()])
        #获取所有订阅
        subscribe_options = [
            {
                'title': f"{subscribe.name} S{int(subscribe.season):02d}",
                'value': subscribe.id,
            }
            for subscribe in self.subscribeoper.list()
            if isinstance(subscribe.season, (int, float, str)) and str(subscribe.season).isdigit()
        ]
        # 用户自定义规则组
        if self.systemconfigoper.get('UserFilterRuleGroups'):
            rule_groups = ([{"title":group.get('name'),"value":group.get('name')} for group in self.systemconfigoper.get('UserFilterRuleGroups') ])
        else:
            rule_groups = []

        return [

            {
                'component': 'VForm',
                'content': [
                    {
                        'component': 'VRow',
                        'content':[
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                    'md': 12
                                },
                                'content': [
                                    {
                                        'component': 'VSelect',
                                        'props': {
                                            'model': 'subscribe_id',
                                            'label': '订阅',
                                            'class': "subscribe_id",
                                            'items': subscribe_options
                                        }
                                    }
                                ]
                            },

                        ]
                    },
                    {
                        'component': 'VRow',
                        'content':[
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                    'md': 8
                                },
                                'content': [
                                    {
                                        'component': 'VTextField',
                                        'props': {
                                            'model': 'keyword',
                                            'label': '搜索关键词',
                                            'placeholder': '指定搜索站点时使用的关键词'
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
                                        'component': 'VTextField',
                                        'props': {
                                            'model': 'start_episode',
                                            'label': '开始集数',
                                            'placeholder': '只对TV类型生效'
                                        }
                                    }
                                ]
                            },
                        ]
                    },
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
                                        'component': 'VSelect',
                                        'props': {
                                            'model': 'quality',
                                            'label': '质量',
                                            'items':[
                                                {
                                                    "title": '全部',
                                                    "value": '',
                                                },
                                                {
                                                    'title': '蓝光原盘',
                                                    'value': 'Blu-?Ray.+VC-?1|Blu-?Ray.+AVC|UHD.+blu-?ray.+HEVC|MiniBD',
                                                },
                                                {
                                                    'title': 'Remux',
                                                    'value': 'Remux',
                                                },
                                                {
                                                    'title': 'BluRay',
                                                    'value': 'Blu-?Ray',
                                                },
                                                {
                                                    'title': 'UHD',
                                                    'value': 'UHD|UltraHD',
                                                },
                                                {
                                                    'title': 'WEB-DL',
                                                    'value': 'WEB-?DL|WEB-?RIP',
                                                },
                                                {
                                                    'title': 'HDTV',
                                                    'value': 'HDTV',
                                                },
                                                {
                                                    'title': 'H265',
                                                    'value': '[Hx].?265|HEVC',
                                                },
                                                {
                                                    'title': 'H264',
                                                    'value': '[Hx].?264|AVC',
                                                }
                                            ]
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
                                        'component': 'VSelect',
                                        'props': {
                                            'model': 'resolution',
                                            'label': '分辨率',
                                            'items': [
                                                {
                                                    'title': '全部',
                                                    'value': '',
                                                },
                                                {
                                                    'title': '4k',
                                                    'value': '4K|2160p|x2160',
                                                },
                                                {
                                                    'title': '1080p',
                                                    'value': '1080[pi]|x1080',
                                                },
                                                {
                                                    'title': '720p',
                                                    'value': '720[pi]|x720',
                                                }
                                            ]
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
                                        'component': 'VSelect',
                                        'props': {
                                            'model': 'effect',
                                            'label': '特效',
                                            'items': [
                                                {
                                                    'title': '全部',
                                                    'value': '',
                                                },
                                                {
                                                    'title': '杜比视界',
                                                    'value': 'Dolby[\\s.]+Vision|DOVI|[\\s.]+DV[\\s.]+',
                                                },
                                                {
                                                    'title': '杜比全景声',
                                                    'value': 'Dolby[\\s.]*\\+?Atmos|Atmos',
                                                },
                                                {
                                                    'title': 'HDR',
                                                    'value': '[\\s.]+HDR[\\s.]+|HDR10|HDR10\\+',
                                                },
                                                {
                                                    'title': 'SDR',
                                                    'value': '[\\s.]+SDR[\\s.]+',
                                                }
                                            ]
                                        }
                                    }
                                ]
                            }
                        ]
                    },
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
                                        'component': 'VSelect',
                                        'props': {
                                            'chips': True,
                                            'multiple': True,
                                            'model': 'sites',
                                            'label': '站点',
                                            'items': site_options
                                        }
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        'component': 'VRow',
                        'content':[
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
                                            'model': 'include',
                                            'label': '包含（关键字、正则式）',
                                            'placeholder': '排除规则，支持正则表达式'
                                        }
                                    }
                                ]
                            },
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
                                            'model': 'exclude',
                                            'label': '排除（关键字、正则式）',
                                            'placeholder': '排除规则，支持正则表达式'
                                        }
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        'component': 'VRow',
                        'content': [
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                    'md': 6,
                                },
                                "content":[
                                    {
                                        'component': 'VSelect',
                                        'props': {
                                            'chips': True,
                                            'multiple': True,
                                            'model': 'filter_groups',
                                            'label': '优先级规则组',
                                            "clearable": True,
                                            "hint":"按选定的过滤规则组对订阅进行过滤",
                                            'items': rule_groups,
                                        }
                                    }
                                ]
                            },
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                    'md': 6,
                                },
                                "content": [
                                    {
                                        'component': 'VTextField',
                                        'props': {
                                            'model': 'media_category',
                                            'label': '自定义类别',
                                            'placeholder': '指定类别名称，留空自动识别'
                                        }
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        'component': 'VRow',
                        'content': [
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                    'md': 3
                                },
                                'content': [
                                    {
                                        'component': 'VSwitch',
                                        'props': {
                                            'model': 'best_version',
                                            'label': '洗版',
                                        }
                                    }
                                ]
                            },
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                    'md': 3
                                },
                                'content': [
                                    {
                                        'component': 'VSwitch',
                                        'props': {
                                            'model': 'search_imdbid',
                                            'label': '使用 ImdbID 搜索',
                                        }
                                    }
                                ]
                            },
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                    'md': 3
                                },
                                'content': [
                                    {
                                        'component': 'VSwitch',
                                        'props': {
                                            'model': 'search',
                                            'label': '保存后开始搜索',
                                        }
                                    }
                                ]
                            },
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                    'md': 3
                                },
                                'content': [
                                    {
                                        'component': 'VSwitch',
                                        'props': {
                                            'model': 'update',
                                            'label': '更新至订阅并清空',
                                        }
                                    }
                                ]
                            },
                        ]
                    },
                    {
                        'component': 'VRow',
                        'content':[
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                    'md': 12
                                },
                                'content': [
                                    {
                                        'component': 'VTextarea',
                                        'props': {
                                            'model': 'custom_words',
                                            'label': '自定义识别词',
                                            'placeholder': '只对该订阅使用的识别词'
                                        }
                                    }
                                ]
                            }
                        ]
                    },
                ]
            }
        ], {
            "subscribe_id": self._subscribe_id,
            'keyword': self._keyword,
            'quality': self._quality,
            'resolution': self._resolution,
            'effect': self._effect,
            'sites': self._sites,
            'include': self._include,
            'exclude': self._exclude,
            'custom_words': self._sites,
            'search':self._search,
            'start_episode':self._start_episode,
            'best_version':self._best_version,
            'search_imdbid':self._search_imdbid,
            'filter_groups':self._filter_groups,
            'media_category':self._media_category,
            'update':self._update
        }

    def get_page(self) -> List[dict]:
        """
        拼装插件详情页面，需要返回页面配置，同时附带数据
        """
        # 查询详情
        histories = self.get_data('history')
        if not histories:
            return [
                {
                    'component': 'div',
                    'text': '暂无数据',
                    'props': {
                        'class': 'text-center',
                    }
                }
            ]
        # 数据按时间降序排序
        histories = sorted(histories, key=lambda x: x.get('pubdate'), reverse=True)
        subscribe_search = self.get_data('subscribe_search')
        contents = []

        for history in histories:
            site_icon = history.get('site_icon')
            title = history.get('title')
            site_name = history.get('site_name')
            description = history.get('description')
            labels = history.get('labels')
            seeders = '↑' + str(history.get('seeders'))
            peers = '↓' + str(history.get('peers'))
            date_elapsed = history.get('date_elapsed')
            size = StringUtils.str_filesize(history.get("size"))
            pubdate = history.get('pubdate')
            page_url = history.get('page_url')
            hit_and_run = history.get('hit_and_run'),
            freedate_diff = history.get('freedate_diff')

            # contents.append(
            #     {
            #         'component': 'VListItem',
            #         "props":{
            #             "variant":"outlined"
            #         },
            #         'content': [
            #             {
            #                 'component':"VListItemTitle",
            #                 "props":{
            #                     'class':"break-words overflow-visible whitespace-break-spaces"
            #                 },
            #                 "content": [
            #                     {
            #                         'component': "VAvatar",
            #                         "props": {
            #                             'class': "rounded",
            #                             'variant': "flat"
            #                         },
            #                         "content": [
            #                             {
            #                                 'component': "VImg",
            #                                 "props": {
            #                                     "src": site_icon
            #                                 }
            #                             }
            #                         ]
            #                     },{
            #                         'component': "text",
            #                         "text":title
            #                     },
            #                     {
            #                         'component': "span",
            #                         "props": {
            #                             "class": "text-green-700 ms-2 text-sm"
            #                         },
            #                         'text': seeders
            #                     },
            #                     {
            #                         'component': "span",
            #                         "props": {
            #                             "class": "text-orange-700 ms-2 text-sm"
            #                         },
            #                         'text': peers
            #                     }
            #                 ]
            #             },
            #             {
            #                 'component':'VListItemSubtitle',
            #                 'text':'['+site_name+'] ' + description
            #             },
            #             {
            #                 'component':'div',
            #                 "props": {
            #                     'class': "pt-2"
            #                 },
            #                 'content':[{'component':'VChip',"props":{"variant":"elevated","size":"small","color":"primary","class":"me-1 mb-1"},'text':label} for label in labels]
            #             }
            #         ]
            #     }
            # )

            title_html = [
                {
                    'component': 'div',
                    'props': {
                        'class': 'text-high-emphasis pt-1'
                    },
                    'text': title
                },
                {
                    'component': 'div',
                    'props': {
                        'class': 'text-sm my-1'
                    },
                    'text': description
                }
            ]
            # if(hit_and_run):
            #     title_html.append({
            #         'component': 'VChip',
            #         'props': {
            #             'variant': 'elevated',
            #             'size': 'small',
            #             'class': 'me-1 mb-1 text-white bg-black'
            #         },
            #         'text': 'H&R'
            #     })
            if freedate_diff:
                title_html.append({
                    'component': 'VChip',
                    'props': {
                        'variant': 'elevated',
                        'color': 'secondary',
                        'size': 'small',
                        'class': 'me-1 mb-1'
                    },
                    'text': freedate_diff
                })
            if labels:
                for label in labels:
                    title_html.append({
                        'component': 'VChip',
                        'props': {
                            'variant': 'elevated',
                            'color': 'primary',
                            'size': 'small',
                            'class': 'me-1 mb-1'
                        },
                        'text': label
                    })

            contents.append({
                'component': 'tr',
                'props': {
                    'class': 'text-sm'
                },
                'content': [
                    {
                        'component': 'td',
                        'props': {
                            'class': 'whitespace-nowrap break-keep text-high-emphasis'
                        },
                        #'text': site_name,
                        'content':[
                            {
                                'component': "VAvatar",
                                "props": {
                                    'class': "rounded",
                                    'variant': "flat"
                                },
                                "content": [
                                    {
                                        'component': "VImg",
                                        "props": {
                                            "src": site_icon
                                        }
                                    }
                                ]
                            },
                            {
                                'component': "br",
                            },
                            {
                                'component': "span",
                                "props":{
                                    'size': 'small',
                                    'variant': 'elevated',
                                    'class': 'me-1 mb-1',
                                    'color': 'warning',
                                },
                                'text': site_name,
                            }
                        ]
                    },
                    {
                        'component': 'td',
                        'content': [{
                            'component': 'a',
                            'props': {
                                'href': 'javascript:void(0)',
                                'torrent-data': '',
                                'class': 'torrent-title-link'
                            },
                            'content': title_html
                        }]
                    },
                    {
                        'component': 'td',
                        'content': [
                            {
                                'component': 'div',
                                'text': date_elapsed
                            },
                            {
                                'component': 'div',
                                'props': {
                                    'class': 'text-sm'
                                },
                                'text': pubdate
                            }
                        ]
                    },
                    {
                        'component': 'td',
                        'content': [
                            {
                                'component': 'div',
                                'props': {
                                    'class': 'text-nowrap whitespace-nowrap'
                                },
                                'text': size
                            }
                        ]
                    },
                    {
                        'component': 'td',
                        'content': [
                            {
                                'component': 'div',
                                'text':seeders
                            }
                        ]
                    },
                    {
                        'component': 'td',
                        'content': [
                            {
                                'component': 'div',
                                'text': peers
                            }
                        ]
                    },
                    {
                        'component': 'td',
                        'content': [
                            {
                                'component': 'div',
                                'content': [
                                    {
                                        'component': 'VChip',
                                        'props': {
                                            'variant': 'elevated',
                                            'size': 'default',
                                            'class': 'me-1 mb-1 text-white bg-sky-500'
                                        },
                                        'content': [
                                            {
                                                'component': 'a',
                                                'props': {
                                                    'href': page_url,
                                                    'target': '_blank'
                                                },
                                                'text': '查看详情'
                                            }
                                        ]
                                    }
                                ]
                            }
                        ]
                    }
                ]
            })

        return [
            {
                'component': 'VRow',
                'content': [
                    {
                        'component': 'VRow',
                        'content': [
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                },
                                'content': [
                                    {
                                        'component': 'VAlert',
                                        'props': {
                                            'type': 'info',
                                            'variant': 'tonal',
                                            'text': f'查询订阅：{subscribe_search}'
                                        }
                                    }
                                ]
                            }
                        ]
                    },
                    # 各站点数据明细
                    {
                        'component': 'VCardText',
                        'props': {
                            'class': 'pt-2',
                        },
                        'content': [
                            {
                                'component': 'VTable',
                                'props': {
                                    'hover': True,
                                    'fixed-header': True,
                                    'height': '500px'
                                },
                                'content': [
                                    {
                                        'component': 'thead',
                                        'content': [
                                            {
                                                'component': 'tr',
                                                'content': [
                                                    {
                                                        'component': 'th',
                                                        'props': {
                                                            'class': 'text-start'
                                                        },
                                                        'text': '站点'
                                                    },
                                                    {
                                                        'component': 'th',
                                                        'props': {
                                                            'class': 'text-start'
                                                        },
                                                        'text': '标题'
                                                    },
                                                    {
                                                        'component': 'th',
                                                        'props': {
                                                            'class': 'text-start'
                                                        },
                                                        'text': '时间'
                                                    },
                                                    {
                                                        'component': 'th',
                                                        'props': {
                                                            'class': 'text-start'
                                                        },
                                                        'text': '大小'
                                                    },
                                                    {
                                                        'component': 'th',
                                                        'props': {
                                                            'class': 'text-start'
                                                        },
                                                        'text': '做种'
                                                    },
                                                    {
                                                        'component': 'th',
                                                        'props': {
                                                            'class': 'text-start'
                                                        },
                                                        'text': '下载'
                                                    },
                                                    {
                                                        'component': 'th',
                                                        'props': {
                                                            'class': 'text-start'
                                                        },
                                                        'text': ''
                                                    }
                                                ]
                                            }
                                        ]
                                    },
                                    {
                                        'component': 'tbody',
                                        'content': contents
                                    }
                                ]
                            }
                        ]
                    },
                    # 自定义样式
                    {
                        'component': 'style',
                        'props': {
                            'type': 'text/css'
                        },
                        'text': """
                                    div.v-toast.v-toast--bottom {
                                        z-index: 3000;
                                    }
                                """
                    }
                ]
            }
        ]

    def stop_service(self):
        """
        退出插件
        """

    def check(self):
        if self._subscribe_id == None:
            return []
        subscribe = self.subscribeoper.get(self._subscribe_id)
        if not subscribe:
            return []
        subscribe.keyword = self._keyword
        subscribe.sites = self._sites
        subscribe.quality = self._quality
        subscribe.include = self._include
        subscribe.exclude = self._exclude
        subscribe.custom_words = self._custom_words
        subscribe.effect = self._effect
        subscribe.resolution = self._resolution
        subscribe.media_category = self._media_category
        subscribe.filter_groups = self._filter_groups
        subscribe.search_imdbid = self._search_imdbid
        subscribe.best_version = self._best_version

        self.save_data('subscribe_search',f"{subscribe.name} S{int(subscribe.season):02d}")

        if (subscribe.type == 'tv' or subscribe.type == 'TV' or subscribe.type == '电视剧') and not self._start_episode :
            subscribe.start_episode = self._start_episode

        matched_contexts = []
        custom_word_list = subscribe.custom_words.split("\n") if subscribe.custom_words else None
        try:
            logger.info(f'开始搜索订阅，标题：{subscribe.name} ...')
            # 生成元数据
            meta = MetaInfo(subscribe.name)
            meta.year = subscribe.year
            meta.begin_season = subscribe.season or None
            try:
                meta.type = MediaType(subscribe.type)
            except ValueError:
                logger.error(f'订阅 {subscribe.name} 类型错误：{subscribe.type}')
                return []
            # 识别媒体信息
            mediainfo = self.subscribechain.recognize_media(meta=meta, mtype=meta.type,tmdbid=subscribe.tmdbid,doubanid=subscribe.doubanid,cache=False)
            if not mediainfo:
                logger.warn(
                    f'未识别到媒体信息，标题：{subscribe.name}，tmdbid：{subscribe.tmdbid}，doubanid：{subscribe.doubanid}')
                return []
            # 站点范围
            sites = self.get_sub_sites(subscribe)
            # 优先级过滤规则
            if subscribe.best_version:
                rule_groups = subscribe.filter_groups \
                              or self.systemconfig.get(SystemConfigKey.BestVersionFilterRuleGroups) or []
            else:
                rule_groups = subscribe.filter_groups \
                              or self.systemconfig.get(SystemConfigKey.SubscribeFilterRuleGroups) or []
            # 搜索，同时电视剧会过滤掉不需要的剧集
            contexts = self.searchchain.process(mediainfo=mediainfo,
                                                keyword=subscribe.keyword,
                                                no_exists=None,
                                                sites=sites,
                                                rule_groups=rule_groups,
                                                area="imdbid" if subscribe.search_imdbid else "title",
                                                custom_words=custom_word_list,
                                                filter_params=self.get_params(subscribe))
            i = 0
            # 过滤搜索结果
            for context in contexts:
                #matched_contexts.append(context)
                if i > 100:
                    break
                site_icon = ''
                site_info = self.siteoper.get(context.torrent_info.site)
                if site_info:
                    site_icon = self.siteoper.get_icon_by_domain(site_info.domain)

                matched_contexts.append({
                    'site_icon':site_icon.base64,# 站點圖標
                    'site_name':context.torrent_info.site_name,# 站点名称
                    'title':context.torrent_info.title,# 种子名称
                    'description': context.torrent_info.description,# 种子副标题
                    'pubdate': context.torrent_info.pubdate,# 发布时间
                    'labels' : context.torrent_info.labels,# 种子标签,
                    'size': context.torrent_info.size,# 种子大小
                    'seeders': context.torrent_info.seeders,#做种者,
                    'peers': context.torrent_info.peers,#完成者
                    'date_elapsed':context.torrent_info.date_elapsed,
                    'page_url':context.torrent_info.page_url,
                    'hit_and_run':context.torrent_info.hit_and_run,
                    'freedate_diff':context.torrent_info.freedate_diff,
                })
                i+=1
            if not matched_contexts:
                logger.warn(f'订阅 {subscribe.name} 没有符合过滤条件的资源')
                return []
        finally:
            return matched_contexts

    def get_params(self, subscribe: Subscribe):
        """
        获取订阅默认参数
        """
        # 默认过滤规则
        default_rule = self.systemconfig.get(SystemConfigKey.SubscribeDefaultParams) or {}
        return {
            "include": subscribe.include or default_rule.get("include"),
            "exclude": subscribe.exclude or default_rule.get("exclude"),
            "quality": subscribe.quality or default_rule.get("quality"),
            "resolution": subscribe.resolution or default_rule.get("resolution"),
            "effect": subscribe.effect or default_rule.get("effect"),
            "tv_size": default_rule.get("tv_size"),
            "movie_size": default_rule.get("movie_size"),
            "min_seeders": default_rule.get("min_seeders"),
            "min_seeders_time": default_rule.get("min_seeders_time"),
        }

    def get_sub_sites(self, subscribe: Subscribe) -> List[int]:
        """
        获取订阅中涉及的站点清单
        :param subscribe: 订阅信息对象
        :return: 涉及的站点清单
        """
        # 从系统配置获取默认订阅站点
        default_sites = self.systemconfig.get(SystemConfigKey.RssSites) or []

        # 如果订阅未指定站点信息，直接返回默认站点
        if not subscribe.sites:
            return default_sites
        # 尝试解析订阅中的站点数据
        user_sites = subscribe.sites
        # 计算 user_sites 和 default_sites 的交集
        intersection_sites = [site for site in user_sites if site in default_sites]
        # 如果交集与原始订阅不一致，更新数据库
        if set(intersection_sites) != set(user_sites):
            self.subscribeoper.update(subscribe.id, {
                "sites": intersection_sites
            })
        # 如果交集为空，返回默认站点
        return intersection_sites if intersection_sites else default_sites

    def get_render_mode(self) -> Tuple[str, str]:
        """
        获取插件渲染模式
        :return: 1、渲染模式，支持：vue/vuetify，默认vuetify
        :return: 2、组件路径，默认 dist/assets
        """
        return "vue", "dist/assets"
