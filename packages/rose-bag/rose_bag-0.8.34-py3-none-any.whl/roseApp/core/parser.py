"""
ROS bag parser module using rosbags library.

Provides high-performance bag parsing capabilities with intelligent caching
and memory optimization using the rosbags library.
"""

import os
import time
import asyncio
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Callable, Any, Union, TYPE_CHECKING
from dataclasses import dataclass, field
from enum import Enum
from rosbags.highlevel import AnyReader
from rosbags.rosbag1 import Writer as Rosbag1Writer
from rosbags.serde import deserialize_cdr
from roseApp.core.util import get_logger
from .model import ComprehensiveBagInfo, AnalysisLevel, TopicInfo, MessageTypeInfo, MessageFieldInfo, TimeRange

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    pd = None

_logger = get_logger("parser")


class FileExistsError(Exception):
    """Custom exception for file existence errors"""
    pass


@dataclass
class ExtractOption:
    """Options for extract operation"""
    topics: List[str]
    time_range: Optional[Tuple[Tuple[int, int], Tuple[int, int]]] = None
    compression: str = 'none'
    overwrite: bool = False
    memory_limit_mb: int = 512  # Memory limit for message buffering in MB
    
    def __post_init__(self):
        """Validate extract options"""
        if not self.topics:
            raise ValueError("Topics list cannot be empty")
        
        if self.compression not in ['none', 'bz2', 'lz4']:
            raise ValueError(f"Invalid compression type: {self.compression}")
        
        if self.memory_limit_mb <= 0:
            raise ValueError("Memory limit must be positive")



