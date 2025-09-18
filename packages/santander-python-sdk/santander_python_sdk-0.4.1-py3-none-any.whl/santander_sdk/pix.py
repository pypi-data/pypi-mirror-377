from decimal import Decimal as D
import uuid
from typing import cast

from santander_sdk.api_client.client import SantanderApiClient
from santander_sdk.api_client.exceptions import SantanderClientError

from santander_sdk.api_client.helpers import (
    get_pix_key_type,
    truncate_value,
)
from santander_sdk.transfer_flow import SantanderPaymentFlow
from santander_sdk.types import (
    SantanderBeneficiary,
    SantanderPixResponse,
    TransferPixResult,
)

PIX_ENDPOINT = "/management_payments_partners/v1/workspaces/:workspaceid/pix_payments"


def transfer_pix(
    client: SantanderApiClient,
    pix_key: str | SantanderBeneficiary,
    value: D,
    description: str,
    tags: list[str] = [],
    id: uuid.UUID | str | None = None,
) -> TransferPixResult:
    transfer_flow = SantanderPaymentFlow(client, PIX_ENDPOINT)

    try:
        if value is None or value <= 0:
            raise ValueError(f"Invalid value for PIX transfer: {value}")

        create_pix_dict = _generate_create_pix_dict(
            pix_key, value, description, tags, id
        )
        create_pix_response = transfer_flow.create_payment(create_pix_dict)
        if not create_pix_response.get("id"):
            raise SantanderClientError("Payment ID was not returned on creation")
        if create_pix_response.get("status") is None:
            raise SantanderClientError("Payment status was not returned on creation")

        transfer_flow.ensure_ready_to_pay(create_pix_response)
        payment_data = {
            "status": "AUTHORIZED",
            "paymentValue": truncate_value(value),
        }
        confirm_response = transfer_flow.confirm_payment(
            payment_data, create_pix_response.get("id")
        )
        return {
            "success": True,
            "request_id": transfer_flow.request_id,
            "data": confirm_response,
            "error": "",
        }
    except Exception as e:
        error_message = str(e)
        client.logger.error(error_message)
        return {
            "success": False,
            "request_id": transfer_flow.request_id,
            "error": error_message,
            "data": None,
        }


def get_transfer(
    client: SantanderApiClient, pix_payment_id: str
) -> SantanderPixResponse:
    if not pix_payment_id:
        raise ValueError("pix_payment_id not provided")
    response = client.get(f"{PIX_ENDPOINT}/{pix_payment_id}")
    return cast(SantanderPixResponse, response)


def _generate_create_pix_dict(
    pix_key: SantanderBeneficiary | str,
    value: D,
    description: str,
    tags: list = [],
    id: uuid.UUID | str | None = None,
) -> dict:
    data = {
        "tags": tags,
        "paymentValue": truncate_value(value),
        "remittanceInformation": description,
    }

    if id:
        data["id"] = str(id)

    if isinstance(pix_key, str):
        pix_type = get_pix_key_type(pix_key)
        data.update({"dictCode": pix_key, "dictCodeType": pix_type})
        return data

    if isinstance(pix_key, dict):
        beneficiary = cast(dict, pix_key.copy())
        if beneficiary.get("bankCode") is None and beneficiary.get("ispb") is None:
            raise ValueError("Either 'bankCode' or 'ispb' must be provided")
        if beneficiary.get("bankCode") and beneficiary.get("ispb"):
            beneficiary.pop("ispb")
        data.update({"beneficiary": beneficiary})
    else:
        raise ValueError("PIX key or Beneficiary not provided")
    return data
