#!/usr/bin/env python3
"""
Test script to verify game components work correctly
"""

import sys
import os

# Add game directory to path
sys.path.insert(0, os.path.dirname(__file__))

def test_imports():
    """Test that all game modules can be imported"""
    print("Testing imports...")
    try:
        from game.game_state import GameState
        from game.game_state_web import GameStateWeb
        from game.player import Player
        from game.world import World
        from game.ai_companion import AICompanion
        from game.enemy_manager import EnemyManager, Enemy
        
        # Optional pygame-dependent imports
        try:
            from game.renderer import Renderer
            from game.input_handler import InputHandler
        except ImportError:
            print("  (Pygame modules skipped - not required for web version)")
        
        print("✓ All imports successful")
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False

def test_player():
    """Test player creation and basic mechanics"""
    print("\nTesting Player...")
    from game.player import Player
    
    player = Player(100, 100)
    assert player.x == 100
    assert player.y == 100
    assert player.health == 100
    assert player.stamina == 100
    assert player.fear == 0
    
    # Test movement (now uses target velocity with interpolation)
    player.move(1, 0)
    assert player.target_velocity_x > 0
    
    # Update player to apply velocity interpolation
    player.update(0.1)  # Small dt to test update
    assert player.velocity_x > 0  # Should have some velocity now
    
    # Test damage
    player.take_damage(20)
    assert player.health == 80
    assert player.fear > 0
    
    print("✓ Player tests passed")
    return True

def test_world():
    """Test world creation and mechanics"""
    print("\nTesting World...")
    from game.world import World
    
    world = World()
    assert len(world.zones) == 15
    assert 0 <= world.fog_density <= 1
    assert 0 <= world.ambient_darkness <= 1
    
    # Test visibility
    visibility = world.get_visibility_radius(0)
    assert visibility > 0
    
    print("✓ World tests passed")
    return True

def test_ai_companion():
    """Test AI companion"""
    print("\nTesting AI Companion...")
    from game.ai_companion import AICompanion
    
    ai = AICompanion()
    ai.load_previous_playthrough()
    
    assert 0 <= ai.confidence <= 1
    assert 0 <= ai.honesty <= 1
    assert 0 <= ai.doubt <= 1
    
    print("✓ AI Companion tests passed")
    return True

def test_enemy_manager():
    """Test enemy management"""
    print("\nTesting Enemy Manager...")
    from game.enemy_manager import EnemyManager, Enemy
    from game.player import Player
    
    manager = EnemyManager()
    player = Player(400, 300)
    
    # Create an enemy
    enemy = Enemy(500, 300, "shadow")
    assert enemy.x == 500
    assert enemy.y == 300
    assert enemy.type == "shadow"
    
    # Test enemy behavior
    attacked = enemy.update(0.1, player, 0.5)
    assert isinstance(attacked, bool)
    
    print("✓ Enemy Manager tests passed")
    return True

def test_game_state():
    """Test game state management"""
    print("\nTesting Game State...")
    from game.game_state import GameState
    
    state = GameState()
    assert state.player is not None
    assert state.world is not None
    assert state.ai_companion is not None
    assert state.enemy_manager is not None
    
    assert state.trust_level == 0.5
    assert state.game_time == 0
    
    # Test trust mechanics
    initial_trust = state.trust_level
    state.follow_advice()
    assert state.trust_level > initial_trust
    
    state.ignore_advice()
    assert state.trust_level < initial_trust + 0.05
    
    print("✓ Game State tests passed")
    return True

def test_web_game_state():
    """Test web game state management"""
    print("\nTesting Web Game State...")
    from game.game_state_web import GameStateWeb
    
    state = GameStateWeb()
    assert state.player is not None
    assert state.world is not None
    assert state.ai_companion is not None
    assert state.enemy_manager is not None
    
    # Test input application
    state.apply_input({'move_x': 1, 'move_y': 0, 'running': False})
    assert state.current_input['move_x'] == 1
    
    # Test state serialization
    state_dict = state.get_state_dict()
    assert 'player' in state_dict
    assert 'world' in state_dict
    assert 'enemies' in state_dict
    assert 'ai' in state_dict
    assert 'game' in state_dict
    
    print("✓ Web Game State tests passed")
    return True

