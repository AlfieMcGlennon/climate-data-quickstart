"""Chunked download engine with resume, retry, and optional merge.

Splits large date-range requests into smaller per-month or per-year
chunks. Each chunk is tracked in a ``.manifest.json`` file in the output
directory, so re-running the same request skips completed chunks and
retries failed ones.

Usage from a download script::

    from common.chunked import plan_chunks, run_chunked_download

    chunks = plan_chunks(years, months, "month", "era5_{year}_{month}.nc")
    result = run_chunked_download(
        download_one=_my_download_fn,
        chunks=chunks,
        output_dir="./data/era5",
        dataset="era5-single-levels",
        chunk_by="month",
    )
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable


@dataclass
class ChunkSpec:
    """Definition of a single chunk to download."""

    chunk_id: str
    years: list[str]
    months: list[str]
    filename: str


@dataclass
class ChunkStatus:
    """Persisted state for a single chunk."""

    chunk_id: str
    filename: str
    state: str = "pending"
    attempts: int = 0
    size_bytes: int | None = None
    error: str | None = None
    completed_at: str | None = None


@dataclass
class Manifest:
    """Full download manifest, serialised to .manifest.json."""

    dataset: str
    chunk_by: str
    total_chunks: int
    merge_output: bool
    merged_filename: str | None = None
    chunks: dict[str, ChunkStatus] = field(default_factory=dict)


ProgressCallback = Callable[[ChunkSpec, ChunkStatus, int, int], None]


def plan_chunks(
    years: list[str],
    months: list[str],
    chunk_by: str,
    filename_template: str,
) -> list[ChunkSpec]:
    """Split a year/month range into chunks.

    Args:
        years: Full list of years requested (as strings).
        months: Full list of months requested (as zero-padded strings).
        chunk_by: ``"month"`` or ``"year"``.
        filename_template: Format string with ``{year}`` and optionally
            ``{month}`` placeholders, e.g. ``"era5_{year}_{month}.nc"``.

    Returns:
        Ordered list of ChunkSpec, one per chunk.
    """
    chunks: list[ChunkSpec] = []

    if chunk_by == "month":
        for y in years:
            for m in months:
                chunk_id = f"{y}-{m}"
                filename = filename_template.format(year=y, month=m)
                chunks.append(ChunkSpec(
                    chunk_id=chunk_id,
                    years=[y],
                    months=[m],
                    filename=filename,
                ))
    elif chunk_by == "year":
        for y in years:
            chunk_id = str(y)
            filename = filename_template.format(year=y, month="all")
            chunks.append(ChunkSpec(
                chunk_id=chunk_id,
                years=[y],
                months=list(months),
                filename=filename,
            ))
    else:
        raise ValueError(f"chunk_by must be 'month' or 'year', got '{chunk_by}'")

    return chunks


def _manifest_path(output_dir: Path) -> Path:
    return output_dir / ".manifest.json"


def load_manifest(output_dir: Path) -> Manifest | None:
    """Load an existing manifest from the output directory.

    Returns:
        The Manifest, or None if no manifest file exists.
    """
    path = _manifest_path(output_dir)
    if not path.exists():
        return None

    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    chunk_statuses = {}
    for cid, cdata in data.get("chunks", {}).items():
        chunk_statuses[cid] = ChunkStatus(**cdata)

    return Manifest(
        dataset=data["dataset"],
        chunk_by=data["chunk_by"],
        total_chunks=data["total_chunks"],
        merge_output=data["merge_output"],
        merged_filename=data.get("merged_filename"),
        chunks=chunk_statuses,
    )


def save_manifest(output_dir: Path, manifest: Manifest) -> Path:
    """Write the manifest atomically to output_dir/.manifest.json.

    Returns:
        Path to the manifest file.
    """
    path = _manifest_path(output_dir)
    tmp_path = path.with_suffix(".json.tmp")

    data: dict[str, Any] = {
        "dataset": manifest.dataset,
        "chunk_by": manifest.chunk_by,
        "total_chunks": manifest.total_chunks,
        "merge_output": manifest.merge_output,
        "merged_filename": manifest.merged_filename,
        "chunks": {cid: asdict(cs) for cid, cs in manifest.chunks.items()},
    }

    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    os.replace(str(tmp_path), str(path))
    return path


def _is_chunk_done(output_dir: Path, status: ChunkStatus) -> bool:
    """Check if a chunk is marked done AND the file still exists on disk."""
    if status.state != "done":
        return False
    chunk_file = output_dir / status.filename
    return chunk_file.exists() and chunk_file.stat().st_size > 0


def run_chunked_download(
    download_one: Callable[[ChunkSpec], Path],
    chunks: list[ChunkSpec],
    output_dir: str | Path,
    dataset: str,
    chunk_by: str,
    max_retries: int = 3,
    retry_backoff: float = 30.0,
    merge_output: bool = True,
    merged_filename: str | None = None,
    data_format: str = "netcdf",
    progress_callback: ProgressCallback | None = None,
) -> Path:
    """Execute a chunked download with resume, retry, and optional merge.

    Args:
        download_one: Callable that takes a ChunkSpec and returns the
            Path of the downloaded file.
        chunks: The chunk plan from plan_chunks().
        output_dir: Where chunk files and the manifest live.
        dataset: Dataset name for the manifest.
        chunk_by: ``"month"`` or ``"year"``.
        max_retries: Maximum attempts per chunk before giving up.
        retry_backoff: Base seconds between retries (multiplied by
            attempt number).
        merge_output: Whether to concatenate chunks into one file.
        merged_filename: Name for the merged file. Auto-generated if None.
        data_format: ``"netcdf"`` or ``"grib"`` - controls merge strategy.
        progress_callback: Optional callback for progress reporting.

    Returns:
        Path to the merged file if merge_output is True, otherwise
        the output directory Path.

    Raises:
        RuntimeError: If any chunk still fails after max_retries.
    """
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    manifest = load_manifest(out_dir)
    if manifest is None:
        manifest = Manifest(
            dataset=dataset,
            chunk_by=chunk_by,
            total_chunks=len(chunks),
            merge_output=merge_output,
            merged_filename=merged_filename,
        )

    for chunk in chunks:
        if chunk.chunk_id not in manifest.chunks:
            manifest.chunks[chunk.chunk_id] = ChunkStatus(
                chunk_id=chunk.chunk_id,
                filename=chunk.filename,
            )

    save_manifest(out_dir, manifest)

    total = len(chunks)
    completed = sum(
        1 for c in chunks if _is_chunk_done(out_dir, manifest.chunks[c.chunk_id])
    )

    for chunk in chunks:
        status = manifest.chunks[chunk.chunk_id]

        if _is_chunk_done(out_dir, status):
            if progress_callback:
                progress_callback(chunk, status, completed, total)
            continue

        status.state = "pending"
        last_error = None

        for attempt in range(1, max_retries + 1):
            status.attempts = attempt
            status.state = "downloading"
            save_manifest(out_dir, manifest)

            try:
                result_path = download_one(chunk)

                status.state = "done"
                status.filename = result_path.name
                status.size_bytes = result_path.stat().st_size
                status.error = None
                status.completed_at = datetime.now(timezone.utc).isoformat()
                completed += 1
                save_manifest(out_dir, manifest)

                print(
                    f"  [{completed}/{total}] {chunk.chunk_id}: "
                    f"{status.size_bytes / 1e6:.1f} MB"
                )

                if progress_callback:
                    progress_callback(chunk, status, completed, total)
                break

            except Exception as exc:
                last_error = str(exc)
                status.state = "failed"
                status.error = last_error
                save_manifest(out_dir, manifest)

                if attempt < max_retries:
                    wait = retry_backoff * attempt
                    print(
                        f"  [{chunk.chunk_id}] attempt {attempt}/{max_retries} "
                        f"failed: {last_error}. Retrying in {wait:.0f}s..."
                    )
                    time.sleep(wait)
                else:
                    print(
                        f"  [{chunk.chunk_id}] FAILED after {max_retries} "
                        f"attempts: {last_error}"
                    )
                    if progress_callback:
                        progress_callback(chunk, status, completed, total)

    failed = [
        cid for cid, s in manifest.chunks.items()
        if s.state == "failed"
    ]
    if failed:
        raise RuntimeError(
            f"{len(failed)} chunk(s) failed after {max_retries} retries: "
            f"{', '.join(failed)}. Re-run to retry. "
            f"Completed chunks are preserved."
        )

    if merge_output:
        chunk_paths = [out_dir / manifest.chunks[c.chunk_id].filename for c in chunks]
        if merged_filename is None:
            merged_filename = f"{dataset.replace('-', '_')}_merged.nc"
        merged_path = out_dir / merged_filename
        merge_chunks(chunk_paths, merged_path, data_format=data_format)

        manifest.merged_filename = merged_filename
        save_manifest(out_dir, manifest)

        print(f"  Merged {len(chunk_paths)} chunks -> {merged_path}")
        return merged_path

    return out_dir


def merge_chunks(
    chunk_paths: list[Path],
    output_path: Path,
    data_format: str = "netcdf",
) -> Path:
    """Concatenate chunk files along the time dimension.

    Args:
        chunk_paths: Ordered list of chunk file paths.
        output_path: Where to write the merged file.
        data_format: ``"netcdf"`` or ``"grib"``. GRIB inputs are read
            via cfgrib and the merged output is written as NetCDF.

    Returns:
        Path to the merged file.
    """
    import xarray as xr

    open_kwargs: dict[str, Any] = {}
    if data_format in ("grib", "grib2"):
        open_kwargs["engine"] = "cfgrib"

    ds = xr.open_mfdataset(
        [str(p) for p in chunk_paths],
        combine="by_coords",
        **open_kwargs,
    )
    ds.to_netcdf(str(output_path))
    ds.close()

    return output_path
