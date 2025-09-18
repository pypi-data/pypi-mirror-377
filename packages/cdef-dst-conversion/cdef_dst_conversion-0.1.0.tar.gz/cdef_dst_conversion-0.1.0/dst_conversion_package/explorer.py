import functools
import json
import logging
import multiprocessing
import os
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import polars as pl  # type: ignore
import pyreadstat  # type: ignore


class SASFileExplorer:
    """
    Explores SAS7BDAT files using pyreadstat to understand structure before conversion
    Focus on analysis and exploration rather than conversion
    """

    def __init__(self, base_directory: str, parquet_output_directory: str):
        self.base_directory = Path(base_directory)
        self.parquet_output_directory = Path(parquet_output_directory)
        self.file_inventory: List[Dict[str, Any]] = []
        self.exploration_results: Dict[str, Any] = {}

        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler("sas_exploration.log"),
                logging.StreamHandler(sys.stdout),
            ],
        )
        self.logger = logging.getLogger(__name__)

        # Check pyreadstat availability
        try:
            import pyreadstat

            self.logger.info(
                "pyreadstat is available - excellent choice for SAS files!"
            )
        except ImportError:
            self.logger.error(
                "pyreadstat not found. Install with: pip install pyreadstat"
            )
            sys.exit(1)

    def discover_sas_files(
        self,
        extensions: List[str] = [".sas7bdat"],
    ) -> List[Dict[str, Any]]:
        """
        Discover all SAS files in directory structure
        """
        self.logger.info(f"Discovering SAS files in: {self.base_directory}")

        for ext in extensions:
            pattern = f"**/*{ext}"
            files = list(self.base_directory.glob(pattern))

            for file_path in files:
                try:
                    relative_path = file_path.relative_to(self.base_directory)
                    file_info = self._get_basic_file_info(file_path, relative_path)
                    self.file_inventory.append(file_info)

                except Exception as e:
                    self.logger.error(f"Error processing {file_path}: {str(e)}")

        # Sort by directory structure for better organization
        self.file_inventory.sort(
            key=lambda x: (x["directory_depth"], x["relative_path"])
        )

        self.logger.info(
            f"Discovered {len(self.file_inventory)} SAS files across {len(set(f['directory'] for f in self.file_inventory))} directories"
        )
        return self.file_inventory

    def _get_basic_file_info(
        self,
        file_path: Path,
        relative_path: Path,
    ) -> Dict[str, Any]:
        """
        Get basic file information without reading the content
        """
        stat = file_path.stat()

        return {
            "filename": file_path.name,
            "dataset_name": file_path.stem,
            "relative_path": str(relative_path),
            "full_path": str(file_path),
            "directory": str(relative_path.parent)
            if relative_path.parent != Path(".")
            else "root",
            "directory_depth": len(relative_path.parts) - 1,
            "size_mb": round(stat.st_size / (1024 * 1024), 2),
            "size_bytes": stat.st_size,
            "modified_date": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "explored": False,
            "exploration_error": None,
            "structure": None,
        }

    def explore_file_metadata(
        self,
        file_info: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """
        Explore a single SAS file using pyreadstat to get metadata without reading all data
        """
        file_path = Path(file_info["full_path"])
        self.logger.info(f"Exploring metadata: {file_info['relative_path']}")

        try:
            # Use pyreadstat to get metadata only (much faster than reading data)
            _, meta = pyreadstat.read_sas7bdat(str(file_path), metadataonly=True)

            metadata = {
                "row_count": meta.number_rows,
                "column_count": meta.number_columns,
                "column_names": meta.column_names,
                "column_labels": meta.column_labels if meta.column_labels else {},
                "original_variable_types": dict(
                    zip(meta.column_names, meta.original_variable_types)
                )
                if hasattr(meta, "original_variable_types")
                else {},
                "file_encoding": meta.file_encoding
                if hasattr(meta, "file_encoding")
                else "unknown",
                "creation_time": meta.creation_time.isoformat()
                if meta.creation_time
                else None,
                "modification_time": meta.modification_time.isoformat()
                if meta.modification_time
                else None,
                "sas_version": getattr(meta, "sas_version", "unknown"),
                "platform": getattr(meta, "platform", "unknown"),
            }

            file_info["structure"] = metadata
            file_info["explored"] = True

            return metadata

        except Exception as e:
            error_msg = f"Failed to explore {file_path}: {str(e)}"
            self.logger.error(error_msg)
            file_info["exploration_error"] = str(e)
            return None

    def explore_file_sample(
        self,
        file_info: Dict[str, Any],
        sample_size: int = 100,
    ) -> Optional[Dict[str, Any]]:
        """
        Explore a sample of data from a SAS file for deeper analysis
        """
        file_path = Path(file_info["full_path"])
        self.logger.info(
            f"Sampling data from: {file_info['relative_path']} ({sample_size} rows)"
        )

        try:
            # Read just a small sample for analysis
            df_sample, meta = pyreadstat.read_sas7bdat(
                str(file_path), row_limit=sample_size
            )

            # Analyze the sample
            sample_analysis = self._analyze_data_sample(df_sample, meta)

            # Add sample analysis to existing structure
            if file_info.get("structure"):
                file_info["structure"]["sample_analysis"] = sample_analysis
            else:
                file_info["structure"] = {"sample_analysis": sample_analysis}

            return sample_analysis

        except Exception as e:
            error_msg = f"Failed to sample {file_path}: {str(e)}"
            self.logger.error(error_msg)
            file_info["exploration_error"] = str(e)
            return None

    def _analyze_data_sample(
        self,
        df: pl.DataFrame,
        meta: pyreadstat.metadata_container,
    ) -> Dict[str, Any]:
        """
        Analyze a data sample for structure insights
        """
        analysis = {
            "sample_rows": len(df),
            "dtypes_summary": {col: str(df[col].dtype) for col in df.columns},
            "null_counts": {col: df[col].is_null().sum() for col in df.columns},
            "memory_usage_mb": round(df.estimated_size(unit="mb"), 4),
            "columns_detail": {},
        }

        # Detailed column analysis
        for col in df.columns:
            col_analysis = {
                "dtype": str(df[col].dtype),
                "non_null_count": df[col].drop_nulls().len(),
                "null_percentage": round((df[col].is_null().sum() / len(df)) * 100, 2),
                "unique_values": df[col].n_unique(),
                "unique_percentage": round((df[col].n_unique() / len(df)) * 100, 2),
            }

            # Add SAS-specific metadata if available
            if meta.column_labels and col in meta.column_labels:
                col_analysis["sas_label"] = meta.column_labels[col]

            # Type-specific analysis
            if df[col].dtype.is_numeric():
                non_null_data = df[col].drop_nulls()
                if len(non_null_data) > 0:
                    col_analysis.update(
                        {
                            "min_value": non_null_data.min(),
                            "max_value": non_null_data.max(),
                            "mean_value": round(non_null_data.mean(), 4),
                            "std_value": round(non_null_data.std(), 4),
                        }
                    )

            elif df[col].dtype == pl.Utf8 or df[col].dtype == pl.Object:
                non_null_data = df[col].drop_nulls().cast(pl.Utf8)
                if len(non_null_data) > 0:
                    col_analysis.update(
                        {
                            "avg_length": round(
                                non_null_data.str.len_bytes().mean(), 2
                            ),
                            "max_length": non_null_data.str.len_bytes().max(),
                            "min_length": non_null_data.str.len_bytes().min(),
                            "contains_special_chars": any(
                                not val.isascii() for val in non_null_data.to_list()
                            ),
                            "sample_values": non_null_data.head(5).to_list(),
                        }
                    )

            elif df[col].dtype.is_temporal():
                non_null_data = df[col].drop_nulls()
                if len(non_null_data) > 0:
                    min_date = non_null_data.min()
                    max_date = non_null_data.max()
                    col_analysis.update(
                        {
                            "min_date": min_date.isoformat()
                            if min_date is not None
                            else None,
                            "max_date": max_date.isoformat()
                            if max_date is not None
                            else None,
                            "date_range_days": (
                                (max_date - min_date).days
                                if min_date is not None and max_date is not None
                                else 0
                            ),
                        }
                    )

            analysis["columns_detail"][col] = col_analysis

        return analysis

    def explore_all_files_metadata(self) -> None:
        """
        Explore metadata for all discovered files (fast operation)
        """
        self.logger.info(f"Exploring metadata for {len(self.file_inventory)} files...")

        for i, file_info in enumerate(self.file_inventory, 1):
            self.logger.info(
                f"Processing metadata {i}/{len(self.file_inventory)}: {file_info['relative_path']}"
            )
            self.explore_file_metadata(file_info)

    def explore_sample_files(
        self,
        max_files: int = 50,
        sample_size: int = 100,
        size_threshold_mb: float = 10.0,
    ) -> None:
        """
        Explore data samples from a subset of files (slower operation)
        Prioritizes smaller files and different directories for representative sampling
        """
        # Filter and prioritize files for sampling
        candidates = [
            f
            for f in self.file_inventory
            if f.get("explored", False) and not f.get("exploration_error")
        ]

        # Sort by size (smaller files first) and ensure directory diversity
        candidates.sort(key=lambda x: (x["size_mb"], x["directory"]))

        # Select diverse sample
        sampled_files: List[Dict[str, Any]] = []
        directories_sampled = set()

        for file_info in candidates:
            if len(sampled_files) >= max_files:
                break

            # Prioritize files under size threshold and from new directories
            if (
                file_info["size_mb"] <= size_threshold_mb
                or file_info["directory"] not in directories_sampled
                or len(sampled_files) < 10
            ):  # Always sample at least 10 files
                sampled_files.append(file_info)
                directories_sampled.add(file_info["directory"])

        self.logger.info(
            f"Sampling data from {len(sampled_files)} files (max {sample_size} rows each)..."
        )

        for i, file_info in enumerate(sampled_files, 1):
            self.logger.info(
                f"Sampling {i}/{len(sampled_files)}: {file_info['relative_path']} ({file_info['size_mb']} MB)"
            )
            self.explore_file_sample(file_info, sample_size)

    def generate_exploration_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive exploration report
        """
        explored_files = [f for f in self.file_inventory if f.get("explored", False)]
        sampled_files = [
            f for f in explored_files if f.get("structure", {}).get("sample_analysis")
        ]
        failed_files = [f for f in self.file_inventory if f.get("exploration_error")]

        report = {
            "summary": {
                "total_files_discovered": len(self.file_inventory),
                "successfully_explored": len(explored_files),
                "data_sampled_files": len(sampled_files),
                "failed_files": len(failed_files),
                "total_size_mb": sum(f["size_mb"] for f in self.file_inventory),
                "total_estimated_rows": sum(
                    f.get("structure", {}).get("row_count", 0) for f in explored_files
                ),
                "exploration_timestamp": datetime.now().isoformat(),
            },
            "directory_analysis": self._analyze_directory_patterns(),
            "file_size_distribution": self._analyze_file_sizes(),
            "schema_patterns": self._analyze_schema_patterns(),
            "data_quality_insights": self._analyze_data_quality(),
            "conversion_readiness": self._assess_conversion_readiness(),
            "recommendations": self._generate_exploration_recommendations(),
            "file_inventory": self.file_inventory,
        }

        return report

    def _analyze_directory_patterns(self) -> Dict[str, Any]:
        """
        Analyze how files are organized in directories
        """
        directory_stats: defaultdict[str, Dict[str, Any]] = defaultdict(
            lambda: {
                "file_count": 0,
                "total_size_mb": 0,
                "total_rows": 0,
                "avg_file_size_mb": 0,
                "file_sizes": [],
            }
        )

        for file_info in self.file_inventory:
            dir_name = file_info["directory"]
            stats = directory_stats[dir_name]

            stats["file_count"] += 1
            stats["total_size_mb"] += file_info["size_mb"]
            stats["file_sizes"].append(file_info["size_mb"])

            if file_info.get("structure", {}).get("row_count"):
                stats["total_rows"] += file_info["structure"]["row_count"]

        # Calculate averages and convert to regular dict
        result = {}
        for dir_name, stats in directory_stats.items():
            stats["avg_file_size_mb"] = round(
                stats["total_size_mb"] / stats["file_count"],
                2,
            )
            stats["size_range"] = {
                "min": min(stats["file_sizes"]),
                "max": max(stats["file_sizes"]),
                "median": sorted(stats["file_sizes"])[len(stats["file_sizes"]) // 2],
            }
            del stats["file_sizes"]  # Remove raw data for cleaner report
            result[dir_name] = stats

        return result

    def _analyze_file_sizes(self) -> Dict[str, Any]:
        """
        Analyze file size distribution
        """
        sizes = [f["size_mb"] for f in self.file_inventory]

        if not sizes:
            return {"error": "No files to analyze"}

        sizes.sort()
        return {
            "total_files": len(sizes),
            "total_size_mb": sum(sizes),
            "size_statistics": {
                "min_mb": min(sizes),
                "max_mb": max(sizes),
                "mean_mb": round(sum(sizes) / len(sizes), 2),
                "median_mb": sizes[len(sizes) // 2],
                "percentile_90_mb": sizes[int(len(sizes) * 0.9)],
                "percentile_95_mb": sizes[int(len(sizes) * 0.95)],
            },
            "size_categories": {
                "small_files_under_10mb": len([s for s in sizes if s < 10]),
                "medium_files_10_100mb": len([s for s in sizes if 10 <= s < 100]),
                "large_files_100mb_plus": len([s for s in sizes if s >= 100]),
            },
        }

    def _analyze_schema_patterns(self) -> Dict[str, Any]:
        """
        Analyze common schema patterns across files
        """
        explored_files = [f for f in self.file_inventory if f.get("structure")]

        if not explored_files:
            return {"error": "No files explored for schema analysis"}

        # Column name frequency
        column_frequency: Counter[str] = Counter()
        column_types: defaultdict[str, Counter[str]] = defaultdict(Counter)
        encoding_patterns: Counter[str] = Counter()

        for file_info in explored_files:
            structure = file_info["structure"]

            # Count column names
            if "column_names" in structure:
                column_frequency.update(structure["column_names"])

                # Track encoding
                if "file_encoding" in structure:
                    encoding_patterns[structure["file_encoding"]] += 1

        # Analyze sampled files for data types
        sampled_files = [
            f for f in explored_files if f.get("structure", {}).get("sample_analysis")
        ]

        for file_info in sampled_files:
            sample_analysis = file_info["structure"]["sample_analysis"]
            if "dtypes_summary" in sample_analysis:
                for col, dtype in sample_analysis["dtypes_summary"].items():
                    column_types[col][dtype] += 1

        return {
            "most_common_columns": dict(column_frequency.most_common(20)),
            "encoding_distribution": dict(encoding_patterns),
            "column_type_consistency": {
                col: dict(types)
                for col, types in column_types.items()
                if len(types) > 1  # Only show columns with type inconsistencies
            },
            "schema_diversity": {
                "unique_column_names": len(column_frequency),
                "files_with_consistent_schemas": len(
                    [
                        f
                        for f in explored_files
                        if len(f.get("structure", {}).get("column_names", [])) > 0
                    ]
                ),
            },
        }

    def _analyze_data_quality(self) -> Dict[str, Any]:
        """
        Analyze data quality patterns from sampled files
        """
        sampled_files = [
            f
            for f in self.file_inventory
            if f.get("structure", {}).get("sample_analysis")
        ]

        if not sampled_files:
            return {"warning": "No files sampled for data quality analysis"}

        null_patterns = []
        encoding_issues = []

        for file_info in sampled_files:
            sample_analysis = file_info["structure"]["sample_analysis"]

            # Analyze null patterns
            if "null_counts" in sample_analysis:
                total_nulls = sum(sample_analysis["null_counts"].values())
                total_cells = sample_analysis["sample_rows"] * len(
                    sample_analysis["null_counts"]
                )
                null_percentage = (
                    (total_nulls / total_cells * 100) if total_cells > 0 else 0
                )

                null_patterns.append(
                    {
                        "file": file_info["relative_path"],
                        "null_percentage": round(null_percentage, 2),
                    }
                )

            # Check for encoding issues
            if "columns_detail" in sample_analysis:
                for col, col_info in sample_analysis["columns_detail"].items():
                    if col_info.get("contains_special_chars", False):
                        encoding_issues.append(
                            {
                                "file": file_info["relative_path"],
                                "column": col,
                                "issue": "special_characters",
                            }
                        )

        return {
            "null_data_summary": {
                "files_analyzed": len(sampled_files),
                "avg_null_percentage": round(
                    sum(p["null_percentage"] for p in null_patterns)
                    / len(null_patterns),
                    2,
                )
                if null_patterns
                else 0,
                "high_null_files": [
                    p for p in null_patterns if p["null_percentage"] > 20
                ],
            },
            "encoding_issues": encoding_issues[:10],  # Show first 10 issues
            "data_quality_score": self._calculate_quality_score(sampled_files),
        }

    def _calculate_quality_score(self, sampled_files: List[Dict]) -> Dict[str, Any]:
        """
        Calculate an overall data quality score
        """
        if not sampled_files:
            return {"score": 0, "reason": "No files sampled"}

        quality_factors = {
            "files_readable": len(
                [f for f in sampled_files if not f.get("exploration_error")]
            ),
            "consistent_encoding": len(
                set(
                    f.get("structure", {}).get("file_encoding", "unknown")
                    for f in sampled_files
                )
            ),
            "low_null_percentage": len(
                [f for f in sampled_files if self._get_file_null_percentage(f) < 10]
            ),
        }

        total_files = len(sampled_files)
        score = (
            (quality_factors["files_readable"] / total_files * 40)
            + (
                40 if quality_factors["consistent_encoding"] <= 2 else 20
            )  # Consistent encoding
            + (quality_factors["low_null_percentage"] / total_files * 20)
        )

        return {
            "score": round(score, 1),
            "max_score": 100,
            "factors": quality_factors,
            "interpretation": "Excellent"
            if score >= 80
            else "Good"
            if score >= 60
            else "Fair"
            if score >= 40
            else "Poor",
        }

    def _get_file_null_percentage(self, file_info: Dict) -> float:
        """
        Calculate null percentage for a file
        """
        sample_analysis = file_info.get("structure", {}).get("sample_analysis", {})
        if "null_counts" in sample_analysis:
            total_nulls = sum(sample_analysis["null_counts"].values())
            total_cells = sample_analysis["sample_rows"] * len(
                sample_analysis["null_counts"]
            )
            return (total_nulls / total_cells * 100) if total_cells > 0 else 0
        return 0

    def _assess_conversion_readiness(self) -> Dict[str, Any]:
        """
        Assess how ready the files are for Parquet conversion
        """
        explored_files = [f for f in self.file_inventory if f.get("explored", False)]

        readiness_factors = {
            "total_files": len(self.file_inventory),
            "successfully_explored": len(explored_files),
            "exploration_success_rate": round(
                len(explored_files) / len(self.file_inventory) * 100,
                1,
            )
            if self.file_inventory
            else 0,
            "large_files_count": len(
                [f for f in self.file_inventory if f["size_mb"] > 500]
            ),
            "encoding_consistency": len(
                set(
                    f.get("structure", {}).get("file_encoding", "unknown")
                    for f in explored_files
                )
            ),
            "estimated_conversion_time_hours": self._estimate_conversion_time(),
        }

        # Overall readiness assessment
        success_rate = readiness_factors["exploration_success_rate"]
        readiness_score = (
            "High" if success_rate >= 95 else "Medium" if success_rate >= 80 else "Low"
        )

        return {
            "readiness_score": readiness_score,
            "factors": readiness_factors,
            "blockers": self._identify_conversion_blockers(),
            "recommendations": self._get_conversion_recommendations(),
        }

    def _estimate_conversion_time(self) -> float:
        """
        Rough estimate of conversion time based on file sizes
        """
        total_size_gb = sum(f["size_mb"] for f in self.file_inventory) / 1024
        # Rough estimate: 1GB per 10-30 minutes depending on complexity
        return round(total_size_gb * 0.5, 1)  # Conservative estimate

    def _identify_conversion_blockers(self) -> List[str]:
        """
        Identify potential blockers for conversion
        """
        blockers = []

        failed_files = [f for f in self.file_inventory if f.get("exploration_error")]
        if len(failed_files) > len(self.file_inventory) * 0.1:  # More than 10% failed
            blockers.append(
                f"High failure rate: {len(failed_files)} files couldn't be explored"
            )

        large_files = [
            f for f in self.file_inventory if f["size_mb"] > 1000
        ]  # >1GB files
        if large_files:
            blockers.append(
                f"{len(large_files)} very large files (>1GB) may need special handling"
            )

        # Check encoding diversity
        explored_files = [f for f in self.file_inventory if f.get("explored", False)]
        encodings = set(
            f.get("structure", {}).get("file_encoding", "unknown")
            for f in explored_files
        )
        if len(encodings) > 3:
            blockers.append(f"Multiple file encodings detected: {list(encodings)}")

        return blockers

    def _get_conversion_recommendations(self) -> List[str]:
        """
        Get specific recommendations for conversion
        """
        recommendations = []

        large_files = [f for f in self.file_inventory if f["size_mb"] > 100]
        if large_files:
            recommendations.append(
                f"Use chunked processing for {len(large_files)} files >100MB"
            )

        directories = len(set(f["directory"] for f in self.file_inventory))
        if directories > 5:
            recommendations.append(
                "Consider partitioned Parquet structure to maintain directory organization"
            )

        recommendations.extend(
            [
                "Test conversion on a small subset first",
                "Monitor memory usage during conversion of large files",
                "Validate data integrity after conversion",
                "Consider compression options (snappy vs gzip) based on usage patterns",
            ]
        )

        return recommendations

    def _generate_exploration_recommendations(self) -> Dict[str, Any]:
        """
        Generate recommendations based on exploration findings
        """
        file_sizes = self._analyze_file_sizes()

        recommendations: Dict[str, Any] = {
            "immediate_actions": [],
            "conversion_strategy": {},
            "optimization_opportunities": [],
        }

        # Immediate actions
        failed_files = [f for f in self.file_inventory if f.get("exploration_error")]
        if failed_files:
            recommendations["immediate_actions"].append(
                f"Investigate {len(failed_files)} files that couldn't be explored"
            )

        # Conversion strategy
        if file_sizes.get("size_categories", {}).get("large_files_100mb_plus", 0) > 0:
            recommendations["conversion_strategy"]["large_files"] = (
                "Use chunked processing for files >100MB"
            )

        if len(set(f["directory"] for f in self.file_inventory)) > 1:
            recommendations["conversion_strategy"]["partitioning"] = (
                "Consider directory-based partitioning"
            )

        # Optimization opportunities
        directories = self._analyze_directory_patterns()
        small_files_dirs = [
            d for d, stats in directories.items() if stats["avg_file_size_mb"] < 10
        ]
        if small_files_dirs:
            recommendations["optimization_opportunities"].append(
                f"Consider combining small files in directories: {small_files_dirs[:3]}"
            )

        return recommendations

    def _convert_file_to_parquet_task(
        self,
        file_info: Dict[str, Any],
        parquet_output_directory: Path,
        logger: logging.Logger,
    ) -> None:
        full_sas_path = Path(file_info["full_path"])
        relative_path = Path(file_info["relative_path"])
        output_parquet_path = parquet_output_directory / relative_path.with_suffix(
            ".parquet"
        )

        logger.info(
            f"Converting: {file_info['relative_path']} -> {output_parquet_path.relative_to(parquet_output_directory)}"
        )

        try:
            output_parquet_path.parent.mkdir(parents=True, exist_ok=True)
            df, _ = pyreadstat.read_sas7bdat(str(full_sas_path), output_format="polars")
            df.write_parquet(output_parquet_path)
            logger.info(f"Successfully converted: {file_info['relative_path']}")
        except Exception as e:
            logger.error(
                f"Failed to convert {file_info['relative_path']} to Parquet: {str(e)}"
            )
            file_info["conversion_error"] = str(e)

    def convert_to_parquet(self) -> None:
        """
        Converts all discovered SAS files to Parquet format, mirroring their original
        relative directory structure in the specified output directory.
        """
        self.logger.info(
            f"Starting conversion of SAS files to Parquet in: {self.parquet_output_directory}"
        )
        self.parquet_output_directory.mkdir(parents=True, exist_ok=True)

        # Determine number of processes to use
        num_processes = multiprocessing.cpu_count()
        self.logger.info(f"Using {num_processes} processes for conversion.")

        # Create a partial function to pass fixed arguments to the worker function
        worker_func = functools.partial(
            self._convert_file_to_parquet_task,
            parquet_output_directory=self.parquet_output_directory,
            logger=self.logger,
        )

        with multiprocessing.Pool(processes=num_processes) as pool:
            # Map the worker function to each file_info in the inventory
            pool.map(worker_func, self.file_inventory)

        self.logger.info("SAS to Parquet conversion complete.")

    def save_exploration_report(self, filename: Optional[str] = None) -> str:
        """
        Save exploration report to JSON file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"sas_exploration_report_{timestamp}.json"

        report = self.generate_exploration_report()

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, default=str)

        self.logger.info(f"Exploration report saved to: {filename}")
        return filename

    def print_exploration_summary(self) -> None:
        """
        Print a nice summary of exploration results
        """
        report = self.generate_exploration_report()

        print("\n" + "=" * 60)
        print("SAS FILES EXPLORATION SUMMARY")
        print("=" * 60)

        summary = report["summary"]
        print(f"📁 Total files discovered: {summary['total_files_discovered']}")
        print(f"✅ Successfully explored: {summary['successfully_explored']}")
        print(f"🔍 Data sampled files: {summary['data_sampled_files']}")
        print(f"❌ Failed files: {summary['failed_files']}")
        print(f"💾 Total size: {summary['total_size_mb']:,.1f} MB")
        print(f"📊 Estimated total rows: {summary['total_estimated_rows']:,}")

        # Directory breakdown
        print("\n📂 DIRECTORY STRUCTURE:")
        dir_analysis = report["directory_analysis"]
        for directory, stats in sorted(dir_analysis.items()):
            print(
                f"   {directory}: {stats['file_count']} files, {stats['total_size_mb']:.1f} MB"
            )

        # File size distribution
        size_dist = report["file_size_distribution"]["size_categories"]
        print("\n📈 FILE SIZE DISTRIBUTION:")
        print(f"   Small (<10MB): {size_dist['small_files_under_10mb']} files")
        print(f"   Medium (10-100MB): {size_dist['medium_files_10_100mb']} files")
        print(f"   Large (>100MB): {size_dist['large_files_100mb_plus']} files")

        # Readiness assessment
        readiness = report["conversion_readiness"]
        print(f"\n🚀 CONVERSION READINESS: {readiness['readiness_score']}")
        print(f"   Success rate: {readiness['factors']['exploration_success_rate']}")
        print(
            f"   Estimated time: {readiness['factors']['estimated_conversion_time_hours']} hours"
        )

        # Show blockers if any
        if readiness["blockers"]:
            print("\n⚠️  POTENTIAL BLOCKERS:")
            for blocker in readiness["blockers"]:
                print(f"   • {blocker}")

        # Top recommendations
        recs = report["recommendations"]["immediate_actions"]
        if recs:
            print("\n💡 IMMEDIATE ACTIONS:")
            for rec in recs[:3]:
                print(f"   • {rec}")

        print("\n" + "=" * 60)


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
    main()
