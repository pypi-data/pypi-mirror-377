# src/df_gallery/thumbnail_server.py
"""
Thumbnail server for df-gallery.
Generates and serves optimized thumbnails for faster image loading.
"""

import hashlib
import time
from pathlib import Path
from typing import Optional, Dict, Any
from http.server import SimpleHTTPRequestHandler
import threading

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


class ThumbnailServer:
    """Handles thumbnail generation and caching for df-gallery."""
    
    def __init__(self, 
                 image_root: Path,
                 cache_dir: Path = Path(".df_gallery_cache"),
                 default_size: int = 200,
                 quality: int = 85):
        self.image_root = image_root.resolve()
        self.cache_dir = cache_dir.resolve()
        self.default_size = default_size
        self.quality = quality
        self.cache_dir.mkdir(exist_ok=True)
        
        # Thread safety
        self._locks: Dict[str, threading.Lock] = {}
        self._global_lock = threading.Lock()
    
    def get_thumbnail_path(self, image_path: str, size: int) -> Path:
        """Get the cache path for a thumbnail."""
        # Create a hash of the original path + size for cache key
        cache_key = hashlib.md5(f"{image_path}:{size}".encode()).hexdigest()
        return self.cache_dir / f"{cache_key}.webp"
    
    def generate_thumbnail(self, image_path: str, size: int) -> Path:
        """Generate a thumbnail for an image."""
        if not PIL_AVAILABLE:
            raise RuntimeError("PIL/Pillow is required for thumbnail generation")
        
        # Resolve the full image path
        full_image_path = self.image_root / image_path
        if not full_image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        # Get cache path
        cache_path = self.get_thumbnail_path(image_path, size)
        
        # Thread-safe thumbnail generation
        cache_key = f"{image_path}:{size}"
        
        # Get or create lock for this specific image+size
        with self._global_lock:
            if cache_key not in self._locks:
                self._locks[cache_key] = threading.Lock()
            lock = self._locks[cache_key]
        
        with lock:
            # Check if thumbnail already exists and is newer than original
            if cache_path.exists():
                cache_time = cache_path.stat().st_mtime
                original_time = full_image_path.stat().st_mtime
                if cache_time > original_time:
                    return cache_path
            
            # Generate new thumbnail
            try:
                with Image.open(full_image_path) as img:
                    # Convert to RGB if necessary (for WebP)
                    if img.mode in ('RGBA', 'LA', 'P'):
                        img = img.convert('RGB')
                    
                    # Calculate new dimensions maintaining aspect ratio
                    img.thumbnail((size, size), Image.Resampling.LANCZOS)
                    
                    # Save as WebP for better compression
                    img.save(cache_path, 'WebP', quality=self.quality, optimize=True)
                    
                    return cache_path
            except Exception as e:
                # If thumbnail generation fails, raise the error
                raise RuntimeError(f"Failed to generate thumbnail: {e}")
    
    def get_thumbnail_info(self, image_path: str, size: int) -> Dict[str, Any]:
        """Get information about a thumbnail (exists, size, etc.)."""
        cache_path = self.get_thumbnail_path(image_path, size)
        full_image_path = self.image_root / image_path
        
        info = {
            'exists': cache_path.exists(),
            'image_path': image_path,
            'size': size,
            'cache_path': str(cache_path),
            'original_exists': full_image_path.exists()
        }
        
        if cache_path.exists():
            info['cache_size'] = cache_path.stat().st_size
            info['cache_mtime'] = cache_path.stat().st_mtime
        
        if full_image_path.exists():
            info['original_size'] = full_image_path.stat().st_size
            info['original_mtime'] = full_image_path.stat().st_mtime
        
        return info


class ThumbnailRequestHandler(SimpleHTTPRequestHandler):
    """HTTP request handler that serves thumbnails."""
    
    def __init__(self, thumbnail_server: ThumbnailServer, *args, **kwargs):
        self.thumbnail_server = thumbnail_server
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests."""
        if self.path.startswith('/thumbnail/'):
            self.handle_thumbnail_request()
        elif self.path.startswith('/original/'):
            self.handle_original_request()
        else:
            # Let the parent class handle other requests
            super().do_GET()
    
    def handle_thumbnail_request(self):
        """Handle thumbnail requests: /thumbnail/{size}/{image_path}"""
        try:
            # Parse URL: /thumbnail/200/images/photo.jpg
            parts = self.path.split('/', 3)
            if len(parts) != 4:
                self.send_error(400, "Invalid thumbnail URL format")
                return
            
            _, _, size_str, image_path = parts
            size = int(size_str)
            
            # Generate or get cached thumbnail
            thumbnail_path = self.thumbnail_server.generate_thumbnail(image_path, size)
            
            # Serve the thumbnail
            self.serve_file(thumbnail_path, 'image/webp')
            
        except (ValueError, FileNotFoundError) as e:
            self.send_error(404, str(e))
        except RuntimeError as e:
            self.send_error(500, str(e))
        except Exception as e:
            self.send_error(500, f"Unexpected error: {e}")
    
    def handle_original_request(self):
        """Handle original image requests: /original/{image_path}"""
        try:
            # Parse URL: /original/images/photo.jpg
            image_path = self.path[9:]  # Remove '/original/'
            full_path = self.thumbnail_server.image_root / image_path
            
            if not full_path.exists():
                self.send_error(404, f"Image not found: {image_path}")
                return
            
            # Determine content type
            content_type = self.get_content_type(full_path)
            self.serve_file(full_path, content_type)
            
        except Exception as e:
            self.send_error(500, f"Error serving original image: {e}")
    
    def serve_file(self, file_path: Path, content_type: str):
        """Serve a file with proper headers."""
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            
            self.send_response(200)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', str(len(content)))
            self.send_header('Cache-Control', 'public, max-age=31536000')  # Cache for 1 year
            self.end_headers()
            self.wfile.write(content)
            
        except Exception as e:
            self.send_error(500, f"Error serving file: {e}")
    
    def get_content_type(self, file_path: Path) -> str:
        """Determine content type based on file extension."""
        ext = file_path.suffix.lower()
        content_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg', 
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp',
            '.bmp': 'image/bmp',
            '.tiff': 'image/tiff',
            '.tif': 'image/tiff'
        }
        return content_types.get(ext, 'application/octet-stream')
    
    def log_message(self, format, *args):
        """Override to reduce log noise."""
        # Only log errors, not every request
        if 'error' in format.lower():
            super().log_message(format, *args)
