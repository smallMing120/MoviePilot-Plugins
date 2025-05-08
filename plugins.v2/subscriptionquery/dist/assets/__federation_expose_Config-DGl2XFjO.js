import { importShared } from './__federation_fn_import-DXLKUql0.js';
import { _ as _export_sfc } from './_plugin-vue_export-helper-pcqpp-6-.js';

const {createTextVNode:_createTextVNode,resolveComponent:_resolveComponent,withCtx:_withCtx,createVNode:_createVNode,toDisplayString:_toDisplayString,openBlock:_openBlock,createBlock:_createBlock,createCommentVNode:_createCommentVNode,withModifiers:_withModifiers,createElementBlock:_createElementBlock} = await importShared('vue');


const _hoisted_1 = { class: "plugin-config" };
const {ref,reactive,onMounted,watch} = await importShared('vue');


// 接收初始配置

const _sfc_main = {
  __name: 'Config',
  props: {
  initialConfig: {
    type: Object,
    default: () => ({

    }),
  },
  api: {
    type: Object,
    default: () => {},
  },
},
  emits: ['save', 'close', 'switch'],
  setup(__props, { emit: __emit }) {

const props = __props;

// 表单状态
const form = ref(null);
const isFormValid = ref(true);
const error = ref(null);
const saving = ref(false);

// 质量选项
const quanlityOptions = [
  { text: '全部', value: '' },
  { text: '蓝光原盘', value: 'Blu-?Ray.+VC-?1|Blu-?Ray.+AVC|UHD.+blu-?ray.+HEVC|MiniBD' },
  { text: 'Remux', value: 'Remux' },
  { text: 'BluRay', value: 'Blu-?Ray' },
  { text: 'UHD', value: 'UHD|UltraHD' },
  { text: 'WEB-DL', value: 'WEB-?DL|WEB-?RIP' },
  { text: 'HDTV', value: 'Blu-?Ray' },
  { text: 'H265', value: '[Hx].?265|HEVC' },
  { text: 'H264', value: '[Hx].?264|AVC' },
];

// 分辨率选项
const resolutionOptions = [
  { text: '全部', value: '' },
  { text: '4K', value: '4K|2160p|x2160' },
  { text: '1080P', value: '1080[pi]|x1080' },
  { text: '720P', value: '720[pi]|x720' },
];

// 特效选项
const effectOptions = [
  { text: '全部', value: '' },
  { text: '杜比视界', value: 'Dolby[\\s.]+Vision|DOVI|[\\s.]+DV[\\s.]+' },
  { text: '杜比全景声', value: 'Dolby[\\s.]*\\+?Atmos|Atmos' },
  { text: 'HDR', value: '[\\s.]+HDR[\\s.]+|HDR10|HDR10\\+' },
  { text: 'SDR', value: '[\\s.]+SDR[\\s.]+' },
];

const sitesOptions = ref([]);
const subscribeOptions = ref([]);
const filterRuleGroups = ref([]);

// 配置数据，使用默认值和初始配置合并
const defaultConfig = {
  subscribe_id: 0,// 订阅
  keyword: '',// 关键词
  start_episode:'',// 起始集数
  quality: '',// 质量
  resolution: '',// 分辨率
  effect: '',// 特效
  sites: [],// 站点
  include: '',// 包含（关键字、正则式）
  exclude: '',// 排除（关键字、正则式）
  filter_groups:[],// 优先级规则组
  media_category: '',// 自定义类别
  best_version: false,// 洗版
  search_imdbid: false,// 搜索IMDB ID
  search: false,// 保存后开始搜索
  update:false,// 更新至订阅并清空
  custom_words:'',//自定义识别词
};

// 合并默认配置和初始配置
const config = reactive({ ...defaultConfig });

// 初始化配置
onMounted(() => {
  // 加载初始配置
  if (props.initialConfig) {
    Object.keys(props.initialConfig).forEach(key => {
      if (key in config) {
        config[key] = props.initialConfig[key];
      }
    });
  }

  getOptions();
});

async function getOptions() {
  // 获取站点列表
  const siteData = await props.api.get('plugin/SubscriptionQuery/getSiteList?apikey='+ props.initialConfig.apikey);
  if (siteData) {
    sitesOptions.value = siteData.map(site => ({ text: site.text, value: site.value }));
  } else {
    console.log('获取站点列表失败:');
  }
  
  const subscribeData = await props.api.get('plugin/SubscriptionQuery/getSubscribeList?apikey='+ props.initialConfig.apikey);
  if (subscribeData) {
    subscribeOptions.value = subscribeData.map(subscribe => ({ text: subscribe.text, value: subscribe.value }));
  } else {
    console.log('获取订阅列表失败:');
  }
  const filterRuleGroupData = await props.api.get('plugin/SubscriptionQuery/getFilterRuleGroupsList?apikey='+ props.initialConfig.apikey);
  if (filterRuleGroupData) {
    filterRuleGroups.value = filterRuleGroupData.map(group => ({ text: group.text, value: group.value }));
  } else {
    console.log('获取优先级规则组列表失败:');
  }
}

// 自定义事件，用于保存配置
const emit = __emit;

// 保存配置
async function saveConfig() {
  if (!isFormValid.value) {
    error.value = '请修正表单错误';
    return
  }

  saving.value = true;
  error.value = null;

  try {
    // 模拟API调用等待
    await new Promise(resolve => setTimeout(resolve, 1000));

    // 发送保存事件
    emit('save', { ...config });
  } catch (err) {
    console.error('保存配置失败:', err);
    error.value = err.message || '保存配置失败';
  } finally {
    saving.value = false;
  }
}

watch(
  () => config.subscribe_id,
  (newValue,oldValue) => {
    console.log('订阅ID变化:', newValue, oldValue);
    if (newValue != oldValue && (newValue != 0 && oldValue != 0)) {
      changSubscribe(newValue);
    }
  }
);

// 修改订阅
async function changSubscribe(subscribe_id){
  const subscribeData = await props.api.get('plugin/SubscriptionQuery/getSubscribe?apikey='+ props.initialConfig.apikey + '&subscribe_id=' + subscribe_id);
  if(subscribeData){
    config.keyword = subscribeData.keyword;
    config.start_episode = subscribeData.start_episode;
    config.quality = subscribeData.quality;
    config.resolution = subscribeData.resolution;
    config.effect = subscribeData.effect;
    config.sites = subscribeData.sites;
    config.include = subscribeData.include;
    config.exclude = subscribeData.exclude;
    config.filter_groups = subscribeData.filter_groups;
    config.media_category = subscribeData.media_category;
    config.best_version = subscribeData.best_version;
    config.search_imdbid = subscribeData.search_imdbid;
  }
}

function notifySwitch() {
  emit('switch');
}

// 通知主应用关闭组件
function notifyClose() {
  emit('close');
}

return (_ctx, _cache) => {
  const _component_v_card_title = _resolveComponent("v-card-title");
  const _component_v_alert = _resolveComponent("v-alert");
  const _component_v_select = _resolveComponent("v-select");
  const _component_v_col = _resolveComponent("v-col");
  const _component_v_row = _resolveComponent("v-row");
  const _component_v_text_field = _resolveComponent("v-text-field");
  const _component_v_switch = _resolveComponent("v-switch");
  const _component_v_textarea = _resolveComponent("v-textarea");
  const _component_v_form = _resolveComponent("v-form");
  const _component_v_card_text = _resolveComponent("v-card-text");
  const _component_v_btn = _resolveComponent("v-btn");
  const _component_v_spacer = _resolveComponent("v-spacer");
  const _component_v_card_actions = _resolveComponent("v-card-actions");
  const _component_v_card = _resolveComponent("v-card");

  return (_openBlock(), _createElementBlock("div", _hoisted_1, [
    _createVNode(_component_v_card, null, {
      default: _withCtx(() => [
        _createVNode(_component_v_card_title, null, {
          default: _withCtx(() => _cache[17] || (_cache[17] = [
            _createTextVNode("插件配置")
          ])),
          _: 1
        }),
        _createVNode(_component_v_card_text, null, {
          default: _withCtx(() => [
            (error.value)
              ? (_openBlock(), _createBlock(_component_v_alert, {
                  key: 0,
                  type: "error",
                  class: "mb-4"
                }, {
                  default: _withCtx(() => [
                    _createTextVNode(_toDisplayString(error.value), 1)
                  ]),
                  _: 1
                }))
              : _createCommentVNode("", true),
            _createVNode(_component_v_form, {
              ref_key: "form",
              ref: form,
              modelValue: isFormValid.value,
              "onUpdate:modelValue": _cache[16] || (_cache[16] = $event => ((isFormValid).value = $event)),
              onSubmit: _withModifiers(saveConfig, ["prevent"])
            }, {
              default: _withCtx(() => [
                _createVNode(_component_v_row, null, {
                  default: _withCtx(() => [
                    _createVNode(_component_v_col, {
                      cols: "12",
                      md: "12"
                    }, {
                      default: _withCtx(() => [
                        _createVNode(_component_v_select, {
                          modelValue: config.subscribe_id,
                          "onUpdate:modelValue": _cache[0] || (_cache[0] = $event => ((config.subscribe_id) = $event)),
                          label: "订阅",
                          items: subscribeOptions.value,
                          variant: "outlined",
                          "item-title": "text",
                          "item-value": "value"
                        }, null, 8, ["modelValue", "items"])
                      ]),
                      _: 1
                    })
                  ]),
                  _: 1
                }),
                _createVNode(_component_v_row, null, {
                  default: _withCtx(() => [
                    _createVNode(_component_v_col, {
                      cols: "12",
                      md: "8"
                    }, {
                      default: _withCtx(() => [
                        _createVNode(_component_v_text_field, {
                          modelValue: config.keyword,
                          "onUpdate:modelValue": _cache[1] || (_cache[1] = $event => ((config.keyword) = $event)),
                          label: "关键词",
                          variant: "outlined",
                          hint: "搜索关键词"
                        }, null, 8, ["modelValue"])
                      ]),
                      _: 1
                    }),
                    _createVNode(_component_v_col, {
                      cols: "12",
                      md: "4"
                    }, {
                      default: _withCtx(() => [
                        _createVNode(_component_v_text_field, {
                          modelValue: config.start_episode,
                          "onUpdate:modelValue": _cache[2] || (_cache[2] = $event => ((config.start_episode) = $event)),
                          label: "开始集数",
                          variant: "outlined",
                          hint: "开始集数"
                        }, null, 8, ["modelValue"])
                      ]),
                      _: 1
                    })
                  ]),
                  _: 1
                }),
                _createVNode(_component_v_row, null, {
                  default: _withCtx(() => [
                    _createVNode(_component_v_col, {
                      cols: "12",
                      md: "4"
                    }, {
                      default: _withCtx(() => [
                        _createVNode(_component_v_select, {
                          modelValue: config.quality,
                          "onUpdate:modelValue": _cache[3] || (_cache[3] = $event => ((config.quality) = $event)),
                          label: "质量",
                          items: quanlityOptions,
                          variant: "outlined",
                          "item-title": "text",
                          "item-value": "value"
                        }, null, 8, ["modelValue"])
                      ]),
                      _: 1
                    }),
                    _createVNode(_component_v_col, {
                      cols: "12",
                      md: "4"
                    }, {
                      default: _withCtx(() => [
                        _createVNode(_component_v_select, {
                          modelValue: config.resolution,
                          "onUpdate:modelValue": _cache[4] || (_cache[4] = $event => ((config.resolution) = $event)),
                          label: "分辨率",
                          items: resolutionOptions,
                          variant: "outlined",
                          "item-title": "text",
                          "item-value": "value"
                        }, null, 8, ["modelValue"])
                      ]),
                      _: 1
                    }),
                    _createVNode(_component_v_col, {
                      cols: "12",
                      md: "4"
                    }, {
                      default: _withCtx(() => [
                        _createVNode(_component_v_select, {
                          modelValue: config.effect,
                          "onUpdate:modelValue": _cache[5] || (_cache[5] = $event => ((config.effect) = $event)),
                          label: "特效",
                          items: effectOptions,
                          variant: "outlined",
                          "item-title": "text",
                          "item-value": "value"
                        }, null, 8, ["modelValue"])
                      ]),
                      _: 1
                    })
                  ]),
                  _: 1
                }),
                _createVNode(_component_v_row, null, {
                  default: _withCtx(() => [
                    _createVNode(_component_v_col, {
                      cols: "12",
                      md: "12"
                    }, {
                      default: _withCtx(() => [
                        _createVNode(_component_v_select, {
                          modelValue: config.sites,
                          "onUpdate:modelValue": _cache[6] || (_cache[6] = $event => ((config.sites) = $event)),
                          label: "站点",
                          variant: "outlined",
                          "item-title": "text",
                          "item-value": "value",
                          items: sitesOptions.value,
                          multiple: "true",
                          chips: "true"
                        }, null, 8, ["modelValue", "items"])
                      ]),
                      _: 1
                    })
                  ]),
                  _: 1
                }),
                _createVNode(_component_v_row, null, {
                  default: _withCtx(() => [
                    _createVNode(_component_v_col, {
                      cols: "12",
                      md: "6"
                    }, {
                      default: _withCtx(() => [
                        _createVNode(_component_v_text_field, {
                          modelValue: config.include,
                          "onUpdate:modelValue": _cache[7] || (_cache[7] = $event => ((config.include) = $event)),
                          label: "包含",
                          variant: "outlined",
                          hint: "包含（关键字、正则式）"
                        }, null, 8, ["modelValue"])
                      ]),
                      _: 1
                    }),
                    _createVNode(_component_v_col, {
                      cols: "12",
                      md: "6"
                    }, {
                      default: _withCtx(() => [
                        _createVNode(_component_v_text_field, {
                          modelValue: config.exclude,
                          "onUpdate:modelValue": _cache[8] || (_cache[8] = $event => ((config.exclude) = $event)),
                          label: "排除",
                          variant: "outlined",
                          hint: "排除（关键字、正则式）"
                        }, null, 8, ["modelValue"])
                      ]),
                      _: 1
                    })
                  ]),
                  _: 1
                }),
                _createVNode(_component_v_row, null, {
                  default: _withCtx(() => [
                    _createVNode(_component_v_col, {
                      cols: "12",
                      md: "6"
                    }, {
                      default: _withCtx(() => [
                        _createVNode(_component_v_select, {
                          modelValue: config.filter_groups,
                          "onUpdate:modelValue": _cache[9] || (_cache[9] = $event => ((config.filter_groups) = $event)),
                          label: "优先级规则组",
                          variant: "outlined",
                          hint: "优先级规则组",
                          items: filterRuleGroups.value,
                          multiple: "true",
                          chips: "true",
                          "item-title": "text",
                          "item-value": "value"
                        }, null, 8, ["modelValue", "items"])
                      ]),
                      _: 1
                    }),
                    _createVNode(_component_v_col, {
                      cols: "12",
                      md: "6"
                    }, {
                      default: _withCtx(() => [
                        _createVNode(_component_v_text_field, {
                          modelValue: config.media_category,
                          "onUpdate:modelValue": _cache[10] || (_cache[10] = $event => ((config.media_category) = $event)),
                          label: "自定义类别",
                          variant: "outlined",
                          hint: "自定义类别"
                        }, null, 8, ["modelValue"])
                      ]),
                      _: 1
                    })
                  ]),
                  _: 1
                }),
                _createVNode(_component_v_row, null, {
                  default: _withCtx(() => [
                    _createVNode(_component_v_col, {
                      cols: "12",
                      md: "3"
                    }, {
                      default: _withCtx(() => [
                        _createVNode(_component_v_switch, {
                          modelValue: config.best_version,
                          "onUpdate:modelValue": _cache[11] || (_cache[11] = $event => ((config.best_version) = $event)),
                          label: "洗版",
                          color: "primary",
                          inset: "",
                          "persistent-hint": ""
                        }, null, 8, ["modelValue"])
                      ]),
                      _: 1
                    }),
                    _createVNode(_component_v_col, {
                      cols: "12",
                      md: "3"
                    }, {
                      default: _withCtx(() => [
                        _createVNode(_component_v_switch, {
                          modelValue: config.search_imdbid,
                          "onUpdate:modelValue": _cache[12] || (_cache[12] = $event => ((config.search_imdbid) = $event)),
                          label: "使用IMDB ID搜索",
                          color: "primary",
                          inset: "",
                          "persistent-hint": ""
                        }, null, 8, ["modelValue"])
                      ]),
                      _: 1
                    }),
                    _createVNode(_component_v_col, {
                      cols: "12",
                      md: "3"
                    }, {
                      default: _withCtx(() => [
                        _createVNode(_component_v_switch, {
                          modelValue: config.search,
                          "onUpdate:modelValue": _cache[13] || (_cache[13] = $event => ((config.search) = $event)),
                          label: "保存后开始搜索",
                          color: "primary",
                          inset: "",
                          "persistent-hint": ""
                        }, null, 8, ["modelValue"])
                      ]),
                      _: 1
                    }),
                    _createVNode(_component_v_col, {
                      cols: "12",
                      md: "3"
                    }, {
                      default: _withCtx(() => [
                        _createVNode(_component_v_switch, {
                          modelValue: config.update,
                          "onUpdate:modelValue": _cache[14] || (_cache[14] = $event => ((config.update) = $event)),
                          label: "更新至订阅并清空",
                          color: "primary",
                          inset: "",
                          "persistent-hint": ""
                        }, null, 8, ["modelValue"])
                      ]),
                      _: 1
                    })
                  ]),
                  _: 1
                }),
                _createVNode(_component_v_row, null, {
                  default: _withCtx(() => [
                    _createVNode(_component_v_col, {
                      cols: "12",
                      md: "12"
                    }, {
                      default: _withCtx(() => [
                        _createVNode(_component_v_textarea, {
                          modelValue: config.custom_words,
                          "onUpdate:modelValue": _cache[15] || (_cache[15] = $event => ((config.custom_words) = $event)),
                          label: "自定义识别词",
                          variant: "outlined",
                          rows: "3",
                          hint: "自定义识别词"
                        }, null, 8, ["modelValue"])
                      ]),
                      _: 1
                    })
                  ]),
                  _: 1
                })
              ]),
              _: 1
            }, 8, ["modelValue"])
          ]),
          _: 1
        }),
        _createVNode(_component_v_card_actions, null, {
          default: _withCtx(() => [
            _createVNode(_component_v_btn, {
              color: "secondary",
              onClick: notifySwitch
            }, {
              default: _withCtx(() => _cache[18] || (_cache[18] = [
                _createTextVNode("查看数据")
              ])),
              _: 1
            }),
            _createVNode(_component_v_spacer),
            _createVNode(_component_v_btn, {
              color: "primary",
              disabled: !isFormValid.value,
              onClick: saveConfig,
              loading: saving.value
            }, {
              default: _withCtx(() => _cache[19] || (_cache[19] = [
                _createTextVNode("保存配置")
              ])),
              _: 1
            }, 8, ["disabled", "loading"]),
            _createVNode(_component_v_btn, {
              color: "primary",
              onClick: notifyClose
            }, {
              default: _withCtx(() => _cache[20] || (_cache[20] = [
                _createTextVNode("关闭")
              ])),
              _: 1
            })
          ]),
          _: 1
        })
      ]),
      _: 1
    })
  ]))
}
}

};
const ConfigComponent = /*#__PURE__*/_export_sfc(_sfc_main, [['__scopeId',"data-v-c7321074"]]);

export { ConfigComponent as default };
