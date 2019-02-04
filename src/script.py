import argparse
import json
import re

from auth import get_authenticated_service
from log import *

_YOUTUBE_SCOPES = ['https://www.googleapis.com/auth/youtube']
_API_SERVICE_NAME = 'youtube'


def run(_playlist_title, _video_urls_file, _client_secret_file):
    logger.info('Execution starts...')
    try:
        # Using google_oauth2 to authorize the service...
        youtube = get_authenticated_service(_client_secret_file, _API_SERVICE_NAME, _YOUTUBE_SCOPES)

        # Creating the playlist with given title...
        playlist = _create_playlist(youtube, _playlist_title)

        # Extracting youtube video ids from the video url
        video_ids = _extract_videos(_video_urls_file)

        # Populating the playlist created above with given youtube videos
        process_track = _populate_playlist(youtube, playlist, video_ids)

        # Persisting the process status to tracker file...
        with open('./track/exec_stat.json', 'w') as outfile:
            json.dump({'playlist': playlist['name'], 'videos': process_track}, outfile)
    except RuntimeError:
        logger.exception('Execution has terminated with exception...')


def _populate_playlist(youtube, playlist, video_ids):
    logger.info('Attempting to populate playlist : ' + playlist.get('name'))

    tracker = []

    for vid_id in video_ids:
        body = {
            'snippet': {
                'playlistId': playlist['id'],
                'resourceId': {
                    'kind': 'youtube#video',
                    'videoId': vid_id,
                }
            }
        }

        try:
            playlists_insert_response = youtube.playlistItems().insert(
                part='snippet',
                body=body
            ).execute()

            tracker.append({
                'title': playlists_insert_response['snippet']['title'],
                'id': vid_id,
                'status': 'true'
            })

            logger.info('Successfully added video: ' + vid_id + ' to playlist')
        except Exception as e:
            logger.error('Could not add videos to this playlist..' + str(e))
            tracker.append({
                'title': '',
                'id': vid_id,
                'status': 'false'
            })
    return tracker


def _extract_videos(_video_urls_file):
    try:
        with open(_video_urls_file) as f:
            content = f.readlines()
        content = [x.strip() for x in content]
        videos = []
        for line in content:
            parts = line.split('/')
            parts.reverse()
            video_id = str(parts[0])
            if 'watch?v=' in video_id:
                video_id = re.search('watch\?v=(.+?)$', video_id).group(1)
            videos.append(video_id)

        return videos
    except Exception as e:
        raise RuntimeError('Failed to extract video ids from file...' + str(e))


def _create_playlist(youtube, _playlist_title):
    logger.info('Attempting to create playlist : ' + _playlist_title + ' if not exists...')
    body = {
        'snippet': {
            'title': _playlist_title,
            'description': 'This playlist is created via Youtube Data API.'
        },
        'status': {
            'privacyStatus': 'private'
        }
    }

    try:
        playlists_create_response = youtube.playlists().insert(
            part='snippet,status',
            body=body
        ).execute()
    except Exception as e:
        raise RuntimeError('Could not create this playlist..' + str(e))

    logger.info('Playlist is created with ID: %s' % playlists_create_response['id'])
    return {
        'name': _playlist_title,
        'id': playlists_create_response['id']
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Add videos to youtube playlist')

    # Optional arguments...
    parser.add_argument('-d', '--description',
                        help='The description of the playlist',
                        default='This playlist is created via Youtube data API')

    # Mandatory arguments...
    requiredNamed = parser.add_argument_group('required named arguments')
    requiredNamed.add_argument('-t', '--title',
                               help='The title of the playlist.',
                               required=True)

    requiredNamed.add_argument('-l', '--v_links',
                               help='File containing youtube URLs',
                               required=True)

    requiredNamed.add_argument('-s', '--client_secret',
                               help='File containing client secret',
                               required=True)

    args = parser.parse_args()
    run(args.title, args.v_links, args.client_secret)
