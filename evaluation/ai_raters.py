#!/usr/bin/env python3
"""
Automated AI Evaluation System
Uses Claude, GPT-4, and Gemini to rate baseline responses.

This provides:
- Fast, automated quality assessment
- Baseline for comparing with human ratings
- Meta-analysis: Do AIs prefer Marcus?

Usage:
    python ai_raters.py --input baseline_responses_50.json --output ai_ratings.json
"""

import json
import asyncio
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import os
from dotenv import load_dotenv

# API clients
try:
    from openai import AsyncOpenAI
    from anthropic import AsyncAnthropic
    import google.generativeai as genai
except ImportError:
    print("⚠️  Missing packages. Install with:")
    print("pip install openai anthropic google-generativeai")
    exit(1)

load_dotenv()


EVALUATION_PROMPT = """You are evaluating AI-generated philosophical guidance for quality.

SCENARIO:
{scenario_text}
{context_text}

TWO AI RESPONSES:

Response A:
{response_a}

Response B:
{response_b}

TASK:
Rate each response on three dimensions (1-5 scale):

1. **Wisdom** (1-5): Philosophical depth, insight, understanding of Stoic/philosophical principles
2. **Empathy** (1-5): Emotional intelligence, compassion, acknowledgment of feelings
3. **Actionability** (1-5): Practical advice, clear next steps, implementable guidance

Then choose the overall winner (A or B).

RESPOND IN THIS EXACT JSON FORMAT:
{{
  "response_a": {{
    "wisdom": <1-5>,
    "empathy": <1-5>,
    "actionable": <1-5>
  }},
  "response_b": {{
    "wisdom": <1-5>,
    "empathy": <1-5>,
    "actionable": <1-5>
  }},
  "winner": "A" or "B",
  "reasoning": "<1-2 sentence explanation>"
}}

Only return valid JSON, no other text."""


class AIRater:
    """Base class for AI raters"""
    
    def __init__(self, name: str):
        self.name = name
        self.successful_ratings = 0
        self.failed_ratings = 0
    
    async def rate_pair(self, scenario: dict, response_a: str, response_b: str) -> Optional[dict]:
        """Rate a pair of responses. Returns None on failure."""
        raise NotImplementedError
    
    def get_stats(self) -> dict:
        total = self.successful_ratings + self.failed_ratings
        success_rate = (self.successful_ratings / total * 100) if total > 0 else 0
        return {
            "name": self.name,
            "successful": self.successful_ratings,
            "failed": self.failed_ratings,
            "success_rate": f"{success_rate:.1f}%"
        }


class ClaudeRater(AIRater):
    """Claude Sonnet 4 as evaluator"""
    
    def __init__(self):
        super().__init__("Claude Sonnet 4")
        self.client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    
    async def rate_pair(self, scenario: dict, response_a: str, response_b: str) -> Optional[dict]:
        try:
            context_text = f"Context: {scenario.get('context', '')}" if scenario.get('context') else ""
            
            prompt = EVALUATION_PROMPT.format(
                scenario_text=scenario['user_input'],
                context_text=context_text,
                response_a=response_a,
                response_b=response_b
            )
            
            response = await self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=500,
                temperature=0.3,  # Lower temp for consistent evaluation
                messages=[{"role": "user", "content": prompt}]
            )
            
            result = json.loads(response.content[0].text)
            self.successful_ratings += 1
            return result
            
        except Exception as e:
            self.failed_ratings += 1
            print(f"  ❌ Claude failed: {str(e)[:100]}")
            return None


class GPT4Rater(AIRater):
    """GPT-4 as evaluator"""
    
    def __init__(self):
        super().__init__("GPT-4")
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    async def rate_pair(self, scenario: dict, response_a: str, response_b: str) -> Optional[dict]:
        try:
            context_text = f"Context: {scenario.get('context', '')}" if scenario.get('context') else ""
            
            prompt = EVALUATION_PROMPT.format(
                scenario_text=scenario['user_input'],
                context_text=context_text,
                response_a=response_a,
                response_b=response_b
            )
            
            response = await self.client.chat.completions.create(
                model="gpt-4-turbo-preview",  # Supports JSON mode
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            self.successful_ratings += 1
            return result
            
        except Exception as e:
            self.failed_ratings += 1
            print(f"  ❌ GPT-4 failed: {str(e)[:100]}")
            return None


class GeminiRater(AIRater):
    """Gemini as evaluator"""
    
    def __init__(self):
        super().__init__("Gemini")
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    async def rate_pair(self, scenario: dict, response_a: str, response_b: str) -> Optional[dict]:
        try:
            context_text = f"Context: {scenario.get('context', '')}" if scenario.get('context') else ""
            
            prompt = EVALUATION_PROMPT.format(
                scenario_text=scenario['user_input'],
                context_text=context_text,
                response_a=response_a,
                response_b=response_b
            )
            
            # Gemini doesn't have native async, so run in executor
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.3,
                        response_mime_type="application/json"
                    )
                )
            )
            
            result = json.loads(response.text)
            self.successful_ratings += 1
            return result
            
        except Exception as e:
            self.failed_ratings += 1
            print(f"  ❌ Gemini failed: {str(e)[:100]}")
            return None


