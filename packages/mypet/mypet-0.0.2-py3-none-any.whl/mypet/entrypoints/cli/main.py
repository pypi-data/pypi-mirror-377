"""Main CLI entry point for mypet."""

import argparse
import sys


from mypet import __version__


def speak_cat():
    """Output cat sound."""
    print("miow")


def speak_dog():
    """Output dog sound."""
    print("wang")


def feed_cat():
    """Output cat food."""
    print("fish")


def feed_dog():
    """Output dog food."""
    print("meat")


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="MyPet - A simple CLI tool for pet commands",
        prog="mypet"
    )
    
    parser.add_argument("--version", action="version", version=f"{__version__}")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Speak command
    speak_parser = subparsers.add_parser("speak", help="Make pet sounds")
    speak_group = speak_parser.add_mutually_exclusive_group(required=True)
    speak_group.add_argument("--cat", action="store_true", help="Cat sound")
    speak_group.add_argument("--dog", action="store_true", help="Dog sound")
    
    # Feed command
    feed_parser = subparsers.add_parser("feed", help="Feed pets")
    feed_group = feed_parser.add_mutually_exclusive_group(required=True)
    feed_group.add_argument("--cat", action="store_true", help="Feed cat")
    feed_group.add_argument("--dog", action="store_true", help="Feed dog")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    if args.command == "speak":
        if args.cat:
            speak_cat()
        elif args.dog:
            speak_dog()
    elif args.command == "feed":
        if args.cat:
            feed_cat()
        elif args.dog:
            feed_dog()


if __name__ == "__main__":
    main()
