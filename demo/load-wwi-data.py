#!/usr/bin/env python3
"""Download Wide World Importers DW Parquet files for the Fabric Sales Agent demo.

Source: Microsoft Fabric tutorial sample data (public Azure Blob Storage).
Downloads Parquet files locally, with optional future support for direct
Lakehouse upload via the Fabric SDK.

Usage:
    python demo/load-wwi-data.py
    python demo/load-wwi-data.py --output-dir demo/sample-data
    python demo/load-wwi-data.py --workspace-id <guid> --lakehouse-id <guid>
"""

from __future__ import annotations

import argparse
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

BASE_URL = (
    "https://fabrictutorialdata.blob.core.windows.net/"
    "sampledata/WideWorldImportersDW/parquet/full"
)

# Table names as they appear in the blob storage (lowercase).
TABLES: list[str] = [
    "fact_sale",
    "dimension_customer",
    "dimension_stock_item",
    "dimension_city",
    "dimension_employee",
]


def _sizeof_fmt(num_bytes: int) -> str:
    """Human-readable file size."""
    for unit in ("B", "KB", "MB", "GB"):
        if abs(num_bytes) < 1024:
            return f"{num_bytes:,.1f} {unit}"
        num_bytes /= 1024  # type: ignore[assignment]
    return f"{num_bytes:,.1f} TB"


def download_table(table: str, output_dir: Path, *, retries: int = 3) -> Path:
    """Download a single Parquet table with retry logic and progress reporting.

    The WWI tutorial data is stored as partitioned Spark output: each table is a
    directory containing multiple ``part-XXXXX-<hash>.snappy.parquet`` files.
    We download part-00000 (the first partition) which is sufficient for demo purposes.
    """
    table_dir = output_dir / table
    table_dir.mkdir(parents=True, exist_ok=True)

    # Discover part files by listing the blob prefix
    list_url = (
        "https://fabrictutorialdata.blob.core.windows.net/sampledata"
        f"?restype=container&comp=list&prefix=WideWorldImportersDW/parquet/full/{table}/part"
    )

    try:
        with urllib.request.urlopen(list_url) as resp:  # noqa: S310
            body = resp.read().decode("utf-8")
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Cannot list blobs for {table}: {exc}") from exc

    import re  # noqa: PLC0415

    part_names = re.findall(r"<Name>([^<]*\.snappy\.parquet)</Name>", body)
    if not part_names:
        raise RuntimeError(f"No parquet parts found for {table}")

    # Download just the first part for demo (keeps download fast)
    part_name = part_names[0]
    part_url = f"https://fabrictutorialdata.blob.core.windows.net/sampledata/{part_name}"
    dest = table_dir / part_name.rsplit("/", 1)[-1]

    if dest.exists():
        print(f"  ✓ {table} — already exists ({_sizeof_fmt(dest.stat().st_size)})")
        return dest

    for attempt in range(1, retries + 1):
        try:
            print(f"  ↓ {table} (attempt {attempt}/{retries}) …", end="", flush=True)
            t0 = time.monotonic()
            urllib.request.urlretrieve(part_url, dest)  # noqa: S310
            elapsed = time.monotonic() - t0
            size = dest.stat().st_size
            print(f" {_sizeof_fmt(size)} in {elapsed:.1f}s")
            return dest
        except urllib.error.HTTPError as exc:
            print(f" HTTP {exc.code}")
            if attempt == retries:
                raise RuntimeError(f"Failed to download {table}: HTTP {exc.code}") from exc
        except urllib.error.URLError as exc:
            print(f" network error ({exc.reason})")
            if attempt == retries:
                raise RuntimeError(f"Failed to download {table}: {exc}") from exc

    raise RuntimeError(f"Failed to download {table} after {retries} attempts")


def download_all(output_dir: Path) -> list[Path]:
    """Download every WWI table, returning paths of successfully downloaded files."""
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"\nDownloading {len(TABLES)} tables to {output_dir.resolve()}\n")

    downloaded: list[Path] = []
    errors: list[str] = []

    for table in TABLES:
        try:
            path = download_table(table, output_dir)
            downloaded.append(path)
        except RuntimeError as exc:
            errors.append(f"  ✗ {table}: {exc}")
            print(f"  ✗ {table} — FAILED")

    print(f"\n{'─' * 50}")
    print(f"Downloaded: {len(downloaded)}/{len(TABLES)}")
    total_bytes = sum(p.stat().st_size for p in downloaded)
    print(f"Total size: {_sizeof_fmt(total_bytes)}")

    if errors:
        print("\nErrors:")
        for e in errors:
            print(e)

    return downloaded


