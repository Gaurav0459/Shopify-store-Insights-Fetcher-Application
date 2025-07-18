import uvicorn
import time
import os

def print_banner():
    """Print a custom banner for the application"""
    banner = """
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║   ███████╗██╗  ██╗ ██████╗ ██████╗ ██╗███╗   ██╗███████╗ ║
    ║   ██╔════╝██║  ██║██╔═══██╗██╔══██╗██║████╗  ██║██╔════╝ ║
    ║   ███████╗███████║██║   ██║██████╔╝██║██╔██╗ ██║███████╗ ║
    ║   ╚════██║██╔══██║██║   ██║██╔═══╝ ██║██║╚██╗██║╚════██║ ║
    ║   ███████║██║  ██║╚██████╔╝██║     ██║██║ ╚████║███████║ ║
    ║   ╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚═╝     ╚═╝╚═╝  ╚═══╝╚══════╝ ║
    ║                                                           ║
    ║   Shopify Store Insights Analyzer                         ║
    ║   Created by: Gaurav                                      ║
    ║   Version: 1.0.0                                          ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """
    print(banner)
    print("    Starting server...")
    time.sleep(1)
    print("    Loading modules...")
    time.sleep(0.5)
    print("    Initializing database...")
    time.sleep(0.5)
    print("    Server ready!\n")

if __name__ == "__main__":
    # Clear the terminal
    os.system('cls' if os.name == 'nt' else 'clear')
    
    # Print the banner
    print_banner()
    
    # Run the server
    print("    Access the application at: http://localhost:8000\n")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)