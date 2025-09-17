
import asyncio
import json
import os


RTL_DIR = "/vols/jasper_users/nipunc/FESA/silicon_agent/incremental_rtl/test_RTL"

def run_rtl_tests(output_file, rtl_analysis_module, rtl_dir=RTL_DIR):
	"""
	Runs RTL test cases from the fixed directory:
		/vols/jasper_users/nipunc/FESA/silicon_agent/incremental_rtl/test_RTL
	using the user's rtl_analysis module. The output JSON is written to the user-specified path.

	Args:
		output_file (str): Path to write the output JSON (in the user's own directory).
		rtl_analysis_module (module): User's rtl_analysis module implementing the required functions.
		rtl_dir (str, optional): Path to RTL test cases. Defaults to the fixed RTL_DIR.

	Note:
		The test cases directory is fixed and should not be moved or copied. Only the output file is user-configurable.
	"""
	async def main():
		try:
			rtl_files = rtl_analysis_module.load_rtl_repo(rtl_dir)
			if not rtl_files:
				print(f"No .v files found in '{rtl_dir}'. (Test cases must remain in this directory.)")
				return
			print(f"Found {len(rtl_files)} RTL files to process in '{rtl_dir}'.")
		except FileNotFoundError:
			print(f"Directory '{rtl_dir}' not found. (Test cases must remain in this directory.)")
			return
		except Exception as e:
			print(f"An error occurred while loading RTL files: {e}")
			return

		print("Starting RTL file analysis...")
		analysis_results = await rtl_analysis_module.analyze_rtl_files_with_llm(rtl_dir, rtl_files)

		try:
			with open(output_file, 'w') as f:
				json.dump(analysis_results, f, indent=4)
			print(f"Successfully analyzed {len(analysis_results.get('file_analysis', {}))} RTL files and saved to '{output_file}'.")
		except IOError as e:
			print(f"Error writing to output file '{output_file}': {e}")
		except Exception as e:
			print(f"An unexpected error occurred during file writing: {e}")

	asyncio.run(main())
