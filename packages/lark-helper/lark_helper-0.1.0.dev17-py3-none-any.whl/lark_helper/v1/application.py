from lark_helper.token_manager import TenantAccessTokenManager
from lark_helper.utils.request import make_lark_request


def get_application_info(
    token_manager: TenantAccessTokenManager,
    app_id: str,
) -> dict:
    """
    获取应用信息
    https://open.feishu.cn/document/server-docs/application-v6/application/get

    Returns:
        dict: 应用信息数据

    Raises:
        LarkResponseError: 当API调用失败时抛出
    """
    url = f"https://open.feishu.cn/open-apis/application/v6/applications/{app_id}?lang=zh_cn"
    headers = {
        "Authorization": f"Bearer {token_manager.get_tenant_access_token()}",
        "Content-Type": "application/json; charset=utf-8",
    }

    def extract_data(data):
        return data

    return make_lark_request(method="GET", url=url, headers=headers, data_extractor=extract_data)
