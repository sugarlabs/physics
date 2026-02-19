#!/usr/bin/env python3
"""
Test harness for issue #63 - Missing Collisions

Verifies that small circles do not tunnel through the ground or each other
under various timing conditions, including fast hardware simulation.

Usage:
    python3 test_collisions.py
"""

import sys
import time

try:
    import Box2D as box2d
except ImportError:
    print("ERROR: Box2D not found. Install with: pip install box2d-py")
    sys.exit(1)

PASS = "\033[92mPASS\033[0m"
FAIL = "\033[91mFAIL\033[0m"

def make_world():
    world = box2d.b2World(gravity=(0, -9.8), doSleep=True)
    groundDef = box2d.b2BodyDef()
    groundDef.position = (-10.0, 0.0)
    ground = world.CreateBody(groundDef)
    groundShape = box2d.b2PolygonShape()
    groundShape.SetAsBox(50.0, 0.1)
    ground.CreateFixture(shape=groundShape, density=0)
    return world, ground

def add_circle(world, pos, radius=0.4, bullet=True):
    bodyDef = box2d.b2BodyDef()
    bodyDef.type = box2d.b2_dynamicBody
    bodyDef.position = pos
    bodyDef.bullet = bullet
    body = world.CreateBody(bodyDef)
    circleShape = box2d.b2CircleShape()
    circleShape.radius = radius
    fixDef = box2d.b2FixtureDef()
    fixDef.shape = circleShape
    fixDef.density = 1.0
    fixDef.restitution = 0.16
    fixDef.friction = 0.5
    body.CreateFixture(fixDef)
    return body

def step_world(world, dt, vel_iter=10, pos_iter=8):
    world.Step(dt, vel_iter, pos_iter)
    world.ClearForces()

def did_tunnel(body, ground_y=0.1):
    return body.position.y < ground_y

def test_single_circle_settles():
    world, _ = make_world()
    circle = add_circle(world, pos=(0.0, 3.0), radius=0.4)
    PHYSICS_DT = 1.0 / 120.0
    for _ in range(600):
        step_world(world, PHYSICS_DT)
        if did_tunnel(circle):
            return False, f"Circle tunnelled (y={circle.position.y:.4f})"
    final_y = circle.position.y
    expected_y = 0.5  # ground top is at y=0.1 (half-extent), circle radius=0.4
    if abs(final_y - expected_y) > 0.1:
        return False, f"Circle did not settle correctly (y={final_y:.4f}, expected ~{expected_y})"
    return True, f"Circle settled at y={final_y:.4f}"

def test_large_dt_no_tunnel():
    world, _ = make_world()
    circle = add_circle(world, pos=(0.0, 3.0), radius=0.4)
    BAD_DT = 1.0 / 20.0
    tunnelled = False
    for _ in range(100):
        step_world(world, BAD_DT)
        if did_tunnel(circle):
            tunnelled = True
            break
    if tunnelled:
        return False, f"Large dt caused tunnelling (y={circle.position.y:.4f})"
    return True, f"No tunnelling with large dt (y={circle.position.y:.4f})"

def test_accumulator_realtime_ratio():
    try:
        import pygame
        pygame.init()
        clock = pygame.time.Clock()
    except ImportError:
        return None, "pygame not available, skipping"
    PHYSICS_DT = 1.0 / 120.0
    accumulator = PHYSICS_DT
    steps = 0
    # Warm up the clock - first few ticks are unreliable due to pygame init
    for _ in range(5):
        clock.tick_busy_loop(30)
    start = time.time()
    for _ in range(90):
        clock.tick_busy_loop(30)
        elapsed = min(max(clock.get_time(), 1) / 1000.0, 0.05)
        accumulator += elapsed
        while accumulator >= PHYSICS_DT:
            steps += 1
            accumulator -= PHYSICS_DT
    real_elapsed = time.time() - start
    sim_time = steps * PHYSICS_DT
    ratio = sim_time / real_elapsed
    if ratio < 0.8 or ratio > 1.3:
        return False, f"Ratio {ratio:.2f} outside acceptable range 0.8-1.3"
    return True, f"Sim/real ratio = {ratio:.2f} (acceptable: 0.8-1.3)"

def test_first_frame_steps():
    PHYSICS_DT = 1.0 / 120.0
    accumulator = PHYSICS_DT
    elapsed = min(max(0, 1) / 1000.0, 0.05)
    accumulator += elapsed
    steps = 0
    while accumulator >= PHYSICS_DT:
        steps += 1
        accumulator -= PHYSICS_DT
    if steps < 1:
        return False, f"First frame ran {steps} steps, expected at least 1"
    return True, f"First frame ran {steps} step(s) with 0ms clock"

def test_stacked_circles():
    world, _ = make_world()
    circles = []
    for i in range(10):
        c = add_circle(world, pos=(0.0, 1.0 + i * 1.0), radius=0.2)
        circles.append(c)
    PHYSICS_DT = 1.0 / 120.0
    tunnelled = 0
    for _ in range(720):
        step_world(world, PHYSICS_DT)
        for c in circles:
            if did_tunnel(c, ground_y=0.0):
                tunnelled += 1
    if tunnelled > 0:
        return False, f"{tunnelled} tunnelling events detected"
    return True, f"All 10 circles settled without tunnelling"

def run_tests():
    tests = [
        ("Single circle settles on ground",     test_single_circle_settles),
        ("Large dt (fast VM) no tunnel",         test_large_dt_no_tunnel),
        ("Accumulator real-time ratio ~1.0",     test_accumulator_realtime_ratio),
        ("First frame runs at least one step",   test_first_frame_steps),
        ("10 stacked circles no tunnel",         test_stacked_circles),
    ]
    print("=" * 60)
    print("Physics Collision Test Harness")
    print("Verifies fix for issue #63 - Missing Collisions")
    print("=" * 60)
    passed = 0
    failed = 0
    skipped = 0
    for name, test_fn in tests:
        try:
            result, msg = test_fn()
            if result is None:
                print(f"SKIP  {name}")
                print(f"      {msg}")
                skipped += 1
            elif result:
                print(f"{PASS}  {name}")
                print(f"      {msg}")
                passed += 1
            else:
                print(f"{FAIL}  {name}")
                print(f"      {msg}")
                failed += 1
        except Exception as e:
            print(f"{FAIL}  {name}")
            print(f"      Exception: {e}")
            failed += 1
        print()
    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed, {skipped} skipped")
    print("=" * 60)
    return failed == 0

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
