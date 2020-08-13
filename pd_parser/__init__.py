"""A toolbox for parsing potentially corrupted photodiode events."""

__version__ = '0.1'


from pd_parser.parse_pd import (parse_pd, diagnose_parser_issues,  # noqa
                                add_relative_events,  # noqa
                                add_events_to_raw, save_to_bids)  # noqa
