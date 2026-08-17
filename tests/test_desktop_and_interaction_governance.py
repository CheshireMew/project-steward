from __future__ import annotations

from governance_text_fixtures import *


class DesktopAndInteractionGovernanceTests(unittest.TestCase):
    def test_nested_scroll_surfaces_prove_their_own_responsive_geometry(
        self,
    ) -> None:
        for fragment in (
            "根页面没有溢出不代表内部表面成立",
            "内在最小尺寸可能把真实内容面撑宽",
            "实际滚动面的 `clientWidth`、`scrollWidth`",
            "只能证明根节点自身，不能替代嵌套表面",
            "长本地化标签、不换行路径或代码、宽工具栏",
            "几何证据说明是哪一层扩大",
            "两者必须来自同一状态和视口",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, LAYOUT_RESPONSIVE_TEXT)

    def test_command_discovery_uses_stable_identity_across_locales(self) -> None:
        interface_text = (
            SKILL_ROOT / "references" / "interface-guidelines.md"
        ).read_text(encoding="utf-8")
        ordered = (
            "每项行动使用一个稳定身份执行",
            "匹配投影由同一规范元数据确定性生成",
            "分别用本地化词和稳定语义别名找到同一行动",
            "由同一稳定身份执行正确结果",
        )
        positions = [interface_text.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))
        for fragment in (
            "不能只索引当前翻译",
            "不能让每种语言、每个入口各自维护同义词表",
            "用显示文字充当执行身份",
            "内部协议 ID 不因参与关联而自动成为可见标签",
            "遵守当前上下文可用性",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, interface_text)

    def test_committed_state_reaches_the_current_live_projection(self) -> None:
        ordered = (
            "唯一提交边界、聚合身份与提交版本",
            "提交成功后发布的语义事件",
            "打开中的编辑器、缓存聚合与派生视图怎样共享、协调、失效或重载",
            "界面绑定实际订阅的框架可观察属性、模型信号或事件",
            "无需关闭、重开或手工刷新即可观察的最终结果",
        )
        positions = [PREVENTION_TEXT.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))
        for fragment in (
            "普通方法，只证明重新调用时返回正确",
            "空集合到首项、首项到更多项以及移除末项",
            "没有活动缓存、动态投影或多个变更入口的普通单入口状态修改不增加这份合同",
            "保持同一编辑器或界面打开",
            "立即完成一次依赖新状态的后续编辑",
            "快照必须携带读取时的聚合身份、基线版本或等价顺序边界",
            "较晚返回的旧快照只能更新它负责的基线分区",
            "无损缓存增量并在快照提交后重放",
            "用受控屏障暂停正式快照生产者",
            "最终同时包含基线内容和实时增量",
            "覆盖其完整责任范围的快照",
            "只改变已列字段的补丁",
            "字段省略表示保持当前值",
            "显式清空必须使用合同内可区分的值或操作",
            "消费者不得把补丁当快照",
            "旧 generation、倒退版本或责任范围不匹配",
            "先发布包含多个字段的完整快照",
            "只更新一个高频指标的补丁",
            "证明其它字段仍然保留",
            "交错一个旧 generation 或倒退版本的补丁",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PREVENTION_TEXT)

        root_cause_route = MAIN_TEXT.split("## 根因治理", 1)[1].split(
            "## 外部工具兼容性",
            1,
        )[0]
        self.assertIn("局部状态、心跳或遥测更新", root_cause_route)
        self.assertIn("完整快照与局部补丁", root_cause_route)

        for fragment in (
            "权威状态正确但活动界面仍旧",
            "提交版本正确而没有事件",
            "事件正确但活动缓存仍是旧版本",
            "普通查询方法此刻能返回新值",
            "全局刷新、关闭重开、切换页面、固定延时",
            "**活动投影**",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, REMEDIATION_TEXT)

        for fragment in (
            "动态状态必须在不重开界面的情况下进入活动投影",
            "空集合 → 第一项 → 更多项 → 移除末项后重新为空",
            "界面更新后立即执行一次依赖新对象或新关系的后续编辑",
            "重新打开后状态正确只证明持久化",
            "动态状态与活动投影",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, IMPLEMENTATION_TEXT)


    def test_verification_coverage_is_bound_to_real_build_targets(self) -> None:
        for fragment in (
            "建立目标覆盖矩阵",
            "被目标条件排除的导入、类型、资源、权限和生命周期代码",
            "任何一项通过都不能替代另一项",
            "不能与修改前的其它层拼成一次完整通过",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PREVENTION_TEXT)

        self.assertIn("目标专属代码", PROJECT_AUDIT_TEXT)

    def test_public_audit_uses_live_remote_and_external_capability_evidence(
        self,
    ) -> None:
        for fragment in (
            "分开本地与实时远端事实",
            "本地缓存的远端跟踪引用",
            "实时远端默认分支与 HEAD",
            "不能把“没有读到”写成“远端不存在”",
            "验证外部默认能力的现实可用性",
            "项目自己的有界连接测试",
            "不能从一次 `401`、`402`、超时或官方资料冲突扩大成服务永久关闭",
            "未获运行授权时只报告合同证据",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PROJECT_AUDIT_TEXT)


    def test_new_file_writers_activate_construction_sites_and_residue_checks(
        self,
    ) -> None:
        for fragment in (
            "新增写入能力先建立副作用激活图",
            "原本只负责构造对象的调用点也可能成为新的生产者",
            "正式入口、CLI、后台任务、桌面窗口、smoke、测试 fixture 和共享 helper",
            "不得静默创建工作区",
            "实际测试必须消费副作用激活图",
            "不能为了得到干净结果直接删除来源不明的文件",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PREVENTION_TEXT)


    def test_deferred_desktop_ui_work_survives_only_its_owned_lifecycle(
        self,
    ) -> None:
        for fragment in (
            "延迟界面工作与对象生命周期",
            "`callLater`、排队信号",
            "生命周期足以覆盖实际执行期",
            "只服务当前页面或面板的工作随该对象销毁并停止",
            "继续排空事件循环",
            "即使没有改变退出码",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, DESKTOP_TEXT)


    def test_desktop_blocking_work_preserves_event_loop_and_result_identity(
        self,
    ) -> None:
        for fragment in (
            "界面线程与后台工作",
            "文件遍历、复制与大文件读写、网络和 provider 调用",
            "只有用代表性数据测得明确上界",
            "不能用开发机上“通常很快”",
            "操作身份、generation、输入内容身份、目标对象",
            "取消发生在任务开始前时不能创建工作目录",
            "不能触碰其它任务或用户已有文件",
            "框架规定只能由界面线程创建、转换或释放",
            "不 mock 掉正在验证的慢生产者",
            "在后台任务终态之前已经被事件循环处理",
            "正常完成、被新 generation 替代、取消以及关闭目标",
            "只断言工作线程已创建、处理器很快返回",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, DESKTOP_TEXT)

        for fragment in (
            "外部 CLI 是否允许配置完整命令字符串或原始 argv",
            "界面事件处理器是否同步执行随输入增长的文件、网络、provider、媒体、进程或序列化工作",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PROJECT_AUDIT_TEXT)


    def test_desktop_runtime_smoke_enumerates_lazy_surfaces_and_uses_fresh_process(
        self,
    ) -> None:
        for fragment in (
            "运行时表面清单与新鲜进程",
            "主窗口、其它主要窗口、首次访问才创建的页面或面板",
            "逐项首次打开、关闭或离开、再次进入",
            "`ReferenceError`、未定义组件、属性、信号、主题或翻译",
            "即使进程最终退出码为零",
            "`QApplication` 或等价应用单例、单实例锁、事件循环",
            "经过同一个生产 `main` 入口",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, DESKTOP_TEXT)


    def test_desktop_visual_materials_are_adopted_only_when_runtime_fit_is_proven(
        self,
    ) -> None:
        for fragment in (
            "先把结构、信息层级和互动机制与视觉表面分开",
            "不是“更现代”的默认皮肤",
            "实际任务密度、背景变化、目标 Windows 合成能力、QML 渲染路径",
            "高密度编辑器、长时间阅读区、参数面板",
            "稳定不透明表面",
            "目标硬件的真实 Windows 合成与 QML 渲染链",
            "稳定不透明回退",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, DESKTOP_TEXT)


    def test_desktop_validation_separates_offscreen_and_native_windows_evidence(
        self,
    ) -> None:
        for fragment in (
            "离屏或 headless 环境用于验证组件能够创建",
            "窗口管理器、系统标题栏、最大化与最小化",
            "DPI 与多显示器迁移、系统背景材质或 Windows 合成器行为",
            "真实 Windows 桌面会话和实际窗口",
            "稳定身份、创建点、框架配置与默认值",
            "Playwright `page.screenshot()` 和 `webContents.capturePage()`",
            "统一标为 `content-only`",
            "不能证明 `integrated` 或 `native-explicit`",
            "真实 Windows 整窗证据",
            "不修改产品来迁就测试驱动",
            "两层分别建立证据",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, DESKTOP_TEXT)


    def test_native_runtime_supply_and_process_isolation_are_governed(
        self,
    ) -> None:
        for fragment in (
            "原生依赖供应、ABI 与进程隔离",
            "源码存在不能证明目标平台存在可用的构建 SDK 和运行时二进制",
            "插件目录只包含插件",
            "进程级环境变量、DLL 搜索路径、插件搜索路径、全局工厂和注册表",
            "加载 → 打开 → 主界面消费真实数据",
            "后续导出或其它原生消费者继续完成用户结果",
            "重复创建和销毁",
            "用户明确要求不打包",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, DESKTOP_TEXT)

    def test_autonomous_closure_and_terminal_lifecycle_are_active(self) -> None:
        for fragment in (
            "内部轮次不是新的授权边界",
            "同一用户结果、同一受影响链和已冻结权限",
            "不能修改产品来迁就测试驱动或夹具",
            "新鲜运行证据",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(
                    fragment,
                    LEARNING_TEXT + PREVENTION_TEXT + REMEDIATION_TEXT,
                )

        for fragment in (
            "终止原因、结果状态和传输收尾",
            "事件消费完成",
            "有界时间内以退出码 0 正常退出",
            "标准输出和标准错误的编码",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, DESKTOP_TEXT)

        for fragment in (
            "当前活动窗口或表面",
            "非离屏且具有非零几何",
            "确认、已读或不再重放",
            "重新取得当前活动元素",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, IMPLEMENTATION_TEXT)

        self.assertIn(
            "发起者、终止原因、结果状态、传输收尾",
            LOG_TEXT,
        )
        self.assertNotIn("执行节奏与停止判断", AGENT_TEXT)
        self.assertNotIn("持久意图", AGENT_TEXT)

    def test_media_led_sections_preserve_content_value_and_scroll_ownership(
        self,
    ) -> None:
        for fragment in (
            "逐章建立内容价值合同",
            "不能替代名称、说明、过程、结果与有效入口",
            "说不清职责、关系和移除后果的素材不生成、不拆分、不进入页面",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PRODUCT_EXPERIENCE_TEXT)

        for fragment in (
            "章节推进合同",
            "有效滚动距离与真实内容视口高度之比",
            "不能用通用卡片、角色立绘或装饰素材替代项目本身",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, DESIGN_METHOD_TEXT)

        for fragment in (
            "不能用“统一删除位移和视差，只保留透明度与颜色”",
            "有效滚动屏数 = 该章实际消费的滚动距离",
            "进入构图和舞台完整就位后的内部推进使用独立进度边界",
            "后续普通章节恢复浏览器或平台的原生滚动所有权",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, INTERACTION_MOTION_TEXT)

        for fragment in (
            "取得开始、一个或多个有信息增量的中段、结束释放",
            "内部动画没有在舞台完整就位前结束",
            "文件存在、资源加载成功和风格相近不能证明",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, IMPLEMENTATION_TEXT)

    def test_restricted_execution_alternatives_have_a_complete_lifecycle(
        self,
    ) -> None:
        for fragment in (
            "### 受限执行路径与临时产物",
            "最小只读探测或无副作用预演",
            "准确目标根与临时根",
            "预期体积",
            "正式消费者",
            "清理授权",
            "等价写入",
            "写回前重新读取目标",
            "清理结果",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PREVENTION_TEXT)

    def test_page_order_and_scroll_performance_are_preventive_contracts(
        self,
    ) -> None:
        for fragment in (
            "先建立正式页面与状态顺序",
            "滚动性能责任合同",
            "脚本执行、样式与布局、绘制、合成、媒体解码与上传、资源加载与并发",
            "全部顺序消费者读取同一真源",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PRODUCT_EXPERIENCE_TEXT)

        for fragment in (
            "### 滚动性能先区分成本",
            "输入与主线程中的监听、脚本和时间线",
            "过场只消费目标解析结果",
            "不保存第二份目的地",
            "组件或文档顺序",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, INTERACTION_MOTION_TEXT)

        for fragment in (
            "全部顺序消费者",
            "媒体解码与上传",
            "恢复完整内容和正常用户路径",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, IMPLEMENTATION_TEXT)

    def test_layered_scroll_experience_selects_architecture_before_tuning(
        self,
    ) -> None:
        for fragment in (
            "体验保证与取舍合同",
            "相邻内容何时允许可见",
            "不能同时硬性保证完全原生的连续手感",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PRODUCT_EXPERIENCE_TEXT)

        for fragment in (
            "多层滚动先选唯一主架构",
            "原生内容流",
            "连续驻留舞台",
            "固定全屏换场",
            "分页落页",
            "有限局部步进",
            "低频媒体门",
            "进入构图",
            "完整就位",
            "内部演出",
            "终态释放",
            "再次进入",
            "自然反向",
            "保持终态",
            "明确重播",
            "按钮可以主动查看上一项，而反向滚轮可以直接交还页面",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, INTERACTION_MOTION_TEXT)

        for fragment in (
            "多个跨页面症状",
            "方向性输入所有权",
            "旧控制器退出条件",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PREVENTION_TEXT)

        for fragment in (
            "逐阶段对照所选主架构的硬保证",
            "第一下有效反向输入",
            "单项切换延迟、最终落点或一张稳定截图通过",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, IMPLEMENTATION_TEXT)


    def test_direct_manipulation_previews_then_commits_once_and_is_discoverable(
        self,
    ) -> None:
        ordered = (
            "按下时从正式生产者读取并冻结本次操作的持久基线",
            "当前正式消费者直接渲染这份预览",
            "释放时把最终值通过既有公共编辑边界提交一次",
            "取消、失去捕获或目标失效时恢复按下时的持久基线",
        )
        positions = [INTERACTION_MOTION_TEXT.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))
        for fragment in (
            "不逐次写入持久化、历史或撤销栈",
            "不得建立第二套时钟、坐标映射、状态机或恢复逻辑",
            "真实指针取得至少一个中间画面",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, INTERACTION_MOTION_TEXT)

        for fragment in (
            "新引入或提升为主操作的控件",
            "目标视口的自然初始任务路径",
            "实际滚动视口矩形以及两者的相交区域",
            "`visible = true`",
            "实际视口的截图或录屏",
            "先前相关的功能结果和截图同时失效",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, IMPLEMENTATION_TEXT)

    def test_direct_manipulation_separates_selection_relation_and_cohort(
        self,
    ) -> None:
        for fragment in (
            "选择集合、持久关联、本次操作集合和操作入口作为四个不同事实",
            "选择本身不能让已解除的关联继续进入本次操作",
            "从任一等价成员发起都必须得到同一对象集合和成对目标映射",
            "一次原子发布",
            "空白或无目标区域点击",
            "父级滚动或手势容器实际参与命中竞争",
            "直接调用控制器、拖动 helper 或提交函数只能证明内部计算",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, INTERACTION_MOTION_TEXT)

        for fragment in (
            "直接操作按入口矩阵验收",
            "从每个合同内等价入口使用真实指针、键盘或触摸",
            "父级滚动、手势或拖拽容器保持活动",
            "直接调用内部处理器、控制器方法、拖动 helper 或提交函数",
            "不能让选中高亮成为角色身份的唯一载体",
            "选择集合、持久关联、本次操作集合、父级容器命中竞争",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, IMPLEMENTATION_TEXT)


    def test_drag_create_preview_and_commit_share_one_placement_proposal(
        self,
    ) -> None:
        ordered = (
            "原始指针与拖拽热点",
            "对象锚点",
            "上下文放置不变量",
            "未锁定时的邻近吸附",
            "冲突与兼容性解析",
            "预期位置、目标容器、决策原因和目标状态版本",
        )
        positions = [INTERACTION_MOTION_TEXT.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))

        for fragment in (
            "所有预览与提交共同调用唯一放置决策边界",
            "命中即锁定，例如空目标首项必须落在原点或中心",
            "临时拖影、落点指示、读数和提示文字只消费这份放置方案",
            "不能显示原始指针位置却提交另一位置",
            "不能在界面和提交层分别实现一套放置规则",
            "释放时通过同一公共放置边界重新核对",
            "真实来源对象和真实指针",
            "远离普通吸附阈值但会触发上下文规则的位置",
            "目标非空或上下文规则不成立的分支",
            "原有自由放置与邻近吸附行为仍成立",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, INTERACTION_MOTION_TEXT)

    def test_existing_objects_use_explicit_relation_changes_and_accepted_variances(
        self,
    ) -> None:
        for fragment in (
            "已有对象使用一份关系变更合同",
            "目标所有者、相邻锚点与顺序",
            "“新增”只创建点名对象",
            "其余已经确认的关系继续保持",
            "把已接受差异从阻塞项中分开",
            "不得阻塞本轮交付的现有差异",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PREVENTION_TEXT)

        for fragment in (
            "直接消费改动前预防中的对象关系变更表",
            "不能把截图像素坐标保存为第二套布局真源",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PRODUCT_EXPERIENCE_TEXT)

        for fragment in (
            "读取已经冻结的接受差异台账",
            "不能在验收层自行改写合同",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, IMPLEMENTATION_TEXT)


    def test_visual_references_and_asset_batches_keep_source_specific_evidence(
        self,
    ) -> None:
        for fragment in (
            "每项输入分别建立素材证据合同",
            "不得从其它素材迁入的称号、符号、道具和设定",
            "每项交付必须能够独立使用",
            "视觉参考还要拆开结构、互动机制、运动关系、构图、内容密度与视觉皮肤",
            "不自动复制参考的配色、材质、容器、品牌元素和文案",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PRODUCT_EXPERIENCE_TEXT)

        for fragment in (
            "参考图是用户明确点名关系的证据",
            "当前项目继续负责视觉皮肤的已接受表面或设计系统",
            "只有在当前内容确实需要分组、裁切、状态、命中或表面层级时才成立",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, DESIGN_METHOD_TEXT)

        for fragment in (
            "面向后续动画的首帧建立运动空间合同",
            "各自的运动包络",
            "四周安全区与最终消费者可能遮挡的区域",
            "不是已经完成动作",
            "不能均匀围满主体并侵占运动包络",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, LAYOUT_RESPONSIVE_TEXT)


    def test_visual_evidence_is_opened_and_reviewed_at_target_scale(
        self,
    ) -> None:
        for fragment in (
            "实际打开、解码并在目标显示比例下查看",
            "文件存在、路径可读、数量正确、尺寸符合或捕获命令成功",
            "信息层级、内容密度、裁切、对比度、焦点与状态表达",
            "可见结论保持未知",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, IMPLEMENTATION_TEXT)


    def test_editable_visual_deliverables_and_scene_graph_transforms_are_governed(
        self,
    ) -> None:
        for fragment in (
            "最终可交付产物合同",
            "既有可编辑基线",
            "中间参考物",
            "不能因为生成成功或看起来接近就替代最终交付物",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PRODUCT_EXPERIENCE_TEXT)

        for fragment in (
            "层级可视对象变换合同",
            "父级或挂载点",
            "局部坐标系与轴向",
            "基础位置、旋转与缩放",
            "动画增量",
            "不能同时保留世界坐标硬编码",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, INTERACTION_MOTION_TEXT)

        for fragment in (
            "空间对象按视角与状态矩阵验收",
            "关键摄像机或观察方向",
            "姿态、交互与动画状态",
            "结构身份和最终画面不能互相代替",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, IMPLEMENTATION_TEXT)

        self.assertIn("可视层级、变换或动效所有权", MAIN_TEXT)

    def test_shared_visual_anchor_governs_surface_different_asset_batches(
        self,
    ) -> None:
        for fragment in (
            "共享视觉锚点与派生素材的依赖顺序",
            "全批次共享的视觉与构图变量",
            "只属于单项状态的动作、场景和特效变量",
            "直接依赖它的图片、视频、转场和界面消费者",
            "必须失效、重做或重新验收的派生物",
            "用户要求先判断共同锚点、再决定是否调整依赖状态时",
            "不受该变量影响的单项状态保持有效",
            "只消费已确认的共享锚点和仍然有效的派生物",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PRODUCT_EXPERIENCE_TEXT)

        for fragment in (
            "第一视觉焦点及其成立依据",
            "不得抢焦点的元素",
            "色相角色、面积、明度与饱和度关系",
            "尺度、透视、遮挡和虚实",
            "结构转折、材质响应、主辅光和接触关系",
            "不能由“3D、电影感、写实渲染”等标签代替",
            "用户纠正其中一个变量时只更新相应字段",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, DESIGN_METHOD_TEXT)


    def test_longer_than_expected_work_exposes_real_state_without_scope_drift(
        self,
    ) -> None:
        for fragment in (
            "把它视为过程透明度证据",
            "不是增加无意义播报",
            "不能用“流程需要”掩盖范围扩张",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, LEARNING_TEXT)

    def test_per_result_timing_separates_work_wait_rework_and_uncertainty(
        self,
    ) -> None:
        for fragment in (
            "按用户结果建立耗时账本",
            "主动检查与实现时间",
            "工具、构建和 CI 等待时间",
            "诊断、返工和重复验证时间",
            "等待用户决定或外部状态时间",
            "从请求到交付的墙钟时间",
            "无法准确还原",
            "不能为了回答完整而编造每项分钟数",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, LEARNING_TEXT)


    def test_technical_migration_does_not_authorize_visual_redesign(self) -> None:
        for fragment in (
            "不能把“迁移后更容易维护”和“迁移后应该换一种设计”合并成一个结果",
            "技术迁移与呈现变化分开授权",
            "实现迁移合同",
            "呈现保护合同",
            "设计改造入口",
            "保护区不能借改版被替换",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PREVENTION_TEXT)

        for fragment in (
            "技术迁移先证明呈现保护合同",
            "最早可见表面、加载过程、首个稳定页面",
            "不能用改版区的“更好看”抵消保护区回归",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, IMPLEMENTATION_TEXT)


    def test_external_media_production_uses_real_capabilities_and_lineage(
        self,
    ) -> None:
        for fragment in (
            "外部媒体生产能力与派生链",
            "过去经验和文件名不能补造不存在的选项",
            "时序来源再取帧",
            "可抠像源再合成",
            "批次源再拆分",
            "可直接使用 / 只使用已指明部分 / 需要重新生产 / 不进入项目",
            "完整不等于堆叠同义形容词",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PRODUCT_EXPERIENCE_TEXT)

        for fragment in (
            "准确源身份、中间处理、派生物和最终消费者",
            "只查看生成任务成功、批次大图、导出目录或消费端临时路径不能证明正式素材成立",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, IMPLEMENTATION_TEXT)


    def test_sensory_assets_separate_runtime_wiring_from_quality_acceptance(
        self,
    ) -> None:
        for fragment in (
            "感知素材的运行状态与验收边界",
            "参考输入、功能占位、检查投影、正式候选或已验收运行时素材",
            "功能接通与感知质量分别收口",
            "只记录为缓解措施",
            "低干扰默认值、独立调节或关闭入口",
            "视觉与听觉生产仍由相应专业能力负责",
            "接受状态：参考输入 / 功能占位 / 检查投影 / 正式候选 / 已验收运行时素材",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, PRODUCT_EXPERIENCE_TEXT)

        for fragment in (
            "分别核对功能链与感知质量",
            "程序音效能够发声、音量数值已经降低",
            "链路已接通、质量未验收",
            "缓解措施只验证它降低了当前影响",
            "本验收层不通过局部补丁替它作出审美决定",
            "感知素材状态：参考输入、功能占位、检查投影、正式候选与已验收运行时素材",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, IMPLEMENTATION_TEXT)


    def test_transparent_media_noise_is_governed_across_the_derivative_chain(
        self,
    ) -> None:
        for fragment in (
            "透明媒体的低 Alpha 画布噪点与派生产物分叉",
            "整幅低 Alpha 噪点、主体边缘污染和编码伪影",
            "固定阈值不能脱离素材证据成为默认值",
            "各交付编码与 poster",
            "至少一明一暗且与缺陷有反差的背景",
            "浏览器能播放、请求成功或单张透明网格预览都不能单独通过",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, INTERFACE_PROBLEM_TEXT)

        for fragment in (
            "母版、Alpha 处理、交付编码、poster、正式清单和活动消费者",
            "Alpha 数值与空间分布",
            "只读“存在 Alpha”或 `alpha_mode`",
            "只修播放文件而不重新生成同源 poster",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, IMPLEMENTATION_TEXT)


if __name__ == "__main__":
    unittest.main()