def test_playthrough_recording():
    """Test playthrough recording system"""
    print("\nTesting Playthrough Recording...")
    from game.game_state import GameState
    import json
    import os
    
    state = GameState()
    
    # Record some actions
    state.record_action("move", {"x": 100, "y": 100})
    state.record_action("advice_followed", {"trust": 0.55})
    
    assert len(state.playthrough_actions) == 2
    
    # Test save (without actually writing)
    assert hasattr(state, 'save_playthrough')
    
    print("✓ Playthrough Recording tests passed")
    return True

def test_endings():
    """Test ending conditions"""
    print("\nTesting Ending Conditions...")
    from game.game_state import GameState
    
    # Test death ending
    state = GameState()
    state.player.health = 0
    state._check_ending_conditions()
    assert state.ending_triggered
    assert state.ending_type == "death"
    
    # Test trust ending
    state = GameState()
    state.trust_level = 0.96
    state.game_time = 200
    state._check_ending_conditions()
    assert state.ending_triggered
    assert state.ending_type == "trust"
    
    print("✓ Ending tests passed")
    return True

def test_behavior_profiler():
    """Test behavior profiler"""
    print("\nTesting Behavior Profiler...")
    from game.behavior_profiler import BehaviorState
    from game.player import Player
    from game.enemy_manager import EnemyManager
    
    profiler = BehaviorState(window_size=30)
    player = Player(400, 300)
    enemy_manager = EnemyManager()
    
    # Test initial state
    assert 0 <= profiler.trust <= 1
    assert 0 <= profiler.fear <= 1
    assert 0 <= profiler.independence <= 1
    
    # Test advice tracking
    profiler.on_advice_given(1.0)
    assert profiler.advice_given_count == 1
    
    profiler.on_advice_followed(2.0)
    assert profiler.advice_followed_count == 1
    assert len(profiler.reaction_times) == 1
    assert profiler.reaction_times[0] == 1.0  # 2.0 - 1.0
    
    profiler.on_advice_given(5.0)
    profiler.on_advice_ignored(8.0)
    assert profiler.advice_ignored_count == 1
    assert len(profiler.reaction_times) == 2
    
    # Test update
    player.move(1, 0)
    profiler.update(0.1, player, enemy_manager, 10.0)
    
    # Test state serialization
    state_dict = profiler.get_state_dict()
    assert 'trust' in state_dict
    assert 'fear' in state_dict
    assert 'independence' in state_dict
    assert 'average_reaction_time' in state_dict
    assert 'advice_follow_ratio' in state_dict
    assert 'hesitation_score' in state_dict
    assert 'risk_tolerance' in state_dict
    
    print("✓ Behavior Profiler tests passed")
    return True

