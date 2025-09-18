import random
import enum
import json
import random

__version__ = '0.0.4'

class Error:
    """class containing all errors
    """
    class AttachmentNotAvailableError(Exception):
        """error for when an AttachmentType isn't available on a Weapon
        """
        pass

class _util:
    @staticmethod
    def random_kvp_from_dict(dic: dict):
        """selects a random key and value from the given dictionary

        Args:
            dic (dict): dictionary containing data

        Returns:
            tuple: key and value tuple randomly selected from the given dictionary
        """
        r = random.randint(0, len(dic)-1)
        key = list(dic.keys())[r]
        val = dic[key]
        return key, val

    @staticmethod
    def random_value_from_list(ls: list):
        """selects a random vale from the given list

        Args:
            ls (list): list containing data

        Returns:
            any: value randomly picked from the given list
        """
        return ls[random.randint(0, len(ls)-1)]

    @staticmethod
    def get_scope_enum(category):
        """gets and returns the correct ScopeAttachment enum for the given ScopeCategory

        Args:
            category (ScopeCategory): scope category to return matching type for

        Raises:
            TypeError: when an invalid ScopeCategory type is passed

        Returns:
            Enum: matching ScopeAttachment for the given ScopeCategory
        """
        if category == Weapon.Attachment.ScopeCategory.IRON or category == Weapon.Attachment.ScopeCategory.IRON.name:
            return Weapon.Attachment.IronSights
        elif category == Weapon.Attachment.ScopeCategory.NONMAGNIFIED or category == Weapon.Attachment.ScopeCategory.NONMAGNIFIED.name:
            return Weapon.Attachment.NonmagnifiedScope
        elif category == Weapon.Attachment.ScopeCategory.MAGNIFIED or category == Weapon.Attachment.ScopeCategory.MAGNIFIED.name:
            return Weapon.Attachment.MagnifiedScope
        elif category == Weapon.Attachment.ScopeCategory.TELESCOPIC or category == Weapon.Attachment.ScopeCategory.TELESCOPIC.name:
            return Weapon.Attachment.TelescopicScope
        else:
            raise TypeError(f'Value {category} of type {type(category).__name__} for category not valid')

    @staticmethod
    def get_attachment_type_from_string(attachment: str):
        """gets a matching AttachmentType from the given attachment string

        Args:
            attachment (str): name of the attachment

        Raises:
            TypeError: if attachment is not of type str

        Returns:
            Enum: matching AttachmentType for the given attachment name
        """
        if not isinstance(attachment, str):
            raise TypeError(f'attachment must be of type str, not {type(attachment).__name__}')

        type_map = {
            'IRON': Weapon.Attachment.IronSights.IRON,
            'RED_DOT_A': Weapon.Attachment.NonmagnifiedScope.RED_DOT_A,
            'RED_DOT_B': Weapon.Attachment.NonmagnifiedScope.RED_DOT_B,
            'RED_DOT_C': Weapon.Attachment.NonmagnifiedScope.RED_DOT_C,
            'HOLO_A': Weapon.Attachment.NonmagnifiedScope.HOLO_A,
            'HOLO_B': Weapon.Attachment.NonmagnifiedScope.HOLO_B,
            'HOLO_C': Weapon.Attachment.NonmagnifiedScope.HOLO_C,
            'HOLO_D': Weapon.Attachment.NonmagnifiedScope.HOLO_D,
            'REFLEX_A': Weapon.Attachment.NonmagnifiedScope.REFLEX_A,
            'REFLEX_B': Weapon.Attachment.NonmagnifiedScope.REFLEX_B,
            'REFLEX_C': Weapon.Attachment.NonmagnifiedScope.REFLEX_C,
            'REFLEX_D': Weapon.Attachment.NonmagnifiedScope.REFLEX_D,
            'MAGNIFIED_A': Weapon.Attachment.MagnifiedScopes.MAGNIFIED_A,
            'MAGNIFIED_B': Weapon.Attachment.MagnifiedScopes.MAGNIFIED_B,
            'MAGNIFIED_C': Weapon.Attachment.MagnifiedScopes.MAGNIFIED_C,
            'TELESCOPIC_A': Weapon.Attachment.TelescopicScopes.TELESCOPIC_A,
            'TELESCOPIC_B': Weapon.Attachment.TelescopicScopes.TELESCOPIC_B,
            'TELESCOPIC_C': Weapon.Attachment.TelescopicScopes.TELESCOPIC_C,
            'COMP': Weapon.Attachment.BarrelAttachment.COMP,
            'EXT': Weapon.Attachment.BarrelAttachment.EXT,
            'FLASH': Weapon.Attachment.BarrelAttachment.FLASH,
            'MUZZLE': Weapon.Attachment.BarrelAttachment.MUZZLE,
            'SUPP': Weapon.Attachment.BarrelAttachment.SUPP,
            'NONE': Weapon.Attachment.BarrelAttachment.COMP,
            'ANGLED': Weapon.Attachment.GripAttachment.ANGLED,
            'HORI': Weapon.Attachment.GripAttachment.HORI,
            'VERT': Weapon.Attachment.GripAttachment.VERT,
            'LASER': Weapon.Attachment.UnderbarrelAttachment.LASER,
            'NONE': Weapon.Attachment.GenericAttachment.NONE
        }

        try: return type_map[attachment]
        except KeyError: return None

    @staticmethod
    def try_cast_enums(key: str, *enums) -> any:
        """static method to cast the key passed into every enum class passed, returning if there's no error thrown

        Args:
            key (str): key to use to find matching keys

        Returns:
            any | None: either returns the object in whatever enum successfully cast first, or None if no new object was created
        """
        for e in enums:
            try:
                new_obj = e[key]
            except:
                continue
            return new_obj
        return None

    @staticmethod
    def operator_data() -> dict:
        """returns the operator data

        Returns:
            dict: all the operator data
        """
        return {
            "attack": [],
            "defend": [
                {
                    "name": "SENTRY",
                    "type": ["SUP"],
                    "difficulty": 1,
                    "speed": 2,
                    "health": 2,
                    "ability": "SPECIAL",
                    "gadgets": ["BARB", "BP", "DEP", "OBV", "IMP", "CF", "PROX"],
                    "weapons": {
                        "primaries": [
                            {
                                "NAME": "COMMANDO_9",
                                "TYPE": "AR",
                                "DAMAGE": 36,
                                "FIRE_RATE": 780,
                                "MAG": 25,
                                "MAX": 176,
                                "ADS": 0.49,
                                "RELOAD": 2.5,
                                "RSM": 0,
                                "DEST": "LOW",
                                "ATTACHMENTS": {
                                    "SCOPES": {
                                        "IRON": ["IRON"],
                                        "NONMAGNIFIED": ["RED_DOT_A", "RED_DOT_B", "RED_DOT_C", "HOLO_A", "HOLO_B", "HOLO_C", "HOLO_D", "REFLEX_A", "REFLEX_B", "REFLEX_C"]
                                    },
                                    "BARRELS": ["FLASH", "COMP", "MUZZLE", "SUPP", "EXT", "NONE"],
                                    "GRIPS": ["VERT", "ANGLED", "HORI"],
                                    "UNDERBARRELS": ["LASER", "NONE"]
                                },
                                "modifiers": {
                                    "IRON": {
                                        "ADS": -0.02
                                    },
                                    "EXT": {
                                        "DAMAGE": 4
                                    },
                                    "ANGLED": {
                                        "RELOAD": -0.5
                                    },
                                    "HORI": {
                                        "RSM": 0.05
                                    },
                                    "LASER": {
                                        "ADS": -0.05
                                    }
                                }
                            },
                            {
                                "NAME": "M870",
                                "TYPE": "SHOTGUN",
                                "DAMAGE": 42,
                                "FIRE_RATE": 0,
                                "MAG": 7,
                                "MAX": 50,
                                "ADS": 0.32,
                                "RELOAD": 1.3,
                                "RSM": 0,
                                "DEST": "FULL",
                                "ATTACHMENTS": {
                                    "SCOPES": {
                                        "IRON": ["IRON"],
                                        "NONMAGNIFIED": ["RED_DOT_A", "RED_DOT_B", "RED_DOT_C", "HOLO_A", "HOLO_B", "HOLO_C", "HOLO_D", "REFLEX_A", "REFLEX_B", "REFLEX_C"]
                                    },
                                    "UNDERBARRELS": ["LASER", "NONE"]
                                },
                                "modifiers": {
                                    "IRON": {
                                        "ADS": -0.01
                                    },
                                    "LASER": {
                                        "ADS": -0.03
                                    }
                                }
                            },
                            {
                                "NAME": "TCSG12",
                                "TYPE": "SLUG",
                                "DAMAGE": 75,
                                "FIRE_RATE": 0,
                                "MAG": 10,
                                "MAX": 121,
                                "ADS": 0.49,
                                "RELOAD": 3.3,
                                "RSM": 0,
                                "DEST": "FULL",
                                "ATTACHMENTS": {
                                    "SCOPES": {
                                        "NONMAGNIFIED": ["RED_DOT_A", "RED_DOT_B", "RED_DOT_C", "HOLO_A", "HOLO_B", "HOLO_C", "HOLO_D", "REFLEX_A", "REFLEX_B", "REFLEX_C"],
                                        "IRON": ["IRON"]
                                    },
                                    "BARRELS": ["SUPP", "NONE"],
                                    "GRIPS": ["VERT", "ANGLED", "HORI"],
                                    "UNDERBARRELS": ["LASER", "NONE"]
                                },
                                "modifiers": {
                                    "IRON": {
                                        "ADS": -0.03
                                    },
                                    "ANGLED": {
                                        "RELOAD": -0.66
                                    },
                                    "HORI": {
                                        "RSM": 0.05
                                    },
                                    "LASER": {
                                        "ADS": -0.05
                                    }
                                }
                            }
                        ],
                        "secondaries": [
                            {
                                "NAME": "C75_AUTO",
                                "TYPE": "MP",
                                "DAMAGE": 35,
                                "FIRE_RATE": 1000,
                                "MAG": 26,
                                "MAX": 131,
                                "ADS": 0.34,
                                "RELOAD": 2.9,
                                "RSM": 0,
                                "DEST": "LOW",
                                "ATTACHMENTS": {
                                    "BARRELS": ["SUPP", "NONE"],
                                    "UNDERBARRELS": ["LASER", "NONE"]
                                },
                                "modifiers": {
                                    "LASER": {
                                        "ADS": -0.03
                                    }
                                }
                            },
                            {
                                "NAME": "SUPER_SHORTY",
                                "TYPE": "SHOTGUN",
                                "DAMAGE": 35,
                                "FIRE_RATE": 0,
                                "MAG": 3,
                                "MAX": 46,
                                "ADS": 0.32,
                                "RELOAD": 1.55,
                                "RSM": 0,
                                "DEST": "FULL",
                                "ATTACHMENTS": {
                                    "SCOPES": {
                                        "IRON": ["IRON"],
                                        "NONMAGNIFIED": ["RED_DOT_A", "RED_DOT_B", "RED_DOT_C", "HOLO_A", "HOLO_B", "HOLO_C", "HOLO_D", "REFLEX_A", "REFLEX_B", "REFLEX_C"]
                                    },
                                    "UNDERBARRELS": ["LASER", "NONE"]
                                },
                                "modifiers": {
                                    "IRON": {
                                        "ADS": -0.01
                                    },
                                    "LASER": {
                                        "ADS": -0.03
                                    }
                                }
                            }
                        ]
                    }
                },
                {
                    "name": "SMOKE",
                    "type": ["AE", "TRAP"],
                    "difficulty": 2,
                    "speed": 2,
                    "health": 2,
                    "ability": "GAS",
                    "gadgets": ["BARB", "PROX"],
                    "weapons": {
                        "primaries": [
                            {
                                "NAME": "M590A1",
                                "TYPE": "SHOTGUN",
                                "DAMAGE": 36,
                                "FIRE_RATE": 0,
                                "MAG": 7,
                                "MAX": 50,
                                "ADS": 0.32,
                                "RELOAD": 1.6,
                                "RSM": 0,
                                "DEST": "FULL",
                                "ATTACHMENTS": {
                                    "SCOPES": {
                                        "IRON": ["IRON"],
                                        "NONMAGNIFIED": ["RED_DOT_A", "RED_DOT_B", "RED_DOT_C", "HOLO_A", "HOLO_B", "HOLO_C", "HOLO_D", "REFLEX_A", "REFLEX_B", "REFLEX_C"]
                                    },
                                    "UNDERBARRELS": ["LASER", "NONE"]
                                },
                                "modifiers": {
                                    "IRON": {
                                        "ADS": -0.01
                                    },
                                    "LASER": {
                                        "ADS": -0.03
                                    }
                                }
                                
                            },
                            {
                                "NAME": "FMG_9",
                                "TYPE": "SMG",
                                "DAMAGE": 34,
                                "FIRE_RATE": 800,
                                "MAG": 30,
                                "MAX": 181,
                                "ADS": 0.44,
                                "RELOAD": 2.96,
                                "RSM": 0,
                                "DEST": "LOW",
                                "ATTACHMENTS": {
                                    "SCOPES": {
                                        "IRON": ["IRON"],
                                        "NONMAGNIFIED": ["RED_DOT_A", "RED_DOT_B", "RED_DOT_C", "HOLO_A", "HOLO_B", "HOLO_C", "HOLO_D", "REFLEX_A", "REFLEX_B", "REFLEX_C"]
                                    },
                                    "BARRELS": ["FLASH", "COMP", "MUZZLE", "SUPP", "EXT", "NONE"],
                                    "UNDERBARRELS": ["LASER", "NONE"]
                                },
                                "modifiers": {
                                    "IRON": {
                                        "ADS": -0.03
                                    },
                                    "EXT": {
                                        "DAMAGE": 4
                                    },
                                    "LASER": {
                                        "ADS": -0.04
                                    }
                                }
                            }
                        ],
                        "secondaries": [
                            {
                                "NAME": "SMG_11",
                                "TYPE": "MP",
                                "DAMAGE": 32,
                                "FIRE_RATE": 1270,
                                "MAG": 16,
                                "MAX": 113,
                                "ADS": 0.36,
                                "RELOAD": 2.7,
                                "RSM": 0,
                                "DEST": "LOW",
                                "ATTACHMENTS": {
                                    "SCOPES": {
                                        "IRON": ["IRON"],
                                        "NONMAGNIFIED": ["RED_DOT_A", "RED_DOT_B", "RED_DOT_C", "HOLO_A", "HOLO_B", "HOLO_C", "HOLO_D", "REFLEX_A", "REFLEX_B", "REFLEX_C"]
                                    },
                                    "BARRELS": ["FLASH", "COMP", "MUZZLE", "SUPP", "EXT", "NONE"],
                                    "GRIPS": ["VERT", "ANGLED", "HORI"],
                                    "UNDERBARRELS": ["LASER", "NONE"]
                                },
                                "modifiers": {
                                    "IRON": {
                                        "ADS": -0.02
                                    },
                                    "EXT": {
                                        "DAMAGE": 3
                                    },
                                    "ANGLED": {
                                        "RELOAD": -0.54
                                    },
                                    "HORI": {
                                        "RSM": 0.05
                                    },
                                    "LASER": {
                                        "ADS": -0.04
                                    }
                                }
                            },
                            {
                                "NAME": "P226_MK_25",
                                "TYPE": "HG",
                                "DAMAGE": 50,
                                "FIRE_RATE": 0,
                                "MAG": 15,
                                "MAX": 97,
                                "ADS": 0.22,
                                "RELOAD": 2.1,
                                "RSM": 0.05,
                                "DEST": "LOW",
                                "ATTACHMENTS": {
                                    "BARRELS": ["MUZZLE", "SUPP", "NONE"],
                                    "UNDERBARRELS": ["LASER", "NONE"]
                                },
                                "modifiers": {
                                    "LASER": {
                                        "ADS": -0.02
                                    }
                                }
                            }
                        ]
                    }
                }
            ]
        }

    @staticmethod
    def get_attachment_category_from_type(attachment_type):
        """returns the matching AttachmentCategory from type_map using the given AttachmentType

        Args:
            attachment_type (AttachmentType): attachment type

        Raises:
            TypeError: if attachment_type is not of type AttachmentType

        Returns:
            Enum: matching AttachmentType for the given AttachmentType
        """
        #print(f'attachment_type={attachment_type}, type(attachment_type)={type(attachment_type).__name__}')
        if not isinstance(attachment_type, Weapon.Attachment.AttachmentType) and not isinstance(attachment_type, str):
            raise TypeError(f'attachment_type must be of type AttachmentType or str, not {type(attachment_type).__name__}')
        
        type_map = {
            Weapon.Attachment.IronSights.IRON: Weapon.Attachment.AttachmentCategory.SCOPES,
            Weapon.Attachment.NonmagnifiedScope.RED_DOT_A: Weapon.Attachment.AttachmentCategory.SCOPES,
            Weapon.Attachment.NonmagnifiedScope.RED_DOT_B: Weapon.Attachment.AttachmentCategory.SCOPES,
            Weapon.Attachment.NonmagnifiedScope.RED_DOT_C: Weapon.Attachment.AttachmentCategory.SCOPES,
            Weapon.Attachment.NonmagnifiedScope.HOLO_A: Weapon.Attachment.AttachmentCategory.SCOPES,
            Weapon.Attachment.NonmagnifiedScope.HOLO_B: Weapon.Attachment.AttachmentCategory.SCOPES,
            Weapon.Attachment.NonmagnifiedScope.HOLO_C: Weapon.Attachment.AttachmentCategory.SCOPES,
            Weapon.Attachment.NonmagnifiedScope.HOLO_D: Weapon.Attachment.AttachmentCategory.SCOPES,
            Weapon.Attachment.NonmagnifiedScope.REFLEX_A: Weapon.Attachment.AttachmentCategory.SCOPES,
            Weapon.Attachment.NonmagnifiedScope.REFLEX_B: Weapon.Attachment.AttachmentCategory.SCOPES,
            Weapon.Attachment.NonmagnifiedScope.REFLEX_C: Weapon.Attachment.AttachmentCategory.SCOPES,
            Weapon.Attachment.NonmagnifiedScope.REFLEX_D: Weapon.Attachment.AttachmentCategory.SCOPES,
            Weapon.Attachment.MagnifiedScopes.MAGNIFIED_A: Weapon.Attachment.AttachmentCategory.SCOPES,
            Weapon.Attachment.MagnifiedScopes.MAGNIFIED_B: Weapon.Attachment.AttachmentCategory.SCOPES,
            Weapon.Attachment.MagnifiedScopes.MAGNIFIED_C: Weapon.Attachment.AttachmentCategory.SCOPES,
            Weapon.Attachment.TelescopicScopes.TELESCOPIC_A: Weapon.Attachment.AttachmentCategory.SCOPES,
            Weapon.Attachment.TelescopicScopes.TELESCOPIC_B: Weapon.Attachment.AttachmentCategory.SCOPES,
            Weapon.Attachment.TelescopicScopes.TELESCOPIC_C: Weapon.Attachment.AttachmentCategory.SCOPES,
            Weapon.Attachment.BarrelAttachment.COMP: Weapon.Attachment.AttachmentCategory.BARRELS,
            Weapon.Attachment.BarrelAttachment.EXT: Weapon.Attachment.AttachmentCategory.BARRELS,
            Weapon.Attachment.BarrelAttachment.FLASH: Weapon.Attachment.AttachmentCategory.BARRELS,
            Weapon.Attachment.BarrelAttachment.MUZZLE: Weapon.Attachment.AttachmentCategory.BARRELS,
            Weapon.Attachment.BarrelAttachment.SUPP: Weapon.Attachment.AttachmentCategory.BARRELS,
            Weapon.Attachment.BarrelAttachment.NONE: Weapon.Attachment.AttachmentCategory.BARRELS,
            Weapon.Attachment.GripAttachment.ANGLED: Weapon.Attachment.AttachmentCategory.GRIPS,
            Weapon.Attachment.GripAttachment.HORI: Weapon.Attachment.AttachmentCategory.GRIPS,
            Weapon.Attachment.GripAttachment.VERT: Weapon.Attachment.AttachmentCategory.GRIPS,
            Weapon.Attachment.UnderbarrelAttachment.LASER: Weapon.Attachment.AttachmentCategory.UNDERBARRELS,
            Weapon.Attachment.UnderbarrelAttachment.NONE: Weapon.Attachment.AttachmentCategory.UNDERBARRELS,
        }

        return type_map[attachment_type]