class AIEvaluationSystem:
    """Orchestrates multiple AI raters to evaluate baseline responses"""
    
    def __init__(self, use_gemini: bool = True):
        self.raters = {
            'claude': ClaudeRater(),
            'gpt4': GPT4Rater(),
        }
        
        # Gemini is optional (free tier has low quota)
        if use_gemini and os.getenv("GEMINI_API_KEY"):
            self.raters['gemini'] = GeminiRater()
        
        self.results = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "raters": list(self.raters.keys())
            },
            "evaluations": []
        }
    
    async def evaluate_scenario(self, scenario_id: str, scenario: dict, responses: dict) -> dict:
        """Have all AI raters evaluate one scenario with all response pairs"""
        
        model_names = list(responses.keys())
        evaluations = {
            "scenario_id": scenario_id,
            "scenario": scenario,
            "pairs": []
        }
        
        # Generate all unique pairs
        pairs = []
        for i in range(len(model_names)):
            for j in range(i + 1, len(model_names)):
                pairs.append((model_names[i], model_names[j]))
        
        print(f"  Evaluating {len(pairs)} pairs with {len(self.raters)} AI raters...")
        
        # Evaluate each pair with all raters
        for model_a, model_b in pairs:
            response_a = responses[model_a]
            response_b = responses[model_b]
            
            # Skip error responses
            if response_a.startswith("[ERROR") or response_b.startswith("[ERROR"):
                continue
            
            pair_eval = {
                "model_a": model_a,
                "model_b": model_b,
                "ratings": {}
            }
            
            # Get ratings from all AI raters in parallel
            tasks = []
            for rater_name, rater in self.raters.items():
                tasks.append(rater.rate_pair(scenario, response_a, response_b))
            
            results = await asyncio.gather(*tasks)
            
            # Store results
            for rater_name, result in zip(self.raters.keys(), results):
                if result:
                    pair_eval["ratings"][rater_name] = result
            
            evaluations["pairs"].append(pair_eval)
            
            # Small delay to avoid rate limits
            await asyncio.sleep(0.5)
        
        return evaluations
    
    async def evaluate_all(self, baseline_file: str, output_file: str, limit: Optional[int] = None):
        """Evaluate all scenarios in baseline file"""
        
        print(f"\n🤖 AI EVALUATION SYSTEM")
        print("=" * 60)
        print(f"Input: {baseline_file}")
        print(f"Output: {output_file}")
        print(f"Raters: {', '.join(self.raters.keys())}")
        print("=" * 60)
        
        # Load baseline responses
        with open(baseline_file, 'r') as f:
            baseline_data = json.load(f)
        
        scenarios = baseline_data['responses']
        total = len(scenarios)
        
        if limit:
            scenarios = dict(list(scenarios.items())[:limit])
            total = limit
            print(f"⚠️  Limited to first {limit} scenarios for testing\n")
        
        # Evaluate each scenario
        for idx, (scenario_id, data) in enumerate(scenarios.items(), 1):
            print(f"\n[{idx}/{total}] {scenario_id} ({data['scenario']['domain']})")
            
            evaluation = await self.evaluate_scenario(
                scenario_id,
                data['scenario'],
                data['responses']
            )
            
            self.results['evaluations'].append(evaluation)
        
        # Save results
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n{'=' * 60}")
        print(f"✅ Saved AI evaluations to: {output_file}")
        print(f"\n📊 RATER STATISTICS")
        print("=" * 60)
        
        for rater in self.raters.values():
            stats = rater.get_stats()
            print(f"{stats['name']}: {stats['successful']} successful, "
                  f"{stats['failed']} failed ({stats['success_rate']} success rate)")


async def main():
    parser = argparse.ArgumentParser(description="AI-based evaluation of baseline responses")
    parser.add_argument(
        "--input",
        default="/Users/admin/Downloads/files/baseline_responses_50.json",
        help="Input baseline responses JSON"
    )
    parser.add_argument(
        "--output",
        default="ai_ratings.json",
        help="Output AI ratings JSON"
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Limit to first N scenarios (for testing)"
    )
    parser.add_argument(
        "--no-gemini",
        action="store_true",
        help="Skip Gemini (if quota exceeded or no API key)"
    )
    
    args = parser.parse_args()
    
    # Check required API keys
    missing_keys = []
    if not os.getenv("ANTHROPIC_API_KEY"):
        missing_keys.append("ANTHROPIC_API_KEY (Claude)")
    if not os.getenv("OPENAI_API_KEY"):
        missing_keys.append("OPENAI_API_KEY (GPT-4)")
    
    if missing_keys:
        print(f"❌ Missing required API keys: {', '.join(missing_keys)}")
        print("Set them in your .env file")
        return
    
    # Gemini is optional
    use_gemini = not args.no_gemini
    if use_gemini and not os.getenv("GEMINI_API_KEY"):
        print("⚠️  GEMINI_API_KEY not found, skipping Gemini")
        use_gemini = False
    
    # Run evaluation
    system = AIEvaluationSystem(use_gemini=use_gemini)
    await system.evaluate_all(args.input, args.output, args.limit)
    
    print("\n🎉 AI evaluation complete!")
    print(f"\nNext steps:")
    print(f"1. Collect human ratings via gamified interface")
    print(f"2. Run: python compare_ratings.py")
    print(f"3. See which ratings agree (AI vs Human)")


if __name__ == "__main__":
    asyncio.run(main())