def test_ai_intent_system():
    """Test AI intent system"""
    print("\nTesting AI Intent System...")
    from game.ai_companion import AICompanion, AIIntent
    from game.game_state import GameState
    
    state = GameState()
    ai = state.ai_companion
    
    # Test initial intent
    assert ai.current_intent in [AIIntent.PROTECT, AIIntent.CONTROL, AIIntent.TEST, AIIntent.CONFESS]
    
    # Test intent evaluation
    initial_intent = ai.current_intent
    ai._evaluate_intent(state)
    # Intent should be set after evaluation
    assert ai.current_intent is not None
    
    # Test intent weights
    assert AIIntent.PROTECT in ai.intent_weights
    assert AIIntent.CONTROL in ai.intent_weights
    assert AIIntent.TEST in ai.intent_weights
    assert AIIntent.CONFESS in ai.intent_weights
    
    # Test advice generation with intents
    advice = ai._generate_advice(state)
    assert 'text' in advice
    assert 'type' in advice
    assert 'intent' in advice
    assert advice['intent'] in [AIIntent.PROTECT, AIIntent.CONTROL, AIIntent.TEST, AIIntent.CONFESS]
    
    # Test protective advice
    state.player.health = 20
    protective_advice = ai._generate_protective_advice(state)
    assert 'text' in protective_advice
    assert len(protective_advice['text']) > 0
    
    # Test controlling advice
    controlling_advice = ai._generate_controlling_advice(state)
    assert 'text' in controlling_advice
    
    # Test testing advice
    testing_advice = ai._generate_testing_advice(state)
    assert 'text' in testing_advice
    
    # Test confession advice (late game)
    state.game_time = 300
    confession_advice = ai._generate_confession_advice(state)
    assert 'text' in confession_advice
    
    # Test confidence modifier
    ai.confidence = 0.3
    advice_with_modifier = ai._apply_confidence_modifier({'text': 'Go left', 'type': 'suggestion'})
    assert 'text' in advice_with_modifier
    
    print("✓ AI Intent System tests passed")
    return True

def test_reality_system():
    """Test reality degradation system"""
    print("\nTesting Reality System...")
    from game.reality_system import RealitySystem
    from game.game_state import GameState
    
    state = GameState()
    reality = state.reality_system
    
    # Test initial state
    assert reality.stability == 1.0
    assert reality.visual_stability == 1.0
    assert reality.audio_stability == 1.0
    assert reality.navigation_stability == 1.0
    
    # Test update
    reality.update(0.1, state)
    assert reality.stability >= 0.0 and reality.stability <= 1.0
    
    # Test fog density modifier
    base_fog = 0.5
    modified_fog = reality.apply_fog_density_modifier(base_fog)
    assert modified_fog >= base_fog  # Should increase fog
    
    # Test geometry warp
    x, y = 100, 100
    warped_x, warped_y = reality.apply_geometry_warp(x, y, 1.0)
    assert isinstance(warped_x, (int, float))
    assert isinstance(warped_y, (int, float))
    
    # Test movement unreliability
    vx, vy = 100, 0
    modified_vx, modified_vy = reality.apply_movement_unreliability(vx, vy)
    assert isinstance(modified_vx, (int, float))
    assert isinstance(modified_vy, (int, float))
    
    # Test with low trust (should degrade reality)
    state.trust_level = 0.2
    state.game_time = 60
    reality.update(10.0, state)
    assert reality.stability < 1.0  # Should degrade
    
    # Test state serialization
    state_dict = reality.get_state_dict()
    assert 'stability' in state_dict
    assert 'visual_stability' in state_dict
    assert 'audio_stability' in state_dict
    assert 'navigation_stability' in state_dict
    assert 'lie_count' in state_dict
    
    print("✓ Reality System tests passed")
    return True

def test_perception_based_enemies():
    """Test perception-based enemy system"""
    print("\nTesting Perception-Based Enemies...")
    from game.enemy_manager import Enemy, EnemyManager
    from game.player import Player
    from game.behavior_profiler import BehaviorState
    
    player = Player(400, 300)
    enemy = Enemy(500, 300, "shadow")
    behavior = BehaviorState()
    
    # Test basic enemy properties
    assert enemy.player_still_timer == 0.0
    assert enemy.attracted_to_stillness == False
    assert enemy.attracted_to_speech == False
    
    # Test update with behavior state
    attacked = enemy.update(0.1, player, 0.5, behavior, False)
    assert isinstance(attacked, bool)
    
    # Test update with AI speaking (should increase detection)
    attacked = enemy.update(0.1, player, 0.5, behavior, True)
    assert enemy.speech_attraction_timer > 0
    
    # Test stillness detection
    # Keep player in same position for multiple updates
    for _ in range(30):
        enemy.update(0.1, player, 0.5, behavior, False)
    
    # After being still, timer should have increased
    assert enemy.player_still_timer > 2.0
    assert enemy.attracted_to_stillness == True
    
    # Test with high hesitation behavior
    behavior.hesitation_score = 0.8
    initial_detection = enemy.detection_radius
    # Enemy should be more likely to detect hesitant player
    # (tested through effective_radius calculation in update)
    
    # Test enemy manager with perception parameters
    manager = EnemyManager()
    manager.enemies.append(enemy)
    manager.update(0.1, player, 0.5, behavior, True)
    
    print("✓ Perception-Based Enemies tests passed")
    return True

