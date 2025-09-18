r"""Cached database functions."""

# Standard library
from datetime import timedelta

# Third party
import streamlit as st

# Local
from cambiato.database import (
    get_all_active_orders,
    get_all_checklists,
    get_all_facilities,
    get_all_order_statuses,
    get_all_order_types,
    get_all_technicians,
    get_all_utilities,
)

hour_1 = timedelta(hours=1)

get_all_checklists_cached = st.cache_resource(ttl=hour_1)(get_all_checklists)
get_all_facilities_cached = st.cache_resource(ttl=hour_1)(get_all_facilities)
get_all_order_statuses_cached = st.cache_resource(ttl=hour_1)(get_all_order_statuses)
get_all_order_types_cached = st.cache_resource(ttl=hour_1)(get_all_order_types)
get_all_orders_cached = st.cache_resource(ttl=hour_1)(get_all_active_orders)
get_all_technicians_cached = st.cache_resource(ttl=hour_1)(get_all_technicians)
get_all_utilities_cached = st.cache_resource(ttl=hour_1)(get_all_utilities)