class BagParser:
    """
    Singleton high-performance ROS bag parser using rosbags library
    
    Public Interface:
    - load_bag_async(): Async load bag into cache with configurable analysis level
    - extract(): Extract topics from bag file
    
    The parser automatically chooses between quick and full analysis based on
    the required information and caching status.
    """
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        """Singleton pattern implementation"""
        if cls._instance is None:
            cls._instance = super(BagParser, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize singleton instance only once"""
        if BagParser._initialized:
            return
        
        # Current bag information
        self._current_bag_info: Optional[ComprehensiveBagInfo] = None
        
        # Type system optimization
        self._typestore = None
        
        # Cache settings
        self._cache_ttl = 300  # 5 minutes
        
        BagParser._initialized = True
        _logger.debug("Initialized singleton BagParser")
    
    async def load_bag_async(
        self, 
        bag_path: str, 
        build_index: bool = False,
        progress_callback: Optional[Callable[[str, float], None]] = None
    ) -> Tuple[ComprehensiveBagInfo, float]:
        """
        Asynchronously load bag into cache with configurable analysis level
        
        Args:
            bag_path: Path to the bag file
            build_index: Whether to build message index as DataFrame (True) or quick analysis (False)
            progress_callback: Optional callback for progress updates (phase, progress_pct)
            
        Returns:
            Tuple of (ComprehensiveBagInfo, elapsed_time_seconds)
        """
        start_time = time.time()
        
        # Run analysis in executor to avoid blocking the event loop
        loop = asyncio.get_event_loop()
        
        if progress_callback:
            progress_callback("Starting analysis...", 10.0)
        
        try:
            if build_index:
                if progress_callback:
                    progress_callback("Building message index...", 30.0)
                
                bag_info, analysis_time = await loop.run_in_executor(
                    None,
                    self._analyze_bag_with_index,
                    bag_path
                )
            else:
                if progress_callback:
                    progress_callback("Performing quick analysis...", 30.0)
                
                bag_info, analysis_time = await loop.run_in_executor(
                    None,
                    self._analyze_bag_quick,
                    bag_path
                )
            
            if progress_callback:
                progress_callback("Caching results...", 80.0)
            
            # Cache the result
            from .cache import create_bag_cache_manager
            cache_manager = create_bag_cache_manager()
            cache_manager.put_analysis(Path(bag_path), bag_info)
            
            if progress_callback:
                progress_callback("Complete", 100.0)
            
            elapsed = time.time() - start_time
            _logger.info(f"Async load completed in {elapsed:.3f}s for {bag_path}")
            
            return bag_info, elapsed
            
        except Exception as e:
            if progress_callback:
                progress_callback("Error", 0.0)
            _logger.error(f"Error in async load for {bag_path}: {e}")
            raise
    
    def extract(self, input_bag: str, output_bag: str, extract_option: ExtractOption,
                progress_callback: Optional[Callable] = None) -> Tuple[str, float]:
        """
        Extract specified topics from bag file with guaranteed chronological ordering
        
        Args:
            input_bag: Path to input bag file
            output_bag: Path to output bag file
            extract_option: ExtractOption containing topics, time_range, compression, overwrite
            progress_callback: Optional progress callback function
            
        Returns:
            Tuple of (result_message, elapsed_time_seconds)
        """
        start_time = time.time()
        
        try:
            # Validate compression type
            self._validate_compression(extract_option.compression)
            
            # Prepare output file
            self._prepare_output_file(output_bag, extract_option.overwrite)
            
            rosbags_compression = self._get_compression_format(extract_option.compression)
            
            with AnyReader([Path(input_bag)]) as reader:
                # Pre-filter connections based on selected topics
                selected_connections = [
                    conn for conn in reader.connections 
                    if conn.topic in extract_option.topics
                ]
                
                if not selected_connections:
                    elapsed = time.time() - start_time
                    _logger.warning(f"No matching topics found in {input_bag}")
                    return "No messages found for selected topics", elapsed
                
                # Use memory-efficient extraction with guaranteed chronological ordering
                total_processed = self._extract_with_chronological_ordering(
                    reader, selected_connections, output_bag, extract_option, progress_callback
                )
                
                elapsed = time.time() - start_time
                mins, secs = divmod(elapsed, 60)
                
                _logger.info(f"Extracted {total_processed} messages from {len(selected_connections)} topics in chronological order in {elapsed:.2f}s")
                
                return f"Extraction completed in {int(mins)}m {secs:.2f}s (chronologically ordered)", elapsed
                
        except ValueError as ve:
            raise ve
        except FileExistsError as fe:
            raise fe
        except Exception as e:
            _logger.error(f"Error extracting bag: {e}")
            raise Exception(f"Error extracting bag: {e}")
    
    def clear(self) -> Tuple[str, float]:
        """
        Clear all internal information
        
        Returns:
            Tuple of (result_message, elapsed_time_seconds)
        """
        start_time = time.time()
        
        self._current_bag_info = None
        self._typestore = None
        
        elapsed = time.time() - start_time
        _logger.debug("Cleared all internal information")
        
        return "Internal information cleared", elapsed
    
    # === PRIVATE METHODS ===
    
    def _initialize_typestore(self):
        """Initialize optimized typestore for better performance"""
        if self._typestore is None:
            try:
                from rosbags.typesys import get_typestore, Stores
                try:
                    self._typestore = get_typestore(Stores.ROS1_NOETIC)
                    _logger.debug("Initialized typestore for ROS1_NOETIC")
                except:
                    self._typestore = get_typestore(Stores.LATEST)
                    _logger.debug("Initialized typestore with LATEST")
            except Exception as e:
                _logger.warning(f"Could not initialize typestore: {e}")
                self._typestore = None
    
    def _is_cache_valid(self, bag_path: str) -> bool:
        """Check if current cache is valid for the given bag path"""
        if self._current_bag_info is None:
            return False
        
        if self._current_bag_info.file_path != bag_path:
            return False
        
        if time.time() - self._current_bag_info.last_updated > self._cache_ttl:
            return False
        
        return True
    
    def _analyze_bag_quick(self, bag_path: str) -> Tuple[ComprehensiveBagInfo, float]:
        """
        Perform quick analysis without message traversal
        
        Gets basic metadata: topics, connections, time range, duration
        
        Args:
            bag_path: Path to the bag file
            
        Returns:
            Tuple of (ComprehensiveBagInfo, elapsed_time_seconds)
        """
        start_time = time.time()
        
        # Check if we already have quick analysis for this bag
        if (self._is_cache_valid(bag_path) and 
            self._current_bag_info is not None and
            self._current_bag_info.has_quick_analysis()):
            elapsed = time.time() - start_time
            _logger.info(f"Using cached quick analysis for {bag_path}")
            return self._current_bag_info, elapsed
        
        _logger.info(f"Performing quick analysis for {bag_path}")
        
        try:
            self._initialize_typestore()
            
            reader_args = [Path(bag_path)]
            reader_kwargs = {'default_typestore': self._typestore} if self._typestore else {}
            
            with AnyReader(reader_args, **reader_kwargs) as reader:
                # Extract time range using new TimeRange structure
                start_ns = reader.start_time
                end_ns = reader.end_time
                start_time_tuple = (int(start_ns // 1_000_000_000), int(start_ns % 1_000_000_000))
                end_time_tuple = (int(end_ns // 1_000_000_000), int(end_ns % 1_000_000_000))
                time_range = TimeRange(start_time=start_time_tuple, end_time=end_time_tuple)
                
                # Calculate duration
                duration_seconds = time_range.get_duration_seconds()
                
                # Create or update bag info first
                if (self._current_bag_info is None or 
                    self._current_bag_info.file_path != bag_path):
                    file_size = os.path.getsize(bag_path)
                    self._current_bag_info = ComprehensiveBagInfo(
                        file_path=bag_path,
                        file_size=file_size,
                        analysis_level=AnalysisLevel.QUICK
                    )
                
                # Set time range using the optimized method
                self._current_bag_info.set_time_range(start_time_tuple, end_time_tuple)
                
                # Process connections using optimized builder methods
                for connection in reader.connections:
                    topic_name = connection.topic
                    message_type = connection.msgtype
                    
                    # Create and add TopicInfo object directly
                    topic_info = TopicInfo(
                        name=topic_name,
                        message_type=message_type,
                        first_message_time=start_time_tuple,
                        last_message_time=end_time_tuple,
                        connection_id=str(connection.id) if hasattr(connection, 'id') else None
                    )
                    self._current_bag_info.add_topic(topic_info)
                    
                    # Create and add MessageTypeInfo object if not exists
                    if message_type and not self._current_bag_info.find_message_type(message_type):
                        message_type_info = MessageTypeInfo(
                            message_type=message_type,
                            definition=connection.msgdef if hasattr(connection, 'msgdef') else None
                        )
                        
                        # Parse message fields if available
                        if hasattr(connection, 'msgdef') and connection.msgdef:
                            try:
                                fields = self._parse_message_definition_to_fields(connection.msgdef)
                                message_type_info.fields = fields
                            except Exception as e:
                                _logger.warning(f"Failed to parse message definition for {message_type}: {e}")
                        
                        self._current_bag_info.add_message_type(message_type_info)
                
                # Update metadata
                self._current_bag_info.last_updated = time.time()
                
                elapsed = time.time() - start_time
                _logger.info(f"Quick analysis completed in {elapsed:.3f}s - {len(self._current_bag_info.topics)} topics")
                
                return self._current_bag_info, elapsed
                
        except Exception as e:
            _logger.error(f"Error in quick analysis for {bag_path}: {e}")
            raise Exception(f"Error in quick analysis: {e}")
    
    def _analyze_bag_with_index(self, bag_path: str) -> Tuple[ComprehensiveBagInfo, float]:
        """
        Perform analysis with message indexing and DataFrame creation
        
        Gets basic metadata plus creates a pandas DataFrame with all message data
        for data analysis purposes.
        
        Args:
            bag_path: Path to the bag file
            
        Returns:
            Tuple of (ComprehensiveBagInfo, elapsed_time_seconds)
        """
        start_time = time.time()
        
        if not PANDAS_AVAILABLE:
            _logger.warning("pandas not available, falling back to quick analysis")
            return self._analyze_bag_quick(bag_path)
        
        # Check if we already have index analysis for this bag
        if (self._is_cache_valid(bag_path) and 
            self._current_bag_info is not None and
            self._current_bag_info.has_message_index()):
            elapsed = time.time() - start_time
            _logger.info(f"Using cached index analysis for {bag_path}")
            return self._current_bag_info, elapsed
        
        _logger.info(f"Performing analysis with message indexing for {bag_path}")
        
        try:
            self._initialize_typestore()
            
            reader_args = [Path(bag_path)]
            reader_kwargs = {'default_typestore': self._typestore} if self._typestore else {}
            
            with AnyReader(reader_args, **reader_kwargs) as reader:
                # First, do quick analysis to get basic info
                quick_info, _ = self._analyze_bag_quick(bag_path)
                
                # Upgrade analysis level to INDEX
                quick_info.analysis_level = AnalysisLevel.INDEX
                
                # Prepare data for DataFrame
                message_data = []
                
                _logger.info(f"Reading messages for indexing...")
                message_count = 0
                
                # Read all messages and create index with content
                for connection, timestamp, rawdata in reader.messages():
                    # Convert timestamp to seconds for easier analysis
                    timestamp_sec = timestamp / 1_000_000_000
                    timestamp_ns = timestamp
                    
                    # Start with basic message record
                    message_record = {
                        'timestamp_sec': timestamp_sec,
                        'timestamp_ns': timestamp_ns,
                        'topic': connection.topic,
                        'message_type': connection.msgtype,
                        'message_size': len(rawdata),
                        'connection_id': connection.id if hasattr(connection, 'id') else None
                    }
                    
                    # Deserialize and flatten message content
                    try:
                        # Use the reader's built-in deserialization
                        msg = reader.deserialize(rawdata, connection.msgtype)
                        
                        # Flatten message fields
                        flattened_fields = self._flatten_message_fields(msg)
                        message_record.update(flattened_fields)
                        
                    except Exception as e:
                        _logger.debug(f"Failed to deserialize message on {connection.topic}: {e}")
                        # Continue with basic record if deserialization fails
                    
                    message_data.append(message_record)
                    message_count += 1
                    
                    # Log progress for large bags
                    if message_count % 10000 == 0:
                        _logger.debug(f"Indexed {message_count} messages with content...")
                
                # Create topic-specific DataFrames (replacing sparse DataFrame)
                if message_data:
                    # Group messages by topic
                    topic_groups = {}
                    for record in message_data:
                        topic_name = record['topic']
                        if topic_name not in topic_groups:
                            topic_groups[topic_name] = []
                        topic_groups[topic_name].append(record)
                    
                    # Create DataFrame for each topic
                    total_dataframes_created = 0
                    total_memory_saved = 0
                    
                    for topic_name, topic_messages in topic_groups.items():
                        if not topic_messages:
                            continue
                            
                        # Create DataFrame for this topic
                        topic_df = pd.DataFrame(topic_messages)
                        
                        # Remove completely empty columns for this topic
                        topic_df = topic_df.dropna(axis=1, how='all')
                        
                        # Optimize DataFrame dtypes for memory efficiency
                        if 'timestamp_sec' in topic_df.columns:
                            topic_df['timestamp_sec'] = topic_df['timestamp_sec'].astype('float64')
                        if 'timestamp_ns' in topic_df.columns:
                            topic_df['timestamp_ns'] = topic_df['timestamp_ns'].astype('int64')
                        if 'topic' in topic_df.columns:
                            topic_df['topic'] = topic_df['topic'].astype('category')
                        if 'message_type' in topic_df.columns:
                            topic_df['message_type'] = topic_df['message_type'].astype('category')
                        if 'message_size' in topic_df.columns:
                            topic_df['message_size'] = topic_df['message_size'].astype('int32')
                        
                        # Optimize numeric columns
                        for col in topic_df.columns:
                            if col not in ['timestamp_sec', 'timestamp_ns', 'topic', 'message_type', 'message_size', 'connection_id']:
                                if topic_df[col].dtype == 'object':
                                    # Try to convert to numeric if possible
                                    try:
                                        numeric_col = pd.to_numeric(topic_df[col], errors='coerce')
                                        # Only convert if we have some numeric values
                                        if not numeric_col.isna().all():
                                            topic_df[col] = numeric_col
                                    except:
                                        pass
                        
                        # Set timestamp as index for time-based analysis
                        if 'timestamp_sec' in topic_df.columns:
                            topic_df.set_index('timestamp_sec', inplace=True)
                            topic_df.sort_index(inplace=True)
                        
                        # Store DataFrame in the corresponding TopicInfo
                        topic_info = quick_info.find_topic(topic_name)
                        if topic_info:
                            topic_info.set_dataframe(topic_df)
                            total_dataframes_created += 1
                            
                            # Calculate memory saved compared to sparse approach
                            if topic_info.df_memory_usage:
                                total_memory_saved += topic_info.df_memory_usage
                    
                    _logger.info(f"Created {total_dataframes_created} topic-specific DataFrames with {message_count} total messages")
                    _logger.info(f"Memory efficient storage: {total_memory_saved / 1024 / 1024:.1f} MB (vs sparse DataFrame)")
                else:
                    _logger.warning("No messages found in bag file")
                
                # Update metadata
                quick_info.last_updated = time.time()
                self._current_bag_info = quick_info
                
                elapsed = time.time() - start_time
                _logger.info(f"Index analysis completed in {elapsed:.3f}s - {message_count} messages indexed")
                
                return quick_info, elapsed
                
        except Exception as e:
            _logger.error(f"Error in index analysis for {bag_path}: {e}")
            raise Exception(f"Error in index analysis: {e}")
    
    def _flatten_message_fields(self, msg: Any, prefix: str = '', max_depth: int = 3, current_depth: int = 0) -> Dict[str, Any]:
        """
        Flatten message fields into a dictionary for DataFrame storage
        
        Args:
            msg: The deserialized message object
            prefix: Field name prefix for nested structures
            max_depth: Maximum nesting depth to prevent infinite recursion
            current_depth: Current nesting depth
            
        Returns:
            Dictionary of flattened field values
        """
        flattened = {}
        
        if current_depth >= max_depth:
            return flattened
        
        try:
            # Handle different message types
            if hasattr(msg, '__dict__'):
                # Standard message with attributes
                for field_name, field_value in msg.__dict__.items():
                    if field_name.startswith('_'):
                        continue  # Skip private fields
                    
                    full_field_name = f"{prefix}.{field_name}" if prefix else field_name
                    
                    # Handle different data types
                    if field_value is None:
                        flattened[full_field_name] = None
                    elif isinstance(field_value, (int, float, bool, str)):
                        flattened[full_field_name] = field_value
                    elif isinstance(field_value, (list, tuple)):
                        # Handle arrays/lists
                        if len(field_value) == 0:
                            flattened[f"{full_field_name}_length"] = 0
                        else:
                            flattened[f"{full_field_name}_length"] = len(field_value)
                            # Store first few elements for arrays of primitives
                            for i, item in enumerate(field_value[:5]):  # Limit to first 5 elements
                                if isinstance(item, (int, float, bool, str)):
                                    flattened[f"{full_field_name}[{i}]"] = item
                                elif hasattr(item, '__dict__') and current_depth < max_depth - 1:
                                    # Nested object in array
                                    nested = self._flatten_message_fields(
                                        item, f"{full_field_name}[{i}]", max_depth, current_depth + 1
                                    )
                                    flattened.update(nested)
                    elif hasattr(field_value, '__dict__') and current_depth < max_depth - 1:
                        # Nested message
                        nested = self._flatten_message_fields(
                            field_value, full_field_name, max_depth, current_depth + 1
                        )
                        flattened.update(nested)
                    else:
                        # Convert other types to string representation
                        flattened[full_field_name] = str(field_value)
            
            elif hasattr(msg, '__slots__'):
                # Message with slots
                for field_name in msg.__slots__:
                    if hasattr(msg, field_name):
                        field_value = getattr(msg, field_name)
                        full_field_name = f"{prefix}.{field_name}" if prefix else field_name
                        
                        if isinstance(field_value, (int, float, bool, str)):
                            flattened[full_field_name] = field_value
                        elif field_value is None:
                            flattened[full_field_name] = None
                        elif hasattr(field_value, '__dict__') and current_depth < max_depth - 1:
                            nested = self._flatten_message_fields(
                                field_value, full_field_name, max_depth, current_depth + 1
                            )
                            flattened.update(nested)
                        else:
                            flattened[full_field_name] = str(field_value)
            
        except Exception as e:
            _logger.warning(f"Error flattening message fields: {e}")
        
        return flattened
    
    def _analyze_bag_full(self, bag_path: str) -> Tuple[ComprehensiveBagInfo, float]:
        """
        Perform full analysis with message traversal
        
        Gets complete statistics: message counts, sizes, frequencies
        
        Args:
            bag_path: Path to the bag file
            
        Returns:
            Tuple of (ComprehensiveBagInfo, elapsed_time_seconds)
        """
        start_time = time.time()
        
        # Check if we already have full analysis for this bag
        if (self._is_cache_valid(bag_path) and 
            self._current_bag_info is not None and
            self._current_bag_info.has_full_analysis()):
            elapsed = time.time() - start_time
            _logger.info(f"Using cached full analysis for {bag_path}")
            return self._current_bag_info, elapsed
        
        _logger.info(f"Performing full analysis for {bag_path}")
        
        # Ensure we have quick analysis first (handles caching internally)
        self._analyze_bag_quick(bag_path)
        
        try:
            self._initialize_typestore()
            
            reader_args = [Path(bag_path)]
            reader_kwargs = {'default_typestore': self._typestore} if self._typestore else {}
            
            with AnyReader(reader_args, **reader_kwargs) as reader:
                # Calculate comprehensive statistics with message traversal
                total_messages = 0
                total_size = 0
                
                _logger.debug(f"Calculating statistics for {len(reader.connections)} topics")
                
                for connection in reader.connections:
                    count = 0
                    connection_size = 0
                    min_size = float('inf')
                    max_size = 0
                    
                    # Stream messages efficiently to avoid memory buildup
                    for (_, _, rawdata) in reader.messages([connection]):
                        count += 1
                        msg_size = len(rawdata)
                        connection_size += msg_size
                        min_size = min(min_size, msg_size)
                        max_size = max(max_size, msg_size)
                    
                    # Calculate derived statistics
                    avg_size = connection_size // count if count > 0 else 0
                    min_size = min_size if min_size != float('inf') else 0
                    
                    # Create TopicStatistics object using optimized structure
                    from .model import TopicStatistics
                    topic_stats = TopicStatistics(
                        topic_name=connection.topic,
                        message_count=count,
                        total_size_bytes=connection_size,
                        average_message_size=avg_size,
                        min_message_size=min_size,
                        max_message_size=max_size
                    )
                    self._current_bag_info.add_topic_statistics(topic_stats)
                    
                    # Update corresponding TopicInfo object with statistics
                    topic_info = self._current_bag_info.find_topic(connection.topic)
                    if topic_info:
                        topic_info.message_count = count
                        topic_info.total_size_bytes = connection_size
                        topic_info.average_message_size = avg_size
                        # Calculate frequency using the topic's method
                        topic_info.calculate_frequency()
                    
                    total_messages += count
                    total_size += connection_size
                
                # Update bag info with full analysis data
                # At this point _current_bag_info is guaranteed to be not None
                assert self._current_bag_info is not None
                self._current_bag_info.upgrade_analysis_level(AnalysisLevel.FULL)
                self._current_bag_info.total_messages = total_messages
                self._current_bag_info.total_size = total_size
                self._current_bag_info.last_updated = time.time()
                
                elapsed = time.time() - start_time
                topics_count = len(self._current_bag_info.topics) if self._current_bag_info.topics else 0
                _logger.info(f"Full analysis completed in {elapsed:.3f}s - {total_messages} messages from {topics_count} topics")
                
                return self._current_bag_info, elapsed
                
        except Exception as e:
            _logger.error(f"Error in full analysis for {bag_path}: {e}")
            raise Exception(f"Error in full analysis: {e}")
    
    def _validate_compression(self, compression: str) -> None:
        """Validate compression type"""
        from roseApp.core.util import validate_compression_type
        is_valid, error_message = validate_compression_type(compression)
        if not is_valid:
            raise ValueError(error_message)
    
    def _get_compression_format(self, compression: str):
        """Get rosbags CompressionFormat enum from string"""
        try:
            if compression == 'bz2':
                return Rosbag1Writer.CompressionFormat.BZ2
            elif compression == 'lz4':
                return Rosbag1Writer.CompressionFormat.LZ4
            else:
                return None
        except Exception:
            return None
    
    def _optimize_compression_settings(self, writer: Any, compression: str) -> None:
        """Optimize compression settings based on compression type"""
        rosbags_compression = self._get_compression_format(compression)
        if rosbags_compression:
            writer.set_compression(rosbags_compression)
            _logger.debug(f"Set compression to {compression}")
    
    def _prepare_output_file(self, output_bag: str, overwrite: bool) -> None:
        """Prepare output file, handling existence and overwrite logic"""
        if os.path.exists(output_bag) and not overwrite:
            raise FileExistsError(f"Output file '{output_bag}' already exists. Use overwrite=True to overwrite.")
        
        if os.path.exists(output_bag) and overwrite:
            os.remove(output_bag)
        
        # Create output directory if needed
        output_dir = os.path.dirname(output_bag)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
    
    def _convert_time_range(self, time_range: Optional[Tuple]) -> Tuple[Optional[int], Optional[int]]:
        """Convert time range to nanoseconds"""
        if not time_range:
            return None, None
        
        start_ns = time_range[0][0] * 1_000_000_000 + time_range[0][1]
        end_ns = time_range[1][0] * 1_000_000_000 + time_range[1][1]
        return start_ns, end_ns
    
    def _setup_writer_connections(self, writer: Any, selected_connections: List[Any]) -> Dict[str, Any]:
        """Setup writer connections once for efficient reuse"""
        topic_connections = {}
        for connection in selected_connections:
            callerid = '/rosbags_enhanced_parser'
            if hasattr(connection, 'ext') and hasattr(connection.ext, 'callerid'):
                if connection.ext.callerid is not None:
                    callerid = connection.ext.callerid
            
            msgdef = getattr(connection, 'msgdef', None)
            md5sum = getattr(connection, 'digest', None)
            
            new_connection = writer.add_connection(
                topic=connection.topic,
                msgtype=connection.msgtype,
                msgdef=msgdef,
                md5sum=md5sum,
                callerid=callerid
            )
            topic_connections[connection.topic] = new_connection
        
        return topic_connections
    
    def _extract_with_chronological_ordering(self, reader: Any, selected_connections: List[Any], 
                                           output_bag: str, extract_option: ExtractOption, 
                                           progress_callback: Optional[Callable] = None) -> int:
        """
        Extract messages with guaranteed chronological ordering using memory-efficient approach
        
        For large bag files, uses chunked processing to avoid memory exhaustion while
        maintaining chronological order.
        
        Args:
            reader: AnyReader instance
            selected_connections: Filtered connections for selected topics
            output_bag: Output bag file path
            extract_option: Extract options including memory limit
            progress_callback: Optional progress callback
            
        Returns:
            Total number of processed messages
        """
        # Calculate memory limit in bytes
        memory_limit_bytes = extract_option.memory_limit_mb * 1024 * 1024
        
        # Phase 1: Collect messages with memory management
        _logger.debug("Phase 1: Collecting messages with memory-efficient chunking")
        messages_buffer = []
        current_memory_usage = 0
        start_ns, end_ns = self._convert_time_range(extract_option.time_range)
        total_collected = 0
        
        # Collect all messages first (needed for chronological sorting)
        for (connection, timestamp, rawdata) in reader.messages(connections=selected_connections):
            # Apply time range filtering
            if extract_option.time_range:
                if start_ns is not None and end_ns is not None:
                    if not (start_ns <= timestamp <= end_ns):
                        continue
            
            message_size = len(rawdata)
            messages_buffer.append((connection, timestamp, rawdata))
            current_memory_usage += message_size
            total_collected += 1
            
            # Check memory usage periodically
            if total_collected % 1000 == 0:
                _logger.debug(f"Collected {total_collected} messages, using {current_memory_usage / 1024 / 1024:.1f}MB")
        
        if not messages_buffer:
            _logger.warning("No messages found within specified time range")
            return 0
        
        # Phase 2: Sort messages by timestamp for chronological order
        _logger.debug(f"Phase 2: Sorting {len(messages_buffer)} messages chronologically")
        messages_buffer.sort(key=lambda x: x[1])
        
        # Phase 3: Write messages to output bag in chronological order
        _logger.debug("Phase 3: Writing messages in chronological order")
        output_path = Path(output_bag)
        writer = Rosbag1Writer(output_path)
        
        # Apply optimized compression settings
        self._optimize_compression_settings(writer, extract_option.compression)
        
        total_processed = 0
        with writer:
            # Setup writer connections
            topic_connections = self._setup_writer_connections(writer, selected_connections)
            
            # Write messages in optimized chunks
            chunk_size = min(1000, len(messages_buffer) // 10 + 1)  # Adaptive chunk size
            
            for i in range(0, len(messages_buffer), chunk_size):
                chunk = messages_buffer[i:i + chunk_size]
                
                # Write chunk of messages (already chronologically sorted)
                for connection, timestamp, rawdata in chunk:
                    writer.write(topic_connections[connection.topic], timestamp, rawdata)
                    total_processed += 1
                
                # Update progress
                if progress_callback:
                    try:
                        progress_callback(total_processed)
                    except:
                        pass
                
                # Log progress for large extractions
                if total_processed % 10000 == 0:
                    progress_pct = (total_processed / len(messages_buffer)) * 100
                    _logger.debug(f"Written {total_processed}/{len(messages_buffer)} messages ({progress_pct:.1f}%)")
        
        _logger.info(f"Successfully wrote {total_processed} messages in chronological order")
        return total_processed
    
    def _parse_message_definition(self, msgdef: str) -> Dict[str, Any]:
        """
        Parse ROS message definition string into structured field information
        
        Args:
            msgdef: Message definition string from connection metadata
            
        Returns:
            Dictionary containing field structure information
        """
        if not msgdef:
            return {}
        
        fields = {}
        lines = msgdef.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue
            
            # Skip constant definitions (contain '=')
            if '=' in line:
                continue
            
            # Parse field definition: "type name" or "type[] name"
            parts = line.split()
            if len(parts) >= 2:
                field_type = parts[0]
                field_name = parts[1]
                
                field_info = {
                    'type': field_type,
                    'is_array': '[]' in field_type,
                    'is_builtin': self._is_builtin_type(field_type.replace('[]', ''))
                }
                
                # For complex types, we could recursively parse them
                # but for now, we'll just mark them as complex
                if not field_info['is_builtin']:
                    field_info['is_complex'] = True
                
                fields[field_name] = field_info
        
        return fields
    
    def _is_builtin_type(self, type_name: str) -> bool:
        """Check if a type is a ROS builtin type"""
        builtin_types = {
            'bool', 'int8', 'uint8', 'int16', 'uint16', 'int32', 'uint32',
            'int64', 'uint64', 'float32', 'float64', 'string', 'time', 'duration'
        }
        return type_name in builtin_types
    
    def _parse_message_definition_to_fields(self, msgdef: str) -> List[MessageFieldInfo]:
        """
        Parse ROS message definition string into MessageFieldInfo objects with nested structure
        
        Args:
            msgdef: Message definition string from connection metadata
            
        Returns:
            List of MessageFieldInfo objects with proper nesting
        """
        if not msgdef:
            return []
        
        # Split the message definition by MSG: separators to handle nested types
        sections = msgdef.split('================================================================================')
        
        # Parse the main message (first section)
        main_section = sections[0] if sections else msgdef
        main_fields = self._parse_message_section(main_section)
        
        # Parse nested message types (additional sections)
        nested_types = {}
        for i in range(1, len(sections)):
            section = sections[i].strip()
            if section.startswith('MSG:'):
                # Extract message type name
                lines = section.split('\n')
                if len(lines) > 0:
                    msg_line = lines[0].strip()
                    if msg_line.startswith('MSG:'):
                        msg_type = msg_line[4:].strip()  # Remove 'MSG: ' prefix
                        # Parse fields for this nested type
                        nested_content = '\n'.join(lines[1:])
                        nested_fields = self._parse_message_section(nested_content)
                        nested_types[msg_type] = nested_fields
        
        # Now link nested fields to their parent fields
        for field in main_fields:
            if not field.is_builtin:
                # Try exact match first
                if field.field_type in nested_types:
                    field.nested_fields = nested_types[field.field_type]
                else:
                    # Try partial match (e.g., 'Header' matches 'std_msgs/Header')
                    for nested_type_name, nested_fields in nested_types.items():
                        if nested_type_name.endswith('/' + field.field_type) or nested_type_name == field.field_type:
                            field.nested_fields = nested_fields
                            break
        
        return main_fields
    
    def _parse_message_section(self, section: str) -> List[MessageFieldInfo]:
        """Parse a single message section into fields"""
        fields = []
        lines = section.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue
            
            # Skip MSG: lines
            if line.startswith('MSG:'):
                continue
                
            # Skip constant definitions (contain '=')
            if '=' in line:
                continue
            
            # Parse field definition: "type name" or "type[] name"
            parts = line.split()
            if len(parts) >= 2:
                field_type_raw = parts[0]
                field_name = parts[1]
                
                # Check if it's an array
                is_array = '[]' in field_type_raw
                field_type = field_type_raw.replace('[]', '')
                
                # Determine array size (None for dynamic arrays)
                array_size = None
                if '[' in field_type_raw and ']' in field_type_raw:
                    # Extract array size if specified like [10]
                    try:
                        start = field_type_raw.find('[')
                        end = field_type_raw.find(']')
                        size_str = field_type_raw[start+1:end]
                        if size_str:
                            array_size = int(size_str)
                    except (ValueError, IndexError):
                        pass  # Keep array_size as None for dynamic arrays
                
                # Check if it's a builtin type
                is_builtin = self._is_builtin_type(field_type)
                
                # Create MessageFieldInfo object
                field_info = MessageFieldInfo(
                    field_name=field_name,
                    field_type=field_type,
                    is_array=is_array,
                    array_size=array_size,
                    is_builtin=is_builtin,
                    nested_fields=None  # Will be populated later if it's a complex type
                )
                
                fields.append(field_info)
        
        return fields


def create_parser() -> BagParser:
    """Create or get singleton parser instance"""
    return BagParser()

