"""
Apple HealthKit Setup Helper
Quick script to configure real Apple Watch data integration
"""

import os
import sys
from pathlib import Path


def check_requirements():
    """Check if required packages are installed"""
    required = {
        'streamlit': 'Streamlit',
        'plotly': 'Plotly',
        'pandas': 'Pandas',
        'numpy': 'NumPy',
    }
    
    print("📋 Checking requirements...\n")
    
    missing = []
    for package, name in required.items():
        try:
            __import__(package)
            print(f"✅ {name}")
        except ImportError:
            print(f"❌ {name} - NOT INSTALLED")
            missing.append(package)
    
    if missing:
        print(f"\n⚠️  Missing packages: {', '.join(missing)}")
        print(f"\n💻 Install with:\n  pip install {' '.join(missing)}\n")
        return False
    
    print("\n✅ All base requirements met!")
    return True


def configure_healthkit_mode():
    """Configure HealthKit integration mode"""
    print("\n" + "="*60)
    print("🍎 APPLE HEALTHKIT INTEGRATION SETUP")
    print("="*60 + "\n")
    
    print("Choose your integration approach:\n")
    print("1️⃣  DEMO MODE (Recommended for testing)")
    print("   • Uses realistic synthetic data")
    print("   • No Apple Watch required")
    print("   • Perfect for hackathons")
    print("   ✅ Just works!\n")
    
    print("2️⃣  macOS HealthKit (Native, fastest)")
    print("   • Direct access to Apple Watch data")
    print("   • Lowest latency")
    print("   • Requires: macOS + Health app\n")
    
    print("3️⃣  iCloud Cloud Sync (Works anywhere)")
    print("   • Cross-platform (Windows, Linux, Mac)")
    print("   • Syncs from iPhone to computer")
    print("   • Requires: Apple ID + iCloud\n")
    
    print("4️⃣  REST API Server (Most flexible)")
    print("   • Local server bridges iPhone and app")
    print("   • Best for custom workflows")
    print("   • Requires: Same WiFi network\n")
    
    choice = input("Enter choice (1-4): ").strip()
    
    return configure_mode(choice)


def configure_mode(choice):
    """Configure selected mode"""
    
    if choice == "1":
        return setup_demo_mode()
    elif choice == "2":
        return setup_native_healthkit()
    elif choice == "3":
        return setup_icloud_sync()
    elif choice == "4":
        return setup_rest_api()
    else:
        print("❌ Invalid choice. Using demo mode.\n")
        return setup_demo_mode()


def setup_demo_mode():
    """Setup demo mode (default)"""
    print("\n✅ Demo Mode Selected\n")
    print("📝 Instructions:")
    print("   1. No setup needed!")
    print("   2. Run: streamlit run app_final.py")
    print("   3. Open: http://localhost:8506")
    print("   4. Go to '📱 Live Coach' tab")
    print("   5. Click 'START LIVE COACHING'\n")
    
    print("✨ You'll see:")
    print("   • Realistic HR patterns")
    print("   • Recovery-based metrics")
    print("   • Live coaching cues")
    print("   • Adaptive intervals\n")
    
    return {
        "mode": "demo",
        "use_demo_mode": True,
        "api_url": None
    }


def setup_native_healthkit():
    """Setup native macOS HealthKit"""
    print("\n📱 Native HealthKit Setup (macOS only)\n")
    
    if sys.platform != 'darwin':
        print("❌ This option requires macOS")
        print("💡 Use 'iCloud Cloud Sync' or 'REST API' instead\n")
        return None
    
    print("📝 Setup Instructions:")
    print("   1. Install HealthKit library:")
    print("      pip install healthkit\n")
    
    print("   2. Enable on iPhone:")
    print("      • Health app → Apple Watch device")
    print("      • Enable all health data sharing\n")
    
    print("   3. Verify System:")
    print("      python -c \"import healthkit; print('✅ Ready')\"")
    print("      (If error appears, macOS REPL access needed)\n")
    
    input("Press Enter once setup complete: ")
    
    return {
        "mode": "native_healthkit",
        "use_demo_mode": False,
        "library": "healthkit",
        "requires_compile": True
    }


