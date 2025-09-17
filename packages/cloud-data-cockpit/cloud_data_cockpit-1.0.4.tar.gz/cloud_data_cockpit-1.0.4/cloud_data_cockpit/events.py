import os
from IPython.display import clear_output

from .aws_utils import make_cloud_object
from .format_handlers import get_format_handler


def connect_events(dc):
    """Wire up callbacks on the DataCockpit instance."""
    dc.bench_toggle.observe(dc._on_bench_toggle, names="value")
    dc.run_bench_btn.on_click(dc._run_benchmark)
    dc.process_btn.on_click(dc._process_data)
    dc.tabs.observe(dc._on_tab_change, names="selected_index")


def _on_bench_toggle(self, change):
    """Show or hide benchmarking controls."""
    self.bench_box.layout.display = "flex" if change["new"] == "Enabled" else "none"


def _run_benchmark(self, _):
    """Run the user's benchmarking function across batch sizes."""
    with self.bench_output:
        clear_output()
        if not self.benchmark_fn:
            print("Error: No benchmarking function provided.")
            return

        uri, widget = self._get_active_source()
        if isinstance(uri, (list, tuple)):
            uri = uri[0] if uri else None
        if not uri:
            print("No dataset selected.")
            return

        if self.min_bs.value > self.max_bs.value:
            print("Error: Min batch size is greater than max.")
            return

        results = {}
        print("Benchmarking…")
        for bs in range(self.min_bs.value, self.max_bs.value + 1, self.step_bs.value):
            try:
                # Process the dataset internally to generate chunks
                fmt_cls, partition_fn = get_format_handler(uri)
                if fmt_cls is None:
                    print(f"Unsupported format for benchmarking: {uri}")
                    continue

                cloud_obj = make_cloud_object(fmt_cls, uri)
                if cloud_obj is None:
                    print(f"Failed to create cloud object for: {uri}")
                    continue

                # Preprocess the data if needed
                ext = os.path.splitext(uri)[1].lower()
                try:
                    if ext == ".fasta":
                        size_int = int(cloud_obj.size)
                        chunk_size = max(1, size_int // 4)
                        cloud_obj.preprocess(
                            parallel_config={"verbose": 0},  # Quiet for benchmarking
                            chunk_size=chunk_size
                        )
                    elif ext == ".ibd":
                        cloud_obj.preprocess(force=True)
                    else:
                        size_int = int(cloud_obj.size)
                        chunk_size = max(1, size_int // 4)
                        cloud_obj.preprocess(debug=False, chunk_size=chunk_size)
                except Exception as e:
                    print(f"Preprocess warning for batch size {bs}: {e}")

                # Generate partitions/chunks based on batch size
                try:
                    if uri.endswith(".gz"):
                        # FASTQ files use num_batches
                        chunks = cloud_obj.partition(partition_fn, num_batches=bs)
                    elif uri.endswith(".ibd"):
                        # IBD files use chunk_size in bytes (batch_size * 1MB)
                        chunk_size_bytes = bs * 1024**2
                        chunks = cloud_obj.partition(partition_fn, chunk_size=chunk_size_bytes)
                    else:
                        # Other formats use num_chunks
                        chunks = cloud_obj.partition(partition_fn, num_chunks=bs)
                    
                    # Now call user's benchmark function with the processed chunks
                    elapsed = self.benchmark_fn(chunks)
                    results[bs] = elapsed
                    print(f"{bs} → {elapsed:.3f}s")
                    
                except Exception as e:
                    print(f"{bs} partition error: {e}")
                    
            except Exception as e:
                print(f"{bs} error: {e}")

        if results:
            best = min(results, key=results.get)
            self.ideal_bs_label.value = f"<strong>Ideal Batch Size:</strong> {best}"
            if hasattr(widget, "update_batch_size"):
                widget.update_batch_size(best)
        else:
            print("No successful benchmarks.")


def _process_data(self, _):
    """Partition the selected dataset into batches or chunks."""
    with self.process_output:
        clear_output()
        uri, widget = self._get_active_source()
        if isinstance(uri, (list, tuple)):
            uri = uri[0] if uri else None
        if not uri:
            print("No dataset selected.")
            return

        if self.bench_toggle.value == "Enabled":
            raw_bs = self._extract_ideal_bs()
            if raw_bs is None:
                print("Enable and run benchmarking first.")
                return
        else:
            raw_bs = widget.get_batch_size()

        try:
            batch_size = int(raw_bs)
        except (TypeError, ValueError):
            print(
                f"Invalid batch size {raw_bs!r} (type {type(raw_bs).__name__}); must be integer."
            )
            return

        print(f"Processing with batch size {batch_size}…")
        # Ensure uri is a str in case a list slipped through
        if isinstance(uri, (list, tuple)):
            uri = uri[0] if uri else ''
        fmt_cls, partition_fn = get_format_handler(uri)
        if fmt_cls is None:
            print(f"Unsupported format: {uri}")
            return

        cloud_obj = make_cloud_object(fmt_cls, uri)
        if cloud_obj is None:
            return

        ext = os.path.splitext(uri)[1].lower()
        # Preprocess: skip or adjust for different formats
        try:
            if ext == ".fasta":
                # FASTA format requires parallel_config and chunk_size
                try:
                    size_int = int(cloud_obj.size)
                    chunk_size = max(1, size_int // 4)
                    # Provide required parameters for FASTA preprocessing
                    cloud_obj.preprocess(
                        parallel_config={"verbose": 10},
                        chunk_size=chunk_size
                    )
                except Exception as e:
                    print(f"Preprocess error for FASTA: {e}")
            elif ext == ".ibd":
                # IBD format requires force=True
                cloud_obj.preprocess(force=True)
            else:
                size_int = int(cloud_obj.size)
                chunk_size = max(1, size_int // 4)
                cloud_obj.preprocess(debug=True, chunk_size=chunk_size)
        except Exception as e:
            print(f"Preprocess warning (skipped): {e}")

        try:
            if uri.endswith(".gz"):
                # FASTQ files use num_batches
                slices = cloud_obj.partition(partition_fn, num_batches=batch_size)
            elif uri.endswith(".ibd"):
                # IBD files use chunk_size in bytes (batch_size * 1MB)
                chunk_size_bytes = batch_size * 1024**2
                slices = cloud_obj.partition(partition_fn, chunk_size=chunk_size_bytes)
            else:
                # Other formats use num_chunks
                slices = cloud_obj.partition(partition_fn, num_chunks=batch_size)
            self._data_slices = slices
            print("Processing complete.")
        except Exception as e:
            print(f"Error during processing: {e}")

def _on_tab_change(self, change):
    """Update widget batch size when switching tabs."""
    uri, widget = self._get_active_source()
    if isinstance(uri, (list, tuple)):
        uri = uri[0] if uri else None
    if uri and hasattr(widget, "update_batch_size"):
        bs = self._extract_ideal_bs()
        if bs is not None:
            widget.update_batch_size(bs)
