import { importShared } from './__federation_fn_import-DXLKUql0.js';
import { _ as _export_sfc } from './_plugin-vue_export-helper-pcqpp-6-.js';

const {toDisplayString:_toDisplayString,createTextVNode:_createTextVNode,resolveComponent:_resolveComponent,withCtx:_withCtx,createVNode:_createVNode,createElementVNode:_createElementVNode,renderList:_renderList,Fragment:_Fragment,openBlock:_openBlock,createElementBlock:_createElementBlock,createBlock:_createBlock,createCommentVNode:_createCommentVNode} = await importShared('vue');


const _hoisted_1 = { class: "plugin-page" };
const _hoisted_2 = { key: 0 };
const _hoisted_3 = { class: "whitespace-nowrap break-keep text-high-emphasis" };
const _hoisted_4 = {
  size: "small",
  class: "me-1 mb-1",
  variant: "elevated",
  color: "warning"
};
const _hoisted_5 = { class: "text-high-emphasis pt-1" };
const _hoisted_6 = { class: "text-sm my-1" };
const _hoisted_7 = { key: 1 };
const _hoisted_8 = { class: "text-sm" };
const _hoisted_9 = { class: "text-nowrap whitespace-nowrap" };
const _hoisted_10 = { key: 1 };

const {ref,onMounted} = await importShared('vue');


// 接收初始配置

