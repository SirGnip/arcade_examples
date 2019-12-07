"""Utilities for examining collisions between objects"""

from flapping import util


class Hit:
    """Describes the intersection between two objects"""
    def __init__(self, delta, normal, pos):
        # vector (2-tuple) representing overlap between the two objects, vector can be added to the colliding
        # object's position to move it back to a non-colliding state.
        self.delta = delta
        # vector (2-tuple) representing surface normal at point of contact
        self.normal = normal
        # vector (2-tuple) representing point of contact between the two objects
        self.pos = pos

    def __str__(self):
        return 'delta={} normal={} pos={}'.format(self.delta, self.normal, self.pos)


def intersect_AABB(sprite1, sprite2):
    """Do intersection test between two Sprites"""
    # Reference: https://noonat.github.io/intersect/
    # Tweaks made to the original algorithm
    # - Arcade sprites are treated as AABB
    # - Explicitly flipped the signs in the delta and normal being returned
    #   to match Arcade's origin & axes
    # - Gave priority to collisions in the Y direction to avoid case where
    #   players moving along ground would "catch" by an intermittent left/right
    #   collision.

    delta_x = sprite2.center_x - sprite1.center_x  # delta in X
    overlap_x = (sprite1.width/2 + sprite2.width/2) - abs(delta_x)
    if overlap_x <= 0:
        return None

    delta_y = sprite2.center_y - sprite1.center_y
    overlap_y = (sprite1.height/2 + sprite2.height/2) - abs(delta_y)
    if overlap_y <= 0:
        return None

    # Add +1 to overlap_x as a way to prioritize collisions in the Y direction
    if overlap_x + 1 < overlap_y:
        sign_x = util.sign(delta_x)
        hit = Hit(
            delta=(overlap_x * sign_x * -1, 0),
            normal=(sign_x * -1, 0),
            pos=(sprite1.center_x + (sprite1.width/2 * sign_x), sprite2.center_y)
        )
    else:
        sign_y = util.sign(delta_y)
        hit = Hit(
            delta=(0, overlap_y * sign_y * -1),
            normal=(0, sign_y * -1),
            pos=(sprite2.center_x, sprite1.center_y + (sprite1.height/2 * sign_y))
        )
    return hit
