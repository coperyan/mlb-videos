import os
import requests
import pandas as pd

import constants as Constants

missed_sample = pd.read_csv("data/missed_calls.csv")

_CHUNK_SIZE = 1024
_QUERY_SUFFIX = "Order By Timestamp DESC"
_SAVE_PATH = "data"
_DEFAULT_FEED = "opt"


class Client:
    """Used to make requests to API endpoints
    Replies with content to DL
    """

    def __init__(self, url: str = None, req_type: str = None):
        """Initialize class, pass two items (url for request & request type)
            req_type = Query, Clip, Download
        Headers are grabbed based on the req_type
        Resp_Path only returns for Query / Clip

        Calls make request
        """
        self.url = url
        self.req_type = req_type
        self.headers = Constants.VideoRoom.Headers.get(req_type, {})
        self.resp = None
        self.resp_path = Constants.VideoRoom.Responses.get(req_type, {})
        self.resp_json = {}
        self._make_request()

    def _make_request(self):
        """Makes request
        Checks for bad status code return, raises Exception if so
        Checks to see if Query/Clip request
            If so - parses JSON based on key path defined in const module
            Sets JSON object of class
        """
        self.resp = requests.get(self.url, headers=self.headers)
        if self.resp.status_code != 200:
            raise Exception(
                f"Bad Request, Status Code: {self.resp.status_code}: {self.resp.text}"
            )
        if self.resp_path:
            wrk = self.resp.json()
            for k in self.resp_path:
                wrk = wrk.get(k, {})
            self.resp_json = wrk

    def download_video(self, fp):
        """Referencing the content of the original req
        Iterates over chunks of said content, writing to local path
        File path is only parameter - will be passed by different class
        """
        with open(fp, "wb") as f:
            for chunk in self.resp.iter_content(chunk_size=_CHUNK_SIZE):
                if chunk:
                    f.write(chunk)

    def get_json(self):
        """Returns JSON in class"""
        return self.resp_json


class Clip:
    """ """

    def __init__(
        self,
        feed=Constants.VideoRoom.FeedTypes.Optimal,
        download: bool = None,
        play_id: str = None,
    ):
        """ """
        self.feed = feed
        self.download = download
        self.play_id = play_id
        self.get_clip()
        self.gen_clip_metadata()
        self.get_clip_feeds()
        self.download_clip()

    def get_clip(self):
        """ """
        clip_url = Constants.VideoRoom.Queries.get("Clip").replace(
            "slug_id", self.play_id
        )
        clip_client = Client(url=clip_url, req_type="Clip")
        self.clip_json = clip_client.get_json()[0]

    def gen_clip_metadata(self):
        """ """
        metadata = {}
        for k, v in Constants.VideoRoom.ClipMetadata.items():
            wrk = self.clip_json.copy()
            if k in ["feeds", "feed_choice"]:
                metadata.update({k: v})
            else:
                for p in v:
                    wrk = wrk.get(p, {})
                if wrk:
                    metadata.update({k: wrk})
                else:
                    metadata.update({k: None})
        self.metadata = metadata.copy()

    def get_clip_feeds(self):
        """ """
        feeds = []
        for cf in self.clip_json["feeds"]:
            for pb in cf["playbacks"]:
                if ".mp4" in os.path.basename(pb["url"]):
                    feeds.append(
                        {
                            "id": f'{cf["type"]}_{pb["name"]}',
                            "type": cf["type"],
                            "name": pb["name"],
                            "url": pb["url"],
                        }
                    )

        for ft in self.feed:
            if ft in [f["id"] for f in feeds]:
                feed_choice = [f for f in feeds if f["id"] == ft][0]
                break

        if feed_choice is not None:
            self.metadata["feeds"] = feeds
            self.metadata["feed_choice"] = feed_choice
            self.feed_choice = feed_choice
        else:
            raise Exception("No valid feeds found.")

    def download_clip(self):
        """ """
        client = Client(url=self.feed_choice["url"], req_type="Download")
        self.file_name = (
            f'{self.metadata["date"]}_'
            + f'{self.metadata["slug"]}_'
            + f'{self.feed_choice["id"]}.mp4'
        )
        self.file_path = os.path.join(_SAVE_PATH, self.file_name)
        client.download_video(fp=self.file_path)


