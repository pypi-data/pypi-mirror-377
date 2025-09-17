# -*- coding: utf-8 -*-
"""
OceanBase dialect for cx_oceanbase driver.
"""

from .cx_oracle import OceanBaseDialect_cx_oracle


class OceanBaseDialect_cx_oceanbase(OceanBaseDialect_cx_oracle):
    """
    OceanBase dialect for cx_oracle driver.
    """

    name = "oceanbase"
    driver = "cx_oceanbase"
