# plexpy

<div align="left">
    <a href="https://speakeasyapi.dev/"><img src="https://custom-icon-badges.demolab.com/badge/-Built%20By%20Speakeasy-212015?style=for-the-badge&logoColor=FBE331&logo=speakeasy&labelColor=545454" /></a>
    <a href="https://opensource.org/licenses/MIT">
        <img src="https://img.shields.io/badge/License-MIT-blue.svg" style="width: 100px; height: 28px;" />
    </a>
</div>

<!-- Start Summary [summary] -->
## Summary

Plex-API: An Open API Spec for interacting with Plex.tv and Plex Media Server

# Plex Media Server OpenAPI Specification

An Open Source OpenAPI Specification for Plex Media Server

Automation and SDKs provided by [Speakeasy](https://speakeasyapi.dev/)

## Documentation

[API Documentation](https://plexapi.dev)

## SDKs

The following SDKs are generated from the OpenAPI Specification. They are automatically generated and may not be fully tested. If you find any issues, please open an issue on the [main specification Repository](https://github.com/LukeHagar/plex-api-spec).

| Language              | Repository                                        | Releases                                                                                         | Other                                                   |
| --------------------- | ------------------------------------------------- | ------------------------------------------------------------------------------------------------ | ------------------------------------------------------- |
| Python                | [GitHub](https://github.com/LukeHagar/plexpy)     | [PyPI](https://pypi.org/project/plex-api-client/)                                                | -                                                       |
| JavaScript/TypeScript | [GitHub](https://github.com/LukeHagar/plexjs)     | [NPM](https://www.npmjs.com/package/@lukehagar/plexjs) \ [JSR](https://jsr.io/@lukehagar/plexjs) | -                                                       |
| Go                    | [GitHub](https://github.com/LukeHagar/plexgo)     | [Releases](https://github.com/LukeHagar/plexgo/releases)                                         | [GoDoc](https://pkg.go.dev/github.com/LukeHagar/plexgo) |
| Ruby                  | [GitHub](https://github.com/LukeHagar/plexruby)   | [Releases](https://github.com/LukeHagar/plexruby/releases)                                       | -                                                       |
| Swift                 | [GitHub](https://github.com/LukeHagar/plexswift)  | [Releases](https://github.com/LukeHagar/plexswift/releases)                                      | -                                                       |
| PHP                   | [GitHub](https://github.com/LukeHagar/plexphp)    | [Releases](https://github.com/LukeHagar/plexphp/releases)                                        | -                                                       |
| Java                  | [GitHub](https://github.com/LukeHagar/plexjava)   | [Releases](https://github.com/LukeHagar/plexjava/releases)                                       | -                                                       |
| C#                    | [GitHub](https://github.com/LukeHagar/plexcsharp) | [Releases](https://github.com/LukeHagar/plexcsharp/releases)                                     | -
<!-- End Summary [summary] -->

<!-- Start Table of Contents [toc] -->
## Table of Contents
<!-- $toc-max-depth=2 -->
* [plexpy](https://github.com/LukeHagar/plexpy/blob/master/./#plexpy)
* [Plex Media Server OpenAPI Specification](https://github.com/LukeHagar/plexpy/blob/master/./#plex-media-server-openapi-specification)
  * [Documentation](https://github.com/LukeHagar/plexpy/blob/master/./#documentation)
  * [SDKs](https://github.com/LukeHagar/plexpy/blob/master/./#sdks)
  * [SDK Installation](https://github.com/LukeHagar/plexpy/blob/master/./#sdk-installation)
  * [IDE Support](https://github.com/LukeHagar/plexpy/blob/master/./#ide-support)
  * [SDK Example Usage](https://github.com/LukeHagar/plexpy/blob/master/./#sdk-example-usage)
  * [Available Resources and Operations](https://github.com/LukeHagar/plexpy/blob/master/./#available-resources-and-operations)
  * [File uploads](https://github.com/LukeHagar/plexpy/blob/master/./#file-uploads)
  * [Retries](https://github.com/LukeHagar/plexpy/blob/master/./#retries)
  * [Error Handling](https://github.com/LukeHagar/plexpy/blob/master/./#error-handling)
  * [Server Selection](https://github.com/LukeHagar/plexpy/blob/master/./#server-selection)
  * [Custom HTTP Client](https://github.com/LukeHagar/plexpy/blob/master/./#custom-http-client)
  * [Authentication](https://github.com/LukeHagar/plexpy/blob/master/./#authentication)
  * [Resource Management](https://github.com/LukeHagar/plexpy/blob/master/./#resource-management)
  * [Debugging](https://github.com/LukeHagar/plexpy/blob/master/./#debugging)
* [Development](https://github.com/LukeHagar/plexpy/blob/master/./#development)
  * [Maturity](https://github.com/LukeHagar/plexpy/blob/master/./#maturity)
  * [Contributions](https://github.com/LukeHagar/plexpy/blob/master/./#contributions)

<!-- End Table of Contents [toc] -->

<!-- Start SDK Installation [installation] -->
## SDK Installation

> [!NOTE]
> **Python version upgrade policy**
>
> Once a Python version reaches its [official end of life date](https://devguide.python.org/versions/), a 3-month grace period is provided for users to upgrade. Following this grace period, the minimum python version supported in the SDK will be updated.

The SDK can be installed with *uv*, *pip*, or *poetry* package managers.

### uv

*uv* is a fast Python package installer and resolver, designed as a drop-in replacement for pip and pip-tools. It's recommended for its speed and modern Python tooling capabilities.

```bash
uv add plex-api-client
```

### PIP

*PIP* is the default package installer for Python, enabling easy installation and management of packages from PyPI via the command line.

```bash
pip install plex-api-client
```

### Poetry

*Poetry* is a modern tool that simplifies dependency management and package publishing by using a single `pyproject.toml` file to handle project metadata and dependencies.

```bash
poetry add plex-api-client
```

### Shell and script usage with `uv`

You can use this SDK in a Python shell with [uv](https://docs.astral.sh/uv/) and the `uvx` command that comes with it like so:

```shell
uvx --from plex-api-client python
```

It's also possible to write a standalone Python script without needing to set up a whole project like so:

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "plex-api-client",
# ]
# ///

from plex_api_client import PlexAPI

sdk = PlexAPI(
  # SDK arguments
)

# Rest of script here...
```

Once that is saved to a file, you can run it with `uv run script.py` where
`script.py` can be replaced with the actual file name.
<!-- End SDK Installation [installation] -->

<!-- Start IDE Support [idesupport] -->
## IDE Support

### PyCharm

Generally, the SDK will work well with most IDEs out of the box. However, when using PyCharm, you can enjoy much better integration with Pydantic by installing an additional plugin.

- [PyCharm Pydantic Plugin](https://docs.pydantic.dev/latest/integrations/pycharm/)
<!-- End IDE Support [idesupport] -->

<!-- Start SDK Example Usage [usage] -->
## SDK Example Usage

### Example

```python
# Synchronous Example
from plex_api_client import PlexAPI


with PlexAPI(
    access_token="<YOUR_API_KEY_HERE>",
) as plex_api:

    res = plex_api.server.get_server_capabilities()

    assert res.object is not None

    # Handle response
    print(res.object)
```

</br>

The same SDK client can also be used to make asynchronous requests by importing asyncio.
```python
# Asynchronous Example
import asyncio
from plex_api_client import PlexAPI

async def main():

    async with PlexAPI(
        access_token="<YOUR_API_KEY_HERE>",
    ) as plex_api:

        res = await plex_api.server.get_server_capabilities_async()

        assert res.object is not None

        # Handle response
        print(res.object)

asyncio.run(main())
```
<!-- End SDK Example Usage [usage] -->

<!-- Start Available Resources and Operations [operations] -->
## Available Resources and Operations

<details open>
<summary>Available methods</summary>

### [activities](https://github.com/LukeHagar/plexpy/blob/master/./docs/sdks/activities/README.md)

* [get_server_activities](https://github.com/LukeHagar/plexpy/blob/master/./docs/sdks/activities/README.md#get_server_activities) - Get Server Activities
* [cancel_server_activities](https://github.com/LukeHagar/plexpy/blob/master/./docs/sdks/activities/README.md#cancel_server_activities) - Cancel Server Activities

### [authentication](https://github.com/LukeHagar/plexpy/blob/master/./docs/sdks/authentication/README.md)

* [get_transient_token](https://github.com/LukeHagar/plexpy/blob/master/./docs/sdks/authentication/README.md#get_transient_token) - Get a Transient Token
* [get_source_connection_information](https://github.com/LukeHagar/plexpy/blob/master/./docs/sdks/authentication/README.md#get_source_connection_information) - Get Source Connection Information
* [get_token_details](https://github.com/LukeHagar/plexpy/blob/master/./docs/sdks/authentication/README.md#get_token_details) - Get Token Details
* [post_users_sign_in_data](https://github.com/LukeHagar/plexpy/blob/master/./docs/sdks/authentication/README.md#post_users_sign_in_data) - Get User Sign In Data

### [butler](https://github.com/LukeHagar/plexpy/blob/master/./docs/sdks/butler/README.md)

* [get_butler_tasks](https://github.com/LukeHagar/plexpy/blob/master/./docs/sdks/butler/README.md#get_butler_tasks) - Get Butler tasks
* [start_all_tasks](https://github.com/LukeHagar/plexpy/blob/master/./docs/sdks/butler/README.md#start_all_tasks) - Start all Butler tasks
* [stop_all_tasks](https://github.com/LukeHagar/plexpy/blob/master/./docs/sdks/butler/README.md#stop_all_tasks) - Stop all Butler tasks
* [start_task](https://github.com/LukeHagar/plexpy/blob/master/./docs/sdks/butler/README.md#start_task) - Start a single Butler task
* [stop_task](https://github.com/LukeHagar/plexpy/blob/master/./docs/sdks/butler/README.md#stop_task) - Stop a single Butler task

### [hubs](https://github.com/LukeHagar/plexpy/blob/master/./docs/sdks/hubs/README.md)

* [get_global_hubs](https://github.com/LukeHagar/plexpy/blob/master/./docs/sdks/hubs/README.md#get_global_hubs) - Get Global Hubs
* [get_recently_added](https://github.com/LukeHagar/plexpy/blob/master/./docs/sdks/hubs/README.md#get_recently_added) - Get Recently Added
* [get_library_hubs](https://github.com/LukeHagar/plexpy/blob/master/./docs/sdks/hubs/README.md#get_library_hubs) - Get library specific hubs

### [library](https://github.com/LukeHagar/plexpy/blob/master/./docs/sdks/library/README.md)

* [get_file_hash](https://github.com/LukeHagar/plexpy/blob/master/./docs/sdks/library/README.md#get_file_hash) - Get Hash Value
* [get_recently_added_library](https://github.com/LukeHagar/plexpy/blob/master/./docs/sdks/library/README.md#get_recently_added_library) - Get Recently Added
* [get_all_libraries](https://github.com/LukeHagar/plexpy/blob/master/./docs/sdks/library/README.md#get_all_libraries) - Get All Libraries
* [get_library_details](https://github.com/LukeHagar/plexpy/blob/master/./docs/sdks/library/README.md#get_library_details) - Get Library Details
* [delete_library](https://github.com/LukeHagar/plexpy/blob/master/./docs/sdks/library/README.md#delete_library) - Delete Library Section
* [get_library_items](https://github.com/LukeHagar/plexpy/blob/master/./docs/sdks/library/README.md#get_library_items) - Get Library Items
* [get_library_sections_all](https://github.com/LukeHagar/plexpy/blob/master/./docs/sdks/library/README.md#get_library_sections_all) - Get Library section media by tag ALL
* [get_refresh_library_metadata](https://github.com/LukeHagar/plexpy/blob/master/./docs/sdks/library/README.md#get_refresh_library_metadata) - Refresh Metadata Of The Library
* [get_search_library](https://github.com/LukeHagar/plexpy/blob/master/./docs/sdks/library/README.md#get_search_library) - Search Library
* [get_genres_library](https://github.com/LukeHagar/plexpy/blob/master/./docs/sdks/library/README.md#get_genres_library) - Get Genres of library media
* [get_countries_library](https://github.com/LukeHagar/plexpy/blob/master/./docs/sdks/library/README.md#get_countries_library) - Get Countries of library media
* [get_actors_library](https://github.com/LukeHagar/plexpy/blob/master/./docs/sdks/library/README.md#get_actors_library) - Get Actors of library media
* [get_search_all_libraries](https://github.com/LukeHagar/plexpy/blob/master/./docs/sdks/library/README.md#get_search_all_libraries) - Search All Libraries
* [get_media_meta_data](https://github.com/LukeHagar/plexpy/blob/master/./docs/sdks/library/README.md#get_media_meta_data) - Get Media Metadata
* [get_media_arts](https://github.com/LukeHagar/plexpy/blob/master/./docs/sdks/library/README.md#get_media_arts) - Get Media Background Artwork
* [post_media_arts](https://github.com/LukeHagar/plexpy/blob/master/./docs/sdks/library/README.md#post_media_arts) - Upload Media Background Artwork
* [get_media_posters](https://github.com/LukeHagar/plexpy/blob/master/./docs/sdks/library/README.md#get_media_posters) - Get Media Posters
* [post_media_poster](https://github.com/LukeHagar/plexpy/blob/master/./docs/sdks/library/README.md#post_media_poster) - Upload Media Poster
* [get_metadata_children](https://github.com/LukeHagar/plexpy/blob/master/./docs/sdks/library/README.md#get_metadata_children) - Get Items Children
* [get_top_watched_content](https://github.com/LukeHagar/plexpy/blob/master/./docs/sdks/library/README.md#get_top_watched_content) - Get Top Watched Content

### [log](https://github.com/LukeHagar/plexpy/blob/master/./docs/sdks/log/README.md)

* [log_line](https://github.com/LukeHagar/plexpy/blob/master/./docs/sdks/log/README.md#log_line) - Logging a single line message.
* [log_multi_line](https://github.com/LukeHagar/plexpy/blob/master/./docs/sdks/log/README.md#log_multi_line) - Logging a multi-line message
* [enable_paper_trail](https://github.com/LukeHagar/plexpy/blob/master/./docs/sdks/log/README.md#enable_paper_trail) - Enabling Papertrail

### [media](https://github.com/LukeHagar/plexpy/blob/master/./docs/sdks/media/README.md)

* [mark_played](https://github.com/LukeHagar/plexpy/blob/master/./docs/sdks/media/README.md#mark_played) - Mark Media Played
* [mark_unplayed](https://github.com/LukeHagar/plexpy/blob/master/./docs/sdks/media/README.md#mark_unplayed) - Mark Media Unplayed
* [update_play_progress](https://github.com/LukeHagar/plexpy/blob/master/./docs/sdks/media/README.md#update_play_progress) - Update Media Play Progress
* [get_banner_image](https://github.com/LukeHagar/plexpy/blob/master/./docs/sdks/media/README.md#get_banner_image) - Get Banner Image
* [get_thumb_image](https://github.com/LukeHagar/plexpy/blob/master/./docs/sdks/media/README.md#get_thumb_image) - Get Thumb Image

### [playlists](https://github.com/LukeHagar/plexpy/blob/master/./docs/sdks/playlists/README.md)

* [create_playlist](https://github.com/LukeHagar/plexpy/blob/master/./docs/sdks/playlists/README.md#create_playlist) - Create a Playlist
* [get_playlists](https://github.com/LukeHagar/plexpy/blob/master/./docs/sdks/playlists/README.md#get_playlists) - Get All Playlists
* [get_playlist](https://github.com/LukeHagar/plexpy/blob/master/./docs/sdks/playlists/README.md#get_playlist) - Retrieve Playlist
* [delete_playlist](https://github.com/LukeHagar/plexpy/blob/master/./docs/sdks/playlists/README.md#delete_playlist) - Deletes a Playlist
* [update_playlist](https://github.com/LukeHagar/plexpy/blob/master/./docs/sdks/playlists/README.md#update_playlist) - Update a Playlist
* [get_playlist_contents](https://github.com/LukeHagar/plexpy/blob/master/./docs/sdks/playlists/README.md#get_playlist_contents) - Retrieve Playlist Contents
* [clear_playlist_contents](https://github.com/LukeHagar/plexpy/blob/master/./docs/sdks/playlists/README.md#clear_playlist_contents) - Delete Playlist Contents
* [add_playlist_contents](https://github.com/LukeHagar/plexpy/blob/master/./docs/sdks/playlists/README.md#add_playlist_contents) - Adding to a Playlist
* [upload_playlist](https://github.com/LukeHagar/plexpy/blob/master/./docs/sdks/playlists/README.md#upload_playlist) - Upload Playlist

### [plex](https://github.com/LukeHagar/plexpy/blob/master/./docs/sdks/plex/README.md)

* [get_companions_data](https://github.com/LukeHagar/plexpy/blob/master/./docs/sdks/plex/README.md#get_companions_data) - Get Companions Data
* [get_user_friends](https://github.com/LukeHagar/plexpy/blob/master/./docs/sdks/plex/README.md#get_user_friends) - Get list of friends of the user logged in
* [get_geo_data](https://github.com/LukeHagar/plexpy/blob/master/./docs/sdks/plex/README.md#get_geo_data) - Get Geo Data
* [get_home_data](https://github.com/LukeHagar/plexpy/blob/master/./docs/sdks/plex/README.md#get_home_data) - Get Plex Home Data
* [get_server_resources](https://github.com/LukeHagar/plexpy/blob/master/./docs/sdks/plex/README.md#get_server_resources) - Get Server Resources
* [get_pin](https://github.com/LukeHagar/plexpy/blob/master/./docs/sdks/plex/README.md#get_pin) - Get a Pin
* [get_token_by_pin_id](https://github.com/LukeHagar/plexpy/blob/master/./docs/sdks/plex/README.md#get_token_by_pin_id) - Get Access Token by PinId


### [search](https://github.com/LukeHagar/plexpy/blob/master/./docs/sdks/search/README.md)

* [perform_search](https://github.com/LukeHagar/plexpy/blob/master/./docs/sdks/search/README.md#perform_search) - Perform a search
* [perform_voice_search](https://github.com/LukeHagar/plexpy/blob/master/./docs/sdks/search/README.md#perform_voice_search) - Perform a voice search
* [get_search_results](https://github.com/LukeHagar/plexpy/blob/master/./docs/sdks/search/README.md#get_search_results) - Get Search Results

### [server](https://github.com/LukeHagar/plexpy/blob/master/./docs/sdks/server/README.md)

* [get_server_capabilities](https://github.com/LukeHagar/plexpy/blob/master/./docs/sdks/server/README.md#get_server_capabilities) - Get Server Capabilities
* [get_server_preferences](https://github.com/LukeHagar/plexpy/blob/master/./docs/sdks/server/README.md#get_server_preferences) - Get Server Preferences
* [get_available_clients](https://github.com/LukeHagar/plexpy/blob/master/./docs/sdks/server/README.md#get_available_clients) - Get Available Clients
* [get_devices](https://github.com/LukeHagar/plexpy/blob/master/./docs/sdks/server/README.md#get_devices) - Get Devices
* [get_server_identity](https://github.com/LukeHagar/plexpy/blob/master/./docs/sdks/server/README.md#get_server_identity) - Get Server Identity
* [get_my_plex_account](https://github.com/LukeHagar/plexpy/blob/master/./docs/sdks/server/README.md#get_my_plex_account) - Get MyPlex Account
* [get_resized_photo](https://github.com/LukeHagar/plexpy/blob/master/./docs/sdks/server/README.md#get_resized_photo) - Get a Resized Photo
* [get_media_providers](https://github.com/LukeHagar/plexpy/blob/master/./docs/sdks/server/README.md#get_media_providers) - Get Media Providers
* [get_server_list](https://github.com/LukeHagar/plexpy/blob/master/./docs/sdks/server/README.md#get_server_list) - Get Server List

### [sessions](https://github.com/LukeHagar/plexpy/blob/master/./docs/sdks/sessions/README.md)

* [get_sessions](https://github.com/LukeHagar/plexpy/blob/master/./docs/sdks/sessions/README.md#get_sessions) - Get Active Sessions
* [get_session_history](https://github.com/LukeHagar/plexpy/blob/master/./docs/sdks/sessions/README.md#get_session_history) - Get Session History
* [get_transcode_sessions](https://github.com/LukeHagar/plexpy/blob/master/./docs/sdks/sessions/README.md#get_transcode_sessions) - Get Transcode Sessions
* [stop_transcode_session](https://github.com/LukeHagar/plexpy/blob/master/./docs/sdks/sessions/README.md#stop_transcode_session) - Stop a Transcode Session

### [statistics](https://github.com/LukeHagar/plexpy/blob/master/./docs/sdks/statistics/README.md)

* [get_statistics](https://github.com/LukeHagar/plexpy/blob/master/./docs/sdks/statistics/README.md#get_statistics) - Get Media Statistics
* [get_resources_statistics](https://github.com/LukeHagar/plexpy/blob/master/./docs/sdks/statistics/README.md#get_resources_statistics) - Get Resources Statistics
* [get_bandwidth_statistics](https://github.com/LukeHagar/plexpy/blob/master/./docs/sdks/statistics/README.md#get_bandwidth_statistics) - Get Bandwidth Statistics

### [updater](https://github.com/LukeHagar/plexpy/blob/master/./docs/sdks/updater/README.md)

* [get_update_status](https://github.com/LukeHagar/plexpy/blob/master/./docs/sdks/updater/README.md#get_update_status) - Querying status of updates
* [check_for_updates](https://github.com/LukeHagar/plexpy/blob/master/./docs/sdks/updater/README.md#check_for_updates) - Checking for updates
* [apply_updates](https://github.com/LukeHagar/plexpy/blob/master/./docs/sdks/updater/README.md#apply_updates) - Apply Updates

### [users](https://github.com/LukeHagar/plexpy/blob/master/./docs/sdks/users/README.md)

* [get_users](https://github.com/LukeHagar/plexpy/blob/master/./docs/sdks/users/README.md#get_users) - Get list of all connected users

### [video](https://github.com/LukeHagar/plexpy/blob/master/./docs/sdks/video/README.md)

* [get_timeline](https://github.com/LukeHagar/plexpy/blob/master/./docs/sdks/video/README.md#get_timeline) - Get the timeline for a media item
* [start_universal_transcode](https://github.com/LukeHagar/plexpy/blob/master/./docs/sdks/video/README.md#start_universal_transcode) - Start Universal Transcode

### [watchlist](https://github.com/LukeHagar/plexpy/blob/master/./docs/sdks/watchlist/README.md)

* [get_watch_list](https://github.com/LukeHagar/plexpy/blob/master/./docs/sdks/watchlist/README.md#get_watch_list) - Get User Watchlist

</details>
<!-- End Available Resources and Operations [operations] -->

<!-- Start File uploads [file-upload] -->
## File uploads

Certain SDK methods accept file objects as part of a request body or multi-part request. It is possible and typically recommended to upload files as a stream rather than reading the entire contents into memory. This avoids excessive memory consumption and potentially crashing with out-of-memory errors when working with very large files. The following example demonstrates how to attach a file stream to a request.

> [!TIP]
>
> For endpoints that handle file uploads bytes arrays can also be used. However, using streams is recommended for large files.
>

```python
from plex_api_client import PlexAPI


with PlexAPI(
    access_token="<YOUR_API_KEY_HERE>",
) as plex_api:

    res = plex_api.library.post_media_arts(rating_key=2268, url="https://api.mediux.pro/assets/fcfdc487-dd07-4993-a0c1-0a3015362e5b")

    assert res is not None

    # Handle response
    print(res)

```
<!-- End File uploads [file-upload] -->

<!-- Start Retries [retries] -->
## Retries

Some of the endpoints in this SDK support retries. If you use the SDK without any configuration, it will fall back to the default retry strategy provided by the API. However, the default retry strategy can be overridden on a per-operation basis, or across the entire SDK.

To change the default retry strategy for a single API call, simply provide a `RetryConfig` object to the call:
```python
from plex_api_client import PlexAPI
from plex_api_client.utils import BackoffStrategy, RetryConfig


with PlexAPI(
    access_token="<YOUR_API_KEY_HERE>",
) as plex_api:

    res = plex_api.server.get_server_capabilities(,
        RetryConfig("backoff", BackoffStrategy(1, 50, 1.1, 100), False))

    assert res.object is not None

    # Handle response
    print(res.object)

```

If you'd like to override the default retry strategy for all operations that support retries, you can use the `retry_config` optional parameter when initializing the SDK:
```python
from plex_api_client import PlexAPI
from plex_api_client.utils import BackoffStrategy, RetryConfig


with PlexAPI(
    retry_config=RetryConfig("backoff", BackoffStrategy(1, 50, 1.1, 100), False),
    access_token="<YOUR_API_KEY_HERE>",
) as plex_api:

    res = plex_api.server.get_server_capabilities()

    assert res.object is not None

    # Handle response
    print(res.object)

```
<!-- End Retries [retries] -->

<!-- Start Error Handling [errors] -->
## Error Handling

[`PlexAPIError`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/plexapierror.py) is the base class for all HTTP error responses. It has the following properties:

| Property           | Type             | Description                                                                             |
| ------------------ | ---------------- | --------------------------------------------------------------------------------------- |
| `err.message`      | `str`            | Error message                                                                           |
| `err.status_code`  | `int`            | HTTP response status code eg `404`                                                      |
| `err.headers`      | `httpx.Headers`  | HTTP response headers                                                                   |
| `err.body`         | `str`            | HTTP body. Can be empty string if no body is returned.                                  |
| `err.raw_response` | `httpx.Response` | Raw HTTP response                                                                       |
| `err.data`         |                  | Optional. Some errors may contain structured data. [See Error Classes](https://github.com/LukeHagar/plexpy/blob/master/./#error-classes). |

### Example
```python
from plex_api_client import PlexAPI
from plex_api_client.models import errors


with PlexAPI(
    access_token="<YOUR_API_KEY_HERE>",
) as plex_api:
    res = None
    try:

        res = plex_api.server.get_server_capabilities()

        assert res.object is not None

        # Handle response
        print(res.object)


    except errors.PlexAPIError as e:
        # The base class for HTTP error responses
        print(e.message)
        print(e.status_code)
        print(e.body)
        print(e.headers)
        print(e.raw_response)

        # Depending on the method different errors may be thrown
        if isinstance(e, errors.GetServerCapabilitiesBadRequest):
            print(e.data.errors)  # Optional[List[errors.Errors]]
            print(e.data.raw_response)  # Optional[httpx.Response]
```

### Error Classes
**Primary error:**
* [`PlexAPIError`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/plexapierror.py): The base class for HTTP error responses.

<details><summary>Less common errors (161)</summary>

<br />

**Network errors:**
* [`httpx.RequestError`](https://www.python-httpx.org/exceptions/#httpx.RequestError): Base class for request errors.
    * [`httpx.ConnectError`](https://www.python-httpx.org/exceptions/#httpx.ConnectError): HTTP client was unable to make a request to a server.
    * [`httpx.TimeoutException`](https://www.python-httpx.org/exceptions/#httpx.TimeoutException): HTTP request timed out.


**Inherit from [`PlexAPIError`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/plexapierror.py)**:
* [`GetServerCapabilitiesBadRequest`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/getservercapabilitiesbadrequest.py): Bad Request - A parameter was not specified, or was specified incorrectly. Status code `400`. Applicable to 1 of 84 methods.*
* [`GetServerPreferencesBadRequest`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/getserverpreferencesbadrequest.py): Bad Request - A parameter was not specified, or was specified incorrectly. Status code `400`. Applicable to 1 of 84 methods.*
* [`GetAvailableClientsBadRequest`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/getavailableclientsbadrequest.py): Bad Request - A parameter was not specified, or was specified incorrectly. Status code `400`. Applicable to 1 of 84 methods.*
* [`GetDevicesBadRequest`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/getdevicesbadrequest.py): Bad Request - A parameter was not specified, or was specified incorrectly. Status code `400`. Applicable to 1 of 84 methods.*
* [`GetMyPlexAccountBadRequest`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/getmyplexaccountbadrequest.py): Bad Request - A parameter was not specified, or was specified incorrectly. Status code `400`. Applicable to 1 of 84 methods.*
* [`GetResizedPhotoBadRequest`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/getresizedphotobadrequest.py): Bad Request - A parameter was not specified, or was specified incorrectly. Status code `400`. Applicable to 1 of 84 methods.*
* [`GetMediaProvidersBadRequest`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/getmediaprovidersbadrequest.py): Bad Request - A parameter was not specified, or was specified incorrectly. Status code `400`. Applicable to 1 of 84 methods.*
* [`GetServerListBadRequest`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/getserverlistbadrequest.py): Bad Request - A parameter was not specified, or was specified incorrectly. Status code `400`. Applicable to 1 of 84 methods.*
* [`MarkPlayedBadRequest`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/markplayedbadrequest.py): Bad Request - A parameter was not specified, or was specified incorrectly. Status code `400`. Applicable to 1 of 84 methods.*
* [`MarkUnplayedBadRequest`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/markunplayedbadrequest.py): Bad Request - A parameter was not specified, or was specified incorrectly. Status code `400`. Applicable to 1 of 84 methods.*
* [`UpdatePlayProgressBadRequest`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/updateplayprogressbadrequest.py): Bad Request - A parameter was not specified, or was specified incorrectly. Status code `400`. Applicable to 1 of 84 methods.*
* [`GetBannerImageBadRequest`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/getbannerimagebadrequest.py): Bad Request - A parameter was not specified, or was specified incorrectly. Status code `400`. Applicable to 1 of 84 methods.*
* [`GetThumbImageBadRequest`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/getthumbimagebadrequest.py): Bad Request - A parameter was not specified, or was specified incorrectly. Status code `400`. Applicable to 1 of 84 methods.*
* [`GetTimelineBadRequest`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/gettimelinebadrequest.py): Bad Request - A parameter was not specified, or was specified incorrectly. Status code `400`. Applicable to 1 of 84 methods.*
* [`StartUniversalTranscodeBadRequest`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/startuniversaltranscodebadrequest.py): Bad Request - A parameter was not specified, or was specified incorrectly. Status code `400`. Applicable to 1 of 84 methods.*
* [`GetServerActivitiesBadRequest`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/getserveractivitiesbadrequest.py): Bad Request - A parameter was not specified, or was specified incorrectly. Status code `400`. Applicable to 1 of 84 methods.*
* [`CancelServerActivitiesBadRequest`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/cancelserveractivitiesbadrequest.py): Bad Request - A parameter was not specified, or was specified incorrectly. Status code `400`. Applicable to 1 of 84 methods.*
* [`GetButlerTasksBadRequest`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/getbutlertasksbadrequest.py): Bad Request - A parameter was not specified, or was specified incorrectly. Status code `400`. Applicable to 1 of 84 methods.*
* [`StartAllTasksBadRequest`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/startalltasksbadrequest.py): Bad Request - A parameter was not specified, or was specified incorrectly. Status code `400`. Applicable to 1 of 84 methods.*
* [`StopAllTasksBadRequest`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/stopalltasksbadrequest.py): Bad Request - A parameter was not specified, or was specified incorrectly. Status code `400`. Applicable to 1 of 84 methods.*
* [`StartTaskBadRequest`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/starttaskbadrequest.py): Bad Request - A parameter was not specified, or was specified incorrectly. Status code `400`. Applicable to 1 of 84 methods.*
* [`StopTaskBadRequest`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/stoptaskbadrequest.py): Bad Request - A parameter was not specified, or was specified incorrectly. Status code `400`. Applicable to 1 of 84 methods.*
* [`GetCompanionsDataBadRequest`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/getcompanionsdatabadrequest.py): Bad Request - A parameter was not specified, or was specified incorrectly. Status code `400`. Applicable to 1 of 84 methods.*
* [`GetUserFriendsBadRequest`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/getuserfriendsbadrequest.py): Bad Request - A parameter was not specified, or was specified incorrectly. Status code `400`. Applicable to 1 of 84 methods.*
* [`GetGeoDataBadRequest`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/getgeodatabadrequest.py): Bad Request - A parameter was not specified, or was specified incorrectly. Status code `400`. Applicable to 1 of 84 methods.*
* [`GetHomeDataBadRequest`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/gethomedatabadrequest.py): Bad Request - A parameter was not specified, or was specified incorrectly. Status code `400`. Applicable to 1 of 84 methods.*
* [`GetServerResourcesBadRequest`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/getserverresourcesbadrequest.py): Bad Request - A parameter was not specified, or was specified incorrectly. Status code `400`. Applicable to 1 of 84 methods.*
* [`GetPinBadRequest`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/getpinbadrequest.py): Bad Request - A parameter was not specified, or was specified incorrectly. Status code `400`. Applicable to 1 of 84 methods.*
* [`GetTokenByPinIDBadRequest`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/gettokenbypinidbadrequest.py): Bad Request - A parameter was not specified, or was specified incorrectly. Status code `400`. Applicable to 1 of 84 methods.*
* [`GetGlobalHubsBadRequest`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/getglobalhubsbadrequest.py): Bad Request - A parameter was not specified, or was specified incorrectly. Status code `400`. Applicable to 1 of 84 methods.*
* [`GetLibraryHubsBadRequest`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/getlibraryhubsbadrequest.py): Bad Request - A parameter was not specified, or was specified incorrectly. Status code `400`. Applicable to 1 of 84 methods.*
* [`PerformSearchBadRequest`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/performsearchbadrequest.py): Bad Request - A parameter was not specified, or was specified incorrectly. Status code `400`. Applicable to 1 of 84 methods.*
* [`PerformVoiceSearchBadRequest`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/performvoicesearchbadrequest.py): Bad Request - A parameter was not specified, or was specified incorrectly. Status code `400`. Applicable to 1 of 84 methods.*
* [`GetSearchResultsBadRequest`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/getsearchresultsbadrequest.py): Bad Request - A parameter was not specified, or was specified incorrectly. Status code `400`. Applicable to 1 of 84 methods.*
* [`GetFileHashBadRequest`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/getfilehashbadrequest.py): Bad Request - A parameter was not specified, or was specified incorrectly. Status code `400`. Applicable to 1 of 84 methods.*
* [`GetRecentlyAddedLibraryBadRequest`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/getrecentlyaddedlibrarybadrequest.py): Bad Request - A parameter was not specified, or was specified incorrectly. Status code `400`. Applicable to 1 of 84 methods.*
* [`GetAllLibrariesBadRequest`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/getalllibrariesbadrequest.py): Bad Request - A parameter was not specified, or was specified incorrectly. Status code `400`. Applicable to 1 of 84 methods.*
* [`GetLibraryDetailsBadRequest`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/getlibrarydetailsbadrequest.py): Bad Request - A parameter was not specified, or was specified incorrectly. Status code `400`. Applicable to 1 of 84 methods.*
* [`DeleteLibraryBadRequest`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/deletelibrarybadrequest.py): Bad Request - A parameter was not specified, or was specified incorrectly. Status code `400`. Applicable to 1 of 84 methods.*
* [`GetLibraryItemsBadRequest`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/getlibraryitemsbadrequest.py): Bad Request - A parameter was not specified, or was specified incorrectly. Status code `400`. Applicable to 1 of 84 methods.*
* [`GetLibrarySectionsAllBadRequest`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/getlibrarysectionsallbadrequest.py): Bad Request - A parameter was not specified, or was specified incorrectly. Status code `400`. Applicable to 1 of 84 methods.*
* [`GetRefreshLibraryMetadataBadRequest`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/getrefreshlibrarymetadatabadrequest.py): Bad Request - A parameter was not specified, or was specified incorrectly. Status code `400`. Applicable to 1 of 84 methods.*
* [`GetSearchLibraryBadRequest`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/getsearchlibrarybadrequest.py): Bad Request - A parameter was not specified, or was specified incorrectly. Status code `400`. Applicable to 1 of 84 methods.*
* [`GetGenresLibraryBadRequest`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/getgenreslibrarybadrequest.py): Bad Request - A parameter was not specified, or was specified incorrectly. Status code `400`. Applicable to 1 of 84 methods.*
* [`GetCountriesLibraryBadRequest`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/getcountrieslibrarybadrequest.py): Bad Request - A parameter was not specified, or was specified incorrectly. Status code `400`. Applicable to 1 of 84 methods.*
* [`GetActorsLibraryBadRequest`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/getactorslibrarybadrequest.py): Bad Request - A parameter was not specified, or was specified incorrectly. Status code `400`. Applicable to 1 of 84 methods.*
* [`GetSearchAllLibrariesBadRequest`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/getsearchalllibrariesbadrequest.py): Bad Request - A parameter was not specified, or was specified incorrectly. Status code `400`. Applicable to 1 of 84 methods.*
* [`GetMediaMetaDataBadRequest`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/getmediametadatabadrequest.py): Bad Request - A parameter was not specified, or was specified incorrectly. Status code `400`. Applicable to 1 of 84 methods.*
* [`GetMetadataChildrenBadRequest`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/getmetadatachildrenbadrequest.py): Bad Request - A parameter was not specified, or was specified incorrectly. Status code `400`. Applicable to 1 of 84 methods.*
* [`GetTopWatchedContentBadRequest`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/gettopwatchedcontentbadrequest.py): Bad Request - A parameter was not specified, or was specified incorrectly. Status code `400`. Applicable to 1 of 84 methods.*
* [`GetWatchListBadRequest`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/getwatchlistbadrequest.py): Bad Request - A parameter was not specified, or was specified incorrectly. Status code `400`. Applicable to 1 of 84 methods.*
* [`LogLineBadRequest`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/loglinebadrequest.py): Bad Request - A parameter was not specified, or was specified incorrectly. Status code `400`. Applicable to 1 of 84 methods.*
* [`LogMultiLineBadRequest`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/logmultilinebadrequest.py): Bad Request - A parameter was not specified, or was specified incorrectly. Status code `400`. Applicable to 1 of 84 methods.*
* [`EnablePaperTrailBadRequest`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/enablepapertrailbadrequest.py): Bad Request - A parameter was not specified, or was specified incorrectly. Status code `400`. Applicable to 1 of 84 methods.*
* [`CreatePlaylistBadRequest`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/createplaylistbadrequest.py): Bad Request - A parameter was not specified, or was specified incorrectly. Status code `400`. Applicable to 1 of 84 methods.*
* [`GetPlaylistsBadRequest`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/getplaylistsbadrequest.py): Bad Request - A parameter was not specified, or was specified incorrectly. Status code `400`. Applicable to 1 of 84 methods.*
* [`GetPlaylistBadRequest`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/getplaylistbadrequest.py): Bad Request - A parameter was not specified, or was specified incorrectly. Status code `400`. Applicable to 1 of 84 methods.*
* [`DeletePlaylistBadRequest`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/deleteplaylistbadrequest.py): Bad Request - A parameter was not specified, or was specified incorrectly. Status code `400`. Applicable to 1 of 84 methods.*
* [`UpdatePlaylistBadRequest`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/updateplaylistbadrequest.py): Bad Request - A parameter was not specified, or was specified incorrectly. Status code `400`. Applicable to 1 of 84 methods.*
* [`GetPlaylistContentsBadRequest`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/getplaylistcontentsbadrequest.py): Bad Request - A parameter was not specified, or was specified incorrectly. Status code `400`. Applicable to 1 of 84 methods.*
* [`ClearPlaylistContentsBadRequest`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/clearplaylistcontentsbadrequest.py): Bad Request - A parameter was not specified, or was specified incorrectly. Status code `400`. Applicable to 1 of 84 methods.*
* [`AddPlaylistContentsBadRequest`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/addplaylistcontentsbadrequest.py): Bad Request - A parameter was not specified, or was specified incorrectly. Status code `400`. Applicable to 1 of 84 methods.*
* [`UploadPlaylistBadRequest`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/uploadplaylistbadrequest.py): Bad Request - A parameter was not specified, or was specified incorrectly. Status code `400`. Applicable to 1 of 84 methods.*
* [`GetTransientTokenBadRequest`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/gettransienttokenbadrequest.py): Bad Request - A parameter was not specified, or was specified incorrectly. Status code `400`. Applicable to 1 of 84 methods.*
* [`GetSourceConnectionInformationBadRequest`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/getsourceconnectioninformationbadrequest.py): Bad Request - A parameter was not specified, or was specified incorrectly. Status code `400`. Applicable to 1 of 84 methods.*
* [`GetTokenDetailsBadRequest`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/gettokendetailsbadrequest.py): Bad Request - A parameter was not specified, or was specified incorrectly. Status code `400`. Applicable to 1 of 84 methods.*
* [`PostUsersSignInDataBadRequest`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/postuserssignindatabadrequest.py): Bad Request - A parameter was not specified, or was specified incorrectly. Status code `400`. Applicable to 1 of 84 methods.*
* [`GetStatisticsBadRequest`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/getstatisticsbadrequest.py): Bad Request - A parameter was not specified, or was specified incorrectly. Status code `400`. Applicable to 1 of 84 methods.*
* [`GetResourcesStatisticsBadRequest`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/getresourcesstatisticsbadrequest.py): Bad Request - A parameter was not specified, or was specified incorrectly. Status code `400`. Applicable to 1 of 84 methods.*
* [`GetBandwidthStatisticsBadRequest`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/getbandwidthstatisticsbadrequest.py): Bad Request - A parameter was not specified, or was specified incorrectly. Status code `400`. Applicable to 1 of 84 methods.*
* [`GetSessionsBadRequest`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/getsessionsbadrequest.py): Bad Request - A parameter was not specified, or was specified incorrectly. Status code `400`. Applicable to 1 of 84 methods.*
* [`GetSessionHistoryBadRequest`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/getsessionhistorybadrequest.py): Bad Request - A parameter was not specified, or was specified incorrectly. Status code `400`. Applicable to 1 of 84 methods.*
* [`GetTranscodeSessionsBadRequest`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/gettranscodesessionsbadrequest.py): Bad Request - A parameter was not specified, or was specified incorrectly. Status code `400`. Applicable to 1 of 84 methods.*
* [`StopTranscodeSessionBadRequest`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/stoptranscodesessionbadrequest.py): Bad Request - A parameter was not specified, or was specified incorrectly. Status code `400`. Applicable to 1 of 84 methods.*
* [`GetUpdateStatusBadRequest`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/getupdatestatusbadrequest.py): Bad Request - A parameter was not specified, or was specified incorrectly. Status code `400`. Applicable to 1 of 84 methods.*
* [`CheckForUpdatesBadRequest`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/checkforupdatesbadrequest.py): Bad Request - A parameter was not specified, or was specified incorrectly. Status code `400`. Applicable to 1 of 84 methods.*
* [`ApplyUpdatesBadRequest`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/applyupdatesbadrequest.py): Bad Request - A parameter was not specified, or was specified incorrectly. Status code `400`. Applicable to 1 of 84 methods.*
* [`GetUsersBadRequest`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/getusersbadrequest.py): Bad Request - A parameter was not specified, or was specified incorrectly. Status code `400`. Applicable to 1 of 84 methods.*
* [`GetServerCapabilitiesUnauthorized`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/getservercapabilitiesunauthorized.py): Unauthorized - Returned if the X-Plex-Token is missing from the header or query. Status code `401`. Applicable to 1 of 84 methods.*
* [`GetServerPreferencesUnauthorized`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/getserverpreferencesunauthorized.py): Unauthorized - Returned if the X-Plex-Token is missing from the header or query. Status code `401`. Applicable to 1 of 84 methods.*
* [`GetAvailableClientsUnauthorized`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/getavailableclientsunauthorized.py): Unauthorized - Returned if the X-Plex-Token is missing from the header or query. Status code `401`. Applicable to 1 of 84 methods.*
* [`GetDevicesUnauthorized`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/getdevicesunauthorized.py): Unauthorized - Returned if the X-Plex-Token is missing from the header or query. Status code `401`. Applicable to 1 of 84 methods.*
* [`GetMyPlexAccountUnauthorized`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/getmyplexaccountunauthorized.py): Unauthorized - Returned if the X-Plex-Token is missing from the header or query. Status code `401`. Applicable to 1 of 84 methods.*
* [`GetResizedPhotoUnauthorized`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/getresizedphotounauthorized.py): Unauthorized - Returned if the X-Plex-Token is missing from the header or query. Status code `401`. Applicable to 1 of 84 methods.*
* [`GetMediaProvidersUnauthorized`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/getmediaprovidersunauthorized.py): Unauthorized - Returned if the X-Plex-Token is missing from the header or query. Status code `401`. Applicable to 1 of 84 methods.*
* [`GetServerListUnauthorized`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/getserverlistunauthorized.py): Unauthorized - Returned if the X-Plex-Token is missing from the header or query. Status code `401`. Applicable to 1 of 84 methods.*
* [`MarkPlayedUnauthorized`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/markplayedunauthorized.py): Unauthorized - Returned if the X-Plex-Token is missing from the header or query. Status code `401`. Applicable to 1 of 84 methods.*
* [`MarkUnplayedUnauthorized`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/markunplayedunauthorized.py): Unauthorized - Returned if the X-Plex-Token is missing from the header or query. Status code `401`. Applicable to 1 of 84 methods.*
* [`UpdatePlayProgressUnauthorized`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/updateplayprogressunauthorized.py): Unauthorized - Returned if the X-Plex-Token is missing from the header or query. Status code `401`. Applicable to 1 of 84 methods.*
* [`GetBannerImageUnauthorized`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/getbannerimageunauthorized.py): Unauthorized - Returned if the X-Plex-Token is missing from the header or query. Status code `401`. Applicable to 1 of 84 methods.*
* [`GetThumbImageUnauthorized`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/getthumbimageunauthorized.py): Unauthorized - Returned if the X-Plex-Token is missing from the header or query. Status code `401`. Applicable to 1 of 84 methods.*
* [`GetTimelineUnauthorized`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/gettimelineunauthorized.py): Unauthorized - Returned if the X-Plex-Token is missing from the header or query. Status code `401`. Applicable to 1 of 84 methods.*
* [`StartUniversalTranscodeUnauthorized`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/startuniversaltranscodeunauthorized.py): Unauthorized - Returned if the X-Plex-Token is missing from the header or query. Status code `401`. Applicable to 1 of 84 methods.*
* [`GetServerActivitiesUnauthorized`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/getserveractivitiesunauthorized.py): Unauthorized - Returned if the X-Plex-Token is missing from the header or query. Status code `401`. Applicable to 1 of 84 methods.*
* [`CancelServerActivitiesUnauthorized`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/cancelserveractivitiesunauthorized.py): Unauthorized - Returned if the X-Plex-Token is missing from the header or query. Status code `401`. Applicable to 1 of 84 methods.*
* [`GetButlerTasksUnauthorized`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/getbutlertasksunauthorized.py): Unauthorized - Returned if the X-Plex-Token is missing from the header or query. Status code `401`. Applicable to 1 of 84 methods.*
* [`StartAllTasksUnauthorized`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/startalltasksunauthorized.py): Unauthorized - Returned if the X-Plex-Token is missing from the header or query. Status code `401`. Applicable to 1 of 84 methods.*
* [`StopAllTasksUnauthorized`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/stopalltasksunauthorized.py): Unauthorized - Returned if the X-Plex-Token is missing from the header or query. Status code `401`. Applicable to 1 of 84 methods.*
* [`StartTaskUnauthorized`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/starttaskunauthorized.py): Unauthorized - Returned if the X-Plex-Token is missing from the header or query. Status code `401`. Applicable to 1 of 84 methods.*
* [`StopTaskUnauthorized`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/stoptaskunauthorized.py): Unauthorized - Returned if the X-Plex-Token is missing from the header or query. Status code `401`. Applicable to 1 of 84 methods.*
* [`GetCompanionsDataUnauthorized`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/getcompanionsdataunauthorized.py): Unauthorized - Returned if the X-Plex-Token is missing from the header or query. Status code `401`. Applicable to 1 of 84 methods.*
* [`GetUserFriendsUnauthorized`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/getuserfriendsunauthorized.py): Unauthorized - Returned if the X-Plex-Token is missing from the header or query. Status code `401`. Applicable to 1 of 84 methods.*
* [`GetGeoDataUnauthorized`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/getgeodataunauthorized.py): Unauthorized - Returned if the X-Plex-Token is missing from the header or query. Status code `401`. Applicable to 1 of 84 methods.*
* [`GetHomeDataUnauthorized`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/gethomedataunauthorized.py): Unauthorized - Returned if the X-Plex-Token is missing from the header or query. Status code `401`. Applicable to 1 of 84 methods.*
* [`GetServerResourcesUnauthorized`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/getserverresourcesunauthorized.py): Unauthorized - Returned if the X-Plex-Token is missing from the header or query. Status code `401`. Applicable to 1 of 84 methods.*
* [`GetGlobalHubsUnauthorized`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/getglobalhubsunauthorized.py): Unauthorized - Returned if the X-Plex-Token is missing from the header or query. Status code `401`. Applicable to 1 of 84 methods.*
* [`GetLibraryHubsUnauthorized`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/getlibraryhubsunauthorized.py): Unauthorized - Returned if the X-Plex-Token is missing from the header or query. Status code `401`. Applicable to 1 of 84 methods.*
* [`PerformSearchUnauthorized`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/performsearchunauthorized.py): Unauthorized - Returned if the X-Plex-Token is missing from the header or query. Status code `401`. Applicable to 1 of 84 methods.*
* [`PerformVoiceSearchUnauthorized`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/performvoicesearchunauthorized.py): Unauthorized - Returned if the X-Plex-Token is missing from the header or query. Status code `401`. Applicable to 1 of 84 methods.*
* [`GetSearchResultsUnauthorized`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/getsearchresultsunauthorized.py): Unauthorized - Returned if the X-Plex-Token is missing from the header or query. Status code `401`. Applicable to 1 of 84 methods.*
* [`GetFileHashUnauthorized`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/getfilehashunauthorized.py): Unauthorized - Returned if the X-Plex-Token is missing from the header or query. Status code `401`. Applicable to 1 of 84 methods.*
* [`GetRecentlyAddedLibraryUnauthorized`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/getrecentlyaddedlibraryunauthorized.py): Unauthorized - Returned if the X-Plex-Token is missing from the header or query. Status code `401`. Applicable to 1 of 84 methods.*
* [`GetAllLibrariesUnauthorized`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/getalllibrariesunauthorized.py): Unauthorized - Returned if the X-Plex-Token is missing from the header or query. Status code `401`. Applicable to 1 of 84 methods.*
* [`GetLibraryDetailsUnauthorized`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/getlibrarydetailsunauthorized.py): Unauthorized - Returned if the X-Plex-Token is missing from the header or query. Status code `401`. Applicable to 1 of 84 methods.*
* [`DeleteLibraryUnauthorized`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/deletelibraryunauthorized.py): Unauthorized - Returned if the X-Plex-Token is missing from the header or query. Status code `401`. Applicable to 1 of 84 methods.*
* [`GetLibraryItemsUnauthorized`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/getlibraryitemsunauthorized.py): Unauthorized - Returned if the X-Plex-Token is missing from the header or query. Status code `401`. Applicable to 1 of 84 methods.*
* [`GetLibrarySectionsAllUnauthorized`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/getlibrarysectionsallunauthorized.py): Unauthorized - Returned if the X-Plex-Token is missing from the header or query. Status code `401`. Applicable to 1 of 84 methods.*
* [`GetRefreshLibraryMetadataUnauthorized`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/getrefreshlibrarymetadataunauthorized.py): Unauthorized - Returned if the X-Plex-Token is missing from the header or query. Status code `401`. Applicable to 1 of 84 methods.*
* [`GetSearchLibraryUnauthorized`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/getsearchlibraryunauthorized.py): Unauthorized - Returned if the X-Plex-Token is missing from the header or query. Status code `401`. Applicable to 1 of 84 methods.*
* [`GetGenresLibraryUnauthorized`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/getgenreslibraryunauthorized.py): Unauthorized - Returned if the X-Plex-Token is missing from the header or query. Status code `401`. Applicable to 1 of 84 methods.*
* [`GetCountriesLibraryUnauthorized`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/getcountrieslibraryunauthorized.py): Unauthorized - Returned if the X-Plex-Token is missing from the header or query. Status code `401`. Applicable to 1 of 84 methods.*
* [`GetActorsLibraryUnauthorized`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/getactorslibraryunauthorized.py): Unauthorized - Returned if the X-Plex-Token is missing from the header or query. Status code `401`. Applicable to 1 of 84 methods.*
* [`GetSearchAllLibrariesUnauthorized`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/getsearchalllibrariesunauthorized.py): Unauthorized - Returned if the X-Plex-Token is missing from the header or query. Status code `401`. Applicable to 1 of 84 methods.*
* [`GetMediaMetaDataUnauthorized`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/getmediametadataunauthorized.py): Unauthorized - Returned if the X-Plex-Token is missing from the header or query. Status code `401`. Applicable to 1 of 84 methods.*
* [`GetMetadataChildrenUnauthorized`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/getmetadatachildrenunauthorized.py): Unauthorized - Returned if the X-Plex-Token is missing from the header or query. Status code `401`. Applicable to 1 of 84 methods.*
* [`GetTopWatchedContentUnauthorized`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/gettopwatchedcontentunauthorized.py): Unauthorized - Returned if the X-Plex-Token is missing from the header or query. Status code `401`. Applicable to 1 of 84 methods.*
* [`GetWatchListUnauthorized`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/getwatchlistunauthorized.py): Unauthorized - Returned if the X-Plex-Token is missing from the header or query. Status code `401`. Applicable to 1 of 84 methods.*
* [`LogLineUnauthorized`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/loglineunauthorized.py): Unauthorized - Returned if the X-Plex-Token is missing from the header or query. Status code `401`. Applicable to 1 of 84 methods.*
* [`LogMultiLineUnauthorized`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/logmultilineunauthorized.py): Unauthorized - Returned if the X-Plex-Token is missing from the header or query. Status code `401`. Applicable to 1 of 84 methods.*
* [`EnablePaperTrailUnauthorized`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/enablepapertrailunauthorized.py): Unauthorized - Returned if the X-Plex-Token is missing from the header or query. Status code `401`. Applicable to 1 of 84 methods.*
* [`CreatePlaylistUnauthorized`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/createplaylistunauthorized.py): Unauthorized - Returned if the X-Plex-Token is missing from the header or query. Status code `401`. Applicable to 1 of 84 methods.*
* [`GetPlaylistsUnauthorized`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/getplaylistsunauthorized.py): Unauthorized - Returned if the X-Plex-Token is missing from the header or query. Status code `401`. Applicable to 1 of 84 methods.*
* [`GetPlaylistUnauthorized`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/getplaylistunauthorized.py): Unauthorized - Returned if the X-Plex-Token is missing from the header or query. Status code `401`. Applicable to 1 of 84 methods.*
* [`DeletePlaylistUnauthorized`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/deleteplaylistunauthorized.py): Unauthorized - Returned if the X-Plex-Token is missing from the header or query. Status code `401`. Applicable to 1 of 84 methods.*
* [`UpdatePlaylistUnauthorized`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/updateplaylistunauthorized.py): Unauthorized - Returned if the X-Plex-Token is missing from the header or query. Status code `401`. Applicable to 1 of 84 methods.*
* [`GetPlaylistContentsUnauthorized`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/getplaylistcontentsunauthorized.py): Unauthorized - Returned if the X-Plex-Token is missing from the header or query. Status code `401`. Applicable to 1 of 84 methods.*
* [`ClearPlaylistContentsUnauthorized`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/clearplaylistcontentsunauthorized.py): Unauthorized - Returned if the X-Plex-Token is missing from the header or query. Status code `401`. Applicable to 1 of 84 methods.*
* [`AddPlaylistContentsUnauthorized`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/addplaylistcontentsunauthorized.py): Unauthorized - Returned if the X-Plex-Token is missing from the header or query. Status code `401`. Applicable to 1 of 84 methods.*
* [`UploadPlaylistUnauthorized`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/uploadplaylistunauthorized.py): Unauthorized - Returned if the X-Plex-Token is missing from the header or query. Status code `401`. Applicable to 1 of 84 methods.*
* [`GetTransientTokenUnauthorized`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/gettransienttokenunauthorized.py): Unauthorized - Returned if the X-Plex-Token is missing from the header or query. Status code `401`. Applicable to 1 of 84 methods.*
* [`GetSourceConnectionInformationUnauthorized`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/getsourceconnectioninformationunauthorized.py): Unauthorized - Returned if the X-Plex-Token is missing from the header or query. Status code `401`. Applicable to 1 of 84 methods.*
* [`GetTokenDetailsUnauthorized`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/gettokendetailsunauthorized.py): Unauthorized - Returned if the X-Plex-Token is missing from the header or query. Status code `401`. Applicable to 1 of 84 methods.*
* [`PostUsersSignInDataUnauthorized`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/postuserssignindataunauthorized.py): Unauthorized - Returned if the X-Plex-Token is missing from the header or query. Status code `401`. Applicable to 1 of 84 methods.*
* [`GetStatisticsUnauthorized`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/getstatisticsunauthorized.py): Unauthorized - Returned if the X-Plex-Token is missing from the header or query. Status code `401`. Applicable to 1 of 84 methods.*
* [`GetResourcesStatisticsUnauthorized`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/getresourcesstatisticsunauthorized.py): Unauthorized - Returned if the X-Plex-Token is missing from the header or query. Status code `401`. Applicable to 1 of 84 methods.*
* [`GetBandwidthStatisticsUnauthorized`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/getbandwidthstatisticsunauthorized.py): Unauthorized - Returned if the X-Plex-Token is missing from the header or query. Status code `401`. Applicable to 1 of 84 methods.*
* [`GetSessionsUnauthorized`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/getsessionsunauthorized.py): Unauthorized - Returned if the X-Plex-Token is missing from the header or query. Status code `401`. Applicable to 1 of 84 methods.*
* [`GetSessionHistoryUnauthorized`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/getsessionhistoryunauthorized.py): Unauthorized - Returned if the X-Plex-Token is missing from the header or query. Status code `401`. Applicable to 1 of 84 methods.*
* [`GetTranscodeSessionsUnauthorized`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/gettranscodesessionsunauthorized.py): Unauthorized - Returned if the X-Plex-Token is missing from the header or query. Status code `401`. Applicable to 1 of 84 methods.*
* [`StopTranscodeSessionUnauthorized`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/stoptranscodesessionunauthorized.py): Unauthorized - Returned if the X-Plex-Token is missing from the header or query. Status code `401`. Applicable to 1 of 84 methods.*
* [`GetUpdateStatusUnauthorized`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/getupdatestatusunauthorized.py): Unauthorized - Returned if the X-Plex-Token is missing from the header or query. Status code `401`. Applicable to 1 of 84 methods.*
* [`CheckForUpdatesUnauthorized`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/checkforupdatesunauthorized.py): Unauthorized - Returned if the X-Plex-Token is missing from the header or query. Status code `401`. Applicable to 1 of 84 methods.*
* [`ApplyUpdatesUnauthorized`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/applyupdatesunauthorized.py): Unauthorized - Returned if the X-Plex-Token is missing from the header or query. Status code `401`. Applicable to 1 of 84 methods.*
* [`GetUsersUnauthorized`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/getusersunauthorized.py): Unauthorized - Returned if the X-Plex-Token is missing from the header or query. Status code `401`. Applicable to 1 of 84 methods.*
* [`GetTokenByPinIDResponseBody`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/gettokenbypinidresponsebody.py): Not Found or Expired. Status code `404`. Applicable to 1 of 84 methods.*
* [`GetServerIdentityRequestTimeout`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/getserveridentityrequesttimeout.py): Request Timeout. Status code `408`. Applicable to 1 of 84 methods.*
* [`ResponseValidationError`](https://github.com/LukeHagar/plexpy/blob/master/././src/plex_api_client/models/errors/responsevalidationerror.py): Type mismatch between the response data and the expected Pydantic model. Provides access to the Pydantic validation error via the `cause` attribute.

</details>

\* Check [the method documentation](https://github.com/LukeHagar/plexpy/blob/master/./#available-resources-and-operations) to see if the error is applicable.
<!-- End Error Handling [errors] -->

<!-- Start Server Selection [server] -->
## Server Selection

### Server Variables

The default server `{protocol}://{ip}:{port}` contains variables and is set to `https://10.10.10.47:32400` by default. To override default values, the following parameters are available when initializing the SDK client instance:

| Variable   | Parameter                         | Supported Values           | Default         | Description                                    |
| ---------- | --------------------------------- | -------------------------- | --------------- | ---------------------------------------------- |
| `protocol` | `protocol: models.ServerProtocol` | - `"http"`<br/>- `"https"` | `"https"`       | The protocol to use for the server connection  |
| `ip`       | `ip: str`                         | str                        | `"10.10.10.47"` | The IP address or hostname of your Plex Server |
| `port`     | `port: str`                       | str                        | `"32400"`       | The port of your Plex Server                   |

#### Example

```python
from plex_api_client import PlexAPI


with PlexAPI(
    protocol="https"
    ip="4982:bc2a:b4f8:efb5:2394:5bc3:ab4f:0e6d"
    port="44765"
    access_token="<YOUR_API_KEY_HERE>",
) as plex_api:

    res = plex_api.server.get_server_capabilities()

    assert res.object is not None

    # Handle response
    print(res.object)

```

### Override Server URL Per-Client

The default server can be overridden globally by passing a URL to the `server_url: str` optional parameter when initializing the SDK client instance. For example:
```python
from plex_api_client import PlexAPI


with PlexAPI(
    server_url="https://10.10.10.47:32400",
    access_token="<YOUR_API_KEY_HERE>",
) as plex_api:

    res = plex_api.server.get_server_capabilities()

    assert res.object is not None

    # Handle response
    print(res.object)

```

### Override Server URL Per-Operation

The server URL can also be overridden on a per-operation basis, provided a server list was specified for the operation. For example:
```python
from plex_api_client import PlexAPI


with PlexAPI(
    access_token="<YOUR_API_KEY_HERE>",
) as plex_api:

    res = plex_api.plex.get_companions_data(server_url="https://plex.tv/api/v2")

    assert res.response_bodies is not None

    # Handle response
    print(res.response_bodies)

```
<!-- End Server Selection [server] -->

<!-- Start Custom HTTP Client [http-client] -->
## Custom HTTP Client

The Python SDK makes API calls using the [httpx](https://www.python-httpx.org/) HTTP library.  In order to provide a convenient way to configure timeouts, cookies, proxies, custom headers, and other low-level configuration, you can initialize the SDK client with your own HTTP client instance.
Depending on whether you are using the sync or async version of the SDK, you can pass an instance of `HttpClient` or `AsyncHttpClient` respectively, which are Protocol's ensuring that the client has the necessary methods to make API calls.
This allows you to wrap the client with your own custom logic, such as adding custom headers, logging, or error handling, or you can just pass an instance of `httpx.Client` or `httpx.AsyncClient` directly.

For example, you could specify a header for every request that this sdk makes as follows:
```python
from plex_api_client import PlexAPI
import httpx

http_client = httpx.Client(headers={"x-custom-header": "someValue"})
s = PlexAPI(client=http_client)
```

or you could wrap the client with your own custom logic:
```python
from plex_api_client import PlexAPI
from plex_api_client.httpclient import AsyncHttpClient
import httpx

class CustomClient(AsyncHttpClient):
    client: AsyncHttpClient

    def __init__(self, client: AsyncHttpClient):
        self.client = client

    async def send(
        self,
        request: httpx.Request,
        *,
        stream: bool = False,
        auth: Union[
            httpx._types.AuthTypes, httpx._client.UseClientDefault, None
        ] = httpx.USE_CLIENT_DEFAULT,
        follow_redirects: Union[
            bool, httpx._client.UseClientDefault
        ] = httpx.USE_CLIENT_DEFAULT,
    ) -> httpx.Response:
        request.headers["Client-Level-Header"] = "added by client"

        return await self.client.send(
            request, stream=stream, auth=auth, follow_redirects=follow_redirects
        )

    def build_request(
        self,
        method: str,
        url: httpx._types.URLTypes,
        *,
        content: Optional[httpx._types.RequestContent] = None,
        data: Optional[httpx._types.RequestData] = None,
        files: Optional[httpx._types.RequestFiles] = None,
        json: Optional[Any] = None,
        params: Optional[httpx._types.QueryParamTypes] = None,
        headers: Optional[httpx._types.HeaderTypes] = None,
        cookies: Optional[httpx._types.CookieTypes] = None,
        timeout: Union[
            httpx._types.TimeoutTypes, httpx._client.UseClientDefault
        ] = httpx.USE_CLIENT_DEFAULT,
        extensions: Optional[httpx._types.RequestExtensions] = None,
    ) -> httpx.Request:
        return self.client.build_request(
            method,
            url,
            content=content,
            data=data,
            files=files,
            json=json,
            params=params,
            headers=headers,
            cookies=cookies,
            timeout=timeout,
            extensions=extensions,
        )

s = PlexAPI(async_client=CustomClient(httpx.AsyncClient()))
```
<!-- End Custom HTTP Client [http-client] -->

<!-- Start Authentication [security] -->
## Authentication

### Per-Client Security Schemes

This SDK supports the following security scheme globally:

| Name           | Type   | Scheme  |
| -------------- | ------ | ------- |
| `access_token` | apiKey | API key |

To authenticate with the API the `access_token` parameter must be set when initializing the SDK client instance. For example:
```python
from plex_api_client import PlexAPI


with PlexAPI(
    access_token="<YOUR_API_KEY_HERE>",
) as plex_api:

    res = plex_api.server.get_server_capabilities()

    assert res.object is not None

    # Handle response
    print(res.object)

```
<!-- End Authentication [security] -->

<!-- Start Resource Management [resource-management] -->
## Resource Management

The `PlexAPI` class implements the context manager protocol and registers a finalizer function to close the underlying sync and async HTTPX clients it uses under the hood. This will close HTTP connections, release memory and free up other resources held by the SDK. In short-lived Python programs and notebooks that make a few SDK method calls, resource management may not be a concern. However, in longer-lived programs, it is beneficial to create a single SDK instance via a [context manager][context-manager] and reuse it across the application.

[context-manager]: https://docs.python.org/3/reference/datamodel.html#context-managers

```python
from plex_api_client import PlexAPI
def main():

    with PlexAPI(
        access_token="<YOUR_API_KEY_HERE>",
    ) as plex_api:
        # Rest of application here...


# Or when using async:
async def amain():

    async with PlexAPI(
        access_token="<YOUR_API_KEY_HERE>",
    ) as plex_api:
        # Rest of application here...
```
<!-- End Resource Management [resource-management] -->

<!-- Start Debugging [debug] -->
## Debugging

You can setup your SDK to emit debug logs for SDK requests and responses.

You can pass your own logger class directly into your SDK.
```python
from plex_api_client import PlexAPI
import logging

logging.basicConfig(level=logging.DEBUG)
s = PlexAPI(debug_logger=logging.getLogger("plex_api_client"))
```
<!-- End Debugging [debug] -->

<!-- Placeholder for Future Speakeasy SDK Sections -->

# Development

## Maturity

This SDK is in beta, and there may be breaking changes between versions without a major version update. Therefore, we recommend pinning usage
to a specific package version. This way, you can install the same version each time without breaking changes unless you are intentionally
looking for the latest version.

## Contributions

While we value open-source contributions to this SDK, this library is generated programmatically.
Feel free to open a PR or a Github issue as a proof of concept and we'll do our best to include it in a future release!

### SDK Created by [Speakeasy](https://docs.speakeasyapi.dev/docs/using-speakeasy/client-sdks)
