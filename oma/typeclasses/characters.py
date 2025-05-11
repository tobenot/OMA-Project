"""
Characters

Characters are (by default) Objects setup to be puppeted by Accounts.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""

from evennia.objects.objects import DefaultCharacter
from evennia.utils import search, logger
import random

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
        This sets up the character's initial state and flags it for initial spawn.
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
        self.db.hunger = 100  # Max 100
        self.db.thirst = 100  # Max 100
        self.db.temperature = 37.0  # Normal body temperature
        self.db.stamina = 100  # Max 100

        # Skill cooldowns (placeholder for future skills)
        self.db.skill_cooldowns = {}

        # Combat state
        self.db.is_in_combat = False
        self.db.combat_target = None

        # --- Flag for initial spawn ---
        self.db.needs_initial_spawn = True
        logger.log_infomsg(f"PrimordialCharacter {self.key} (ID: {self.id}) created. Flagged for initial spawn.")

    def at_post_puppet(self, **kwargs):
        """
        Called every time the character is puppeted by an account (e.g. login, possession).
        We use this to handle the initial random spawn.
        """
        # Call the parent's at_post_puppet method first
        # Depending on which DefaultCharacter you inherit from, super() might not have it.
        # DefaultCharacter itself does not have at_post_puppet, but player-controlled
        # characters often gain it from a Player/Account mixin or a custom parent.
        # For safety, we can check or assume it's handled if your Character class structure implies it.
        # If DefaultCharacter is the direct parent that matters here and has no at_post_puppet,
        # then a super call for it is not needed for at_post_puppet.
        # Let's assume for now no super().at_post_puppet() is strictly needed unless Character class has it.

        if hasattr(self.db, 'needs_initial_spawn') and self.db.needs_initial_spawn:
            spawn_tag = "forest_spawn_point"
            possible_spawn_locations = search.search_object_by_tag(spawn_tag, typeclass="typeclasses.rooms.ForestRoom")

            if possible_spawn_locations:
                spawn_location = random.choice(possible_spawn_locations)
                logger.log_infomsg(f"PrimordialCharacter {self.key} (ID: {self.id}) at_post_puppet: Performing initial spawn to {spawn_location.key} (ID: {spawn_location.id}).")
                
                # Before moving, ensure the current location is not the target, to avoid messages if already there by chance
                if self.location != spawn_location:
                    self.move_to(spawn_location, quiet=False, move_hooks=True) # Make the move non-quiet so player sees room desc
                
                self.msg("你在一片陌生的森林中醒来，四周弥漫着潮湿的泥土气息...") # Custom message
                self.execute_cmd("look") # Force a look around
                
                del self.db.needs_initial_spawn # Remove the flag so it doesn't happen again
                # or self.db.needs_initial_spawn = False
            else:
                logger.log_warnmsg(f"PrimordialCharacter {self.key} (ID: {self.id}) at_post_puppet: No rooms found with tag '{spawn_tag}' for initial spawn.")
                self.msg("你在一片虚无中醒来，周围什么都没有...") # Fallback message
                self.execute_cmd("look") # Still look, even if in Limbo

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
        self.db.current_hp = self.db.max_hp / 2  # Respawn with half HP
        self.db.is_in_combat = False
        self.db.combat_target = None
        # Potentially move to a designated respawn location
        # self.move_to(some_limbo_room)
        self.msg("你在朦胧中醒来...")