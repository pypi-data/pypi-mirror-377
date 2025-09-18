# SPDX-License-Identifier: Apache-2.0
# Copyright 2024 Mike Schultz

from pjk.sources.csv_source import CSVSource
from pjk.sources.lazy_file import LazyFile
from pjk.sources.format_usage import FormatUsage

class TSVSource(CSVSource):
    is_format = True
    @classmethod
    def usage(cls):
        return FormatUsage('tsv', component_class=cls)
    
    def __init__(self, lazy_file: LazyFile):
        super().__init__(lazy_file, delimiter="\t")
