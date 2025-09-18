"""Command-line interface for gitfind."""

import argparse
import sys
from colorama import init, Fore, Style
from gitfind.core import repo_summary, GitHubAPIError

init()  # Initialize colorama

def print_colored_report(report: dict) -> None:
    """
    Print a colored report to the terminal with exact field names as requested.
    
    Args:
        report (dict): The repository report
    """
    print(f"\n{Fore.CYAN}🔍 GitHub Repository Analysis Report{Style.RESET_ALL}")
    print(f"{Fore.CYAN}====================================={Style.RESET_ALL}")
    
    # Display exact fields as requested
    print(f"{Fore.GREEN}⭐ {Fore.WHITE}Total Stars: {Fore.YELLOW}{report['Total Stars']}{Style.RESET_ALL}")
    print(f"{Fore.BLUE}🍴 {Fore.WHITE}Total Forks: {Fore.YELLOW}{report['Total Forks']}{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}👨‍💻 {Fore.WHITE}Total Contributors: {Fore.YELLOW}{report['Total Contributors']}{Style.RESET_ALL}")
    print(f"{Fore.RED}⏳ {Fore.WHITE}Last Commit Date: {Fore.YELLOW}{report['Last Commit Date']}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}🖥️  {Fore.WHITE}Primary Programming Languages: {Fore.YELLOW}{report['Primary Programming Languages']}{Style.RESET_ALL}")
    
    print(f"\n{Fore.YELLOW}📝 {Fore.WHITE}Auto-generated summary report:{Style.RESET_ALL}")
    print(f"{Fore.WHITE}{report['Auto-generated summary report']}{Style.RESET_ALL}")
    
    # Additional info (optional)
    print(f"\n{Fore.WHITE}Additional Information:{Style.RESET_ALL}")
    print(f"{Fore.WHITE}Repository URL: {Fore.BLUE}{report['Repository URL']}{Style.RESET_ALL}")
    if report['Description'] and report['Description'] != 'No description available':
        print(f"{Fore.WHITE}Description: {Fore.BLUE}{report['Description']}{Style.RESET_ALL}")

def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(description="Analyze a GitHub repository and generate a detailed report.")
    parser.add_argument("url", help="URL of the GitHub repository to analyze")
    
    args = parser.parse_args()
    
    try:
        report = repo_summary(args.url)
        print_colored_report(report)
    except Exception as e:
        print(f"{Fore.RED}❌ Error: {str(e)}{Style.RESET_ALL}")
        sys.exit(1)

if __name__ == "__main__":
    main()