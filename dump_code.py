import os

# List of every core script file in your strategy ecosystem
core_files = ['reason1.py', 'reason2.py', 'reason3.py', 'matrix.py', 'looker_feed.py']
output_bundle = 'complete_system_dump.txt'

try:
    with open(output_bundle, 'w', encoding='utf-8') as out:
        out.write("=========================================================================\n")
        out.write("          🪐 COMPLETE NEXUS ALGORITHMIC SYSTEM SOURCE DUMP 🪐            \n")
        out.write("=========================================================================\n\n")
        
        for file_name in core_files:
            out.write(f"// =====================================================================\n")
            out.write(f"// START OF FILE: {file_name}\n")
            out.write(f"// =====================================================================\n\n")
            
            if os.path.exists(file_name):
                with open(file_name, 'r', encoding='utf-8') as src:
                    out.write(src.read())
            else:
                out.write(f"# ⚠️ SYSTEM ALERT: {file_name} was not found in this directory path.\n")
                
            out.write(f"\n\n// =====================================================================\n")
            out.write(f"// END OF FILE: {file_name}\n")
            out.write(f"// =====================================================================\n\n\n")
            
    print("🟢 SUCCESS: Every piece of system code compiled into 'complete_system_dump.txt'!")
except Exception as e:
    print(f"❌ COMPILATION CRASHED: {str(e)}")
