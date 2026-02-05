#!/usr/bin/env python3
"""
Script de teste para V-LLM Directors API

Usage:
    python examples/test_api.py
"""

import json
import httpx
import asyncio
from pathlib import Path


BASE_URL = "http://localhost:5025"


async def test_health():
    """Testa health check"""
    print("\n🏥 Testing Health Check...")
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/health")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        return response.status_code == 200


async def test_list_directors():
    """Lista directors disponíveis"""
    print("\n📋 Listing Directors...")
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/directors")
        data = response.json()
        print(f"   Status: {response.status_code}")
        print(f"   Total Directors: {data.get('total_directors', 0)}")
        
        for level, directors in data.get('levels', {}).items():
            if directors:
                print(f"\n   Level {level}:")
                for director in directors:
                    print(f"     - {director['name']}")
                    print(f"       Endpoint: {director['endpoint']}")
        
        return response.status_code == 200


async def test_motion_graphics_plan(prompt_file: str = "tutorial_3_passos.json"):
    """Testa planejamento de motion graphics"""
    print(f"\n🎬 Testing Motion Graphics Plan...")
    print(f"   Using prompt: {prompt_file}")
    
    # Carregar exemplo de prompt
    prompt_path = Path(__file__).parent / "prompts" / prompt_file
    
    if not prompt_path.exists():
        print(f"   ❌ Prompt file not found: {prompt_path}")
        return False
    
    with open(prompt_path, 'r', encoding='utf-8') as f:
        prompt_data = json.load(f)
    
    payload = {
        "user_prompt": prompt_data["user_prompt"],
        "context": prompt_data["context"]
    }
    
    print(f"   User Prompt: {payload['user_prompt'][:80]}...")
    print(f"   Context: {len(prompt_data['context']['words'])} words, "
          f"{len(prompt_data['context']['text_layout'])} text elements")
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            response = await client.post(
                f"{BASE_URL}/directors/level-0/motion-graphics/plan",
                json=payload
            )
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('status') == 'success':
                    plan = data.get('plan', {})
                    mgs = plan.get('motion_graphics', [])
                    
                    print(f"   ✅ Plan created successfully!")
                    print(f"   Motion Graphics: {len(mgs)}")
                    
                    for i, mg in enumerate(mgs, 1):
                        print(f"\n   MG #{i}:")
                        print(f"     ID: {mg['id']}")
                        print(f"     Type: {mg['type']}")
                        print(f"     Target: {mg['target_word']}")
                        print(f"     Timing: {mg['timing']['start_time']}s "
                              f"(duration: {mg['timing']['duration']}s)")
                        print(f"     Justification: {mg['justification'][:80]}...")
                    
                    # Mostrar reasoning
                    reasoning = plan.get('reasoning', {})
                    if reasoning:
                        print(f"\n   Strategy: {reasoning.get('strategy', 'N/A')[:100]}...")
                    
                    # Mostrar uso de LLM
                    llm_usage = data.get('llm_usage', {})
                    if llm_usage:
                        print(f"\n   LLM Usage:")
                        print(f"     Model: {llm_usage.get('model', 'N/A')}")
                        print(f"     Tokens: {llm_usage.get('total_tokens', 'N/A')}")
                    
                    # Salvar resposta
                    response_dir = Path(__file__).parent / "responses"
                    response_dir.mkdir(exist_ok=True)
                    
                    response_file = response_dir / f"{Path(prompt_file).stem}_test_response.json"
                    with open(response_file, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
                    
                    print(f"\n   💾 Response saved to: {response_file}")
                    
                    return True
                else:
                    print(f"   ❌ Plan failed: {data.get('error')}")
                    print(f"   Details: {data.get('details')}")
                    return False
            else:
                print(f"   ❌ HTTP Error: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                return False
                
        except httpx.TimeoutException:
            print(f"   ❌ Timeout: Request took too long")
            return False
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False


async def run_all_tests():
    """Executa todos os testes"""
    print("=" * 60)
    print("🧪 V-LLM Directors API Test Suite")
    print("=" * 60)
    
    results = {}
    
    # Test 1: Health
    results['health'] = await test_health()
    
    # Test 2: List Directors
    results['list_directors'] = await test_list_directors()
    
    # Test 3: Motion Graphics Plan - Tutorial
    results['mg_tutorial'] = await test_motion_graphics_plan("tutorial_3_passos.json")
    
    # Test 4: Motion Graphics Plan - Promocional
    results['mg_promo'] = await test_motion_graphics_plan("video_promocional.json")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    print("=" * 60)
    
    return all(results.values())


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    exit(0 if success else 1)
