import multiprocessing
import os
from pathlib import Path

from .explorer import SASFileExplorer


def main():
    """
    Example usage focusing on exploration
    """
    # Use the current directory as the base for exploration
    # For a real scenario, you might pass a specific path, e.g., "/path/to/your/sas/files"
    base_directory = os.getcwd()

    print(f"Starting SAS file exploration in: {base_directory}")

    # Define output directory for Parquet files
    parquet_output_directory = Path(base_directory) / "output_parquet"
    print(f"Parquet files will be saved to: {parquet_output_directory}")

    # 1. Initialize the explorer
    explorer = SASFileExplorer(base_directory, str(parquet_output_directory))

    # 2. Discover all SAS files
    explorer.discover_sas_files()

    # 3. Explore metadata for all discovered files (fast operation)
    explorer.explore_all_files_metadata()

    # 4. Explore data samples from a representative subset of files (slower operation)
    # This helps in understanding data quality, types, and patterns.
    # We can customize the number of files to sample, the sample size, and size threshold.
    explorer.explore_sample_files(max_files=50, sample_size=100, size_threshold_mb=20.0)

    # 5. Convert all discovered SAS files to Parquet
    explorer.convert_to_parquet()

    # 6. Print a summary report to the console
    explorer.print_exploration_summary()

    # 7. Save the detailed exploration report to a JSON file
    report_filename = explorer.save_exploration_report()
    print(f"\nDetailed report saved to: {report_filename}")
    print("Exploration complete.")


if __name__ == "__main__":
    # This is necessary for multiprocessing to work correctly on Windows
    # when the script is run as a package entry point.
    multiprocessing.freeze_support()
    main()