def test_cross_playthrough_memory():
    """Test cross-playthrough memory and AI adaptation"""
    print("\nTesting Cross-Playthrough Memory...")
    import json
    import os
    from game.ai_companion import AICompanion, AIIntent
    from game.game_state import GameState
    
    # Create a mock previous playthrough
    os.makedirs("playthroughs", exist_ok=True)
    mock_playthrough = {
        "ending": "death",
        "final_trust": 0.3,
        "behavior_profile": {
            "independence": 0.3,  # More dependent player
            "hesitation_score": 0.6,
            "risk_tolerance": 0.4,
            "average_reaction_time": 6.0,
            "advice_follow_ratio": 0.4
        },
        "actions": []
    }
    
    with open("playthroughs/latest.json", "w") as f:
        json.dump(mock_playthrough, f)
    
    # Create new AI and load previous playthrough
    ai = AICompanion()
    ai.load_previous_playthrough()
    
    # Test that AI adapted to death ending
    assert ai.doubt > 0.5  # Should be more doubtful
    # Protection intent should be prioritized (may be adjusted by behavior)
    assert ai.intent_weights[AIIntent.PROTECT] > 0.4
    
    # Test opening greeting references previous behavior
    greeting = ai.get_opening_greeting()
    assert isinstance(greeting, str)
    assert len(greeting) > 0
    
    # Test that AI adapted to behavior profile
    # Dependent + hesitant player should get more guidance
    assert ai.intent_weights[AIIntent.PROTECT] > 0.4
    
    # Test with high trust previous playthrough
    mock_playthrough["final_trust"] = 0.9
    mock_playthrough["ending"] = "trust"
    with open("playthroughs/latest.json", "w") as f:
        json.dump(mock_playthrough, f)
    
    ai2 = AICompanion()
    ai2.load_previous_playthrough()
    
    # Should be more confident and controlling
    assert ai2.confidence > 0.7
    assert ai2.doubt < 0.3
    assert ai2.intent_weights[AIIntent.CONTROL] > 0.4
    
    # Clean up
    if os.path.exists("playthroughs/latest.json"):
        os.remove("playthroughs/latest.json")
    
    print("✓ Cross-Playthrough Memory tests passed")
    return True

def test_threat_layers():
    """Test new threat layer system"""
    print("\nTesting Threat Layers...")
    from game.threat_layers import Hunter, Watcher, CorruptionField, ThreatLayerManager
    from game.player import Player
    
    player = Player(400, 300)
    
    # Test Hunter
    hunter = Hunter(500, 300)
    assert hunter.active == True
    assert hunter.always_moving == True
    attacked = hunter.update(0.1, player, 0.5)
    assert isinstance(attacked, bool)
    
    # Test Watcher
    watcher = Watcher(450, 300)
    assert watcher.active == True
    effect = watcher.update(0.1, player, 0.5)
    # Should be observing player
    assert watcher.is_observing == True
    assert effect is not None
    assert 'camera_lock' in effect
    
    # Test Corruption Field
    field = CorruptionField(400, 400)
    assert field.active == True
    effect = field.update(0.1, player, 0.5)
    # Player is close enough to be affected
    assert effect is None or 'intensity' in effect
    
    # Test Threat Manager
    manager = ThreatLayerManager()
    manager.update(0.1, player, 0.5, 0.5)
    assert manager.get_total_threat_count() >= 0
    
    print("✓ Threat Layers tests passed")
    return True

