"""
Sony Walkman MP3 Playlist Generator
Generates M3U playlists (pure filenames, UTF-8) based on Artist, Album, 
Latest Import, or Random selection. Optimized for Sony Walkman devices.
"""

import os
import sys
import random
import shutil
import logging
import argparse
from datetime import timedelta
from mutagen.mp3 import MP3
from mutagen.id3 import ID3NoHeaderError

# 配置全局日志格式
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s"
)
logger = logging.getLogger(__name__)

def get_mp3_files(directory):
    """扫描目录，返回所有 MP3 文件的绝对路径列表。"""
    mp3_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith('.mp3'):
                mp3_files.append(os.path.join(root, file))
    return mp3_files

def write_m3u(filepath, tracks):
    """将歌曲列表写入 M3U 文件。针对索尼 Walkman 优化：强制 UTF-8 编码，且只写入纯文件名。"""
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write("#EXTM3U\n")
        for track in tracks:
            f.write(f"{os.path.basename(track)}\n")
    logger.info(f"✅ Generated: {filepath} ({len(tracks)} tracks)")

def deploy_playlists(output_dir, target_music_dir):
    """将生成的播放列表强制拷贝到指定的音乐目录中，自动跳过源文件与目标相同的情况。"""
    if not os.path.isdir(target_music_dir):
        logger.warning(f"Target music directory '{target_music_dir}' does not exist. Skipping deploy.")
        return

    deployed_count = 0
    for file in os.listdir(output_dir):
        if file.lower().endswith('.m3u'):
            src_path = os.path.join(output_dir, file)
            dst_path = os.path.join(target_music_dir, file)
            
            # 核心修复：如果源路径和目标路径是同一个文件，直接跳过拷贝
            if os.path.abspath(src_path) == os.path.abspath(dst_path):
                continue
                
            shutil.copy2(src_path, dst_path)
            deployed_count += 1
            
    logger.info(f"🚀 Successfully deployed {deployed_count} playlist(s) to '{target_music_dir}'.")

def create_latest_playlist(mp3_files, output_dir, limit=100):
    """按文件修改时间排序，生成最新导入的播放列表。"""
    sorted_files = sorted(mp3_files, key=os.path.getmtime, reverse=True)
    latest_tracks = sorted_files[:limit]
    m3u_path = os.path.join(output_dir, f"Latest_{limit}.m3u")
    write_m3u(m3u_path, latest_tracks)

def create_random_playlist(mp3_files, output_dir, limit=50):
    """随机抽取歌曲，生成随机播放列表。支持自定义数量。"""
    # 如果指定的数量大于总歌曲数，则限制为总歌曲数
    if len(mp3_files) < limit:
        limit = len(mp3_files)
        
    random_tracks = random.sample(mp3_files, limit)
    # 动态生成文件名，例如 Random_100.m3u
    m3u_path = os.path.join(output_dir, f"Random_{limit}.m3u")
    write_m3u(m3u_path, random_tracks)

def create_artist_playlists(mp3_files, output_dir, top_n=None):
    """按演唱者分类，生成多个播放列表。"""
    playlists = {}
    for file_path in mp3_files:
        try:
            audio = MP3(file_path)
            name = str(audio.tags.get('TPE1')).strip() if audio.tags.get('TPE1') else "Unknown_Artist"
        except (ID3NoHeaderError, Exception):
            name = "Unknown_Artist"
        playlists.setdefault(name, []).append(file_path)
        
    if top_n is not None:
        sorted_playlists = sorted(playlists.items(), key=lambda x: len(x[1]), reverse=True)[:top_n]
        playlists = dict(sorted_playlists)
        logger.info(f"🎤 Top {top_n} Artists selected based on track count.")
        
    for name, tracks in playlists.items():
        safe_name = "".join([c for c in name if c not in r'\/:*?"<>|']).strip() or "Unknown_Artist"
        m3u_path = os.path.join(output_dir, f"{safe_name}.m3u")
        write_m3u(m3u_path, sorted(tracks))

def create_album_playlists(mp3_files, output_dir, top_n=None):
    """按专辑分类，生成多个播放列表。"""
    playlists = {}
    for file_path in mp3_files:
        try:
            audio = MP3(file_path)
            name = str(audio.tags.get('TALB')).strip() if audio.tags.get('TALB') else "Unknown_Album"
        except (ID3NoHeaderError, Exception):
            name = "Unknown_Album"
        playlists.setdefault(name, []).append(file_path)
        
    if top_n is not None:
        sorted_playlists = sorted(playlists.items(), key=lambda x: len(x[1]), reverse=True)[:top_n]
        playlists = dict(sorted_playlists)
        logger.info(f"💿 Top {top_n} Albums selected based on track count.")
        
    for name, tracks in playlists.items():
        safe_name = "".join([c for c in name if c not in r'\/:*?"<>|']).strip() or "Unknown_Album"
        m3u_path = os.path.join(output_dir, f"{safe_name}.m3u")
        write_m3u(m3u_path, sorted(tracks))

