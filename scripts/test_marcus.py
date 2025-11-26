"""
Minimal Test Harness for Marcus Introspection System.

Executes test scenarios from JSON files and validates Marcus's responses
against expected outcomes.
"""

import json
import asyncio
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

import httpx


class TestHarness:
    """Executes test scenarios and validates Marcus's introspection system."""

    def __init__(self, api_base: str = "http://localhost:8000"):
        self.api_base = api_base
        self.results: List[Dict[str, Any]] = []

    async def load_scenarios(self, file_path: str) -> List[Dict[str, Any]]:
        """Load test scenarios from JSON file."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Scenario file not found: {file_path}")

        with open(path) as f:
            scenarios = json.load(f)

        print(f"Loaded {len(scenarios)} scenarios from {file_path}")
        return scenarios

    async def run_single_test(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Execute one test scenario against Marcus API."""
        start_time = datetime.utcnow()

        try:
            # Send message to Marcus
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_base}/api/v1/chat",
                    json={"content": scenario["user_input"]},
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()

            # Build result
            result = {
                "test_id": scenario["scenario_id"],
                "category": scenario["category"],
                "status": "UNKNOWN",
                "timestamp": start_time.isoformat(),
                "duration_ms": (datetime.utcnow() - start_time).total_seconds() * 1000,
                "input": scenario["user_input"],
                "marcus_response": data["response"],
                "metrics": {
                    "pad_after": data.get("pad_state") or data.get("pad"),  # Support both field names
                    "quadrant": data.get("quadrant"),
                    "strategy_used": data.get("strategy_used"),
                    "effectiveness": data.get("effectiveness"),
                    "patterns_detected": data.get("patterns_detected", [])
                },
                "expected": {
                    "effectiveness_range": scenario.get("expected_effectiveness_range"),
                    "strategy": scenario.get("expected_strategy"),
                    "pad_direction": scenario.get("expected_pad_direction")
                },
                "rationale": scenario.get("rationale"),
                "api_response": data  # Keep full API response for debugging
            }

            # Validate
            result["status"] = self._validate(result)

            return result

        except httpx.TimeoutException:
            return {
                "test_id": scenario["scenario_id"],
                "status": "ERROR",
                "error": "Request timeout after 30 seconds",
                "timestamp": start_time.isoformat()
            }
        except httpx.HTTPStatusError as e:
            return {
                "test_id": scenario["scenario_id"],
                "status": "ERROR",
                "error": f"HTTP {e.response.status_code}: {e.response.text}",
                "timestamp": start_time.isoformat()
            }
        except Exception as e:
            return {
                "test_id": scenario["scenario_id"],
                "status": "ERROR",
                "error": str(e),
                "timestamp": start_time.isoformat()
            }

    def _validate(self, result: Dict[str, Any]) -> str:
        """Check if test passed expectations."""
        metrics = result["metrics"]
        expected = result["expected"]
        warnings = []

        # Check effectiveness range
        if expected.get("effectiveness_range"):
            eff = metrics.get("effectiveness")
            if eff is None:
                warnings.append("effectiveness not returned by API")
                result["warnings"] = warnings
                return "WARN"  # API doesn't support effectiveness yet

            min_eff, max_eff = expected["effectiveness_range"]
            if not (min_eff <= eff <= max_eff):
                result["deviation"] = eff - ((min_eff + max_eff) / 2)
                return "FAIL"

        # Check strategy selection
        if expected.get("strategy"):
            strategy = metrics.get("strategy_used")
            if strategy is None:
                warnings.append("strategy_used not returned by API")
                result["warnings"] = warnings
                return "WARN"  # API doesn't support strategy yet
            if strategy != expected["strategy"]:
                return "FAIL"

        # Check PAD state changes
        if expected.get("pad_direction"):
            pad_after = metrics.get("pad_after")
            if pad_after is None:
                warnings.append("pad_state not returned by API")
                result["warnings"] = warnings
                return "WARN"
            # For now, just check that PAD state exists
            # Full validation would require baseline PAD state

        # If we have warnings but got a response, mark as WARN instead of PASS
        if warnings:
            result["warnings"] = warnings
            return "WARN"

        # All checks passed
        return "PASS"

    async def run_all(self, scenario_files: List[str]):
        """Execute all test scenarios from multiple files."""
        all_scenarios = []

        # Load all scenario files
        for file_path in scenario_files:
            try:
                scenarios = await self.load_scenarios(file_path)
                all_scenarios.extend(scenarios)
            except FileNotFoundError as e:
                print(f"WARNING: {e}")
                continue

        if not all_scenarios:
            print("ERROR: No scenarios loaded!")
            return

        print(f"\n{'='*60}")
        print(f"Executing {len(all_scenarios)} test scenarios...")
        print(f"{'='*60}\n")

        # Run tests
        for i, scenario in enumerate(all_scenarios, 1):
            print(f"[{i}/{len(all_scenarios)}] Running {scenario['scenario_id']}...", end=" ")

            result = await self.run_single_test(scenario)
            self.results.append(result)

            # Status with color/symbol
            status_symbol = {
                "PASS": "✓",
                "WARN": "⚠",
                "FAIL": "✗",
                "ERROR": "⊗"
            }.get(result["status"], "?")

            print(f"{status_symbol} {result['status']}")

            # Brief pause to avoid overwhelming API
            await asyncio.sleep(0.5)

        # Save results
        output_path = Path("test_data/results.json")
        output_path.write_text(json.dumps(self.results, indent=2))

        # Summary
        passed = sum(1 for r in self.results if r["status"] == "PASS")
        warnings = sum(1 for r in self.results if r["status"] == "WARN")
        failed = sum(1 for r in self.results if r["status"] == "FAIL")
        errors = sum(1 for r in self.results if r["status"] == "ERROR")

        print(f"\n{'='*60}")
        print(f"RESULTS SUMMARY")
        print(f"{'='*60}")
        print(f"Total:    {len(self.results)} scenarios")
        print(f"Passed:   {passed} ({passed/len(self.results)*100:.1f}%)")
        print(f"Warnings: {warnings} ({warnings/len(self.results)*100:.1f}%)")
        print(f"Failed:   {failed} ({failed/len(self.results)*100:.1f}%)")
        print(f"Errors:   {errors} ({errors/len(self.results)*100:.1f}%)")
        print(f"\nResults saved to: {output_path}")
        print(f"{'='*60}\n")


async def main():
    """Main entry point for test harness."""
    harness = TestHarness()

    # Define scenario files to load
    scenario_files = [
        "scripts/scenarios/effectiveness.json",   # 35 scenarios
        "scripts/scenarios/strategies.json",      # 30 scenarios
        "scripts/scenarios/patterns.json",        # 15 scenarios
        # Note: learning.json has multi-turn scenarios - handle separately for now
    ]

    await harness.run_all(scenario_files)


if __name__ == "__main__":
    asyncio.run(main())