def test_pressure_spawning():
    """Test pressure-based spawning system"""
    print("\nTesting Pressure Spawning...")
    from game.pressure_spawning import PressureSpawningSystem
    from game.player import Player
    from game.threat_layers import ThreatLayerManager
    from game.ai_companion import AICompanion
    
    pressure = PressureSpawningSystem()
    player = Player(400, 300)
    threat_manager = ThreatLayerManager()
    ai = AICompanion()
    
    # Initial pressure
    initial_pressure = pressure.update(0.1, player, threat_manager, ai, 0.5)
    assert 0.0 <= initial_pressure <= 1.0
    
    # Test stillness increases pressure
    player.stop()
    for _ in range(100):
        pressure.update(0.1, player, threat_manager, ai, 0.5)
    
    assert pressure.player_stillness_duration > 0
    
    # Test on damage resets timer
    pressure.on_player_damaged()
    assert pressure.time_since_last_damage == 0
    
    print("✓ Pressure Spawning tests passed")
    return True

def test_player_abilities():
    """Test player abilities system"""
    print("\nTesting Player Abilities...")
    from game.player_abilities import PlayerAbilities
    from game.player import Player
    from game.threat_layers import ThreatLayerManager
    from game.enemy_manager import EnemyManager
    from game.ai_companion import AICompanion
    from game.reality_system import RealitySystem
    
    abilities = PlayerAbilities()
    player = Player(400, 300)
    threat_manager = ThreatLayerManager()
    enemy_manager = EnemyManager()
    ai = AICompanion()
    reality = RealitySystem()
    
    # Test Focus
    assert abilities.can_use_focus() == True
    focus_result = abilities.use_focus(player)
    assert focus_result is not None
    assert abilities.focus_active == True
    
    # Test Burn (need energy first)
    abilities.burn_energy = 100
    assert abilities.can_use_burn() == True
    burn_result = abilities.use_burn(player, threat_manager, enemy_manager)
    assert burn_result is not None
    assert 'cleared_count' in burn_result
    
    # Test Break
    assert abilities.can_use_break() == True
    break_result = abilities.use_break(ai, reality)
    assert break_result is not None
    assert 'type' in break_result
    
    # Test update
    abilities.update(0.1)
    
    print("✓ Player Abilities tests passed")
    return True

def test_phase_system():
    """Test phase escalation system"""
    print("\nTesting Phase System...")
    from game.phase_system import PhaseSystem
    
    phase_system = PhaseSystem()
    
    # Initial phase
    assert phase_system.current_phase == 0
    current_phase = phase_system.get_current_phase()
    assert current_phase.phase_number == 0
    
    # Update to advance phase
    phase_system.time_in_phase = 120  # Force advancement
    phase_system.update(0.1, 120)
    
    # Check if rule exists
    active_rules = phase_system.get_active_rule_effects()
    assert isinstance(active_rules, dict)
    
    # Test time distortion
    time_factor = phase_system.get_time_distortion_factor()
    assert time_factor > 0
    
    print("✓ Phase System tests passed")
    return True

def test_objectives_system():
    """Test objectives system"""
    print("\nTesting Objectives System...")
    from game.objectives_system import ObjectivesSystem, StabilizeZone, ReachSignal
    from game.player import Player
    from game.threat_layers import ThreatLayerManager
    
    objectives = ObjectivesSystem()
    player = Player(400, 300)
    threat_manager = ThreatLayerManager()
    
    # Test stabilize zone objective
    stab_zone = StabilizeZone(450, 300)
    assert stab_zone.active == True
    stab_zone.update(0.1, player)
    progress = stab_zone.get_progress_ratio()
    assert 0.0 <= progress <= 1.0
    
    # Test reach signal objective
    signal = ReachSignal(500, 300)
    assert signal.active == True
    signal.update(0.1, player)
    
    # Test objectives system update
    objectives.update(1.0, player, threat_manager, 50.0)
    objectives_count = objectives.get_objectives_count()
    assert 'active' in objectives_count
    
    print("✓ Objectives System tests passed")
    return True

