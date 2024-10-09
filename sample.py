import json
import os
import base64
from flask import Flask, request, jsonify
from flask_cors import CORS  # 添加这行
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.lke.v20231130 import lke_client, models

app = Flask(__name__)
CORS(app)  # 添加这行

def reconstruct_document(file_url, mode):
    """
    使用腾讯云文档重建服务解析指定 URL 的文档。

    Args:
        file_url (str): 要解析的文档的 URL。
        mode (str): 解析模式，'01' 返回 Markdown 文本，'02' 返回 MarkdownBase64。

    Returns:
        dict: 包含状态码、消息和结果的字典。
    """
    try:
        # 从环境变量获取 SecretId 和 SecretKey
        secret_id = os.environ.get("TENCENT_SECRET_ID")
        secret_key = os.environ.get("TENCENT_SECRET_KEY")

        if not secret_id or not secret_key:
            raise ValueError("请设置 TENCENT_SECRET_ID 和 TENCENT_SECRET_KEY 环境变量")

        # 实例化认证对象
        cred = credential.Credential(secret_id, secret_key)

        # 配置 HTTP 选项
        http_profile = HttpProfile()
        http_profile.endpoint = "lke.tencentcloudapi.com"

        # 配置客户端选项
        client_profile = ClientProfile()
        client_profile.httpProfile = http_profile

        # 实例化 LKE 客户端
        client = lke_client.LkeClient(cred, "ap-guangzhou", client_profile)

        # 准备请求参数
        req = models.ReconstructDocumentRequest()
        params = {
            "FileUrl": file_url
        }
        req.from_json_string(json.dumps(params))

        # 发送请求并获取响应
        resp = client.ReconstructDocument(req)
        json_result = json.loads(resp.to_json_string())
        
        # 获取 MarkdownBase64 并解码
        markdown_base64 = json_result.get('MarkdownBase64', '')
        
        if mode == '01':
            result = base64.b64decode(markdown_base64).decode('utf-8')
        elif mode == '02':
            result = markdown_base64
        else:
            return {
                "code": "98",
                "msg": "解析失败",
                "result": "参数错误"
            }
        
        return {
            "code": "01",
            "msg": "解析成功",
            "result": result
        }

    except (TencentCloudSDKException, ValueError, Exception) as err:
        return {
            "code": "99",
            "msg": "解析失败",
            "result": str(err)
        }

@app.route('/parse_document', methods=['POST'])
def parse_document():
    data = request.json
    file_url = data.get('fileurl')
    mode = data.get('mode')
    
    if not file_url:
        return jsonify({
            "code": "99",
            "msg": "解析失败",
            "result": "缺少 fileurl 参数"
        }), 400

    if mode not in ['01', '02']:
        return jsonify({
            "code": "98",
            "msg": "解析失败",
            "result": "参数错误"
        }), 400

    result = reconstruct_document(file_url, mode)
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8999)
