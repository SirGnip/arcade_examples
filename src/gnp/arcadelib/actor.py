"""
Interface that allows app code to manage a wide variety of dynamic game objects with one interface
"""
import arcade


class Actor:
    """Actor is an "interface" that allows the app to manage drawing, updating, and lifetime of dynamic objects"""
    def update(self, delta_time: float):
        raise NotImplementedError("Must implement")

    def draw(self):
        raise NotImplementedError("Must implement")

    def can_reap(self) -> bool:
        """Allows an Actor to manage its own lifetime"""
        raise NotImplementedError("Must implement")

    def kill(self):
        """Mark this actor as dead so that it can be reaped the next time possible.

        This method is not necessary for most Actor-like objects as they usually manage
        their own lifetime via can_reap.  But, kill() it is a common addition if an Actor's
        lifetime needs to be managed or short from an outside client."""
        raise NotImplementedError("Must implement")


# monkey patch existing arcade classes to make them Actor-like
arcade.Sprite.can_reap = lambda other_self: None
arcade.SpriteList.can_reap = lambda other_self: None
# monkey patch Emitter to handle Actor passing "delta_time" to update() method
arcade.Emitter._original_update = arcade.Emitter.update
arcade.Emitter.update = lambda other_self, delta_time: other_self._original_update()


class ActorList(list, Actor):
    """ActorList is a container of Actors. An ActorList is-a Actor, so it can be easily assembled into hierarchies"""
    def draw(self):
        for actor in self:
            actor.draw()

    def update(self, delta_time: float):
        actors_to_delete = []
        for actor in self:
            actor.update(delta_time)
            if actor.can_reap():
                actors_to_delete.append(actor)
        for actor_to_del in actors_to_delete:
            self.remove(actor_to_del)

    def can_reap(self) -> bool:
        return all([actor.can_reap() for actor in self])

    def kill(self):
        for actor in self:
            actor.kill()
        self.clear()