class Search:
    """ """

    def __init__(
        self,
        feed=Constants.VideoRoom.FeedTypes.Optimal,
        download: bool = False,
        pitch=None,
        params: list = Constants.VideoRoom.DefaultParameters,
    ):
        """Initialization of search class
        Feed defaults to 'opt' - this combines best quality & file size
        Download boolean defaults to false
        Passing entire pitch as named_tuple
        Params are defined in constants - basically fields that specify video == pitch
        """
        self.feed = feed
        self.download = download
        self.pitch = pitch
        self.params = params

        self.query = ""
        self.req_url = ""
        self.build_query()

        self.query_json = {}
        self.clip_ct = None
        self.play_id = None
        self.perform_search()

    def build_query(self):
        """Builds a query string using a Graph QL template discovered
        Iterates over parameters passed to initialize phase
        Finds corresponding Parameter tuple + attribs from constants
        Determines the value based on the corresponding key within the pitch dict
        Does some funky formatting, concatenates into a single request string (url)
        """
        for param in self.params:
            param_ref = next(
                filter(lambda x: x["Name"] == param, Constants.VideoRoom.Parameters)
            )
            param_val = self.pitch.get(param_ref["Ref"], {})
            eq_sep = "=" * param_ref["EqCt"]
            sp_pad = r"\"" if param_ref["Type"] == "str" else ""

            sparam_str = (
                f'{param_ref["Url"]} ' + f"{eq_sep} " + f"[{sp_pad}{param_val}{sp_pad}]"
            )

            if self.query == "":
                self.query = sparam_str
            else:
                self.query = f"{self.query} AND {sparam_str}"

        self.query = f"{self.query} {_QUERY_SUFFIX}"
        self.req_url = Constants.VideoRoom.Queries.get("Query").replace(
            '"query":""', f'"query":"{self.query}"'
        )

    def perform_search(self):
        """Initilization of client
        Passing query URL, specifying Query request type
        Snag query json & length to determine if we've got > 1 result
        """
        query_client = Client(url=self.req_url, req_type="Query")
        self.query_json = query_client.get_json()
        self.clip_ct = len(self.query_json)
        self.play_id = self.query_json[0]["mediaPlayback"][0]["slug"]

    def get_play_id(self):
        """ """
        return self.play_id


for _, row in missed_sample.iterrows():
    srch = Search(download=True, pitch=row.to_dict())
    clp = Clip(play_id=srch.play_id)

# srch = Search(
#     pitch = missed_sample.iloc[0].to_dict(),
# )
# clp = Clip(
#     feed = srch.feed, download = srch.download, play_id = srch.play_id
# )


# for param in srch.params:
#     param_ref = next(filter(lambda x: x['Name'] == param, Constants.VideoRoom.Parameters))
#     param_val = srch.pitch.get(param_ref["Ref"],{})
#     eq_sep = '=' * param_ref['EqCt']
#     sp_pad = r'\"' if param_ref['Type'] == 'str' else ''

#     sparam_str = f'{param_ref["Url"]} ' + \
#         f'{eq_sep} ' + \
#         f'[{sp_pad}{param_val}{sp_pad}]'

#     if srch.query == '':
#         srch.query = sparam_str
#     else:
#         srch.query = f'{srch.query} AND {sparam_str}'

# srch.query = f'{srch.query} {_QUERY_SUFFIX}'
# srch.req_url = Constants.VideoRoom.Queries.get('Query').replace(
#     '"query":""',f'"query":"{srch.query}"'
# )

# query_client = Client(
#     url = srch.req_url,
#     req_type = 'Query'
# )
# srch.query_json = query_client.get_json()
# srch.clip_ct = len(srch.query_json)