class Randomizable:
    """parent class for any class that can be used to create randomized (finished) classes
    """
    def __init__(self):
        """constructor for Randomizable class
        """
        pass
    
    def randomize(self):
        """randomize whatever information needs to be and return it
        """
        raise NotImplementedError(f'randomize method hasn\'t been implemented on the class side')


class Portable:
    """parent class for any class that can import and export data into json parsable data
    """
    def export(self, **options):
        """exports the data within this class into json parsable data
        """
        raise NotImplementedError(f'this feature is not implemented on the class side')

    @staticmethod
    def import_from(data, **options):
        """static method for importing information from data variable

        Args:
            any: data being imported into the class
        """
        raise NotImplementedError(f'this feature is not implemented on the class side')

class Weapon(Portable):
    """class containing all functionality for weapon data
    """
    class WeaponCategory(enum.Enum):
        """class for weapon categories
        """
        AR = "Assault rifle"
        SMG = "Submachine gun"
        LMG = "Light machine gun"
        SHOTGUN = "Shotgun"
        SLUG = "Slug"
        RIFLE = "Precision rifle"
        MP = "Machine pistol"
        HG = "Handgun"
        HC = "Hand cannon"
        SHIELD = "Shield"

    class WeaponType(enum.Enum):
        """class for weapon types
        """
        COMMANDO_9 = "Commando 9"
        M870 = "M870"
        TCSG12 = "TCSG12"
        C75_AUTO = "C75 Auto"
        SUPER_SHORTY = "Super Shorty"
        M590A1 = "M590A1"
        FMG_9 = "Fmg-9"
        SMG_11 = "Smg 11"
        P226_MK_25 = "P226 Mk 25"

    class Destruction(enum.Enum):
        """enum for destruction levels
        """
        LOW = "Low"
        MED = "Medium"
        HIGH = "High"
        FULL = "Full"

    class Loadout(Portable, Randomizable):
        """class related to storage of loadout data for weapons
        """
        class AttachmentLoadout(Portable):
            """class related to storage of loadout data for attachments
            """
            def __init__(self, **attachments):
                """constructor for class AttachmentLoadout

                Raises:
                    TypeError: if attachment category list is not of type dictionary or list
                    TypeError: if an attachment within an attachment category list is not of AttachmentType
                    TypeError: if an attachment within a scope category list is not of type AttachmentType
                """
                self._attachments = {}
                for c, d in attachments.items():
                    category = Weapon.Attachment.AttachmentCategory[c]
                    if not isinstance(d, list) and not isinstance(d, dict):
                        raise TypeError(f'attachment list ({d}) must be of type list or dict, not {type(d).__name__}')

                    if isinstance(d, list):
                        attach_list = []
                        for a in range(len(d)):
                            attachment = _util.get_attachment_type_from_string(d[a])
                            attach_list.append(attachment)
                        self._attachments.update({category: attach_list})
                        setattr(self, category.name.lower(), attach_list)
                    else:
                        scope_dict = {}
                        for sc, sd in d.items():
                            scope_category = Weapon.Attachment.ScopeCategory[sc]
                            scope_dict.update({scope_category: [_util.get_attachment_type_from_string(s) for s in sd]})
                        self._attachments.update({category: scope_dict})
                        setattr(self, category.name.lower(), scope_dict)

            def export(self):
                data = {}
                for ac, al in self._attachments.items():
                    if isinstance(al, dict):
                        scope_data = {}
                        for sc, sl in al.items():
                            scope_data.update({sc.name: [s.name for s in sl]})
                        data.update({ac.name: scope_data})
                    elif isinstance(al, list):
                        data.update({ac.name: [a.name for a in al]})
                    else:
                        raise TypeError(f'attachment lists for any attachment category must be of type dict or list, not {type(al).__name__}')

                return data

            @staticmethod
            def import_from(data, **options):
                if not isinstance(data, dict):
                    raise TypeError(f'data must be of type dict, not {type(data).__name__}')
                
                return Weapon.Loadout.AttachmentLoadout(**data)

            def _get_attachments_by_category(self, category) -> list:
                """gets all attachments available for a given AttachmentCategory

                Args:
                    category (AttachmentCategory): the category to get the attachments for

                Raises:
                    TypeError: if category is not of type AttachmentCategory

                Returns:
                    list: list containing AttachmentType's for the given AttachmentCategory
                """
                if not isinstance(category, Weapon.Attachment.AttachmentCategory):
                    raise TypeError(f'category must be of type AttachmentCategory, not {type(category).__name__}')
                
                for c, a in self._attachments.items():
                    if c == category:
                        return a
                return None

            def get_scopes(self) -> list:
                """gets all attachments in the scopes attachment category

                Returns:
                    list: list containing AttachmentType's for the SCOPES AttachmentCategory
                """
                return self._get_attachments_by_category(Weapon.Attachment.AttachmentCategory.SCOPES)
            
            def get_barrels(self) -> list:
                """gets all attachments in the barrels attachment category

                Returns:
                    list: list containing AttachmentType's for the BARRELS AttachmentType
                """
                return self._get_attachments_by_category(Weapon.Attachment.AttachmentCategory.BARRELS)
            
            def get_grips(self) -> list:
                """gets all attachments in the grips attachment category

                Returns:
                    list: list containing AttachmentType's for the GRIPS AttachmentType
                """
                return self._get_attachments_by_category(Weapon.Attachment.AttachmentCategory.GRIPS)
            
            def get_underbarrels(self) -> list:
                """gets all attachments in the underbarrels attachment category

                Returns:
                    list: list containing AttachmentType's for the UNDERBARRELS AttachmentType
                """
                return self._get_attachments_by_category(Weapon.Attachment.AttachmentCategory.UNDERBARRELS)
            
            def __repr__(self) -> str:
                """representation for AttachmentLoadout class

                Returns:
                    str: stringified AttachmentLoadout
                """
                return f'AttachmentLoadout<_attachments={self._attachments}>'

        def __init__(self, _data: dict, primaries: list, secondaries: list):
            """constructor for Loadout class

            Args:
                _data (dict): loadout's data
                primaries (list): list of Weapon types for primaries
                secondaries (list): list of Weapon types for secondaries

            Raises:
                TypeError: if _data is not of type dict
                TypeError: if any value in primaries is not of type Weapon
                TypeError: if any value in secondaries is not of type Weapon
            """
            if not isinstance(_data, dict):
                raise TypeError(f'_data must be of type dict, not {type(_data).__name__}')

            for p in range(len(primaries)):
                primary = primaries[p]
                if not isinstance(primary, Weapon): raise TypeError(f'Primary at index {p} must be of type Weapon, not {type(primary).__name__}')

            for p in range(len(secondaries)):
                secondary = secondaries[p]
                if not isinstance(secondary, Weapon): raise TypeError(f'Secondary at index {p} must be of type Weapon, not {type(primary).__name__}')

            self._data = _data
            self.primaries = primaries
            self.secondaries = secondaries

        def export(self):
            return {
                'primaries': [p.export() for p in self.primaries],
                'secondaries': [s.export() for s in self.secondaries]
            }

        @staticmethod
        def import_from(data, **options):
            primaries = data['primaries']
            secondaries = data['secondaries']

            if not isinstance(primaries, list):
                raise TypeError(f'primaries corresponding value must be of type list, not {type(primaries).__name__}')
            
            if not isinstance(secondaries, list):
                raise TypeError(f'secondaries corresponding value must be of type list, not {type(secondaries).__name__}')
            
            classed_primaries = [Weapon.import_from(p) for p in primaries]
            classed_secondaries = [Weapon.import_from(s) for s in secondaries]
            
            return Weapon.Loadout(data, classed_primaries, classed_secondaries)

        def _random_attachments(self, attachments: AttachmentLoadout, *, categorize_scopes: bool = False) -> dict:
            """gets and returns a dictionary of random attachments using the attachments and any other arguments passed

            Args:
                attachments (AttachmentLoadout): attachment loadout to select random attachments for
                categorize_scopes (bool, optional): whether to categorize scopes and randomly select a category, then a scope, or just select randomly from a combined list, defaults to False

            Raises:
                TypeError: if attachments is not of type AttachmentLoadout
                TypeError: attachments internal _attachments dictionary contains attachment data for a category that is not of type dict or list

            Returns:
                dict: a list of random attachments, keys being of type AttachmentCategory, values being AttachmentType
            """
            if not isinstance(attachments, self.AttachmentLoadout):
                raise TypeError(f'attachments must be of type AttachmentLoadout, not {type(attachments).__name__}')

            random_attachments = {}
            for c, d in attachments._attachments.items():
                if isinstance(d, dict):
                    if categorize_scopes:
                        scope_category_data = d[list(d.keys())[random.randint(0,len(d.keys())-1)]]
                        random_scope = scope_category_data[random.randint(0,len(scope_category_data)-1)]
                    else:
                        all_scopes = []
                        for d in d.values():
                            all_scopes = all_scopes + d
                        random_scope = all_scopes[random.randint(0,len(all_scopes)-1)]
                    random_attachments.update({c: random_scope})
                elif isinstance(d, list):
                    attach = d[random.randint(0,len(d)-1)]
                    random_attachments.update({c: attach})
                else:
                    raise TypeError(f'attachment data in each attachment category should be of type list of dict, not {type(d).__name__}')
            return random_attachments

        def randomize(self):
            """get a finished version of this loadout with random data

            Returns:
                _Loadout: a finished loadout class with randomized primaries and secondaries
            """
            random_primary = self.primaries[random.randint(0, len(self.primaries)-1)]
            random_attachments_primary = self._random_attachments(random_primary.attachments)
            primary = Finished._Weapon(self._data, random_primary.weapon_category, random_primary.weapon_type, random_primary.damage, random_primary.fire_rate, random_primary.mag, random_primary.max_mag, random_primary.ads, random_primary.reload_speed, random_primary.rsm, random_primary.destruction, Finished._Weapon._Loadout._AttachmentLoadout(**{k.name: v for k, v in random_attachments_primary.items()}), random_primary.modifiers)

            random_secondary = self.secondaries[random.randint(0, len(self.secondaries)-1)]
            random_attachments_secondary = self._random_attachments(random_secondary.attachments)
            secondary = Finished._Weapon(self._data, random_secondary.weapon_category, random_secondary.weapon_type, random_secondary.damage, random_secondary.fire_rate, random_secondary.mag, random_secondary.max_mag, random_secondary.ads, random_secondary.reload_speed, random_secondary.rsm, random_secondary.destruction, Finished._Weapon._Loadout._AttachmentLoadout(**{k.name: v for k, v in random_attachments_secondary.items()}), random_secondary.modifiers)

            return Finished._Weapon._Loadout(primary, secondary)
        
        def __repr__(self) -> str:
            """representation for Loadout class

            Returns:
                rep (str): stringified loadout
            """
            return f'Loadout<primaries={self.primaries}, secondaries={self.secondaries}>'

    class Attachment:
        """contains all classes and methods related to attachment creation and management
        """
        class AttachmentCategory(enum.Enum): 
            """enum for attachment categories, with corresponding labels
            """
            SCOPES = "Scope"
            BARRELS = "Barrel"
            GRIPS = "Grip"
            UNDERBARRELS = "Underbarrel"

        class AttachmentType: 
            """base class for each attachment type
            """
            def get_category(self):
                """gets the AttachmentCategory of AttachmentType self

                Returns:
                    category (AttachmentCategory): category of the AttachmentType
                """
                return _util.get_attachment_category_from_type(self)

        class ScopeAttachment(AttachmentType): 
            """base class for each scope attachment type
            """
            pass

        class ScopeCategory(enum.Enum):
            """enum for scope categories, with corresponding labels
            """
            IRON = "Iron"
            NONMAGNIFIED = "Nonmagnified"
            MAGNIFIED = "Magnified"
            TELESCOPIC = "Telescopic"

        class IronSights(ScopeAttachment, enum.Enum):
            """child enum of ScopeAttachment for scopes categorized as iron sights, with corresponding labels
            """
            IRON = "Iron sights"

        class NonmagnifiedScope(ScopeAttachment, enum.Enum):
            """child enum of ScopeAttachment for scopes categorized as nonmagnified, with corresponding labels
            """
            RED_DOT_A = "Red dot A"
            RED_DOT_B = "Red dot B"
            RED_DOT_C = "Red dot C"
            HOLO_A = "Holo A"
            HOLO_B = "Holo B"
            HOLO_C = "Holo C"
            HOLO_D = "Holo D"
            REFLEX_A = "Reflex A"
            REFLEX_B = "Reflex B"
            REFLEX_C = "Reflex C"
            REFLEX_D = "Reflex D"

        class MagnifiedScopes(ScopeAttachment, enum.Enum):
            """child enum of ScopeAttachment for scopes categorized as magnified, with corresponding labels
            """
            MAGNIFIED_A = "Magnified A"
            MAGNIFIED_B = "Magnified B"
            MAGNIFIED_C = "Magnified C"

        class TelescopicScopes(ScopeAttachment, enum.Enum):
            """child enum of ScopeAttachment for scopes categorized as telescopic, with corresponding labels
            """
            TELESCOPIC_A = "Telescopic A"
            TELESCOPIC_B = "Telescopic B"
            TELESCOPIC_C = "Telescopic C"

        class BarrelAttachment(AttachmentType, enum.Enum):
            """child enum of AttachmentType for barrel attachments, with corresponding labels
            """
            FLASH = "Flash hider"
            COMP = "Compensator"
            MUZZLE = "Muzzle break"
            SUPP = "Suppressor"
            EXT = "Extended barrel"
            NONE = "None"

        class GripAttachment(AttachmentType, enum.Enum):
            """child enum of AttachmentType for grip attachments, with corresponding labels
            """
            VERT = "Vertical grip"
            ANGLED = "Angled"
            HORI = "Horizontal"

        class UnderbarrelAttachment(AttachmentType, enum.Enum):
            """child enum of AttachmentType for underbarrel attachments, with corresponding labels
            """
            LASER = "Laser sight"
            NONE = "None"

        class GenericAttachment(AttachmentType, enum.Enum):
            """child enum of AttachmentType for underbarrel attachments, with corresponding labels
            """
            NONE = "None"

    class ModifierManager(Portable):
        class ModifiableWeaponAttribute(enum.Enum):
            """enum of modifiable weapon attributes, with corresponding labels and types
            """
            DAMAGE = ("Damage", int)
            ADS = ("Ads time", float)
            RELOAD = ("Reload speed", float)
            RSM = ("Run speed modifier", float)
            
        class AttributeModifier(Portable):
            """class for attribute modifiers
            """
            def __init__(self, modified_attribute, modifier: int | float, source):
                """constructor for AttributeModifier class

                Args:
                    modified_attribute (ModifiableWeaponAttribute): attribute being modified by the AttributeModifier
                    modifier (int | float): value to modify the ModifiableWeaponAttribute by
                    source (AttachmentType): source of the modification

                Raises:
                    TypeError: if modified_attribute is not of type ModifiableWeaponAttribute
                    TypeError: if modifier is not of type expected by the given modified_attribute (see Enum definition)
                    TypeError: if source is not of type AttachmentType
                """
                if not isinstance(modified_attribute, Weapon.ModifierManager.ModifiableWeaponAttribute):
                    raise TypeError(f'modified_attribute must be of type ModifiableWeaponAttribute, not {type(modified_attribute).__name__}')

                expected_type = modified_attribute.value[1]
                if not isinstance(modifier, expected_type):
                    raise TypeError(f'modifier must be of type {expected_type.__name__} for attribute {modified_attribute}, not {type(modifier).__name__}')
                
                if not isinstance(source, Weapon.Attachment.AttachmentType):
                    raise TypeError(f'source must be of type AttachmentType, not {type(source).__name__}')

                self.modified_attribute = modified_attribute
                self.modifier = modifier
                self.source = source

            def export(self, **options) -> dict:
                """export method from Portable

                Returns:
                    dict: AttributeModifier data in jsonable format
                """
                return {
                    self.source.name: {
                        self.modified_attribute.name: self.modifier
                    }
                }

            def __repr__(self):
                """representation for AttributeModifier class

                Returns:
                    str: stringified AttributeModifier
                """
                return f"AttributeModifier<modified_attribute={self.modified_attribute}, modifier={self.modifier}, source={self.source}>"

        def __init__(self, **modifiers): 
            """constructor for ModifierManager class

            Raises:
                TypeError: modifier list within modifiers is not of type dict
                TypeError: modifiers for any attachment is not of type dict
            """
            self._modifiers = []
            if len(modifiers) == 0: 
                return
            
            for att, mod_list in modifiers.items():
                if not isinstance(mod_list, dict):
                    raise TypeError(f'modifiers for each attachment category must be of type dict, not {type(m).__name__}')
                
                attach_type = _util.get_attachment_type_from_string(att)
                for attr, mod in mod_list.items():
                    attr_type = Weapon.ModifierManager.ModifiableWeaponAttribute[attr]
                    self._modifiers.append(Weapon.ModifierManager.AttributeModifier(attr_type, mod, attach_type))

        def export(self, **options):
            mods = {}
            if 'attachments' in options:
                attachments = options['attachments']
                aa = attachments.get_all_attachments()
                for m in self._modifiers:
                    if(m.source not in aa):
                        continue
                    
                    mods.update({
                        m.source.name: {
                            m.modified_attribute.name: m.modifier
                        }
                    })
            else:
                for m in self._modifiers:
                    mods.update({
                        m.source.name: {
                            m.modified_attribute.name: m.modifier
                        }
                    })
                    
            return mods
        
        @staticmethod
        def import_from(data, **options):
            if isinstance(data, str):
                data = json.loads(data)

            if not isinstance(data, dict):
                raise TypeError(f'data must be a dict or a dict in a json string')
            
            return Weapon.ModifierManager(**data)

        def has_modifier(self, attachment_type) -> bool:
            """gets whether there are any modifiers for the given AttachmentType

            Args:
                attachment_type (AttachmentType): attachment type to get modifiers for

            Raises:
                TypeError: if attachment_type is not of type AttachmentType

            Returns:
                bool: whether the modifier is within the modifiers
            """
            if not isinstance(attachment_type, Weapon.Attachment.AttachmentType):
                raise TypeError(f'attachment_type must be of type AttachmentType, not {attachment_type}')
            
            for t, _ in self._modifiers.items():
                if t == attachment_type:
                    return True
            return False

        def get_modifiers(self, attachment_type) -> list | None:
            """gets available modifiers for the given AttachmentType

            Args:
                attachment_type (AttachmentType): attachment type to get modifiers for

            Raises:
                TypeError: if attachment_type is not of type AttachmentType

            Returns:
                list | None: either a list of AttributeModifier's or None if the passed AttachmentType has no corresponding modifiers
            """
            if not isinstance(attachment_type, Weapon.Attachment.AttachmentType):
                raise TypeError(f'attachment_type must be of type AttachmentType, not {attachment_type}')
            
            for t, m in self._modifiers.items():
                if t == attachment_type:
                    return m
            return None
        
        def get_all_modifiers(self) -> list:
            """gets all modifiers

            Returns:
                list: list of AttributeModifier's
            """
            mods = []
            for m in self._modifiers:
                mods.append(m)
            return mods
        
        def __repr__(self) -> str:
            """representation for ModifierManager class

            Returns:
                str: stringified ModifierManager
            """
            return f'ModifierManager<_modifiers={self._modifiers}>'

    def __init__(self, _data: dict, weapon_category: WeaponCategory, weapon_type: WeaponType, damage: int, fire_rate: int, mag: int, max_mag: int, ads: float | int, reload_speed: float | int, rsm: float | int, destruction: Destruction, attachments: Loadout.AttachmentLoadout, modifiers: ModifierManager):
        """constructor for Weapon class

        Args:
            _data (dict): weapon's data
            weapon_category (WeaponCategory): weapon's category
            weapon_type (WeaponType): type of weapon
            damage (int): damage per bullet
            fire_rate (int): fire rate (0 = SEMI AUTO)
            mag (int): max bullets allowed in mag
            max_mag (int): max bullets allowed
            ads (float | int): aim down sight speed in seconds
            reload_speed (float | int): reload speed in seconds
            rsm (float | int): run speed modifier in percents
            destruction (Destruction): type of weapon destruction
            attachments (Loadout.AttachmentLoadout): all attachment for weapon
            modifiers (ModifierManager): modifier manager for weapon

        Raises:
            TypeError: if _data is not of type dict
            TypeError: if weapon_category is not of type WeaponCategory
            TypeError: if weapon_type is not of type WeaponType
            TypeError: if damage is not of type int
            TypeError: if fire_rate is not of type int
            TypeError: if mag is not of type int
            TypeError: if max_mag is not of type int
            TypeError: if ads is not of type float or int
            TypeError: if reload_speed is not of type float or int
            TypeError: if rsm is not of type float or int
            TypeError: if destruction is not of type Destruction
            TypeError: if attachments is not of type AttachmentLoadout
            TypeError: if modifiers is not of type ModifierManager
        """
        if not isinstance(_data, dict):
            raise TypeError(f'_data ({_data}) must be of type dict, not {type(_data).__name__}')
        if not isinstance(weapon_category, self.WeaponCategory):
            raise TypeError(f'weapon_category must be of type WeaponCategory, not {type(weapon_category).__name__}')
        if not isinstance(weapon_type, self.WeaponType):
            raise TypeError(f'weapon_type must be of type WeaponType, not {type(weapon_type).__name__}')
        if not isinstance(damage, int):
            raise TypeError(f'damage must be of type int, not {type(damage).__name__}')
        if not isinstance(fire_rate, int):
            raise TypeError(f'fire_rate must be of type int, not {type(fire_rate).__name__}')
        if not isinstance(mag, int):
            raise TypeError(f'mag must be of type int, not {type(mag).__name__}')
        if not isinstance(max_mag, int):
            raise TypeError(f'max_mag must be of type int, not {type(max_mag).__name__}')
        if not isinstance(ads, float):
            if isinstance(ads, int): ads = float(ads)
            else: raise TypeError(f'ads must be of type float, not {type(ads).__name__}')
        if not isinstance(reload_speed, float):
            if isinstance(reload_speed, int): reload_speed = float(reload_speed)
            else: raise TypeError(f'reload_speed must be of type float, not {type(reload_speed).__name__}')
        if not isinstance(rsm, float):
            if isinstance(rsm, int): rsm = float(rsm)
            else: raise TypeError(f'rsm must be of type float, not {type(rsm).__name__}')
        if not isinstance(destruction, self.Destruction):
            raise TypeError(f'destruction must be Destruction, not {type(destruction).__name__}')
        if not isinstance(attachments, self.Loadout.AttachmentLoadout):
            raise TypeError(f'attachments must be of type AttachmentLoadout, not {type(attachments).__name__}')
        if not isinstance(modifiers, self.ModifierManager):
            raise TypeError(f'modifiers must be of type ModifierManager, not {type(modifiers).__name__}')

        self._data = _data
        self.weapon_category = weapon_category
        self.weapon_type = weapon_type
        self.damage = damage
        self.fire_rate = fire_rate
        self.mag = mag
        self.max_mag = max_mag
        self.ads = ads
        self.reload_speed = reload_speed
        self.rsm = rsm
        self.destruction = destruction
        self.attachments = attachments
        self.modifiers = modifiers

    def export(self):
        return {
            'NAME': self.weapon_type.name,
            'TYPE': self.weapon_category.name,
            'DAMAGE': self.damage,
            'FIRE_RATE': self.fire_rate,
            'MAG': self.mag,
            'MAX': self.max_mag,
            'ADS': self.ads,
            'RELOAD': self.reload_speed,
            'RSM': self.rsm,
            'DEST': self.destruction.name,
            'ATTACHMENTS': self.attachments.export(),
            'modifiers': self.modifiers.export()
        }

    @staticmethod
    def import_from(data, **options):
        category = Weapon.WeaponCategory[data['TYPE']]
        weapon_type = Weapon.WeaponType[data['NAME']]
        destruction = Weapon.Destruction[data['DEST']]
        attachments = Weapon.Loadout.AttachmentLoadout.import_from(data['ATTACHMENTS'])
        modifiers = Weapon.ModifierManager.import_from(data['modifiers'])

        return Weapon(
            data,
            category,
            weapon_type,
            data['DAMAGE'],
            data['FIRE_RATE'],
            data['MAG'],
            data['MAX'],
            data['ADS'],
            data['RELOAD'],
            data['RSM'],
            destruction,
            attachments,
            modifiers
        )

    def __repr__(self) -> str: 
        """representation for class Weapon

        Returns:
            str: stringified Weapon
        """
        return f'Weapon<weapon_category={self.weapon_category}, weapon_type={self.weapon_type}, damage={self.damage}, fire_rate={self.fire_rate}, mag={self.mag}, max_mag={self.max_mag}, ads={self.ads}, reload_speed={self.reload_speed}, rsm={self.rsm}, destruction={self.destruction}, attachments={self.attachments}, modifiers={self.modifiers}>'

