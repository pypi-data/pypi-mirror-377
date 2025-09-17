"""Downloader implementation for ColliderML (manifest-driven)."""

from typing import Optional, List, Dict
from pathlib import Path
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import os
import hashlib
from dataclasses import dataclass
import h5py

from ..data.config import DEFAULT_URLS

@dataclass
class DownloadResult:
    """Result of a file download operation."""
    success: bool
    path: Path
    error: Optional[str] = None
    checksum: Optional[str] = None
    size: Optional[int] = None
    metadata: Optional[Dict] = None

class DataDownloader:
    """A client for downloading ColliderML files by relative path."""
    
    def __init__(
        self,
        base_urls: List[str] = None,
        chunk_size: int = 8192,
        validate_urls: bool = True,
        connect_timeout_seconds: int = 10,
    ):
        """Initialize the downloader.
        
        Args:
            base_urls: List of base URLs to try for data download.
                      Will try each URL in order until successful.
            chunk_size: Size of chunks to download in bytes.
        """
        self.base_urls = base_urls or DEFAULT_URLS
        self.chunk_size = chunk_size
        self.session = requests.Session()
        # requests timeout as (connect, read). read=None disables read timeout
        self._timeout = (connect_timeout_seconds, None)

        # Optionally validate base URLs early to provide fast failure in CI/tests
        if validate_urls:
            any_ok = False
            for base_url in self.base_urls:
                try:
                    resp = self.session.head(base_url, timeout=self._timeout)
                    if 200 <= resp.status_code < 500:  # consider reachable
                        any_ok = True
                        break
                except Exception:
                    continue
            if not any_ok:
                raise RuntimeError("Failed to connect to any data URLs")

    def _parse_remote_metadata(self, remote_path: str) -> Dict:
        """Parse campaign/dataset/version/data_type/object and filename from remote path.

        Returns minimal dict for logging and path derivation. Falls back to filename only.
        """
        try:
            # remote_path like: taster/ttbar/v2/reco/tracker_hits/....events0-99.h5
            parts = Path(remote_path).parts
            # Expect .../<campaign>/<dataset>/<version>/<data_type>/<object>/<filename>
            if len(parts) >= 6:
                return {
                    "campaign": parts[-6],
                    "dataset": parts[-5],
                    "version": parts[-4],
                    "data_type": parts[-3],
                    "object": parts[-2],
                    "filename": parts[-1],
                }
        except Exception:
            pass
        return {"filename": os.path.basename(remote_path)}

    def _derive_local_path(self, remote_path: str, local_dir: Path) -> Path:
        """Derive a hierarchical local path from a ColliderML filename.

        Expected filename format:
        campaign.dataset.version.data_type.object.eventsS-E.h5 ->
        local_dir/campaign/dataset/version/data_type/object/eventsS-E.h5

        Falls back to mirroring the remote subdirectories if parsing fails.
        """
        filename = os.path.basename(remote_path)
        name_parts = filename.split('.')
        # Minimal validation: expect ... .events... .h5
        if len(name_parts) >= 7 and name_parts[-1] == 'h5' and name_parts[-2].startswith('events'):
            campaign, dataset, version, data_type, object_name = name_parts[0:5]
            filename_tail = '.'.join(name_parts[5:])  # e.g. events0-99.h5
            return local_dir / campaign / dataset / version / data_type / object_name / filename_tail
        # Fallback: preserve remote directory structure under local_dir
        return local_dir / Path(os.path.dirname(remote_path)) / filename
    
    def _compute_checksum(self, file_path: Path) -> str:
        """Compute SHA-256 checksum of a file.
        
        Args:
            file_path: Path to the file.
            
        Returns:
            Hexadecimal string of the checksum.
        """
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(self.chunk_size), b''):
                sha256.update(chunk)
        return sha256.hexdigest()
    
    def _validate_hdf5(self, file_path: Path) -> Dict:
        """Extract lightweight metadata from an HDF5 file.

        Returns only file-level attributes as a dictionary to keep behavior
        simple and aligned with unit tests.
        """
        try:
            with h5py.File(file_path, 'r') as f:
                return dict(f.attrs)
        except (OSError, KeyError) as e:
            raise ValueError(f"Invalid HDF5 file: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error validating HDF5 file: {str(e)}")
    
    def _download_single_file(
        self,
        remote_path: str,
        local_path: Path,
        resume: bool = True,
    ) -> DownloadResult:
        """Download a single file.
        
        Args:
            remote_path: Path to the file on the server.
            local_path: Local path to save the file to.
            resume: Whether to attempt to resume a partial download.
            
        Returns:
            DownloadResult containing the download status and details.
        """
        # Create parent directories if they don't exist
        local_path.parent.mkdir(parents=True, exist_ok=True)
        
        last_error = None
        # Try each base URL
        for base_url in self.base_urls:
            url = f"{base_url.rstrip('/')}/{remote_path.lstrip('/')}"
            try:
                # Check existence via HEAD first
                head = self.session.head(url, timeout=self._timeout)
                if head.status_code != 200:
                    last_error = f"HTTP {head.status_code}"
                    continue

                # Simple GET request, like wget
                response = self.session.get(url, stream=True, timeout=self._timeout)
                response.raise_for_status()
                
                # Download with progress bar, show object type if parseable
                meta = self._parse_remote_metadata(remote_path)
                desc = meta.get("object") + ": " + meta.get("filename") if meta.get("object") else local_path.name
                with tqdm(
                    unit='B',
                    unit_scale=True,
                    desc=desc
                ) as pbar:
                    with open(local_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=self.chunk_size):
                            if chunk:
                                f.write(chunk)
                                pbar.update(len(chunk))
                
                # Get final size
                final_size = local_path.stat().st_size
                
                try:
                    # Validate HDF5 and get metadata
                    metadata = self._validate_hdf5(local_path)
                    
                    # Compute checksum after successful download
                    checksum = self._compute_checksum(local_path)
                    
                    return DownloadResult(
                        True,
                        local_path,
                        checksum=checksum,
                        size=final_size,
                        metadata=metadata
                    )
                except ValueError as e:
                    # If HDF5 validation fails, consider it a failed download
                    if local_path.exists():
                        local_path.unlink()
                    return DownloadResult(
                        False,
                        local_path,
                        error=str(e)
                    )
                
            except Exception as e:
                last_error = e
                continue  # Try next URL
                
        # All URLs failed
        return DownloadResult(
            False,
            local_path,
            error=f"Failed to access file: {str(last_error)}"
        )

    def download_files(
        self,
        remote_paths: List[str],
        local_dir: Path | str,
        max_workers: int = 4,
        resume: bool = True,
    ) -> Dict[str, DownloadResult]:
        """Download multiple files given their remote relative paths.

        Args:
            remote_paths: Relative paths under the base URL.
            local_dir: Destination directory.
            max_workers: Degree of parallelism.
            resume: Whether to attempt resuming partial downloads.
        """
        local_dir = Path(local_dir)
        local_dir.mkdir(parents=True, exist_ok=True)

        results: Dict[str, DownloadResult] = {}
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_path = {}
            for rp in remote_paths:
                lp = self._derive_local_path(rp, local_dir)
                future = executor.submit(self._download_single_file, rp, lp, resume)
                future_to_path[future] = rp
            for future in as_completed(future_to_path):
                rp = future_to_path[future]
                try:
                    results[rp] = future.result()
                except Exception as e:
                    results[rp] = DownloadResult(False, local_dir / os.path.basename(rp), error=str(e))
        return results
    
    # Legacy dataset-specific helpers have been removed; selection is manifest-driven.