from enum import Enum

class Role(Enum):
    ADMIN = 'Admin'
    DEVELOPER = 'Developer'

    def __str__(self):
        return self.name