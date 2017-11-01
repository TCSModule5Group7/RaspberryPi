from Vec2 import Vec2


def aabb_vs_aabb(manifold):
    entity_a = manifold.entity_a
    entity_b = manifold.entity_b

    normal = entity_b.pos - entity_a.pos

    abox = entity_a.shape
    bbox = entity_b.shape

    a_extent = (abox.max.x - abox.min.x) / 2
    b_extent = (bbox.max.x - bbox.min.x) / 2

    x_overlap = a_extent + b_extent - abs(normal.x)

    if x_overlap > 0:
        a_extent = (abox.max.y - abox.min.y) / 2
        b_extent = (bbox.max.y - bbox.min.y) / 2

        y_overlap = a_extent + b_extent - abs(normal.y)

        if y_overlap > 0:
            if x_overlap < y_overlap:
                if normal.x < 0:
                    manifold.normal = Vec2(-1, 0)
                else:
                    manifold.normal = Vec2(1, 0)
                manifold.penetration = x_overlap
                return True
            else:
                if normal.y < 0:
                    manifold.normal = Vec2(0, -1)
                else:
                    manifold.normal = Vec2(0, 1)
                manifold.penetration = y_overlap
                return True
    return False


def resolve_collision(manifold):
    a = manifold.entity_a
    b = manifold.entity_b
    normal = manifold.normal

    #  Calculate relative velocity
    relative_velocity = b.velocity - a.velocity
    #  Calculate relative velocity in terms of the normal direction
    vel_along_normal = relative_velocity.dot_product(normal)

    # Do not resolve if velocities are separating
    if vel_along_normal > 0:
        return

    # Calculate restitution
    e = min(a.restitution, b.restitution)

    # Calculate impulse scalar
    j = -(1 + e) * vel_along_normal
    j /= a.inv_mass + b.inv_mass

    # Apply impulse
    impulse = normal * j
    a.velocity -= impulse * a.inv_mass
    b.velocity += impulse * b.inv_mass
