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
    
    # Test movement
    player.move(1, 0)
    assert player.velocity_x > 0
    
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
