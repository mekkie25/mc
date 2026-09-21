import os

# List of files we want to audit
files = ['reason1.py', 'reason2.py', 'reason3.py', 'matrix.py', 'looker_feed.py']

try:
    with open('nexus_system_audit.txt', 'w', encoding='utf-8') as out:
        for f in files:
            if os.path.exists(f):
                out.write(f"=== FILE: {f} ===\n")
                with open(f, 'r', encoding='utf-8') as src:
                    out.write(src.read())
                out.write("\n\n")
    print("🟢 SUCCESS: System files successfully compiled into nexus_system_audit.txt!")
except Exception as e:
    print(f"❌ FAILED: {str(e)}")

