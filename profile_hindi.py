# profile_hindi.py
import cProfile
import pstats
from src.adobe_parser import DocumentParser

# The name of your slow Hindi PDF
HINDI_PDF = "input/bhsr1ps.pdf#_~_text=हि_ंदी भाषा की पाठ ्,26.pdf" 

def run_profiling():
    print(f"Profiling {HINDI_PDF}...")
    parser = DocumentParser(HINDI_PDF)
    parser.extract_outline()
    print("Profiling finished.")

# Create a profiler object
profiler = cProfile.Profile()

# Run the function under the profiler
profiler.enable()
run_profiling()
profiler.disable()

# Print the stats, sorted by cumulative time spent in each function
stats = pstats.Stats(profiler).sort_stats('cumulative')
stats.print_stats(20) # Print the top 20 slowest functions