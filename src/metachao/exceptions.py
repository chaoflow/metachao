class AspectCollision(RuntimeError):
    def __init__(self, name, left=None, right=None):
        msg = "\n".join([
            "'%s'",
            "    %s",
            "  collides with:",
            "    %s",
            ]) % (name, left, right) if right else name
        super(AspectCollision, self).__init__(msg)