class Operator(Portable, Randomizable):
    class OperatorType:
        """parent class for operator types
        """
        pass

    class AttackOperatorType(OperatorType, enum.Enum):
        """child of OperatorType class for attacker operator types, with corresponding labels
        """
        pass

    class DefendOperatorType(OperatorType, enum.Enum):
        """child of OperatorType class for defender operator types, with corresponding labels
        """
        SENTRY = "Sentry"
        SMOKE = "Smoke"

    class Role(enum.Enum):
        """enum for operator roles
        """
        INTEL = "Intel"
        AG = "Anti gadget"
        SUPP  = "Support"
        FL = "Front line"
        MP = "Map control"
        BREACH = "Breach"
        TRAP = "Trapper"
        AE = "Anti entry"
        CC = "Crowd control"

    class OperatorGadget: 
        """parent class for operators gadgets
        """
        pass

    class AttackerGadget(OperatorGadget, enum.Enum):
        """child enum of OperatorGadget for attacker gadgets, with corresponding labels
        """
        SOFT = "Breaching charge"
        CLAY = "Claymore"
        EMP = "Impact emp grenade"
        FRAG = "Frag grenade"
        HARD = "Hard breach"
        SMOKE = "Smoke grenade"
        FLASH = "Flash grenade"

    class DefenderGadget(OperatorGadget, enum.Enum):
        """child enum of OperatorGadget for defender gadgets, with corresponding labels
        """
        BARB = "Barbed wire"
        BP = "Bulletproof camera"
        DEP = "Deployable shield"
        OBV = "Observation blocker"
        IMP = "Impact grenade"
        CF = "C4"
        PROX = "Proximity alarm"

    class Ability: 
        """parent class for operator abilities
        """
        pass

    class AttackerAbility(Ability, enum.Enum): 
        """child enum of Ability for attacher gadgets, with corresponding labels
        """
        pass

    class DefenderAbility(Ability, enum.Enum): 
        """child enum of Ability for defender gadgets, with corresponding labels
        """
        SPECIAL = "Special"
        GAS = "Gas Grenade"

    def __init__(self, _data: dict, operator_type: OperatorType, roles: list[Role], difficulty: int, speed: int, health: int, ability: Ability, gadgets: list[OperatorGadget], weapons: Weapon.Loadout):
        """constructor for Operator class

        Args:
            _data (dict): operator's data
            operator_type (OperatorType): type of operator
            operator_data (dict): operator data
            roles (list[Role]): operator's roles
            difficulty (int): difficulty of the operator (1-3)
            speed (int): speed of operator (1-3)
            health (int): health of operator (1-3)
            ability (Ability): operator's ability
            gadgets (list[OperatorGadget]): operator's gadgets
            weapons (Weapon.Loadout): operator's weapons

        Raises:
            TypeError: if _data is not of type dict
            TypeError: if operator_type is not of type OperatorType
            TypeError: if operator_data is not of type dict
            TypeError: if roles is not of type list
            TypeError: if any role within role is not of type Role
            TypeError: if difficulty is not of type int
            TypeError: if speed is not of type int
            TypeError: if health is not of type int
            TypeError: if ability is not of type Ability
            TypeError: if gadgets is not of type list
            TypeError: if any gadget within gadgets is not of type Gadget
            TypeError: if weapons is not of type Loadout
        """
        if not isinstance(_data, dict):
            raise TypeError(f'_data must be of type dict, not {type(_data).__name__}')
        if not isinstance(operator_type, Operator.OperatorType):
            raise TypeError(f'operator_type must be of type OperatorType, not {type(operator_type).__name__}')
        if not isinstance(roles, list):
            raise TypeError(f'operator_type must be of type list, not {type(operator_type).__name__}')
        else:
            for r in range(len(roles)):
                role = roles[r]
                if not isinstance(role, Operator.Role):
                    raise TypeError(f'role at index {r} must be of type Role, not {type(role).__name__}')

        if not isinstance(difficulty, int):
            raise TypeError(f'difficulty must be of type int, not {type(difficulty).__name__}')
        if not isinstance(speed, int):
            raise TypeError(f'speed must be of type int, not {type(speed).__name__}')
        if not isinstance(health, int):
            raise TypeError(f'health must be of type int, not {type(health).__name__}')
        if not isinstance(ability, Operator.Ability):
            raise TypeError(f'ability must be of type Ability, not {type(ability).__name__}')

        if not isinstance(gadgets, list):
            raise TypeError(f'gadgets must be of type list, not {type(gadgets).__name__}')
        else:
            for g in range(len(gadgets)):
                gadget = gadgets[g]
                if not isinstance(gadget, Operator.OperatorGadget):
                    raise TypeError(f'gadget at index {g} must be of type OperatorGadget, not {type(gadget).__name__}')

        if not isinstance(weapons, Weapon.Loadout):
            raise TypeError(f'weapons must be of type Loadout, not {type(weapons).__name__}')
        
        self._data = _data
        self.operator_type = operator_type
        self.roles = roles
        self.difficulty = difficulty
        self.speed = speed
        self.health = health
        self.ability = ability
        self.gadgets = gadgets
        self.weapons = weapons

    def randomize(self):
        """returns a finished version of this operator with random data

        Returns:
            _Operator: finished operator class
        """
        return Finished._Operator(self._data, self.operator_type, self.roles, self.difficulty, self.speed, self.health, self.ability, self.gadgets[random.randint(0,len(self.gadgets)-1)], self.weapons.randomize())
    
    @staticmethod
    def import_from(data, **options):
        op_name = data['name']
        op_type = _util.try_cast_enums(op_name, Operator.AttackOperatorType, Operator.DefendOperatorType)
        if op_type == None:
            raise ValueError(f'value for operator name {op_name} has no corresponding AttackOperatorType or DefendOperatorType')
        
        roles = [Operator.Role[r] for r in data['type']]

        op_ability = data['ability']
        ability = _util.try_cast_enums(op_ability, Operator.AttackerAbility, Operator.DefenderAbility)
        if ability == None:
            raise ValueError(f'value for operator ability {op_ability} has no corresponding AttackerAbility or DefenderAbility')
        
        gadgets = [_util.try_cast_enums(g, Operator.AttackerGadget, Operator.DefenderGadget) for g in data['gadgets']]
        for g in gadgets:
            if g == None:
                raise ValueError(f'a value within gadgets didn\'t have a corresponding AttackerGadget or DefenderGadget')
            
        loadout = Weapon.Loadout.import_from(data['weapons'])
        
        #print(f'op_type={op_type}, roles={roles}, ability={ability}, gadgets={gadgets}, loadout={loadout}')

        return Operator(
            data,
            op_type,
            roles,
            data['difficulty'],
            data['speed'],
            data['health'],
            ability,
            gadgets,
            loadout
        )
    
    def export(self):
        return {
            'name': self.operator_type.name,
            'roles': [r.name for r in self.roles],
            'difficulty': self.difficulty,
            'speed': self.speed,
            'health': self.health,
            'ability': self.ability.name,
            'gadgets': [g.name for g in self.gadgets],
            'weapons': self.weapons.export()
        }

    @staticmethod
    def get(operator_type: OperatorType):
        """static method for getting an Operator object using an OperatorType or corresponding string representation

        Args:
            operator_type (OperatorType): type of operator

        Raises:
            TypeError: if operator_type is not of type OperatorType

        Returns:
            Operator: operator data class
        """
        if not isinstance(operator_type, Operator.OperatorType):
            raise TypeError(f'operator_type must be of type str or OperatorType, not {type(operator_type).__name__}')
        
        categorized_operators = _util.operator_data()
        for c in categorized_operators:
            for d in categorized_operators[c]:
                if d['name'] != operator_type.name: continue

                return Operator.import_from(d)
            
    def __repr__(self) -> str:
        """representation for Operator class

        Returns:
            str: stringified Operator
        """
        return f'Operator<operator_type={self.operator_type}, roles={self.roles}, difficulty={self.difficulty}, speed={self.speed}, health={self.health}, ability={self.ability}, gadgets={self.gadgets}, weapons={self.weapons}>'

