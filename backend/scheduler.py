import time
import subprocess
import sys

# CONFIG
# For demo purposes, we treat "24 hours" as "30 seconds"
INTERVAL_SECONDS = 30 

def main():
    print(f"--- ANIMA AUTO-SCHEDULER ACTIVATED ---")
    print(f"Goal: Automate curation every {INTERVAL_SECONDS} seconds.")
    print(f"Press Ctrl+C to stop.\n")

    iteration = 1
    try:
        while True:
            print(f"[{time.strftime('%H:%M:%S')}] CYCLE #{iteration}: Scanning Global News...")
            
            # Run the curator script
            result = subprocess.run(
                [sys.executable, "curator.py"], 
                capture_output=True, 
                text=True
            )
            
            # Print curator output with indentation
            for line in result.stdout.splitlines():
                print(f"    | {line}")
            
            if result.stderr:
                print(f"    | ERROR: {result.stderr}")

            print(f"[{time.strftime('%H:%M:%S')}] SLEEPING: Next update in {INTERVAL_SECONDS}s...\n")
            
            time.sleep(INTERVAL_SECONDS)
            iteration += 1

    except KeyboardInterrupt:
        print("\n--- SCHEDULER STOPPED ---")

if __name__ == "__main__":
    main()
