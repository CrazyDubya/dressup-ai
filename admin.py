"""
Admin interface for monitoring A/B testing and error tracking in the Fashion Outfit Generator.
"""

import sys
import logging
from typing import Dict, List
from datetime import datetime
from dress_maker import OutfitGenerator

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdminInterface:
    def __init__(self):
        self.outfit_generator = OutfitGenerator()
    
    def display_stats(self):
        """Display current A/B testing statistics."""
        results = self.outfit_generator.get_ab_results()
        
        print("\n=== A/B Testing Statistics ===")
        print("\nPrompt A (Standard):")
        self._display_prompt_stats(results['A'])
        
        print("\nPrompt B (XML):")
        self._display_prompt_stats(results['B'])
    
    def _display_prompt_stats(self, stats: Dict):
        """Display statistics for a single prompt type."""
        print(f"Success Rate: {stats['success_rate']:.2%}")
        print(f"Total Attempts: {stats['total']}")
        print(f"Total Errors: {stats['total_errors']}")
        print("\nAverage Scores:")
        print(f"  Formality: {stats['avg_formality']:.1f}/10")
        print(f"  Trendiness: {stats['avg_trendiness']:.1f}/10")
        print(f"  Comfort: {stats['avg_comfort']:.1f}/10")
        print("\nError Rates:")
        for error_type, rate in stats['error_rates'].items():
            print(f"  {error_type}: {rate:.2%}")
    
    def display_recent_errors(self, prompt_type: str, limit: int = 10):
        """Display recent errors for a prompt type."""
        errors = self.outfit_generator.get_error_logs(prompt_type, limit)
        
        print(f"\n=== Recent Errors for Prompt {prompt_type} ===")
        if not errors:
            print("No recent errors.")
            return
        
        for error in errors:
            timestamp = datetime.fromisoformat(error['timestamp'])
            print(f"\nTime: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Type: {error['type']}")
            print(f"Message: {error['message']}")
    
    def clear_error_logs(self, prompt_type: str):
        """Clear error logs for a prompt type."""
        self.outfit_generator.clear_error_logs(prompt_type)
        print(f"Cleared error logs for Prompt {prompt_type}")
    
    def run(self):
        """Run the admin interface."""
        while True:
            print("\n=== Fashion Outfit Generator Admin ===")
            print("1. View A/B Testing Statistics")
            print("2. View Recent Errors (Prompt A)")
            print("3. View Recent Errors (Prompt B)")
            print("4. Clear Error Logs (Prompt A)")
            print("5. Clear Error Logs (Prompt B)")
            print("6. Exit")
            
            choice = input("\nEnter your choice (1-6): ")
            
            if choice == "1":
                self.display_stats()
            elif choice == "2":
                self.display_recent_errors('A')
            elif choice == "3":
                self.display_recent_errors('B')
            elif choice == "4":
                self.clear_error_logs('A')
            elif choice == "5":
                self.clear_error_logs('B')
            elif choice == "6":
                print("Goodbye!")
                break
            else:
                print("Invalid choice. Please try again.")

if __name__ == "__main__":
    admin = AdminInterface()
    admin.run() 