def show_music_stats(mp3_files):
    """统计并打印音乐库的详细信息。"""
    total_size = 0
    total_duration = 0
    artists = set()
    albums = set()
    errors = 0
    
    for file_path in mp3_files:
        total_size += os.path.getsize(file_path)
        try:
            audio = MP3(file_path)
            total_duration += audio.info.length
            artist = audio.tags.get('TPE1')
            album = audio.tags.get('TALB')
            if artist: artists.add(str(artist).strip())
            if album: albums.add(str(album).strip())
        except (ID3NoHeaderError, Exception):
            errors += 1
            
    size_mb = total_size / (1024 * 1024)
    formatted_time = str(timedelta(seconds=int(total_duration)))
    
    logger.info("\n📊 Music Library Statistics:")
    logger.info("-" * 30)
    logger.info(f"🎵 Total Tracks: {len(mp3_files)}")
    logger.info(f"💾 Total Size:   {size_mb:.2f} MB")
    logger.info(f"⏱️ Total Length: {formatted_time}")
    logger.info(f"🎤 Artists:      {len(artists)}")
    logger.info(f"💿 Albums:       {len(albums)}")
    if errors > 0:
        logger.warning(f"⚠️ Read Errors:  {errors}")
    logger.info("-" * 30)

def main():
    """程序主入口函数。"""
    parser = argparse.ArgumentParser(
        description="🎵 Sony Walkman MP3 Playlist Generator: Generates M3U playlists or shows library stats.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    parser.add_argument("directory", help="The root directory path containing MP3 files to scan.")
    parser.add_argument("-o", "--output", help="Output directory for the generated M3U playlists.", default=None)
    parser.add_argument("-n", "--limit", type=int, metavar="N",
                        help="Generate playlists only for the top N Artists or Albums (sorted by track count).")
    parser.add_argument("--deploy", action="store_true", 
                        help="Automatically copy generated playlists to the music directory, overwriting existing ones.")
    
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument("--latest", action="store_true", help="Generate a playlist of the most recently added songs.")
    mode_group.add_argument("--artist", action="store_true", help="Generate separate playlists grouped by Artist tag.")
    mode_group.add_argument("--album", action="store_true", help="Generate separate playlists grouped by Album tag.")
    mode_group.add_argument("--random", action="store_true", help="Generate a playlist with randomly selected songs.")
    mode_group.add_argument("--stats", action="store_true", help="Scan the directory and display music library statistics.")
    
    args = parser.parse_args()
    
    logger.info(f"🔍 Scanning directory: {args.directory}")
    mp3_files = get_mp3_files(args.directory)
    
    if not mp3_files:
        logger.warning("No MP3 files found in the specified directory.")
        sys.exit(1)
        
    logger.info(f"🎶 Found {len(mp3_files)} MP3 files.")
    
    if args.stats:
        show_music_stats(mp3_files)
        sys.exit(0)
        
    save_dir = args.output if args.output else args.directory
    if not os.path.isdir(save_dir):
        os.makedirs(save_dir)
        
    logger.info("Generating playlist...")
    
    # 处理 --latest 和 --random 的数量限制 (Sony Walkman 最大支持 999 首)
    if args.latest:
        latest_limit = 100 
        if args.limit is not None:
            if args.limit > 999:
                logger.warning(f"⚠️ Sony Walkman limit detected! Capping latest tracks from {args.limit} to 999.")
                latest_limit = 999
            else:
                latest_limit = args.limit
        create_latest_playlist(mp3_files, save_dir, limit=latest_limit)
        
    elif args.random:
        random_limit = 50 
        if args.limit is not None:
            if args.limit > 999:
                logger.warning(f"⚠️ Sony Walkman limit detected! Capping random tracks from {args.limit} to 999.")
                random_limit = 999
            else:
                random_limit = args.limit
        create_random_playlist(mp3_files, save_dir, limit=random_limit)
        
    elif args.artist:
        create_artist_playlists(mp3_files, save_dir, top_n=args.limit)
        
    elif args.album:
        create_album_playlists(mp3_files, save_dir, top_n=args.limit)
        
    if args.deploy:
        deploy_playlists(save_dir, args.directory)

if __name__ == "__main__":
    main()