def print_upload_instructions(output_dir: Path) -> None:
    """Print manual upload instructions for Fabric Lakehouse."""
    print(
        f"""
╔══════════════════════════════════════════════════════════════╗
║  Manual Upload to Microsoft Fabric Lakehouse                ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  1. Open your Fabric workspace in the browser                ║
║  2. Navigate to your Lakehouse → Files section               ║
║  3. Click "Upload" → "Upload files"                          ║
║  4. Select all .parquet files from:                          ║
║     {str(output_dir.resolve()):<56s} ║
║  5. Once uploaded, right-click each file →                   ║
║     "Load to Tables" to create Delta tables                  ║
║                                                              ║
║  Alternatively, use a Fabric Notebook:                       ║
║                                                              ║
║    import shutil                                             ║
║    tables = {TABLES!r:.46s}║
║    for t in tables:                                          ║
║        src = f"/lakehouse/default/Files/{{t}}.parquet"       ║
║        df = spark.read.parquet(src)                          ║
║        df.write.mode("overwrite")                            ║
║          .format("delta")                                    ║
║          .saveAsTable(t)                                     ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝"""
    )


def try_fabric_upload(
    workspace_id: str, lakehouse_id: str, parquet_files: list[Path]
) -> bool:
    """Attempt to upload files via the Fabric SDK. Returns True on success."""
    try:
        from sempy import fabric  # type: ignore[import-untyped]

        client = fabric.FabricRestClient()
        print(f"\nUploading to workspace={workspace_id}, lakehouse={lakehouse_id} …")

        for path in parquet_files:
            table_name = path.stem
            print(f"  ↑ {table_name} …", end="", flush=True)
            with open(path, "rb") as f:
                response = client.post(
                    f"/v1/workspaces/{workspace_id}/lakehouses/{lakehouse_id}"
                    f"/tables/{table_name}/load",
                    json={
                        "relativePath": f"Files/{path.name}",
                        "pathType": "File",
                        "mode": "Overwrite",
                    },
                )
                if response.status_code < 300:
                    print(" ✓")
                else:
                    print(f" HTTP {response.status_code}")
        return True

    except ImportError:
        print("\n⚠  sempy (Fabric SDK) not installed — skipping direct upload.")
        print("   Install with: pip install semantic-link")
        return False
    except Exception as exc:  # noqa: BLE001
        print(f"\n⚠  Fabric SDK upload failed: {exc}")
        return False


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Download Wide World Importers DW sample data for Fabric demo"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("demo/sample-data"),
        help="Local directory for downloaded Parquet files (default: demo/sample-data)",
    )
    parser.add_argument(
        "--workspace-id",
        default=None,
        help="Fabric workspace GUID (optional — enables direct Lakehouse upload)",
    )
    parser.add_argument(
        "--lakehouse-id",
        default=None,
        help="Fabric Lakehouse GUID (optional — enables direct Lakehouse upload)",
    )
    parser.add_argument(
        "--skip-download",
        action="store_true",
        help="Skip download, only attempt Fabric upload of existing files",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    print("=" * 55)
    print("  Wide World Importers DW — Sample Data Loader")
    print("=" * 55)

    if args.skip_download:
        parquet_files = list(args.output_dir.glob("*.parquet"))
        if not parquet_files:
            print(f"No .parquet files found in {args.output_dir}")
            return 1
        print(f"Found {len(parquet_files)} existing Parquet files")
    else:
        parquet_files = download_all(args.output_dir)
        if not parquet_files:
            print("No files were downloaded. Check your network connection.")
            return 1

    # Attempt Fabric SDK upload if IDs provided
    if args.workspace_id and args.lakehouse_id:
        uploaded = try_fabric_upload(
            args.workspace_id, args.lakehouse_id, parquet_files
        )
        if uploaded:
            print("\n✓ Data uploaded to Fabric Lakehouse successfully!")
            return 0

    # Fall back to manual instructions
    print_upload_instructions(args.output_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
