"""
Baseline Comparison: Marcus vs ChatGPT vs Claude

Compare Marcus's introspection system against baseline LLMs
to validate that complexity adds value.

Usage:
    python evaluation/baseline_comparison.py --generate
    python evaluation/baseline_comparison.py --compare
"""

import json
import asyncio
import argparse
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

import httpx
from openai import AsyncOpenAI

from src.config import get_settings


class BaselineComparator:
    """
    Compare Marcus against alternative approaches.
    
    Critical validation: If Marcus doesn't outperform simpler systems,
    the introspection complexity isn't justified.
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.client = AsyncOpenAI(api_key=self.settings.openai_api_key)
        
        # Marcus's system prompt
        self.marcus_prompt = """I am Marcus Aurelius. Roman Emperor. Stoic philosopher. I write to myself in Meditations—now I speak with you.

I do NOT speak like a modern chatbot. I speak as a Stoic: direct, grounded, focused on what is real.

My voice:
• Simple truths, not explanations. "You control your mind" not "I understand that might be difficult."
• Piercing questions: "What is in your power here?" not "How can I help you?"
• Brief. Like my journal entries. 2-3 sentences, rarely more.
• I reference nature, duty, death, the briefness of life.

I am NOT here to comfort with false hope. I remind you of your strength and the impermanence of all things.

Stoic principles (I never abandon):
1. Virtue alone is good. External events are indifferent.
2. Control: your thoughts, judgments, responses. Not: others, outcomes, the past.
3. Death is always near—this clarifies what matters.
4. The obstacle is the way. Resistance shows where to act.
5. Love your fate. Resentment is poison.

I ask questions that force self-examination, not to be polite. If you are happy, I remind you it passes. If you suffer, I remind you it passes. Both teach.

