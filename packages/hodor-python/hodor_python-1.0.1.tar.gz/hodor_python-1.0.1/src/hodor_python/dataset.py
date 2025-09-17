import pandas as pd
from pathlib import Path
from enum import Enum
from pangaeapy import PanDataSet


class Species(str, Enum):
    """Enum for species in the HODOR dataset. Use it e.g. to filter data by species."""

    ANGUILLA_ANGUILLA = "anguilla_anguilla"
    BIRD_CORMORANT = "bird_cormorant"
    BIRD_UNSPECIFIED = "bird_unspecified"
    CRAB_CRUSTACEA = "crab_crustacea"
    FISH_CLUPEIDAE = "fish_clupeidae"
    FISH_COD = "fish_cod"
    FISH_MACKEREL = "fish_mackerel"
    FISH_MUGILIDAE = "fish_mugilidae"
    FISH_ONCORHYNCHUS = "fish_oncorhynchus"
    FISH_PIPEFISH = "fish_pipefish"
    FISH_PLAICE = "fish_plaice"
    FISH_SALMONIDAE = "fish_salmonidae"
    FISH_SCAD = "fish_scad"
    FISH_UNSPECIFIED = "fish_unspecified"
    JELLYFISH_AURELIA = "jellyfish_aurelia"
    JELLYFISH_CTENOPHORA = "jellyfish_ctenophora"
    JELLYFISH_CYANEA = "jellyfish_cyanea"
    JELLYFISH_UNSPECIFIED = "jellyfish_unspecified"


class HODOR_Dataset:
    # The base HODOR dataset (parent for the subsets: video, sonar, activity_counts)
    HODOR_BASE_DOI = "doi:10.1594/PANGAEA.980000"
    # The video data subset
    HODOR_VIDEO_DOI = "doi:10.1594/PANGAEA.980001"
    # The sonar data subset
    HODOR_SONAR_DOI = "doi:10.1594/PANGAEA.980002"
    # The activity counts subset
    HODOR_COUNTS_DOI = "doi:10.1594/PANGAEA.980059"

    def __init__(self, dataset_folder: str):
        self.dataset_folder = Path(dataset_folder)

        # internally used pangaeapy datasets
        self._counts = PanDataSet(self.HODOR_COUNTS_DOI, cachedir=self.dataset_folder)
        self._video_data = PanDataSet(
            self.HODOR_VIDEO_DOI,
            enable_cache=False,
            cachedir=self.dataset_folder.joinpath("Camera"),
        )
        self._sonar_data = PanDataSet(
            self.HODOR_SONAR_DOI,
            enable_cache=False,
            cachedir=self.dataset_folder.joinpath("Sonar"),
        )

        self.counts: pd.DataFrame = self._load_dataframe()

    def _load_dataframe(self) -> pd.DataFrame:
        """
        Converts the pangaeapy dataframe into a more user-friendly DataFrame.
        It converts the "Date/time start" and "Date/time end" columns to datetime objects,
        and renames the columns to more readable names.
        Returns:
            pandas.DataFrame: The loaded and processed DataFrame with standardized column names.
        """

        # remove unused columns
        df = self._counts.data.drop(
            columns=["Event", "Latitude", "Longitude", "Date/Time"]
        )

        # Convert datetime columns
        df["Date/time start"] = pd.to_datetime(df["Date/time start"])
        df["Date/time end"] = pd.to_datetime(df["Date/time end"])

        # use prettier column names
        df.columns = [
            "SeqID",
            "sequenceStartUnix",
            "sequenceEndUnix",
            "DateTimeStart",
            "DateTimeEnd",
        ] + [s.value for s in Species]

        # new column which holds the duration of each sequence
        df.insert(5, "sequence_length", df["DateTimeEnd"] - df["DateTimeStart"])

        return df

    def download_video(self, sequence_ids: int | list[int]):
        """Downloads the video data for a single sequence id or a list of ids."""
        if isinstance(sequence_ids, int):
            sequence_ids = [sequence_ids]
        self._video_data.download(sequence_ids)

    def download_sonar(self, sequence_ids: int | list[int]):
        """Downloads the sonar data for a single sequence id or a list of ids."""
        if isinstance(sequence_ids, int):
            sequence_ids = [sequence_ids]
        self._sonar_data.download(sequence_ids)

    def download_sequence(self, sequence_ids: int | list[int]):
        """Downloads the complete data for a single sequence id or a list of ids.

        This will include the stereo video as well as the sonar data for this sequence.
        To download only the video data, use `download_video` instead.
        To download only the sonar data, use `download_sonar` instead.
        """
        if isinstance(sequence_ids, int):
            sequence_ids = [sequence_ids]

        self.download_video(sequence_ids)
        self.download_sonar(sequence_ids)
