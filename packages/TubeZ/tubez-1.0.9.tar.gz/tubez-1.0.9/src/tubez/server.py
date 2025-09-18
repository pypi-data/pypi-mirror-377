# src/tubez/server.py

import os
import json
import subprocess
import re
import uuid
import time
import threading
import requests
import yt_dlp
import hashlib
import socket
import io
import base64
import qrcode
import urllib.parse
from flask import (
    render_template, request, redirect, url_for,
    send_from_directory, flash, jsonify, session
)
from youtubesearchpython import VideosSearch
from packaging.version import parse as parse_version
from functools import wraps
import httpx
# --- Import from our package's __init__.py ---
from . import app, __version__, DOWNLOAD_FOLDER, HISTORY_FILE, CONFIG_FILE, load_config, DEFAULT_CONFIG, HISTORY_THUMB_CACHE
from .queue_manager import DOWNLOAD_QUEUE, DOWNLOAD_TASKS

def login_required(f):
    """Decorator to protect routes with a password if one is set."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        password = app.config.get("PASSWORD")
        if password and not session.get('logged_in'):
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def load_history():
    """Loads viewing history from the JSON file."""
    if not HISTORY_FILE.exists(): return []
    try:
        with open(HISTORY_FILE, 'r') as f: return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError): return []

def save_history_item(video_info):
    """Adds an item to the history, ensuring no duplicates and trimming to the limit."""
    history = load_history()
    video_identifier = video_info.get('webpage_url') or video_info.get('id')
    thumbnail_url_or_path = video_info.get('thumbnail')
    
    if 'instagram.com' in video_identifier:
        public_thumb_url = video_info.get('thumbnail')
        if public_thumb_url:
            try:
                # Create a secure, unique filename from the URL
                url_hash = hashlib.sha256(video_identifier.encode()).hexdigest()
                thumb_path = HISTORY_THUMB_CACHE / url_hash
                
                # Download and save the image
                response = requests.get(public_thumb_url, timeout=10)
                response.raise_for_status()
                with open(thumb_path, 'wb') as f:
                    f.write(response.content)
                
                # Store the local path instead of the public URL
                thumbnail_url_or_path = f"/thumb/{url_hash}"
                
            except requests.exceptions.RequestException as e:
                print(f"WARNING: Could not download Instagram thumbnail: {e}")
                thumbnail_url_or_path = None # Fallback if download fails
    new_item = {
        'id': video_identifier,
        'title': video_info.get('title'),
        'thumbnail': thumbnail_url_or_path
    }
    if not new_item['id'] or not new_item['title']: return
    history = [item for item in history if item.get('id') != new_item['id']]
    history.insert(0, new_item)
    with open(HISTORY_FILE, 'w') as f: json.dump(history[:20], f, indent=4)

# src/tubex/server.py
# In server.py, replace the old get_local_ip function with this one.

def get_local_ip():
    """
    Finds the local IP address of the server using a robust method.
    Tries connecting to a public DNS server to determine the active network interface.
    Falls back to resolving the hostname if the first method fails.
    """
    # Method 1: Connect to a public server (most reliable)
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Connect to a known public DNS server (doesn't send any data)
        s.connect(('8.8.8.8', 80))
        ip_address = s.getsockname()[0]
        s.close()
        return ip_address
    except Exception:
        # Method 2: Fallback to hostname resolution
        try:
            # This can sometimes return 127.0.0.1, so it's a fallback
            return socket.gethostbyname(socket.gethostname())
        except Exception:
            # If all else fails, return localhost
            return '127.0.0.1'
# --- REPLACE your old, subprocess-based get_video_info with this superior library version ---
def get_video_info(url_or_id, playlist=False):
    """
    Gets video or playlist metadata by using yt-dlp as a Python library.
    This is much faster and more efficient than using subprocesses.
    """
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': 'in_playlist' if playlist else False, # Efficiently get playlist entries
        'skip_download': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # The extract_info call does all the work and returns a Python dictionary
            info = ydl.extract_info(url_or_id, download=False)
            
            # For playlists, the result contains an 'entries' key
            if playlist and 'entries' in info:
                # We need to add playlist_title to each entry for the template
                playlist_title = info.get('title')
                for entry in info['entries']:
                    entry['playlist_title'] = playlist_title
                return info['entries']
            
            # For single videos, it's just the info dictionary
            return info
            
    except yt_dlp.utils.DownloadError as e:
        # This is the specific exception yt-dlp throws for download errors
        flash(f"Error fetching metadata: {e.msg}", "error")
        return None
    except Exception as e:
        # Catch any other unexpected errors
        flash(f"An unexpected error occurred: {e}", "error")
        return None

@app.template_filter('url_encode_path')
def url_encode_path_filter(s):
    """A template filter to safely encode a string for use in a URL path."""
    return urllib.parse.quote(s, safe='')

@app.route('/')
@login_required
def index():
    history = load_history()
    return render_template('index.html', history=history)

# In server.py, replace the entire old function with this one.
# --- Monkey patch to fix httpx 'proxies' error in youtubesearchpython ---
old_post = httpx.post

def safe_post(*args, **kwargs):
    # Strip out unsupported 'proxies' argument if present
    kwargs.pop("proxies", None)
    return old_post(*args, **kwargs)

httpx.post = safe_post

@app.route('/search')
@login_required
def search():
    query = request.args.get('q', '').strip()
    if not query:
        return redirect(url_for('index'))

    # Check if the query is a URL
    if re.match(r'https?://\S+', query):
        # Handle special case: YouTube Mixes are not standard playlists
        if 'youtube.com' in query and 'list=RD' in query:
            match = re.search(r'v=([^&]+)', query) or re.search(r'list=RD([^&]+)', query)
            if match:
                video_id = match.group(1)
                flash("YouTube Mix playlists are not supported. Loading the starting video of the mix instead.", "info")
                return redirect(url_for('formats', video_id=video_id))
        
        # Handle standard playlists, channels, etc.
        playlist_indicators = ['list=', 'playlist?', '/c/', '/channel/', '/user/']
        if any(indicator in query for indicator in playlist_indicators):
            return redirect(url_for('playlist', playlist_url=query))
        
        # If it's a URL but not a playlist, treat it as a single video
        return redirect(url_for('formats', video_id=query))
    
    # If not a URL, perform a search
    else:
        try:
            videos_search = VideosSearch(query, limit=12)
            search_data = videos_search.result()

            # --- THIS IS THE FIX ---
            # Defensively check if the results exist and are a list before proceeding.
            if search_data and 'result' in search_data and search_data['result']:
                results = search_data['result']
                return render_template('results.html', results=results, query=query)
            else:
                # If there are no results, render the same page with an empty list.
                # This prevents a crash and allows the template to show a "No results" message.
                return render_template('results.html', results=[], query=query)

        except Exception as e:
            # This will now catch other errors, like network issues.
            flash(f"An error occurred during YouTube search: {e}", "danger")
            return redirect(url_for('index'))

@app.route('/formats/<path:video_id>')
@login_required
def formats(video_id):
    video_id = urllib.parse.unquote(video_id)
    info = get_video_info(video_id)
    if not info: return redirect(request.referrer or url_for('index'))
    save_history_item(info)
  
    thumbnail_url = info.get('thumbnail')
    if not thumbnail_url and info.get('thumbnails'):
        thumbnail_url = info['thumbnails'][-1].get('url')

    
    format_list = []
    for f in info.get('formats', []):
        if 'storyboard' in f.get('format_note', ''): continue
        if f.get('vcodec') == 'none' and f.get('acodec') == 'none': continue
        is_video_only = f.get('vcodec') != 'none' and f.get('acodec') == 'none'
        is_audio_only = f.get('vcodec') == 'none' and f.get('acodec') != 'none'
        desc = ""
        if is_audio_only: desc = f"{int(f.get('abr', 0))}k ({f.get('ext')}, Audio Only)"
        else:
            desc = f"{f.get('height', 0)}p ({f.get('ext')})"
            if is_video_only: desc += " (Video Only)"
            else: desc += " (Video + Audio)"
        filesize = f.get('filesize_approx') or f.get('filesize')
        size_str = f"{filesize / (1024*1024):.2f} MB" if filesize else "N/A"
        format_list.append({'id': f['format_id'], 'description': desc, 'size': size_str, 'is_video_only': is_video_only, 'is_audio_only': is_audio_only})
        
    return render_template('formats.html', formats=format_list, video_id=video_id, title=info.get('title', ''), thumbnail=thumbnail_url)

@app.route('/playlist')
@login_required
def playlist():
    playlist_url = request.args.get('playlist_url')
    if not playlist_url: return redirect(url_for('index'))
    playlist_items = get_video_info(playlist_url, playlist=True)
    if not playlist_items: return redirect(url_for('index'))
    playlist_title = playlist_items[0].get('playlist_title', 'Playlist')
    return render_template('playlist.html', videos=playlist_items, title=playlist_title, playlist_url=playlist_url)

@app.route('/play/<path:video_id>')
@login_required
def play(video_id):
    video_id = urllib.parse.unquote(video_id)
    title = request.args.get('title', 'Loading video...')
    return render_template('play.html', video_id=video_id, title=title)

@app.route('/files')
@login_required
def files():
    finished = sorted([task for task in DOWNLOAD_TASKS.values() if task['status'] in ['completed', 'error']], key=lambda x: x.get('timestamp', 0), reverse=True)
    try:
        completed_files = sorted([f for f in os.listdir(DOWNLOAD_FOLDER) if not f.startswith('.')], reverse=True)
    except FileNotFoundError:
        completed_files = []
    return render_template('files.html', completed_files=completed_files, finished_tasks=finished[:5])

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        current_config = load_config()
        current_config['DOWNLOAD_PATH'] = request.form.get('download_path', DEFAULT_CONFIG['DOWNLOAD_PATH'])
        current_config['DEFAULT_AUDIO_FORMAT'] = request.form.get('audio_format', DEFAULT_CONFIG['DEFAULT_AUDIO_FORMAT'])
        current_config['ALLOW_LAN_ACCESS'] = 'allow_lan_access' in request.form
        new_password = request.form.get('password')
        if new_password:
            current_config['PASSWORD'] = new_password
        with open(CONFIG_FILE, 'w') as f:
            json.dump(current_config, f, indent=4)
        flash('Settings saved! Please restart the server for all changes to take effect.', 'success')
        return redirect(url_for('settings'))
    return render_template('settings.html', config=load_config())

# In server.py
@app.route('/share')
@login_required
def share():
    """Displays a QR code for connecting from other devices on the LAN."""
    # Get the server's actual running host from the app config
    server_host = app.config.get('SERVER_HOST', '127.0.0.1')
    
    # Get the user's desired setting from the config file
    config = load_config()
    lan_access_enabled_in_config = config.get('ALLOW_LAN_ACCESS', False)

    # The feature is only TRULY available if the server is listening on a network address
    is_accessible = server_host in ['0.0.0.0', '::']

    if not is_accessible:
        # If the server is not accessible, the reason depends on the config
        if lan_access_enabled_in_config:
            # The user has enabled it but hasn't restarted the server yet.
            reason = "restart_required"
        else:
            # The feature is simply disabled in the settings.
            reason = "disabled"
        return render_template('share.html', lan_access_allowed=False, reason=reason)

    # If we get here, the server is accessible, so we can generate the QR code
    local_ip = get_local_ip()
    port = app.config.get('SERVER_PORT', 8089)
    server_url = f"http://{local_ip}:{port}"

    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
    qr.add_data(server_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    
    return render_template(
        'share.html', 
        lan_access_allowed=True, 
        server_url=server_url, 
        qr_code_image=img_str
    )

@app.route('/progress/<task_id>')
@login_required
def progress_page(task_id):
    task = DOWNLOAD_TASKS.get(task_id)
    if not task:
        flash("Task not found or has been cleared.", "warning")
        return redirect(url_for('files'))
    return render_template('progress.html', task_id=task_id, title=task.get('title'))

# In server.py

@app.route('/login', methods=['GET', 'POST'])
def login():
    password = app.config.get("PASSWORD")

    # --- ADD THIS BLOCK ---
    # If a user is already logged in, don't show them the login page again.
    if session.get('logged_in'):
        return redirect(url_for('index'))
    # --- END ADDED BLOCK ---

    if not password:
        # This part is fine, it correctly allows access if no password is set.
        session['logged_in'] = True
        return redirect(url_for('index'))

    if request.method == 'POST':
        if request.form.get('password') == password:
            session['logged_in'] = True
            flash('You were successfully logged in!', 'success')
            return redirect(request.args.get('next') or url_for('index'))
        else:
            flash('Invalid password provided.', 'danger')
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out.', 'success')
    return redirect(url_for('login'))

# In server.py, replace the entire old function with this one.

# In server.py, replace the entire old function with this one.

def add_to_download_queue(video_id, format_code, title, is_video_only=False, is_audio_only=False, sub_lang=None):
    """Helper function to add a download job to the global queue."""
    task_id = str(uuid.uuid4())
    output_template = str(DOWNLOAD_FOLDER / '%(title).200s - [%(id)s].%(ext)s')
    
    base_command = ['yt-dlp', '-o', output_template, '--progress', '--restrict-filenames']
    
    if is_audio_only:
        command_args = [
            '-f', format_code, 
            '-x', '--audio-format', app.config.get("DEFAULT_AUDIO_FORMAT", "m4a")
        ]
    else:
        final_format_code = f"{format_code}+bestaudio[ext=m4a]/best" if is_video_only else format_code
        command_args = [
            '-f', final_format_code,
            '--merge-output-format', 'mp4'
        ]
        
        if sub_lang and sub_lang != 'none':
            command_args.extend([
                '--write-subs',
                # --- THIS IS THE CRITICAL FIX ---
                # Force subtitles to be downloaded in the highly compatible SRT format.
                '--sub-format', 'srt',
                '--sub-lang', sub_lang, 
                '--embed-subs'
            ])

    command = base_command + command_args + ['--', video_id]

    DOWNLOAD_TASKS[task_id] = {
        'status': 'queued',
        'stage': 'Waiting in queue...', 
        'progress': 0, 
        'title': title, 
        'id': task_id, 
        'timestamp': time.time()
    }
    DOWNLOAD_QUEUE.put((task_id, command, title))
    return title

@app.route('/download', methods=['POST'])
@login_required
def download():
    title = add_to_download_queue(
        video_id=request.form.get('video_id'),
        format_code=request.form.get('format_code'),
        title=request.form.get('title', 'Untitled'),
        is_video_only=request.form.get('is_video_only') == 'true',
        is_audio_only=request.form.get('is_audio_only') == 'true',
        sub_lang=request.form.get('sub_lang')
    )
    flash(f'"{title}" added to the download queue!', 'success')
    return redirect(url_for('files'))

@app.route('/quick_download_audio/<path:video_id>', methods=['POST'])
@login_required
def quick_download_audio(video_id):
    video_id = urllib.parse.unquote(video_id)
    info = get_video_info(video_id)
    if not info: return redirect(request.referrer or url_for('index'))
    title = add_to_download_queue(
        video_id=video_id,
        format_code='bestaudio[ext=m4a]/bestaudio',
        title=info.get('title', 'Untitled Audio'),
        is_audio_only=True
    )
    flash(f'"{title}" (Audio) added to the download queue!', 'success')
    return redirect(url_for('files'))

@app.route('/download_playlist', methods=['POST'])
@login_required
def download_playlist():
    video_ids = request.form.getlist('video_ids')
    if not video_ids:
        flash('You did not select any videos to download.', 'warning')
        return redirect(request.referrer)
    
    count = 0
    for video_id in video_ids:
        info = get_video_info(video_id)
        if info:
            add_to_download_queue(
                video_id=video_id,
                format_code='bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                title=info.get('title', f'Playlist Video {video_id}'),
                is_video_only=True
            )
            count += 1
    
    flash(f'Successfully added {count} videos to the download queue!', 'success')
    return redirect(url_for('files'))

@app.route('/api/delete_file', methods=['POST'])
@login_required
def delete_file():
    filename = request.form.get('filename')
    if not filename: return jsonify({'success': False, 'error': 'No filename provided.'}), 400
    try:
        file_path = DOWNLOAD_FOLDER.joinpath(filename).resolve()
        if not file_path.is_file() or DOWNLOAD_FOLDER.resolve() not in file_path.parents:
            raise FileNotFoundError("Invalid path or file does not exist.")
        os.remove(file_path)
        flash(f'"{filename}" was deleted successfully.', 'success')
        return jsonify({'success': True})
    except Exception as e:
        flash(f'Error deleting file: {e}', 'danger')
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/get_video_info/<path:video_id>')
@login_required
def api_get_video_info(video_id):
    video_id = urllib.parse.unquote(video_id)
    info = get_video_info(video_id)
    if not info: return jsonify({'error': "Failed to retrieve video metadata."}), 404
    save_history_item(info)
    return jsonify({'title': info.get('title', 'Untitled')})

# src/tubex/server.py

@app.route('/api/get_stream_url/<path:video_id>')
@login_required
def api_get_stream_url(video_id):
    video_id = urllib.parse.unquote(video_id)
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'format': 'best[vcodec!=none][acodec!=none]',
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_id, download=False)
            # The library puts the best URL in the 'url' key after processing formats
            stream_url = info.get('url')
            if not stream_url:
                return jsonify({'stream_url': None, 'playback_supported': False})
            return jsonify({'stream_url': stream_url, 'playback_supported': True})
    except Exception as e:
        return jsonify({'stream_url': None, 'playback_supported': False})


# In server.py, replace the old api_get_subtitles function with this one.

@app.route('/api/get_subtitles/<path:video_id>')
@login_required
def api_get_subtitles(video_id):
    video_id = urllib.parse.unquote(video_id)
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'listsubtitles': True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_id, download=False)
            
            sub_list = []
            
            # Process manually uploaded subtitles
            for lang_code, subs in info.get('subtitles', {}).items():
                lang_name = subs[0].get('name', lang_code) if subs else lang_code
                sub_list.append({'code': lang_code, 'name': lang_name})

            # Process auto-generated subtitles (automatic captions)
            for lang_code, subs in info.get('automatic_captions', {}).items():
                lang_name = subs[0].get('name', lang_code) if subs else lang_code
                # Check if this language is already present from manual subs
                if not any(d['code'] == lang_code for d in sub_list):
                    sub_list.append({'code': lang_code, 'name': f"{lang_name} (auto)"})

            # Sort the final list by language name
            sorted_subs = sorted(sub_list, key=lambda x: x['name'])
            return jsonify({'subtitles': sorted_subs})
            
    except Exception as e:
        print(f"Error getting subtitles for {video_id}: {e}")
        return jsonify({'error': 'Subtitle check failed.'}), 500

@app.route('/api/get_active_tasks')
@login_required
def api_get_active_tasks():
    active_tasks = [task for task in DOWNLOAD_TASKS.values() if task['status'] in ['queued', 'downloading']]
    return jsonify(active_tasks)

@app.route('/status/<task_id>')
@login_required
def task_status(task_id):
    return jsonify(DOWNLOAD_TASKS.get(task_id, {'status': 'not_found'}))

@app.route('/download_file/<path:filename>')
@login_required
def download_file(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename, as_attachment=True)

@app.route('/api/check_update')
def check_update():
    try:
        pypi_url = f"https://pypi.org/pypi/TubeZ/json"
        response = requests.get(pypi_url, timeout=5)
        response.raise_for_status()
        latest = response.json()['info']['version']
        update = parse_version(latest) > parse_version(__version__)
        return jsonify({'current_version': __version__, 'latest_version': latest, 'update_available': update})
    except: return jsonify({'error': 'Could not connect to update server.'}), 503

@app.route('/api/get_queue_count')
@login_required
def api_get_queue_count():
    """Returns the number of tasks currently in the queue or being downloaded."""
    count = DOWNLOAD_QUEUE.qsize() + sum(1 for task in DOWNLOAD_TASKS.values() if task['status'] == 'downloading')
    return jsonify({'count': count})

@app.route('/thumb/<file_hash>')
@login_required
def serve_thumbnail(file_hash):
    """Serves a privately stored thumbnail image."""
    # Security: Sanitize the hash to prevent path traversal attacks
    safe_hash = re.sub(r'[^a-zA-Z0-9]', '', file_hash)
    file_path = HISTORY_THUMB_CACHE / safe_hash
    
    if not file_path.is_file():
        return "Not Found", 404
        
    return send_from_directory(HISTORY_THUMB_CACHE, safe_hash, mimetype='image/jpeg')

@app.route('/api/delete_history_item', methods=['POST'])
@login_required
def delete_history_item():
    """Deletes a single item from the history and its associated thumbnail."""
    item_id = request.form.get('id')
    if not item_id:
        return jsonify({'success': False, 'error': 'No ID provided.'}), 400

    history = load_history()
    
    # Find the item to delete
    item_to_delete = next((item for item in history if item.get('id') == item_id), None)
    
    if item_to_delete:
        # Check if it has a local thumbnail that needs to be deleted
        thumbnail_path = item_to_delete.get('thumbnail', '')
        if thumbnail_path.startswith('/thumb/'):
            file_hash = thumbnail_path.split('/')[-1]
            thumb_file = HISTORY_THUMB_CACHE / file_hash
            if thumb_file.exists():
                try:
                    os.remove(thumb_file)
                except OSError as e:
                    print(f"WARNING: Could not delete thumbnail {thumb_file}: {e}")
    
    # Filter the history list to remove the item
    new_history = [item for item in history if item.get('id') != item_id]
    
    # Save the updated history
    with open(HISTORY_FILE, 'w') as f:
        json.dump(new_history, f, indent=4)
        
    flash("History item removed.", "success")
    return jsonify({'success': True})
