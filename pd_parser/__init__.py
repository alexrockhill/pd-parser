"""A toolbox for parsing potentially corrupted photodiode events."""

__version__ = '0.2.dev0'


from pd_parser.parse_pd import (find_pd_params, parse_pd,  # noqa
                                add_pd_off_events, add_pd_relative_events,  # noqa
                                add_pd_events_to_raw, pd_parser_save_to_bids,
                                simulate_pd_data)  # noqa
