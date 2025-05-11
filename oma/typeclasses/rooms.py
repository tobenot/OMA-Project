"""
Room

Rooms are simple containers that has no location of their own.

"""

from evennia.objects.objects import DefaultRoom

from .objects import ObjectParent


class Room(ObjectParent, DefaultRoom):
    """
    Rooms are like any Object, except their location is None
    (which is default). They also use basetype_setup() to
    add locks so they cannot be puppeted or picked up.
    (to change that, use at_object_creation instead)

    See mygame/typeclasses/objects.py for a list of
    properties and methods available on all Objects.
    """

    pass


class ForestRoom(DefaultRoom):
    """
    This class represents a room in the "荧露树林" (Glimmerdew Forest).
    It can hold information about available resources, danger levels, etc.
    """
    def at_object_creation(self):
        """
        Called only once, when the object is first created.
        """
        super().at_object_creation()
        # Example environmental attributes
        self.db.has_forageables = True # Can players find edible plants here?
        self.db.has_wood = True       # Can players chop wood here?
        self.db.has_flint = False      # Are there flint stones to mine?
        self.db.danger_level = 1      # Arbitrary danger level (1 = low, 5 = high)
        self.db.description_details = "空气中弥漫着潮湿的泥土和腐叶的气息。"

    def get_display_name(self, looker, **kwargs):
        """
        Displays the name of the room.
        Can be customized to add [Forest] tag or similar if desired.
        """
        return super().get_display_name(looker, **kwargs)

    def return_appearance(self, looker, **kwargs):
        """
        This is called when a player looks at the room.
        We can customize this to add details about resources or dangers.
        """
        description = super().return_appearance(looker, **kwargs)
        # Add custom details to the room description
        details = []
        if self.db.has_forageables:
            details.append("你注意到这里似乎有一些可食用的植物。")
        if self.db.has_wood:
            details.append("周围有不少树木，可以砍伐。")
        if self.db.has_flint:
            details.append("你看到一些岩石，也许能找到燧石。")
        
        if self.db.description_details:
            description += f"\n{self.db.description_details}"
            
        if details:
            description += "\n" + "\n".join(details)

        # Could add danger level hints for higher perception characters
        # if looker.db.perception > 7 and self.db.danger_level > 3:
        #     description += "\n你隐约感觉到这片区域有些危险。"
            
        return description