const _sfc_main = {
  __name: 'Page',
  props: {
  api: {
    type: Object,
    default: () => {},
  },
},
  emits: ['action', 'switch', 'close'],
  setup(__props, { emit: __emit }) {

const props = __props;

// 组件状态
const title = ref('加載中...');
const histories = ref([]);
const loading = ref(true);
// 自定义事件，用于通知主应用刷新数据
const emit = __emit;

// 获取和刷新数据
async function refreshData() {
  loading.value = true;
  try {
    // 模拟API调用 - 实际开发中应使用 fetch 调用真实API
    const response = await props.api.get('plugin/SubscriptionQuery/getHistory');
    title.value = response.subscribe_search || '';
    histories.value = Array.isArray(response.histories) ? response.histories : [];
  } catch (err) {
    console.error('获取数据失败:', err);
  } finally {
    loading.value = false;
    // 通知主应用组件已更新
    emit('action');
  }
}

// 通知主应用切换到配置页面
function notifySwitch() {
  emit('switch');
}

// 通知主应用关闭组件
function notifyClose() {
  emit('close');
}

// 组件挂载时加载数据
onMounted(() => {
  refreshData();
});

return (_ctx, _cache) => {
  const _component_v_card_title = _resolveComponent("v-card-title");
  const _component_v_img = _resolveComponent("v-img");
  const _component_v_avatar = _resolveComponent("v-avatar");
  const _component_v_chip = _resolveComponent("v-chip");
  const _component_v_table = _resolveComponent("v-table");
  const _component_v_card_text = _resolveComponent("v-card-text");
  const _component_v_spacer = _resolveComponent("v-spacer");
  const _component_v_icon = _resolveComponent("v-icon");
  const _component_v_btn = _resolveComponent("v-btn");
  const _component_v_card_actions = _resolveComponent("v-card-actions");
  const _component_v_card = _resolveComponent("v-card");

  return (_openBlock(), _createElementBlock("div", _hoisted_1, [
    _createVNode(_component_v_card, null, {
      default: _withCtx(() => [
        _createVNode(_component_v_card_title, null, {
          default: _withCtx(() => [
            _createTextVNode("訂閲查詢:" + _toDisplayString(title.value), 1)
          ]),
          _: 1
        }),
        _createVNode(_component_v_card_text, { class: "pt-2" }, {
          default: _withCtx(() => [
            _createVNode(_component_v_table, {
              hover: "true",
              "fixex-header": "true",
              height: "500px"
            }, {
              default: _withCtx(() => [
                _cache[3] || (_cache[3] = _createElementVNode("thead", null, [
                  _createElementVNode("tr", null, [
                    _createElementVNode("th", { class: "text-start" }, "站点"),
                    _createElementVNode("th", { class: "text-start" }, "标题"),
                    _createElementVNode("th", { class: "text-start" }, "时间"),
                    _createElementVNode("th", { class: "text-start" }, "大小"),
                    _createElementVNode("th", { class: "text-start" }, "做种"),
                    _createElementVNode("th", { class: "text-start" }, "下载"),
                    _createElementVNode("th", { class: "text-start" })
                  ])
                ], -1)),
                (histories.value)
                  ? (_openBlock(), _createElementBlock("tbody", _hoisted_2, [
                      (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(histories.value, (item, index) => {
                        return (_openBlock(), _createElementBlock("tr", { key: index }, [
                          _createElementVNode("td", _hoisted_3, [
                            _createVNode(_component_v_avatar, {
                              class: "rounded",
                              variant: "flat"
                            }, {
                              default: _withCtx(() => [
                                _createVNode(_component_v_img, {
                                  src: item.site_icon
                                }, null, 8, ["src"])
                              ]),
                              _: 2
                            }, 1024),
                            _cache[0] || (_cache[0] = _createElementVNode("br", null, null, -1)),
                            _createElementVNode("span", _hoisted_4, _toDisplayString(item.site_name), 1)
                          ]),
                          _createElementVNode("td", null, [
                            _createElementVNode("div", _hoisted_5, _toDisplayString(item.title), 1),
                            _createElementVNode("div", _hoisted_6, _toDisplayString(item.description), 1),
                            (item.freedate_diff)
                              ? (_openBlock(), _createBlock(_component_v_chip, {
                                  key: 0,
                                  variant: "elevated",
                                  color: "secondary",
                                  size: "small",
                                  class: "me-1 mb-1"
                                }, {
                                  default: _withCtx(() => [
                                    _createTextVNode(_toDisplayString(item.freedate_diff), 1)
                                  ]),
                                  _: 2
                                }, 1024))
                              : _createCommentVNode("", true),
                            (item.labels)
                              ? (_openBlock(), _createElementBlock("div", _hoisted_7, [
                                  (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(item.labels, (label) => {
                                    return (_openBlock(), _createBlock(_component_v_chip, {
                                      variant: "elevated",
                                      color: "secondary",
                                      size: "small",
                                      class: "me-1 mb-1",
                                      key: label
                                    }, {
                                      default: _withCtx(() => [
                                        _createTextVNode(_toDisplayString(label), 1)
                                      ]),
                                      _: 2
                                    }, 1024))
                                  }), 128))
                                ]))
                              : _createCommentVNode("", true)
                          ]),
                          _createElementVNode("td", null, [
                            _createElementVNode("div", null, _toDisplayString(item.date_elapsed), 1),
                            _createElementVNode("div", _hoisted_8, _toDisplayString(item.pubdate), 1)
                          ]),
                          _createElementVNode("td", null, [
                            _createElementVNode("div", _hoisted_9, _toDisplayString(item.size), 1)
                          ]),
                          _createElementVNode("td", null, _toDisplayString(item.seeders), 1),
                          _createElementVNode("td", null, _toDisplayString(item.peers), 1),
                          _createElementVNode("td", null, [
                            _createElementVNode("div", null, [
                              _createVNode(_component_v_chip, {
                                variant: "elevated",
                                size: "default",
                                class: "me-1 mb-1 text-white bg-sky-500"
                              }, {
                                default: _withCtx(() => _cache[1] || (_cache[1] = [
                                  _createElementVNode("a", {
                                    href: "{{ item.page_url }}",
                                    target: "_blank"
                                  }, "查看详情", -1)
                                ])),
                                _: 1
                              })
                            ])
                          ])
                        ]))
                      }), 128))
                    ]))
                  : (_openBlock(), _createElementBlock("tbody", _hoisted_10, _cache[2] || (_cache[2] = [
                      _createElementVNode("tr", null, [
                        _createElementVNode("td", {
                          colspan: "7",
                          class: "text-center"
                        }, "没有数据")
                      ], -1)
                    ])))
              ]),
              _: 1
            })
          ]),
          _: 1
        }),
        _createVNode(_component_v_card_actions, null, {
          default: _withCtx(() => [
            _createVNode(_component_v_spacer),
            (loading.value)
              ? (_openBlock(), _createBlock(_component_v_btn, {
                  key: 0,
                  color: "primary",
                  onClick: refreshData,
                  loading: loading.value
                }, {
                  default: _withCtx(() => [
                    _createVNode(_component_v_icon, { left: "" }, {
                      default: _withCtx(() => _cache[4] || (_cache[4] = [
                        _createTextVNode("mdi-refresh")
                      ])),
                      _: 1
                    })
                  ]),
                  _: 1
                }, 8, ["loading"]))
              : _createCommentVNode("", true),
            _createVNode(_component_v_btn, {
              color: "primary",
              onClick: notifySwitch
            }, {
              default: _withCtx(() => [
                _createVNode(_component_v_icon, { left: "" }, {
                  default: _withCtx(() => _cache[5] || (_cache[5] = [
                    _createTextVNode("mdi-cog")
                  ])),
                  _: 1
                }),
                _cache[6] || (_cache[6] = _createTextVNode(" 配置 "))
              ]),
              _: 1
            }),
            _createVNode(_component_v_btn, {
              color: "primary",
              onClick: notifyClose
            }, {
              default: _withCtx(() => [
                _createVNode(_component_v_icon, { left: "" }, {
                  default: _withCtx(() => _cache[7] || (_cache[7] = [
                    _createTextVNode("mdi-close")
                  ])),
                  _: 1
                }),
                _cache[8] || (_cache[8] = _createTextVNode(" 关闭 "))
              ]),
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
const PageComponent = /*#__PURE__*/_export_sfc(_sfc_main, [['__scopeId',"data-v-710cb752"]]);

export { PageComponent as default };
