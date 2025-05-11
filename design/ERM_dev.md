**开发方案：“茹毛饮血” (Windows 服务器 & 即时制战斗)**

**当前日期：** 2025年5月11日

**阶段零：环境搭建与基础 (Windows)**

1.  **安装 Python：**
    * 从 Python 官网下载最新稳定版的 Python (如 3.10+)。
    * 安装时务必勾选 "Add Python to PATH"。
    * 验证安装：打开命令提示符(CMD)或 PowerShell，输入 `python --version` 和 `pip --version`。
2.  **安装 Git：**
    * 从 Git官网 下载并安装 Git for Windows。这将提供版本控制能力。
3.  **创建项目目录与虚拟环境：**
    * 在你喜欢的位置创建一个项目主文件夹 (例如 `D:\MUD_Projects\`)。
    * 打开 CMD 或 PowerShell，导航到该目录：`cd D:\MUD_Projects\`
    * 创建虚拟环境：`python -m venv rumaoyinxue_env`
    * 激活虚拟环境：`rumaoyinxue_env\Scripts\activate` (激活后，命令行提示符前会出现 `(rumaoyinxue_env)`)
4.  **安装 Evennia：**
    * 在激活的虚拟环境下：`pip install evennia`
5.  **初始化 Evennia 游戏项目：**
    * `evennia_init rumaoyinxue` (游戏项目文件夹会被创建在 `D:\MUD_Projects\rumaoyinxue_env\rumaoyinxue`)
    * `cd rumaoyinxue`
6.  **首次运行与超级用户创建：**
    * `evennia migrate`
    * `evennia start` (服务器启动，会显示 Telnet 和 Web 客户端端口)
    * 用 MUD 客户端 (如 Mudlet, PuTTY) 连接 `localhost:4000`。
    * 输入 `create <玩家名> <密码>` 来创建你的第一个角色。
    * 在游戏中，输入 `@py self.is_superuser = True` 将你的角色提升为超级用户。
    * 停止服务器：在 Evennia 的 CMD 窗口按 `Ctrl+C`，或在游戏内用超管账户输入 `@shutdown`。
7.  **代码编辑器/IDE：**
    * 推荐 VS Code (Visual Studio Code)，它对 Python 支持良好。

**阶段一：Evennia 核心概念巩固与游戏基础框架**

1.  **学习/复习 Evennia 核心：**
    * Typeclasses (`objects.py`, `characters.py`, `rooms.py`)
    * Commands (`commands/command.py`, `commands/default_cmds.py`)
    * Scripts (`scripts/scripts.py`)
    * Attributes (`.db`, `.ndb`)
    * `settings.py` 的配置
2.  **玩家角色 (`PrimordialCharacter`)：**
    * 在 `typeclasses/characters.py` 创建，继承 `DefaultCharacter`。
    * `at_object_creation()`：设置初始描述（藤蔓蔽体）、基础属性（力量、敏捷等），以及**战斗相关属性**（如 `self.db.max_hp`, `self.db.current_hp`, `self.db.attack_power`, `self.db.defense`, `self.db.attack_speed = 2.5` (表示攻击间隔秒数)）。
    * 在 `settings.py` 中设置 `BASE_CHARACTER_TYPECLASS`。
3.  **需求系统 (`NeedsSystem` Script)：**
    * 在 `scripts/` 下创建全局脚本，按固定间隔更新饥饿、干渴、体温、精力。
    * 影响：低状态时发送消息，可能降低战斗属性或造成微量伤害。
4.  **世界构建 (“荧露树林”)：**
    * 用 `@dig` 创建房间，设置描述，连接出口。
    * 考虑创建自定义房间类型 `ForestRoom` (`typeclasses/rooms.py`)，可以包含环境信息（如资源点、危险等级）。

**阶段二：核心生存与创造机制**

1.  **资源收集 (Commands)：**
    * `CmdForage`, `CmdChopWood`, `CmdMineFlint` 等。
    * 检查环境（房间是否有资源）、玩家状态（是否有工具，精力是否足够）。
    * 成功则给予物品，消耗精力。
2.  **物品原型与基础制造 (`CmdCraft`)：**
    * 在 `world/prototypes.py` 定义物品原型（工具、食物、篝火材料）。
    * 创建 `CmdCraft`，根据配方（可以硬编码或用字典存储）检查玩家物品，消耗材料，生成新物品。
3.  **基础建造 (`CmdBuildCampfire`)：**
    * 消耗物品（如木柴、燧石），在房间内生成一个“篝火”对象。
    * 篝火对象可以是一个有持续时间的 `Script`，提供温暖并允许烹饪。

**阶段三：即时制战斗系统核心 (自定义开发)**

这将是工作量最大的部分，因为没有现成的即时制战斗 Contrib。

1.  **战斗状态与目标：**
    * 角色 `db` 属性：`self.db.is_in_combat = False`, `self.db.combat_target = None`。
2.  **进入/离开战斗命令：**
    * `CmdAttack <目标>`:
        * 验证目标是否存在且可被攻击。
        * 设置 `self.db.is_in_combat = True` 和 `self.db.combat_target = 目标对象`。
        * 通知双方进入战斗。
        * **启动攻击脚本** (见下文) 或通知已有的脚本开始攻击。
    * `CmdFlee`: 尝试脱离战斗（可能有成功率判定，消耗精力）。成功则清除战斗状态。
3.  **核心攻击脚本 (`CombatTickScript`):**
    * 这是一个附加到每个可战斗角色 (玩家和NPC) 身上的脚本。
    * `at_script_creation()`: 获取宿主 (host) 的攻击速度 (`host.db.attack_speed`)，并以此设置脚本的 `interval`。
    * `at_repeat()`:
        * 检查宿主是否在战斗中 (`host.db.is_in_combat`) 且有目标 (`host.db.combat_target`)。
        * 如果目标已死亡或不在同一房间，清除战斗状态，停止脚本或使其无效。
        * **执行攻击：**
            * 计算命中几率 (例如，基于敏捷差异)。
            * 如果命中，计算伤害 ( `host.db.attack_power` vs `target.db.defense`)。
            * 对目标应用伤害：`target.db.current_hp -= damage_amount`。
            * 发送战斗消息给房间内的玩家（“A攻击了B，造成了X点伤害！”）。
            * 检查目标是否死亡 (`target.db.current_hp <= 0`)。
    * **启动/停止：**
        * 当角色执行 `CmdAttack` 时，如果此脚本不在运行，则添加并启动它。
        * 当战斗结束 (逃跑、一方死亡、目标丢失)，停止并删除此脚本，或通过设置一个标志使其在 `at_repeat` 中不执行任何操作。
4.  **受伤与死亡：**
    * 在 `PrimordialCharacter` 上创建 `at_damage(self, amount, attacker)` 方法：
        * 处理伤害减免 (如果设计了护甲值)。
        * `self.msg(f"{attacker.key} 对你造成了 {amount} 点伤害！")`
        * `if self.db.current_hp <= 0: self.at_death(killer=attacker)`
    * `at_death(self, killer)` 方法：
        * 发送死亡消息。
        * 处理死亡惩罚（例如，掉落物品，经验损失，传送到重生点）。
        * 清除战斗状态。
5.  **技能系统 (初步)：**
    * `CmdUseSkill <技能名> [目标]`
    * 技能定义：可以存在一个全局字典中，包含效果、冷却时间、消耗等。
        ```python
        SKILLS = {
            "猛击": {"cost_stamina": 10, "cooldown": 5, "damage_multiplier": 1.5, "type": "attack"},
            "治疗术": {"cost_stamina": 15, "cooldown": 10, "heal_amount": 20, "type": "heal"}
        }
        ```
    * 角色 `db` 属性：`self.db.skill_cooldowns = {"猛击": 0}` (0表示可用，否则存储到期的时间戳)。
    * 命令执行时：
        * 检查精力、冷却时间。
        * 如果是攻击技能，则在下一个攻击点（或立即，取决于设计）造成额外效果。
        * 设置技能冷却时间：`self.db.skill_cooldowns["猛击"] = time.time() + SKILLS["猛击"]["cooldown"]`。
        * `CombatTickScript` 或另一个专门的 `EffectScript` 可以用来处理持续性技能效果和冷却时间的递减。

**阶段四：NPC 与互动**

1.  **怪物NPC (`MonsterCharacter`)：**
    * 创建继承自 `PrimordialCharacter` 的新类型类。
    * 赋予其基础AI：
        * **仇恨范围：** 可以使用一个简单的 `Script` 定期检查周围是否有玩家，或者在房间的 `at_object_enter` 钩子中检测。
        * **自动攻击：** 一旦发现玩家，自动执行类似 `CmdAttack` 的逻辑，并启动其自身的 `CombatTickScript`。
        * **战斗逻辑：** （可选）简单的技能使用逻辑。
    * 在荧露树林中放置怪物原型。
2.  **“火堆营地”原始人NPC：**
    * **对话：** 可以考虑使用 `evennia.contrib.npcs.talking_npc`。为NPC定义简单的对话树和关键词响应。
        * 安装方法：主要是在NPC类型类中继承 `TalkingNPC` 并设置 `self.dialogue_tree`。
    * **交易：** 可以考虑使用 `evennia.contrib.game_systems.barter`。
        * 安装方法：可能需要在NPC和玩家角色上添加交易相关的命令集。NPC需要逻辑来决定接受哪些交易。

**阶段五：环境增强与 Contribs 集成**

1.  **天气系统 (`evennia.contrib.game_systems.weather`)：**
    * 安装：通常是在游戏中用 `@scripts/add evennia.contrib.game_systems.weather.WeatherScript` 启动一个全局天气脚本。
    * 集成：修改你的 `NeedsSystem`，使其读取当前房间或区域的天气状况（通常天气脚本会将信息存储在房间的属性或标签上），并据此调整玩家的“温暖度”变化。
2.  **高级制造 (可选 `evennia.contrib.game_systems.crafting`)：**
    * 如果你觉得你的基础制造系统不够用，可以研究这个 Contrib。它提供了更结构化的配方管理和制造站概念。
    * 安装：可能涉及定义配方数据，并让你的 `CmdCraft` 使用此 Contrib 提供的函数。
3.  **魔法线索与世界观：**
    * 通过物品描述、房间描述、特殊地点的神秘现象来逐步揭示。
    * “发光水晶”可以是一个有特殊 `examine` 描述的对象，或者 `touch` 命令会触发一次性的微弱效果（直接修改属性，然后进入“冷却”）。

**阶段六：测试、迭代与平衡**

* 不断测试所有功能，特别是战斗系统。
* 根据测试结果调整数值（怪物强度、物品效果、制造难度、生存需求消耗速度等）。
* 邀请朋友进行小范围测试，收集反馈。

**阶段七：部署到 Windows 服务器**

1.  **代码同步：**
    * 使用 Git 将你本地的代码库推送到远程仓库（如 GitHub, GitLab），然后在服务器上拉取。或者直接用 `scp` 或 `WinSCP` 传输整个游戏文件夹。
2.  **服务器环境配置：**
    * 在服务器上重复阶段零的 Python 安装、虚拟环境创建和 Evennia 安装步骤。
3.  **Evennia 生产配置 (`mygame/server/conf/settings.py`)：**
    * `ALLOWED_HOSTS = ["your_server_ip_address", "your_domain_name_if_any"]`
    * `TELNET_PORTS = [4000]` (或其他你想要的端口)
    * `WEBSERVER_PORTS = [(8001, 8001)]` (第一个是Evennia监听的，第二个是外部看到的。如果想用80端口，需要管理员权限或反向代理)
    * `MAX_CHAR_LIMIT = 50` (根据服务器性能调整)
    * 数据库：默认 SQLite (`mygame/server/evennia.db3`) 对初期够用。若需更强性能，可在 Windows 上安装 PostgreSQL 并配置 Evennia 使用它（参照 Evennia 文档）。
4.  **Windows 防火墙：**
    * 打开 Windows Defender 防火墙高级设置。
    * 创建新的“入站规则”，允许 TCP 流量通过你为 Telnet (如 4000) 和 Web 客户端 (如 8001 或 80) 设置的端口。
5.  **持久化运行 Evennia 服务器：**
    * **开发阶段：** 直接在激活虚拟环境的 CMD 窗口运行 `evennia start` 就行。关闭窗口服务器就停了。
    * **生产/长期运行：**
        * **NSSM (Non-Sucking Service Manager):** 这是推荐的方案。NSSM 可以将任何应用程序（包括Python脚本）作为 Windows 服务运行。
            1.  下载 NSSM。
            2.  `nssm install EvenniaMUD` (服务名随意)
            3.  Path: `C:\Python3X\python.exe` (你的Python路径)
            4.  Startup directory: `D:\MUD_Projects\rumaoyinxue_env\rumaoyinxue` (你的游戏项目路径)
            5.  Arguments: `D:\MUD_Projects\rumaoyinxue_env\Scripts\evennia_portal.py start --production` (注意这里用 `evennia_portal.py` 并确保路径正确，或者直接是 `evennia start --production` 如果 `evennia` 命令在服务环境下能被找到路径) *更可靠的是指向虚拟环境中的 `evennia.exe` 或 `evennia_runner.py`。你需要测试具体的命令组合，确保它能在NSSM环境下正确启动虚拟环境和Evennia。* 确保它在 `evennia start --production` 模式下运行。
            6.  配置日志、依赖服务等。
            7.  `nssm start EvenniaMUD`
        * **`evennia start --production`：** 在某些 Evennia 版本和 Windows 配置下，这可能能让 Evennia 作为后台进程运行。但不如 NSSM 可靠。
        * **计划任务 (Scheduled Task):** 可以设置一个在系统启动时运行的计划任务，但管理和日志不如服务方便。

6.  **测试连接：**
    * 从其他电脑用 MUD 客户端连接 `your_server_ip_address:4000`。
    * 用浏览器访问 `http://your_server_ip_address:8001`。

**开发建议：**

* **版本控制 (Git)！** 从第一行代码开始就用 Git。
* **小步快跑，频繁测试。** 先让一个极简的即时攻击循环跑起来，再逐步增加复杂性。
* **阅读 Evennia 源码和文档。** 特别是 `DefaultCharacter`、`Script` 基类以及你感兴趣的 Contribs 的代码。
* **日志！** 使用 Evennia 的日志系统 (`from evennia.utils import logger`) 或 Python 的 `logging` 模块来记录关键事件和错误，方便调试。

这个方案更侧重于你自定义即时战斗的需求，并考虑了 Windows 环境。祝你开发顺利！