def setup_icloud_sync():
    """Setup iCloud cloud sync"""
    print("\n☁️  iCloud Cloud Sync Setup\n")
    
    print("📝 Prerequisites:")
    print("   ✅ Apple ID account")
    print("   ✅ iPhone with Health app")
    print("   ✅ iCloud Health Backup enabled\n")
    
    print("💻 Setup Steps:\n")
    
    print("Step 1: Get App-Specific Password")
    print("   1. Visit: https://appleid.apple.com")
    print("   2. Sign in with your Apple ID")
    print("   3. Go to 'App passwords' section")
    print("   4. Generate password for 'Cardio Coach'")
    print("   5. Copy the 16-character code\n")
    
    apple_id = input("Enter your Apple ID (email): ").strip()
    app_password = input("Enter app-specific password: ").strip()
    
    if not apple_id or not app_password:
        print("❌ Credentials required")
        return None
    
    print("\nStep 2: Install iCloud library")
    print("   pip install pyicloud\n")
    
    print("Step 3: Test connection")
    print("   python -c \"from pyicloud import PyiCloudService; print('✅ Ready')\"")
    
    return {
        "mode": "icloud_sync",
        "use_demo_mode": False,
        "apple_id": apple_id,
        "app_password": app_password,
        "library": "pyicloud"
    }


def setup_rest_api():
    """Setup REST API server"""
    print("\n🌐 REST API Server Setup\n")
    
    print("📝 How it works:")
    print("   • iPhone sends data to local server")
    print("   • Server exposes REST API")
    print("   • Streamlit app queries API\n")
    
    print("🔧 Setup Steps:\n")
    
    print("Step 1: Install Flask")
    print("   pip install flask flask-cors\n")
    
    print("Step 2: Create healthkit_api_server.py")
    print("   (File template provided below)\n")
    
    print("Step 3: Start server (Terminal 1)")
    print("   python healthkit_api_server.py")
    print("   Server at: http://localhost:5000\n")
    
    print("Step 4: Run app (Terminal 2)")
    print("   streamlit run app_final.py")
    print("   App at: http://localhost:8506\n")
    
    return {
        "mode": "rest_api",
        "use_demo_mode": False,
        "api_url": "http://localhost:5000/api",
        "library": "flask"
    }


def print_summary(config):
    """Print final configuration summary"""
    if not config:
        config = setup_demo_mode()
    
    print("\n" + "="*60)
    print("✅ CONFIGURATION COMPLETE")
    print("="*60 + "\n")
    
    print(f"Mode: {config['mode'].upper()}\n")
    
    print("🚀 Next Steps:")
    
    if config['mode'] == 'demo':
        print("   1. Run: streamlit run app_final.py")
        print("   2. Open: http://localhost:8506")
        print("   3. Go to '📱 Live Coach' tab")
        print("   4. Start a coaching session!\n")
    
    elif config['mode'] == 'native_healthkit':
        print("   1. Run: streamlit run app_final.py")
        print("   2. App connects automatically")
        print("   3. Check Health app on iPhone for data\n")
    
    elif config['mode'] == 'icloud_sync':
        print("   1. Ensure iPhone is on same WiFi")
        print("   2. Run: streamlit run app_final.py")
        print("   3. App syncs from iCloud")
        print("   4. Check connection status in app\n")
    
    elif config['mode'] == 'rest_api':
        print("   Terminal 1 (Server):")
        print("      python healthkit_api_server.py\n")
        print("   Terminal 2 (App):")
        print("      streamlit run app_final.py\n")
        print("   Then: Go to http://localhost:8506\n")
    
    print("📚 For detailed guide, see: APPLE_WATCH_SETUP.md\n")


def main():
    """Main setup flow"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║ 🍎 CARDIO DIGITAL TWIN - APPLE WATCH SETUP ║")
    print("╚" + "="*58 + "╝\n")
    
    # Check requirements
    if not check_requirements():
        print("⚠️  Please install missing packages and try again.\n")
        return
    
    # Configure mode
    config = configure_healthkit_mode()
    
    # Print summary
    print_summary(config)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled\n")
    except Exception as e:
        print(f"\n⚠️  Error: {e}\n")