def test_countdown_system():
    """Test countdown/uncertainty system"""
    print("\nTesting Countdown System...")
    from game.countdown_system import CountdownSystem, Countdown
    from game.game_state import GameState
    
    # Test individual countdown
    countdown = Countdown(5.0, 'spawn', True)
    assert countdown.active == True
    assert countdown.will_trigger == True
    countdown.update(0.1)
    assert countdown.time_remaining < 5.0
    
    # Test countdown system
    system = CountdownSystem()
    game_state = GameState()
    
    system.update(0.1, game_state)
    visible = system.get_visible_countdowns()
    assert isinstance(visible, list)
    
    stats = system.get_lie_statistics()
    assert 'lie_ratio' in stats
    assert 'total' in stats
    
    print("✓ Countdown System tests passed")
    return True

def test_forced_spawn_mechanism():
    """Test the 5-second forced spawn rule"""
    print("\nTesting Forced Spawn Mechanism...")
    from game.game_state import GameState
    from game.pressure_spawning import PressureSpawningSystem
    from game.threat_layers import ThreatLayerManager
    from game.player import Player
    
    # Test initial spawn (should have enemies within 3 seconds)
    state = GameState()
    
    # Check that enemies were spawned at initialization
    initial_threat_count = state.threat_manager.get_total_threat_count()
    initial_enemy_count = len(state.enemy_manager.enemies)
    assert initial_threat_count > 0 or initial_enemy_count > 0, "No enemies spawned at start!"
    
    # Test forced spawn after 5 seconds of no interaction
    # Start with a clean slate - no threats
    pressure_system = PressureSpawningSystem()
    threat_manager = ThreatLayerManager()
    player = Player(400, 300)
    from game.ai_companion import AICompanion
    ai = AICompanion()
    ai.current_advice = None  # No advice
    
    # Make sure there are no threats initially
    assert threat_manager.get_total_threat_count() == 0
    
    # Simulate 5 seconds of no interaction (no threats, no damage, no advice)
    for i in range(51):  # 51 * 0.1 = 5.1 seconds (slightly over threshold)
        pressure_system.update(0.1, player, threat_manager, ai, 0.5)
    
    # Should trigger forced spawn flag
    assert pressure_system.should_force_spawn() == True, "Forced spawn not triggered after 5 seconds"
    assert pressure_system.time_since_last_interaction >= 5.0
    
    # Test that interaction resets the timer
    pressure_system.on_player_damaged()
    assert pressure_system.time_since_last_interaction == 0
    assert pressure_system.should_force_spawn() == False
    
    # Test forced spawn at screen edge
    threat_count_before = threat_manager.get_total_threat_count()
    result = threat_manager.spawn_forced_threat_at_edge(player)
    assert result == True
    threat_count_after = threat_manager.get_total_threat_count()
    assert threat_count_after > threat_count_before, "Forced spawn didn't create threat"
    
    # Verify hunter was spawned (should be 1)
    assert len(threat_manager.hunters) == 1
    
    # Test reset after forced spawn
    pressure_system.reset_forced_spawn()
    assert pressure_system.should_force_spawn() == False
    assert pressure_system.time_since_last_interaction == 0
    
    print("✓ Forced Spawn Mechanism tests passed")
    return True

def main():
    """Run all tests"""
    print("=" * 50)
    print("One Breath Left - Component Tests")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_player,
        test_world,
        test_ai_companion,
        test_enemy_manager,
        test_game_state,
        test_web_game_state,
        test_playthrough_recording,
        test_endings,
        test_behavior_profiler,
        test_ai_intent_system,
        test_reality_system,
        test_perception_based_enemies,
        test_cross_playthrough_memory,
        test_threat_layers,
        test_pressure_spawning,
        test_player_abilities,
        test_phase_system,
        test_objectives_system,
        test_countdown_system,
        test_forced_spawn_mechanism,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 50)
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
