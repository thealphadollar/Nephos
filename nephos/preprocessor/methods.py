"""
Contains all the methods applied in preprocessing
"""


class ApplyProcessMethods:

    def __init__(self, path_to_file):
        """
        Loads the file to be processed and applies all the methods till new file output.

        Parameters
        ----------
        path_to_file
            type: str
            path to file to be processed

        """
        self.addr = path_to_file
        # TODO: Complete this

    @staticmethod
    def get_lang(path_to_file):
        """
        Uses ffprobe to gather information about languages present in the stream.

        Parameters
        ----------
        path_to_file
            type: str
            path to file to be processed

        Returns
        -------
        lang
            type: str
            audio languages
        sub_lang
            type: str
            subtitle languages

        """
        # TODO: use ffprobe
        lang = ["eng"]
        sub_lang = ["eng", "spa"]

        return " ".join(lang), " ".join(sub_lang)
