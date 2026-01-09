"""
Launch the Lead Generation Dashboard
Simple launcher script for the web interface
"""

import subprocess
import sys

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 Starting Lead Generation Dashboard...")
    print("=" * 60)
    print("\n📌 Dashboard will open in your browser")
    print("🔗 URL: http://localhost:8501")
    print("⏹️  Press Ctrl+C to stop the server\n")
    print("=" * 60)
    
    try:
        subprocess.run([
            sys.executable,
            "-m",
            "streamlit",
            "run",
            "dashboard.py",
            "--server.port=8501",
            "--server.headless=true"
        ])
    except KeyboardInterrupt:
        print("\n\n👋 Dashboard stopped. Goodbye!")