class Finished:
    """class containing everything about finished data
    """
    class _Weapon(Portable):
        """child of Portable for finished weapon data
        """
        class _Loadout(Portable):
            """child of Portable for finished loadout data
            """
            class _AttachmentLoadout(Portable):
                """child of Portable for finished attachment data
                """
                def __init__(self, **attachments):
                    """constructor for _AttachmentLoadout

                    Raises:
                        TypeError: if any value within attachments is not of type AttachmentType
                    """
                    self._attachments = {}
                    for c, a in attachments.items():
                        #print(f'c={c}, a={a}, type(a)={type(a).__name__}')
                        if not isinstance(a, Weapon.Attachment.AttachmentType):
                            raise TypeError(f'attachment must be of type AttachmentType, not {type(a).__name__}')
                                
                        category = Weapon.Attachment.AttachmentCategory[c]
                        self._attachments.update({category: a})
                        setattr(self, category.name.lower(), a)

                def export(self, **options):
                    """export method from Portable

                    Returns:
                        dict: _AttachmentLoadout data in jsonable format
                    """
                    return {c.name[:-1]:a.name for c, a in self._attachments.items()}
                                
                @staticmethod
                def import_from(data, **options):
                    if isinstance(data, str):
                        data = json.loads(data)

                    if not isinstance(data, dict):
                        raise TypeError(f'data must be a dict or a dict in a json string')

                    new_attachments = {}
                    for c, a in data.items():
                        attach_type = _util.get_attachment_type_from_string(a)
                        new_attachments.update({c + 'S': attach_type})

                    return Finished._Weapon._Loadout._AttachmentLoadout(**new_attachments)
                
                def get_all_attachments(self) -> list[Weapon.Attachment.AttachmentType]:
                    attachments = []
                    for _, a in self._attachments.items():
                        attachments.append(a)
                    return attachments

                def _get_attachment_by_category(self, category) -> Weapon.Attachment.AttachmentType:
                    """gets an attachment currently equip by AttachmentCategory

                    Args:
                        category (AttachmentCategory): category to get attachment for

                    Raises:
                        TypeError: if category is not of type AttachmentCategory

                    Returns:
                        Weapon.Attachment.AttachmentType: type of attachment currently equip in the given category
                    """
                    if not isinstance(category, Weapon.Attachment.AttachmentCategory):
                        raise TypeError(f'category must be of type AttachmentCategory, not {type(category).__name__}')
                    
                    for c, a in self._attachments.items():
                        if c == category:
                            return a
                    return None

                def get_scope(self) -> Weapon.Attachment.ScopeAttachment:
                    """gets currently equip scope

                    Returns:
                        Weapon.Attachment.ScopeAttachment: scope attachment type
                    """
                    return self._get_attachment_by_category(Weapon.Attachment.AttachmentCategory.SCOPES)
                
                def get_barrel(self) -> Weapon.Attachment.BarrelAttachment:
                    """gets currently equip barrel

                    Returns:
                        Weapon.Attachment.BarrelAttachment: barrel attachment type
                    """
                    return self._get_attachment_by_category(Weapon.Attachment.AttachmentCategory.BARRELS)
                
                def get_grip(self) -> Weapon.Attachment.GripAttachment:
                    """gets currently equip grip

                    Returns:
                        Weapon.Attachment.GripAttachment: grip attachment type
                    """
                    return self._get_attachment_by_category(Weapon.Attachment.AttachmentCategory.GRIPS)
                
                def get_underbarrel(self) -> Weapon.Attachment.UnderbarrelAttachment:
                    """gets currently equip underbarrel

                    Returns:
                        Weapon.Attachment.UnderbarrelAttachment: underbarrel attachment type
                    """
                    return self._get_attachment_by_category(Weapon.Attachment.AttachmentCategory.UNDERBARRELS)
                
            def __init__(self, primary, secondary):
                """constructor for _Loadout class

                Args:
                    primary (_Weapon): finished weapon for primary
                    secondary (_Weapon): finished weapon for secondary

                Raises:
                    TypeError: if primary not of type _Weapon
                    TypeError: if secondary not of type _Weapon
                """
                if not isinstance(primary, Finished._Weapon):
                    raise TypeError(f'primary must be of type _Weapon, not {type(primary).__name__}')

                if not isinstance(secondary, Finished._Weapon):
                    raise TypeError(f'secondary must be of type _Weapon, not {type(secondary).__name__}')

                self.primary = primary
                self.secondary = secondary

            def export(self, **options) -> dict:
                """export method from Portable

                Returns:
                    dict: _Loadout data in jsonable format
                """
                return {
                    'primary': self.primary.export(),
                    'secondary': self.secondary.export()
                }
            
            @staticmethod
            def import_from(data, **options):
                if isinstance(data, str):
                    data = json.loads(data)

                if not isinstance(data, dict):
                    raise TypeError(f'data must be a dict or a dict in a json string')
                
                primary_data = data['primary']
                secondary_data = data['secondary']

                return Finished._Weapon._Loadout(
                    primary=Finished._Weapon.import_from(primary_data),
                    secondary=Finished._Weapon.import_from(secondary_data)
                )

            def __repr__(self) -> str:
                """representation for _Loadout class

                Returns:
                    str: stringified _Loadout
                """
                return f'_Loadout<primary={self.primary}, secondary={self.secondary}>'

        def __init__(self, _data: dict, weapon_category: Weapon.WeaponCategory, weapon_type: Weapon.WeaponType, damage: int, fire_rate: int, mag: int, max_mag: int, ads: float, reload_speed: float, rsm: float, destruction: Weapon.Destruction, attachments: _Loadout._AttachmentLoadout, modifiers: Weapon.ModifierManager):
            """constructor for _Weapon

            Args:
                _data (dict): weapon's original data
                weapon_category (WeaponCategory): weapon's category
                weapon_type (WeaponType): type of weapon
                damage (int): damage per bullet
                fire_rate (int): fire rate (0 = SEMI AUTO)
                mag (int): max bullets allowed in mag
                max_mag (int): max bullets allowed
                ads (float | int): aim down sight speed in seconds
                reload_speed (float | int): reload speed in seconds
                rsm (float | int): run speed modifier in percents
                destruction (Destruction): type of weapon destruction
                attachments (_Loadout._AttachmentLoadout): all finished attachment for weapon
                modifiers (ModifierManager): modifier manager for weapon

            Raises:
                TypeError: if _data is not of type dict
                TypeError: if weapon_category is not of type WeaponCategory
                TypeError: if weapon_type is not of type WeaponType
                TypeError: if damage is not of type int
                TypeError: if fire_rate is not of type int
                TypeError: if mag is not of type int
                TypeError: if max_mag is not of type int
                TypeError: if ads is not of type float or int
                TypeError: if reload_speed is not of type float or int
                TypeError: if rsm is not of type float or int
                TypeError: if destruction is not of type Destruction
                TypeError: if attachments is not of type _AttachmentLoadout
                TypeError: if modifiers is not of type ModifierManager
            """
            if not isinstance(_data, dict):
                raise TypeError(f'_data must be of type dict, not {type(_data).__name__}')
            if not isinstance(weapon_category, Weapon.WeaponCategory):
                raise TypeError(f'weapon_category ({weapon_category}) must be of type WeaponCategory, not {type(weapon_category).__name__}')
            if not isinstance(weapon_type, Weapon.WeaponType):
                raise TypeError(f'weapon_type ({weapon_type}) must be of type WeaponType, not {type(weapon_type).__name__}')
            if not isinstance(damage, int):
                raise TypeError(f'damage ({damage}) must be of type int, not {type(damage).__name__}')
            if not isinstance(fire_rate, int):
                raise TypeError(f'fire_rate ({fire_rate}) must be of type int, not {type(fire_rate).__name__}')
            if not isinstance(mag, int):
                raise TypeError(f'mag ({msg}) must be of type int, not {type(mag).__name__}')
            if not isinstance(max_mag, int):
                raise TypeError(f'max_mag ({max_mag}) must be of type int, not {type(max_mag).__name__}')
            if not isinstance(ads, float):
                if isinstance(ads, int): ads = float(ads)
                else: raise TypeError(f'ads ({ads}) must be of type float, not {type(ads).__name__}')
            if not isinstance(reload_speed, float):
                if isinstance(reload_speed, int): reload_speed = float(reload_speed)
                else: raise TypeError(f'reload_speed ({reload_speed}) must be of type float, not {type(reload_speed).__name__}')
            if not isinstance(rsm, float):
                if isinstance(rsm, int): rsm = float(rsm)
                else: raise TypeError(f'rsm ({rsm}) must be of type float, not {type(rsm).__name__}')
            if not isinstance(destruction, Weapon.Destruction):
                raise TypeError(f'destruction must be Destruction, not {type(destruction).__name__}')
            if not isinstance(attachments, Finished._Weapon._Loadout._AttachmentLoadout):
                raise TypeError(f'attachments must be of type _AttachmentLoadout, not {type(attachments).__name__}')
            if not isinstance(modifiers, Weapon.ModifierManager):
                raise TypeError(f'modifiers must be of type ModifierManager, not {type(modifiers).__name__}')

            self._data = _data
            self.weapon_category = weapon_category
            self.weapon_type = weapon_type
            self._base_damage = damage
            self.fire_rate = fire_rate
            self.mag = mag
            self.max_mag = max_mag
            self._base_ads = ads
            self._base_reload_speed = reload_speed
            self._base_rsm = rsm
            self.destruction = destruction
            self.attachments = attachments
            self.modifiers = modifiers

        def export(self, **options):
            """export method from Portable

            Returns:
                dict: _Weapon data in jsonable format
            """
            return {
                'NAME': self.weapon_type.name,
                'TYPE': self.weapon_category.name,
                'DAMAGE': self._base_damage,
                'FIRE_RATE': self.fire_rate,
                'MAG': self.mag,
                'MAX': self.max_mag,
                'ADS': self._base_ads,
                'RELOAD': self._base_reload_speed,
                'RSM': self._base_rsm,
                'DEST': self.destruction.name,
                'ATTACHMENTS': self.attachments.export(),
                'MODIFIERS': self.modifiers.export(attachments=self.attachments)
            }
        
        @staticmethod
        def import_from(data, **options):
            if isinstance(data, str):
                data = json.loads(data)

            if not isinstance(data, dict):
                raise TypeError(f'data must be a dict or a dict in a json string')

            return Finished._Weapon(
                Weapon.WeaponCategory[data['TYPE']],
                Weapon.WeaponType[data['NAME']],
                data['DAMAGE'],
                data['FIRE_RATE'],
                data['MAG'],
                data['MAX'],
                data['ADS'],
                data['RELOAD'],
                data['RSM'],
                Weapon.Destruction[data['DEST']],
                Finished._Weapon._Loadout._AttachmentLoadout.import_from(data['ATTACHMENTS']),
                Weapon.ModifierManager.import_from(data['MODIFIERS'])
            )

        def __repr__(self):
            """representation of _Weapon class

            Returns:
                str: stringified _Weapon
            """
            return f'_Weapon<weapon_category={self.weapon_category}, weapon_type={self.weapon_type}, _base_damage={self._base_damage}, fire_rate={self.fire_rate}, mag={self.mag}, max_mag={self.max_mag}, _base_ads={self._base_ads}, _base_reload_speed={self._base_reload_speed}, _base_rsm={self._base_rsm}, destruction={self.destruction}, attachments={self.attachments}, modifiers={self.modifiers}>'

        def equip(self, attachment_type):
            """equips an attachment based on the given AttachmentType

            Args:
                attachment_type (AttachmentType): type of attachment to equip

            Raises:
                TypeError: if attachment_type is not of type AttachmentType
                Error.AttachmentNotAvailableError: if attachment doesn't allow for given attachment_type's category
            """
            if not isinstance(attachment_type, Weapon.Attachment.AttachmentType):
                raise TypeError(f'attachment_type must be of type AttachmentType, not {type(attachment_type).__name__}')

            category = _util.get_attachment_category_from_type(attachment_type)
            for c, a in self.attachments._attachments.items():
                if c != category: continue

                if attachment_type == a: 
                    return
                
                self.attachments._attachments[c] = attachment_type
                break
            else:
                raise Error.AttachmentNotAvailableError(f"Attachment category {category.name} isn\'t available on weapon {self.weapon_type.name}")
            
        def has_attachment(self, attachment_type) -> bool:
            """whether the weapon has a given AttachmentType

            Args:
                attachment_type (AttachmentType): attachment type to check for

            Raises:
                TypeError: if attachment_type is not of type AttachmentType

            Returns:
                bool: whether the weapon has the AttachmentType
            """
            if not isinstance(attachment_type, Weapon.Attachment.AttachmentType):
                raise TypeError(f'attachment_type must be of type AttachmentType, not {type(attachment_type).__name__}')
            
            for _, d in self.attachments._attachments.items():
                if attachment_type != d:
                    continue
                return True
            return False
        
        def allows_attachment(self, attachment_type) -> bool:
            """whether an attachment is allowed on the weapon

            Args:
                attachment_type (AttachmentType): attachment type to check for

            Raises:
                TypeError: if attachment_type not of type AttachmentType

            Returns:
                bool: whether the attachment is allowed
            """
            if not isinstance(attachment_type, Weapon.Attachment.AttachmentType):
                raise TypeError(f'attachment_type must be of type AttachmentType, not {type(attachment_type).__name__}')
            
            category = attachment_type.get_category()
            for c, _ in self.attachments._attachments.items():
                if c != category: 
                    continue
                return True
            return False
        
        def allows_attachment_category(self, attachment_category) -> bool:
            """whether a category of attachments is allowed on the weapon

            Args:
                attachment_category (AttachmentCategory): category to check for

            Raises:
                TypeError: if attachment_category not of type AttachmentCategory

            Returns:
                bool: whether the category is allowed or not
            """
            if not isinstance(attachment_category, Weapon.Attachment.AttachmentCategory):
                raise TypeError(f'attachment_category must be of type AttachmentCategory, not {type(attachment_category).__name__}')
            
            for c, _ in self.attachments._attachments.items():
                if c != attachment_category: 
                    continue
                return True
            return False

        def get_all_attachments(self) -> list[Weapon.Attachment.AttachmentType]:
            """gets all AttachmentType's for the weapon

            Returns:
                list[Weapon.Attachment.AttachmentType]: list of AttachmentType's
            """
            return [a for _, a in self.attachments._attachments.items()]

        def get_all_modifiers(self) -> list[Weapon.ModifierManager.AttributeModifier]:
            """gets all AttributeModifier's on weapon

            Returns:
                list[Weapon.ModifierManager.AttributeModifier]: list of AttributeModifier's
            """
            return self.modifiers.get_all_modifiers()
        
        def get_attachment(self, attachment_category: Weapon.Attachment.AttachmentCategory) -> Weapon.Attachment.AttachmentType | None:
            """gets whatever attachment is in given AttachmentCategory

            Args:
                attachment_category (Weapon.Attachment.AttachmentCategory): attachment category to find AttachmentType for

            Returns:
                Weapon.Attachment.AttachmentType | None: either the equip AttachmentType or None if no attachments are in given AttachmentCategory
            """
            for c, a in self.attachments._attachments.items():
                if c == attachment_category:
                    return a
            return None
        
        def get_scope(self) -> Weapon.Attachment.ScopeAttachment | None:
            """gets equip scope

            Returns:
                Weapon.Attachment.ScopeAttachment | None: either currently equip scope or None if not contained
            """
            return self.get_attachment(Weapon.Attachment.AttachmentCategory.SCOPES)
        
        def get_barrel(self) -> Weapon.Attachment.BarrelAttachment | None:
            """gets equip barrel

            Returns:
                Weapon.Attachment.BarrelAttachment | None: either currently equip barrel or None if not contained
            """
            return self.get_attachment(Weapon.Attachment.AttachmentCategory.BARRELS)

        def get_grip(self) -> Weapon.Attachment.GripAttachment | None:
            """gets equip grip

            Returns:
                Weapon.Attachment.GripAttachment | None: either currently equip grip or None if not contained
            """
            return self.get_attachment(Weapon.Attachment.AttachmentCategory.GRIPS)

        def get_underbarrel(self) -> Weapon.Attachment.UnderbarrelAttachment | None:
            """gets underbarrel

            Returns:
                Weapon.Attachment.UnderbarrelAttachment | None: either currently equip underbarrel or None if not contained
            """
            return self.get_attachment(Weapon.Attachment.AttachmentCategory.UNDERBARRELS)
        
        def get_available_modifiers(self) -> list[Weapon.ModifierManager.AttributeModifier]:
            """gets all available modifiers with the current attachment loadout

            Returns:
                list[Weapon.ModifierManager.AttributeModifier]: list of AttributeModifiers available
            """
            available_modifiers = []
            for m in self.modifiers.get_all_modifiers():
                all_attachment_types = self.get_all_attachments()
                if not m.source in all_attachment_types:
                    continue

                available_modifiers.append(m)
            return available_modifiers

        def _get_modified_value(self, base_val: int | float, attr: Weapon.ModifierManager.ModifiableWeaponAttribute):
            """gets a modified value give a base value and the modified attribute

            Args:
                base_val (int | float): base value for attribute
                attr (Weapon.ModifierManager.ModifiableWeaponAttribute): attribute to get

            Raises:
                TypeError: if base_val is not of type int or float
                TypeError: if attr is not of type ModifiableWeaponAttribute

            Returns:
                int | float: return type will be the type of base_val
            """
            if not isinstance(base_val, int) and not isinstance(base_val, float):
                raise TypeError(f'base_val must be of type int or float, not {type(base_val).__name__}')

            if not isinstance(attr, Weapon.ModifierManager.ModifiableWeaponAttribute):
                raise TypeError(f'attr must be of type ModifiableWeaponAttribute, not {type(attr).__name__}')

            for m in self.get_available_modifiers():
                if m.modified_attribute != attr:
                    continue
                base_val = base_val + m.modifier

            return base_val

        @property
        def damage(self) -> int:
            """property for weapon damage per bullet

            Returns:
                int: damage per bullet
            """
            return self._get_modified_value(self._base_damage, Weapon.ModifierManager.ModifiableWeaponAttribute.DAMAGE)

        @property
        def ads(self) -> float:
            """property for aim down sight speed

            Returns:
                float: aim down sight speed
            """
            return self._get_modified_value(self._base_ads, Weapon.ModifierManager.ModifiableWeaponAttribute.ADS)

        @property
        def reload_speed(self) -> float:
            """property for reload speed

            Returns:
                float: _description_
            """
            return self._get_modified_value(self._base_reload_speed, Weapon.ModifierManager.ModifiableWeaponAttribute.RELOAD)

        @property
        def rsm(self) -> float:
            """property for run speed modifier

            Returns:
                float: run speed modifier
            """
            return self._get_modified_value(self._base_rsm, Weapon.ModifierManager.ModifiableWeaponAttribute.RSM)
        
        @property
        def name(self) -> str:
            """property for name

            Returns:
                str: name of weapon
            """
            return self.weapon_type.value

    class _Operator(Portable):
        """child of Portable class for finished operator data
        """
        def __init__(self, _data: dict, operator_type: Operator.OperatorType, roles: list[Operator.Role], difficulty: int, speed: int, health: int, ability: Operator.Ability, gadget: Operator.OperatorGadget, weapons):
            """constructor for _Operator class

            Args:
                _data (dict): operator data
                operator_type (Operator.OperatorType): type of operator
                operator_data (dict): operator's data
                roles (list[Operator.Role]): roles of operator
                difficulty (int): operator's difficulty (1-3)
                speed (int): operator's speed (1-3)
                health (int): operator's health (1-3)
                ability (Operator.Ability): operator's ability
                gadget (Operator.OperatorGadget): operator's gadget
                weapons (_type_): operator's loadout

            Raises:
                TypeError: if _data is not of type dict
                TypeError: if operator_type is not of type OperatorType
                TypeError: if operator_data is not of type dict
                TypeError: if roles is not of type list
                TypeError: if any role within roles is not of type Role
                TypeError: difficulty is not of type int
                TypeError: speed is not of type int
                TypeError: health is not of type int
                TypeError: ability is not of type Ability
                TypeError: gadget is not of type OperatorGadget
                TypeError: weapons is not of type _Loadout
            """

            if not isinstance(_data, dict):
                raise TypeError(f'_data must be of type dict, not {type(_data).__name__}')
            if not isinstance(operator_type, Operator.OperatorType):
                raise TypeError(f'operator_type must be of type OperatorType, not {type(operator_type).__name__}')
            if not isinstance(roles, list):
                raise TypeError(f'operator_type must be of type list, not {type(operator_type).__name__}')
            else:
                for r in range(len(roles)):
                    role = roles[r]
                    if not isinstance(role, Operator.Role):
                        raise TypeError(f'role at index {r} must be of type Role, not {type(role).__name__}')

            if not isinstance(difficulty, int):
                raise TypeError(f'difficulty must be of type int, not {type(difficulty).__name__}')
            if not isinstance(speed, int):
                raise TypeError(f'speed must be of type int, not {type(speed).__name__}')
            if not isinstance(health, int):
                raise TypeError(f'health must be of type int, not {type(health).__name__}')
            if not isinstance(ability, Operator.Ability):
                raise TypeError(f'ability must be of type Ability, not {type(ability).__name__}')

            if not isinstance(gadget, Operator.OperatorGadget):
                raise TypeError(f'gadgets must be of type OperatorGadget, not {type(gadget).__name__}')
            if not isinstance(weapons, Finished._Weapon._Loadout):
                raise TypeError(f'weapons must be of type Loadout, not {type(weapons).__name__}')

            self._data = _data
            self.operator_type = operator_type
            self.roles = roles
            self.difficulty = difficulty
            self.speed = speed
            self.health = health
            self.ability = ability
            self.gadget = gadget
            self.weapons = weapons

        def export(self, **options):
            """export method from Portable

            Returns:
                dict: _Operator data in jsonable format
            """
            return {
                'name': self.operator_type.name,
                'type': [r.name for r in self.roles],
                'difficulty': self.difficulty,
                'speed': self.speed,
                'health': self.health,
                'ability': self.ability.name,
                'gadget': self.gadget.name,
                'weapons': self.weapons.export(),
            }
        
        @staticmethod
        def import_from(data, **options):
            """static import method from Portable

            Args:
                data (any): data to import from

            Returns:
                _Operator: finished operator class
            """

            if isinstance(data, str):
                data = json.loads(data)

            if not isinstance(data, dict):
                raise TypeError(f'data must be a dict or a dict in a json string')

            op_type = _util.try_cast_enums(data['name'], Operator.AttackOperatorType, Operator.DefendOperatorType)
            roles = [Operator.Role[r] for r in data['type']]
            ability = _util.try_cast_enums(data['ability'], Operator.AttackerAbility, Operator.DefenderAbility)
            gadget = _util.try_cast_enums(data['gadget'], Operator.AttackerGadget, Operator.DefenderGadget)

            weapon_data = data['weapons']
            weapons = Finished._Weapon._Loadout.import_from(weapon_data)

            return Finished._Operator(
                op_type,
                roles,
                data['difficulty'],
                data['speed'],
                data['health'],
                ability,
                gadget,
                weapons
            )
        
        def get_primary(self):
            """gets operators primary

            Returns:
                _Weapon: current primary
            """
            return self.weapons.primary

        def get_secondary(self):
            """gets operators secondary

            Returns:
                _Weapon: current secondary
            """
            return self.weapons.secondary

        def change_gadget(self, new_gadget: Operator.OperatorGadget):
            if not isinstance(new_gadget, Operator.OperatorGadget):
                raise TypeError(f'new_gadget must be of type OperatorGadget, not {type(new_gadget).__name__}')

            if(self.gadget == new_gadget): return
            if(new_gadget.name not in self._data['gadgets']):
                raise ValueError(f'operator {self.operator_type.name} cannot have gadget {new_gadget.name}, only {', '.join([_ for _ in self._data['gadgets']])}')
            
            self.gadget = new_gadget

            exit(0)

        def __repr__(self):
            """representation for class _Operator

            Returns:
                str: stringified _Operator
            """
            return f'_Operator<operator_type={self.operator_type}, roles={self.roles}, difficulty={self.difficulty}, speed={self.speed}, health={self.health}, ability={self.ability}, gadgets={self.gadget}, weapons={self.weapons}>'