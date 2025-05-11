r"""
Evennia settings file.

The available options are found in the default settings file found
here:

https://www.evennia.com/docs/latest/Setup/Settings-Default.html

Remember:

Don't copy more from the default file than you actually intend to
change; this will make sure that you don't overload upstream updates
unnecessarily.

When changing a setting requiring a file system path (like
path/to/actual/file.py), use GAME_DIR and EVENNIA_DIR to reference
your game folder and the Evennia library folders respectively. Python
paths (path.to.module) should be given relative to the game's root
folder (typeclasses.foo) whereas paths within the Evennia library
needs to be given explicitly (evennia.foo).

If you want to share your game dir, including its settings, you can
put secret game- or server-specific settings in secret_settings.py.

"""

# Use the defaults from Evennia unless explicitly overridden
from evennia.settings_default import *

######################################################################
# Evennia base server config
######################################################################

# This is the name of your game. Make it catchy!
SERVERNAME = "oma"

######################################################################
# Typeclass bases
######################################################################
# Server-side session class for sessions connecting to the Portal.
# SERVER_SESSION_CLASS = "evennia.server.serversession.ServerSession"
# Base typeclass for all objects.
# BASE_OBJECT_TYPECLASS = "evennia.objects.objects.DefaultObject"
# Base typeclass for all characters directly controlled by players.
BASE_CHARACTER_TYPECLASS = "typeclasses.characters.PrimordialCharacter"
# Base typeclass for all rooms.
# BASE_ROOM_TYPECLASS = "evennia.objects.objects.DefaultRoom"
# Base typeclass for all exits.
# BASE_EXIT_TYPECLASS = "evennia.objects.objects.DefaultExit"
# Base typeclass for all Channels.
# BASE_CHANNEL_TYPECLASS = "evennia.comms.comms.DefaultChannel"
# Base typeclass for all Player accounts.
# BASE_ACCOUNT_TYPECLASS = "evennia.accounts.accounts.DefaultAccount"
# Typeclass for Scripts.
# BASE_SCRIPT_TYPECLASS = "evennia.scripts.scripts.DefaultScript"

######################################################################
# Settings given in secret_settings.py override those in this file.
######################################################################
try:
    from server.conf.secret_settings import *
except ImportError:
    print("secret_settings.py file not found or failed to import.")

GLOBAL_SCRIPTS = {
    "needs_system": {  # 这个键名 "needs_system" 会成为脚本在游戏中的默认key
        "typeclass": "scripts.needs_system.NeedsSystem",  # 指向脚本类的Python路径
        "interval": 60,  # 脚本的 at_repeat() 方法被调用的时间间隔（秒）
        "repeats": -1,   # 脚本重复执行的次数。-1 代表无限次重复
        "desc": "Manages character needs.",
        # "obj": some_object, # （可选）如果脚本需要绑定到特定对象而不是纯全局
        # "start_delay": False, # （可选）如果为True，脚本在首次启动时不立即执行其at_repeat方法，而是等待第一个interval过去
        # "persistent": True, # （可选）通常全局脚本都应持久化，这也是默认行为。脚本内部的 self.persistent = True 也会确保这点。
    }
}

BATCHCODE_PATHS = ["world","world.map", "evennia.contrib", "evennia.contrib.tutorials"]