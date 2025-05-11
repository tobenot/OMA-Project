"""
Characters

Characters are (by default) Objects setup to be puppeted by Accounts.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""

from evennia.objects.objects import DefaultCharacter

from .objects import ObjectParent


class Character(ObjectParent, DefaultCharacter):
    """
    The Character just re-implements some of the Object's methods and hooks
    to represent a Character entity in-game.

    See mygame/typeclasses/objects.py for a list of
    properties and methods available on all Object child classes like this.

    """

    pass


class PrimordialCharacter(DefaultCharacter):
    """
    This class represents the player character in the "茹毛饮血" (Primordial) setting.
    It includes basic attributes and needs for survival.
    """
    def at_object_creation(self):
        """
        Called only once, when the object is first created.
        This sets up the character's initial state.
        """
        super().at_object_creation()
        # Set initial description
        self.db.desc = "一个身上被藤蔓覆盖的人类，看起来很瘦弱，眼神中带着一丝警惕和茫然。"

        # Base attributes (as per ERM_dev.md)
        self.db.strength = 5
        self.db.agility = 5
        self.db.constitution = 5
        self.db.perception = 5

        # Combat-related attributes (as per ERM_dev.md)
        self.db.max_hp = 50
        self.db.current_hp = 50
        self.db.attack_power = 5
        self.db.defense = 1
        self.db.attack_speed = 2.5  # Seconds per attack

        # Needs system attributes (placeholders, will be managed by NeedsSystem script)
        self.db.hunger = 100 # Max 100
        self.db.thirst = 100 # Max 100
        self.db.temperature = 37.0 # Normal body temperature
        self.db.stamina = 100 # Max 100

        # Skill cooldowns (placeholder for future skills)
        self.db.skill_cooldowns = {}
        
        # Combat state
        self.db.is_in_combat = False
        self.db.combat_target = None

    def at_damage(self, amount, attacker=None):
        """
        Called when the character takes damage.
        """
        self.db.current_hp -= amount
        if attacker:
            self.msg(f"你受到了来自 {attacker.key} 的 {amount} 点伤害！")
        else:
            self.msg(f"你受到了 {amount} 点伤害！")

        if self.db.current_hp <= 0:
            self.at_death(killer=attacker)

    def at_death(self, killer=None):
        """
        Called when the character's HP drops to 0 or below.
        """
        if killer:
            self.msg(f"你被 {killer.key} 杀死了！")
            self.location.msg_contents(f"{self.key} 被 {killer.key} 杀死了。", exclude=self)
        else:
            self.msg("你死了！")
            self.location.msg_contents(f"{self.key} 死了。", exclude=self)

        # Basic death penalty: move to a "limbo" room or starting room
        # For now, just heal up and clear combat state
        self.db.current_hp = self.db.max_hp / 2 # Respawn with half HP
        self.db.is_in_combat = False
        self.db.combat_target = None
        # Potentially move to a designated respawn location
        # self.move_to(some_limbo_room)
        self.msg("你在朦胧中醒来...")
