
import asyncio
import json
import os
ECN_DIR="/vols/jasper_users/nipunc/FESA/silicon_agent/incremental_rtl/test_ECN"
def run_ecn_tests(output_file, rtl_analysis_module, ecn_dir=ECN_DIR):
	"""
	Processes all ECN (.txt) files in the given directory using the user's rtl_analysis module.
	Writes the parsed results to the output_file as JSON.
	"""
	async def process_ecn_file(file_path):
		try:
			ecn_content = rtl_analysis_module.parse_change_document(file_path)
			parsed_data = await rtl_analysis_module.analyze_specification_with_llm(ecn_content)
			if parsed_data:
				parsed_data['source_file'] = os.path.basename(file_path)
				return parsed_data
			else:
				return None
		except Exception:
			return None

	async def main():
		try:
			ecn_files = sorted([f for f in os.listdir(ecn_dir) if f.endswith('.txt')])
			if not ecn_files:
				print(f"No .txt files found in '{ecn_dir}'.")
				return
		except FileNotFoundError:
			print(f"Directory '{ecn_dir}' not found.")
			return

		tasks = []
		for ecn_file in ecn_files:
			file_path = os.path.join(ecn_dir, ecn_file)
			tasks.append(process_ecn_file(file_path))
		results = await asyncio.gather(*tasks)
		all_parsed_data = [res for res in results if res is not None]
		try:
			with open(output_file, 'w') as f:
				json.dump(all_parsed_data, f, indent=4)
			print(f"Successfully parsed {len(all_parsed_data)} ECNs and saved to '{output_file}'.")
		except IOError as e:
			print(f"Error writing to output file '{output_file}': {e}")

	asyncio.run(main())
