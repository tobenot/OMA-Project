# OMA-Project

创建并激活 Python 虚拟环境（强烈推荐）：在安装 Evennia 之前，强烈建议创建一个 Python 虚拟环境。这会将 Evennia 的安装及其依赖项与系统的全局 Python 包隔离开，从而防止潜在的冲突，并确保项目环境的纯净 。  

    在你的项目文件夹中打开终端，运行（以 Python 3.11 为例）：
        Linux/macOS: $ python3.11 -m venv evenv
        Windows: $ py -m venv evenv (如果 python 命令指向正确的版本，也可以使用 python -m venv evenv)
    激活虚拟环境：
        Linux/macOS: $ source evenv/bin/activate
        Windows: $ evenv\Scripts\activate 激活后，你的终端提示符通常会显示虚拟环境的名称。


要更新已安装的 Evennia 到最新版本，可以使用以下命令 ：
 
$ pip install --upgrade evennia


quell 命令：作为超级用户，你拥有绕过游戏内限制的能力。为了以普通玩家的视角体验游戏或测试权限设置，你可以使用 quell 命令来临时压制你的超级用户权限。再次输入 unquell (或有时仅需 quell 再次切换) 可以恢复这些权限 。   