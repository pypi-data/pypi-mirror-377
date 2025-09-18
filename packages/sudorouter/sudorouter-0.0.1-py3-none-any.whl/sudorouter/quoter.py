import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict

from .tdx import verify_raw_quote


@dataclass
class Report:
    user_data: bytes
    nonce: bytes
    measure: Dict[str, bytes] = field(default_factory=dict)


class TeeType(Enum):
    mock = "mock"
    tdx = "tdx"
    tsm_tdx = "tsm-tdx"


class TeeQuoter(ABC):
    @abstractmethod
    def verify(self, quote_data: bytes, nonce_data: bytes) -> Report:
        pass


class TeeMockQuoter(TeeQuoter):
    def verify(self, quote_data: bytes, nonce_data: bytes) -> Report:
        return Report(
            user_data=quote_data,
            nonce=nonce_data,
            measure={
                "measure_1": os.urandom(32),
                "measure_2": os.urandom(32),
            },
        )


class TeeTdxQuoter(TeeQuoter):
    def verify(self, quote_data: bytes, nonce_data: bytes) -> Report:
        quote = verify_raw_quote(quote_data)
        nonce = quote.report_body.report_data[32:]
        if nonce_data != nonce:
            raise ValueError("nonce incorrect")
        return Report(
            user_data=quote.report_body.report_data[:32],
            nonce=nonce,
            measure={
                "mr_td": quote.report_body.mr_td,
                "rt_mr_0": quote.report_body.rt_mr[0],
                "rt_mr_1": quote.report_body.rt_mr[1],
                "rt_mr_2": quote.report_body.rt_mr[2],
                "rt_mr_3": quote.report_body.rt_mr[3],
            },
        )


def get_tee_quoter(type: TeeType) -> TeeQuoter:
    if type == TeeType.mock:
        return TeeMockQuoter()
    if type == TeeType.tdx:
        return TeeTdxQuoter()
    if type == TeeType.tsm_tdx:
        return TeeTdxQuoter()
    raise ValueError(f"unknown tee type: {type}")
