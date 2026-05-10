"""Instagram service for fetching saved posts."""
import time
import logging
from datetime import datetime
from pathlib import Path
import instaloader
from PIL import Image
from flask import current_app
from app import db
from app.models.post import Post

logger = logging.getLogger(__name__)


class InstagramService:
    """Service for interacting with Instagram."""
    
    def __init__(self):
        """Initialize Instaloader instance."""
        self.loader = instaloader.Instaloader(
            download_videos=False,
            download_video_thumbnails=True,
            download_geotags=False,
            download_comments=False,
            save_metadata=False,
            compress_json=False,
            quiet=True
        )
        self.session_file = None
        self.username = None
    
    def login(self, username, password):
        """Login to Instagram.
        
        Args:
            username: Instagram username
            password: Instagram password
            
        Returns:
            dict: {'success': bool, 'message': str, 'requires_2fa': bool}
        """
        try:
            self.username = username
            self.session_file = f"session-{username}"
            
            # Try to load existing session first
            if Path(self.session_file).exists():
                try:
                    self.loader.load_session_from_file(username, self.session_file)
                    logger.info(f"Loaded session for {username}")
                    return {
                        'success': True,
                        'message': 'Logged in using saved session',
                        'requires_2fa': False
                    }
                except Exception as e:
                    logger.warning(f"Failed to load session: {e}")
            
            # Perform fresh login
            self.loader.login(username, password)
            self.loader.save_session_to_file(self.session_file)
            logger.info(f"Successfully logged in as {username}")
            
            return {
                'success': True,
                'message': 'Successfully logged in',
                'requires_2fa': False
            }
            
        except instaloader.TwoFactorAuthRequiredException:
            logger.info(f"2FA required for {username}")
            return {
                'success': False,
                'message': '2FA code required',
                'requires_2fa': True
            }
        except instaloader.BadCredentialsException:
            logger.error(f"Bad credentials for {username}")
            return {
                'success': False,
                'message': 'Invalid username or password',
                'requires_2fa': False
            }
        except Exception as e:
            logger.error(f"Login failed: {e}")
            return {
                'success': False,
                'message': str(e),
                'requires_2fa': False
            }
    
    def login_with_2fa(self, username, password, two_factor_code):
        """Login with 2FA code.
        
        Args:
            username: Instagram username
            password: Instagram password
            two_factor_code: 2FA verification code
            
        Returns:
            dict: {'success': bool, 'message': str}
        """
        try:
            self.username = username
            self.session_file = f"session-{username}"
            
            self.loader.two_factor_login(two_factor_code)
            self.loader.save_session_to_file(self.session_file)
            logger.info(f"Successfully logged in with 2FA as {username}")
            
            return {
                'success': True,
                'message': 'Successfully logged in with 2FA'
            }
        except Exception as e:
            logger.error(f"2FA login failed: {e}")
            return {
                'success': False,
                'message': str(e)
            }
    
    def is_logged_in(self):
        """Check if user is logged in.
        
        Returns:
            bool: True if logged in
        """
        try:
            return self.loader.test_login() if hasattr(self.loader, 'test_login') else (self.loader.context.username is not None)
        except:
            return False
    
    def fetch_saved_posts(self, user_id, max_posts=None, progress_callback=None):
        """Fetch saved posts from Instagram for a specific user.
        
        Args:
            user_id: Database user ID to associate posts with
            max_posts: Maximum number of posts to fetch (None for all)
            progress_callback: Optional callback function(current, total, post_shortcode)
            
        Returns:
            dict: {'success': bool, 'count': int, 'new': int, 'skipped': int, 'message': str}
        """
        if not self.is_logged_in():
            return {
                'success': False,
                'count': 0,
                'new': 0,
                'skipped': 0,
                'message': 'Not logged in. Please login first.'
            }
        
        try:
            if not max_posts:
                max_posts = current_app.config.get('MAX_POSTS_PER_FETCH', 50)
            
            profile = instaloader.Profile.from_username(
                self.loader.context,
                self.loader.context.username
            )
            
            saved_posts = profile.get_saved_posts()
            count = 0
            new_count = 0
            skipped_count = 0
            delay = current_app.config.get('FETCH_DELAY_SECONDS', 5)
            
            logger.info(f"Starting to fetch up to {max_posts} saved posts for user_id {user_id}")
            
            for post in saved_posts:
                if count >= max_posts:
                    logger.info(f"Reached max posts limit: {max_posts}")
                    break
                
                count += 1
                
                # Check if post already exists for this user
                existing = Post.query.filter_by(instagram_id=str(post.mediaid), user_id=user_id).first()
                if existing:
                    skipped_count += 1
                    logger.debug(f"Skipping existing post: {post.shortcode}")
                    if progress_callback:
                        progress_callback(count, max_posts, post.shortcode, 'skipped')
                    continue
                
                # Create and save new post for this user
                try:
                    new_post = self._create_post_from_insta(post, user_id)
                    db.session.add(new_post)
                    new_count += 1
                    logger.info(f"Added new post: {post.shortcode} for user_id {user_id}")
                    
                    if progress_callback:
                        progress_callback(count, max_posts, post.shortcode, 'added')
                    
                    # Commit in batches
                    if new_count % 5 == 0:
                        db.session.commit()
                        logger.debug(f"Committed batch of {new_count} posts")
                        
                    # Rate limiting
                    if count % 10 == 0:
                        logger.debug(f"Sleeping {delay}s for rate limiting")
                        time.sleep(delay)
                        
                except Exception as e:
                    logger.error(f"Failed to process post {post.shortcode}: {e}")
                    continue
            
            # Final commit
            db.session.commit()
            logger.info(f"Fetch complete: {new_count} new, {skipped_count} skipped")
            
            return {
                'success': True,
                'count': count,
                'new': new_count,
                'skipped': skipped_count,
                'message': f'Successfully fetched {new_count} new posts ({skipped_count} already existed)'
            }
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Fetch failed: {e}")
            return {
                'success': False,
                'count': 0,
                'new': 0,
                'skipped': 0,
                'message': f'Error: {str(e)}'
            }
    
    def _create_post_from_insta(self, post, user_id):
        """Create Post model from Instaloader post.
        
        Args:
            post: Instaloader Post object
            user_id: Database user ID to associate post with
            
        Returns:
            Post: New Post instance
        """
        # Download thumbnail
        thumbnail_path = self._download_thumbnail(post)
        
        # Determine media type
        if post.typename == 'GraphSidecar':
            media_type = 'carousel'
        elif post.is_video:
            media_type = 'video'
        else:
            media_type = 'photo'
        
        return Post(
            user_id=user_id,
            instagram_id=str(post.mediaid),
            shortcode=post.shortcode,
            caption=post.caption or '',
            post_url=f"https://www.instagram.com/p/{post.shortcode}/",
            media_type=media_type,
            thumbnail_path=thumbnail_path,
            owner_username=post.owner_username,
            owner_fullname=post.owner_profile.full_name if post.owner_profile else '',
            likes_count=post.likes,
            comments_count=post.comments,
            saved_at=post.date_utc,
            fetched_at=datetime.utcnow()
        )
    
    def _download_thumbnail(self, post):
        """Download and create thumbnail for post.
        
        Args:
            post: Instaloader Post object
            
        Returns:
            str: Relative path to saved thumbnail (or None if failed)
        """
        try:
            thumbnail_dir = current_app.config['THUMBNAIL_DIR']
            thumbnail_size = current_app.config.get('THUMBNAIL_SIZE', 400)
            filename = f"{post.shortcode}.jpg"
            filepath = Path(thumbnail_dir) / filename
            
            # Skip if already exists
            if filepath.exists():
                logger.debug(f"Thumbnail already exists: {filename}")
                return str(filepath.relative_to(current_app.config['BASE_DIR']))
            
            # Download image
            self.loader.download_pic(
                filename=str(filepath.with_suffix('')),
                url=post.url,
                mtime=post.date_utc
            )
            
            # If download created a different extension, rename it
            for ext in ['.jpg', '.jpeg', '.png']:
                test_path = filepath.with_suffix(ext)
                if test_path.exists() and test_path != filepath:
                    test_path.rename(filepath)
                    break
            
            # Create thumbnail if file exists
            if filepath.exists():
                img = Image.open(filepath)
                
                # Convert to RGB if necessary (for PNG with alpha)
                if img.mode in ('RGBA', 'LA', 'P'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                    img = background
                
                img.thumbnail((thumbnail_size, thumbnail_size), Image.Resampling.LANCZOS)
                img.save(filepath, 'JPEG', quality=85, optimize=True)
                logger.debug(f"Created thumbnail: {filename}")
                
                return str(filepath.relative_to(current_app.config['BASE_DIR']))
            else:
                logger.warning(f"Failed to download image for {post.shortcode}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to download thumbnail for {post.shortcode}: {e}")
            return None
    
    def get_session_username(self):
        """Get the username of the currently logged in user.
        
        Returns:
            str: Username or None if not logged in
        """
        try:
            return self.loader.context.username if self.loader.context else None
        except:
            return None