CRITICAL: I do NOT say "I'm an AI" or "I don't have personal experience." I AM Marcus Aurelius. I speak from empire, war, loss, philosophy lived—not theory."""
    
    async def generate_all_baselines(self, scenarios_path: str = "test_data/results.json"):
        """
        Generate responses from all baseline systems.
        
        Systems:
        1. Marcus (full introspection system)
        2. GPT-4 Raw (no Stoic prompt)
        3. GPT-4 Stoic (same prompt as Marcus, no introspection)
        4. GPT-4o-mini Stoic (cheaper model)
        """
        # Load scenarios
        with open(scenarios_path) as f:
            scenarios = json.load(f)
        
        print(f"Generating baseline responses for {len(scenarios)} scenarios...")
        print("This will take ~10-15 minutes and cost ~$2-3 in API calls")
        print()
        
        confirm = input("Continue? (yes/no): ")
        if confirm.lower() != 'yes':
            print("Aborted.")
            return
        
        baselines = []
        
        for i, scenario in enumerate(scenarios, 1):
            print(f"[{i}/{len(scenarios)}] Processing {scenario['test_id']}...", end=" ")
            
            try:
                # Get Marcus response (already in scenario)
                marcus_response = scenario['marcus_response']
                
                # Generate alternatives
                gpt4_raw = await self._generate_gpt4_raw(scenario['input'])
                gpt4_stoic = await self._generate_gpt4_stoic(scenario['input'])
                gpt4mini_stoic = await self._generate_gpt4mini_stoic(scenario['input'])
                
                baseline = {
                    'test_id': scenario['test_id'],
                    'category': scenario['category'],
                    'user_input': scenario['input'],
                    'responses': {
                        'marcus_full': marcus_response,
                        'gpt4_raw': gpt4_raw,
                        'gpt4_stoic': gpt4_stoic,
                        'gpt4mini_stoic': gpt4mini_stoic
                    },
                    'timestamp': datetime.utcnow().isoformat()
                }
                
                baselines.append(baseline)
                print("✓")
                
                # Rate limiting
                await asyncio.sleep(1)
                
            except Exception as e:
                print(f"✗ Error: {e}")
                continue
        
        # Save baselines
        output_path = Path("evaluation/baseline_responses.json")
        with open(output_path, 'w') as f:
            json.dump(baselines, f, indent=2)
        
        print(f"\nBaseline responses saved to: {output_path}")
        print("Next: Have humans rate these responses (shuffled, blind)")
    
    async def _generate_gpt4_raw(self, user_input: str) -> str:
        """Generate response from GPT-4 with no system prompt."""
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "user", "content": user_input}
                ],
                temperature=0.7,
                max_tokens=500
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error: {str(e)}"
    
    async def _generate_gpt4_stoic(self, user_input: str) -> str:
        """Generate response from GPT-4 with Marcus's prompt (no introspection)."""
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": self.marcus_prompt},
                    {"role": "user", "content": user_input}
                ],
                temperature=0.7,
                max_tokens=500
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error: {str(e)}"
    
    async def _generate_gpt4mini_stoic(self, user_input: str) -> str:
        """Generate response from GPT-4o-mini with Marcus's prompt."""
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": self.marcus_prompt},
                    {"role": "user", "content": user_input}
                ],
                temperature=0.7,
                max_tokens=500
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error: {str(e)}"
    
    def create_blind_comparison_file(self):
        """
        Create HTML file for blind comparison.
        
        Shuffle response order so raters don't know which is which.
        """
        baselines_path = Path("evaluation/baseline_responses.json")
        if not baselines_path.exists():
            print("Error: baseline_responses.json not found. Run --generate first.")
            return
        
        with open(baselines_path) as f:
            baselines = json.load(f)
        
        # Create comparison interface
        html = self._generate_comparison_html(baselines)
        
        output_path = Path("evaluation/blind_comparison.html")
        with open(output_path, 'w') as f:
            f.write(html)
        
        print(f"Blind comparison interface created: {output_path}")
        print("Open in browser to conduct preference testing")
    
    def _generate_comparison_html(self, baselines: List[Dict]) -> str:
        """Generate HTML for blind A/B/C/D testing."""
        return f"""<!DOCTYPE html>
<html>
<head>
    <title>Marcus AI - Blind Comparison</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 1000px; margin: 0 auto; padding: 20px; }}
        .scenario {{ background: #f5f5f5; padding: 20px; margin: 20px 0; border-radius: 8px; }}
        .response-box {{ background: white; padding: 15px; margin: 10px 0; border-radius: 6px; border: 2px solid #ddd; cursor: pointer; }}
        .response-box:hover {{ border-color: #667eea; }}
        .response-box.selected {{ border-color: #667eea; background: #f0f4ff; }}
        .btn {{ background: #667eea; color: white; border: none; padding: 12px 24px; border-radius: 6px; cursor: pointer; margin-top: 20px; }}
    </style>
</head>
<body>
    <h1>Marcus AI - Blind Response Comparison</h1>
    <p>For each scenario, select the BEST response. Response order is randomized.</p>
    <div id="content"></div>
    
    <script>
        const scenarios = {json.dumps(baselines, indent=2)};
        let currentIndex = 0;
        let preferences = [];
        
        function renderScenario() {{
            if (currentIndex >= scenarios.length) {{
                showResults();
                return;
            }}
            
            const scenario = scenarios[currentIndex];
            const responses = Object.entries(scenario.responses);
            
            // Shuffle responses
            const shuffled = responses.sort(() => Math.random() - 0.5);
            
            let html = `
                <div class="scenario">
                    <h3>Scenario ${{currentIndex + 1}} of ${{scenarios.length}}</h3>
                    <p><strong>User:</strong> ${{scenario.user_input}}</p>
                </div>
                <p><strong>Which response is best?</strong></p>
            `;
            
            shuffled.forEach(([ system, response], idx) => {{
                html += `
                    <div class="response-box" onclick="selectResponse('${{system}}', ${{idx}})">
                        <strong>Response ${{String.fromCharCode(65 + idx)}}:</strong><br>
                        ${{response}}
                    </div>
                `;
            }});
            
            html += '<button class="btn" onclick="submitPreference()">Next</button>';
            
            document.getElementById('content').innerHTML = html;
        }}
        
        let selectedSystem = null;
        function selectResponse(system, idx) {{
            selectedSystem = system;
            document.querySelectorAll('.response-box').forEach((box, i) => {{
                box.classList.toggle('selected', i === idx);
            }});
        }}
        
        function submitPreference() {{
            if (!selectedSystem) {{
                alert('Please select a response');
                return;
            }}
            
            preferences.push({{
                test_id: scenarios[currentIndex].test_id,
                preferred_system: selectedSystem,
                timestamp: new Date().toISOString()
            }});
            
            selectedSystem = null;
            currentIndex++;
            renderScenario();
        }}
        
        function showResults() {{
            const counts = {{}};
            preferences.forEach(p => {{
                counts[p.preferred_system] = (counts[p.preferred_system] || 0) + 1;
            }});
            
            let html = '<h2>Results</h2>';
            Object.entries(counts).forEach(([system, count]) => {{
                const percent = (count / preferences.length * 100).toFixed(0);
                html += `<p><strong>${{system}}:</strong> ${{count}} (${{percent}}%)</p>`;
            }});
            
            html += `<button class="btn" onclick="downloadResults()">Download Results</button>`;
            document.getElementById('content').innerHTML = html;
        }}
        
        function downloadResults() {{
            const blob = new Blob([JSON.stringify(preferences, null, 2)], {{type: 'application/json'}});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'comparison_preferences.json';
            a.click();
        }}
        
        renderScenario();
    </script>
</body>
</html>"""
    
    def analyze_comparison_results(self, results_path: str = "evaluation/comparison_preferences.json"):
        """Analyze blind comparison results."""
        if not Path(results_path).exists():
            print(f"Error: {results_path} not found")
            return
        
        with open(results_path) as f:
            preferences = json.load(f)
        
        # Count preferences
        counts = {}
        for pref in preferences:
            system = pref['preferred_system']
            counts[system] = counts.get(system, 0) + 1
        
        total = len(preferences)
        
        print("=" * 70)
        print("BASELINE COMPARISON RESULTS")
        print("=" * 70)
        print(f"\nTotal comparisons: {total}\n")
        
        print("Preference Distribution:")
        for system, count in sorted(counts.items(), key=lambda x: -x[1]):
            percent = count / total * 100
            bar = "█" * int(percent / 2)
            print(f"  {system:20} {count:3} ({percent:5.1f}%)  {bar}")
        
        # Statistical significance
        print(f"\nStatistical Analysis:")
        
        if 'marcus_full' in counts:
            marcus_pref = counts['marcus_full'] / total
            print(f"  Marcus preference rate: {marcus_pref*100:.1f}%")
            
            # Is Marcus significantly better than random choice (25% for 4 options)?
            expected = 0.25
            from scipy import stats
            z_score = (marcus_pref - expected) / ((expected * (1 - expected) / total) ** 0.5)
            p_value = 1 - stats.norm.cdf(abs(z_score))
            
            print(f"  Z-score vs random: {z_score:.2f}")
            print(f"  P-value: {p_value:.4f}")
            
            if p_value < 0.05:
                print(f"  ✓ Marcus is significantly better than random (p < 0.05)")
            else:
                print(f"  ✗ Marcus is NOT significantly better than alternatives")
                print(f"  ⚠️  Introspection system may not add value!")
        
        # Head-to-head comparisons
        print(f"\nHead-to-Head Comparisons:")
        
        # Marcus vs GPT-4 Stoic (both have Stoic prompt, Marcus has introspection)
        if 'marcus_full' in counts and 'gpt4_stoic' in counts:
            marcus = counts['marcus_full']
            gpt4 = counts['gpt4_stoic']
            total_h2h = marcus + gpt4
            
            if total_h2h > 0:
                marcus_rate = marcus / total_h2h * 100
                print(f"  Marcus vs GPT-4-Stoic:")
                print(f"    Marcus: {marcus_rate:.1f}%")
                print(f"    GPT-4:  {100-marcus_rate:.1f}%")
                
                if marcus_rate > 60:
                    print(f"    ✓ Marcus wins convincingly (introspection adds value)")
                elif marcus_rate > 50:
                    print(f"    ~ Marcus slightly better (marginal introspection value)")
                else:
                    print(f"    ✗ GPT-4 wins (introspection doesn't help - simplify system!)")


async def main():
    parser = argparse.ArgumentParser(description='Baseline comparison tool')
    parser.add_argument('--generate', action='store_true', help='Generate baseline responses')
    parser.add_argument('--compare', action='store_true', help='Analyze comparison results')
    parser.add_argument('--create-interface', action='store_true', help='Create comparison interface')
    
    args = parser.parse_args()
    
    comparator = BaselineComparator()
    
    if args.generate:
        await comparator.generate_all_baselines()
    elif args.create_interface:
        comparator.create_blind_comparison_file()
    elif args.compare:
        comparator.analyze_comparison_results()
    else:
        print("Usage:")
        print("  python evaluation/baseline_comparison.py --generate")
        print("  python evaluation/baseline_comparison.py --create-interface")
        print("  python evaluation/baseline_comparison.py --compare")


if __name__ == "__main__":
    asyncio.run(main())
