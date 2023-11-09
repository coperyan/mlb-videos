import os


from mlb_videos.youtube.api import API
from mlb_videos.youtube._enum import Category


DEFAULTS = {
    "tags": ["mlb", "baseball"],
    "privacy": "private",
    "categoryId": Category.SPORTS.value,
    "defaultLanguage": "en_US",
    "defaultAudioLanguage": "en_US",
    "selfDeclaredMadeForKids": False,
}


class Video:
    def __init__(self, file: str, **kwargs):
        self.client = API()
        self.file = file
        self.thumbnail = kwargs.pop("thumbnail")
        self.playlist = kwargs.pop("playlist")

        # Validate video file path
        if not os.path.isfile(file):
            raise Exception("Invalid `file` parameter passed, must be local path str.")

        # Use enum to get categoryId from category name
        if "category" in kwargs:
            category = kwargs.pop("category")
            try:
                kwargs["categoryId"] = Category[category].value
            except KeyError as e:
                print(
                    f"Category parameter: {category} does not match a YouTube category ID.."
                )

        # Apply default params
        for param, val in DEFAULTS.items():
            if param not in kwargs:
                kwargs[param] = val

        self.kwargs = kwargs
        self.video_id = self.client.video_insert(self.file, **kwargs)

        if self.thumbnail:
            self.client.thumbnails_set(self.video_id, self.thumbnail)

        if self.playlist:
            self.client.playlist_items_insert(self.video_id, self.playlist)
