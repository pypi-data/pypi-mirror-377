from .analyzer import analyze_text
import sys
import json

def main():
    if len(sys.argv) < 2:
        print("Usage: TextAnalyzerLib <text>")
        return
    text = sys.argv[1]
    result = analyze_text(text)
    print(json.dumps(result, indent=4))

if __name__ == "__main__":
    main()
