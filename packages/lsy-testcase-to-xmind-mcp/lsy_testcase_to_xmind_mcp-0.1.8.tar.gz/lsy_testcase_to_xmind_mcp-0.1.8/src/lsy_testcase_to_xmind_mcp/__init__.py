import xmind
import json
import zipfile
import os
import tempfile
import time
from typing import Dict
from mcp.server import FastMCP

# Create an MCP server
mcp = FastMCP("lsy-testcase-to-xmind")


def create_xmind_from_test_cases(test_case_data: Dict, output_path: str):
    """
    根据测试用例JSON数据创建XMind文件，根据path字段创建层级结构

    Args:
        test_case_data: 测试用例JSON数据
        output_path: 输出XMind文件路径
    """
    # 检查文件是否存在，如果存在则删除
    if os.path.exists(output_path):
        try:
            os.remove(output_path)
            print(f"已删除已存在的文件: {output_path}")
        except Exception as e:
            print(f"删除文件时出错: {e}")
            return False

    # 创建一个新的工作簿
    workbook = xmind.load(output_path)

    # 获取第一个画布
    sheet = workbook.getPrimarySheet()

    # 设置画布标题
    sheet.setTitle(test_case_data["feature"])

    # 获取根主题
    root_topic = sheet.getRootTopic()
    root_topic.setTitle(test_case_data["feature"])

    # 为每个测试用例创建层级结构
    for test_case in test_case_data["test_cases"]:
        # 解析路径，创建层级结构
        path_parts = test_case["path"].split('/')
        current_topic = root_topic

        # 遍历路径的每一部分，创建或获取对应的主题
        for i, part in enumerate(path_parts):
            # 检查当前层级是否已存在同名主题
            existing_topics = current_topic.getSubTopics()
            found = False

            for topic in existing_topics:
                if topic.getTitle() == part:
                    current_topic = topic
                    found = True
                    break

            # 如果不存在，创建新主题
            if not found:
                new_topic = current_topic.addSubTopic()
                new_topic.setTitle(part)
                current_topic = new_topic

        # 在路径的最后一层创建测试用例主题（名称前加上优先级）
        case_topic = current_topic.addSubTopic()
        priority = test_case["priority"].replace('p', '')
        case_title = f"tc-p{priority}：{test_case['name']}"
        case_topic.setTitle(case_title)

        # 设置优先级标记
        priority_markers = {
            "p0": "priority-1",
            "p1": "priority-2",
            "p2": "priority-3",
            "p3": "priority-4"
        }
        if test_case["priority"] in priority_markers:
            case_topic.addMarker(priority_markers[test_case["priority"]])

        # 添加前置条件（如果有）- 使用pc：中文冒号
        if test_case.get("preconditions"):
            preconditions_topic = case_topic.addSubTopic()
            preconditions_topic.setTitle(f"pc：{test_case['preconditions']}")

        # 添加测试步骤（步骤描述和期望结果分成两级）
        for step in test_case["steps"]:
            # 创建步骤主题
            step_topic = case_topic.addSubTopic()
            step_topic.setTitle(step["action"])

            # 创建期望结果子主题
            result_topic = step_topic.addSubTopic()
            result_topic.setTitle(step["expected_result"])

        # 添加备注（如果有）- 使用rc：中文冒号
        if test_case.get("remark"):
            remark_topic = case_topic.addSubTopic()
            remark_topic.setTitle(f"rc：{test_case['remark']}")

    # 保存工作簿
    xmind.save(workbook, output_path)

    # 修复XMind文件的META-INF结构
    fix_xmind_structure(output_path)

    print(f"XMind文件已生成: {output_path}")
    return True


def fix_xmind_structure(xmind_path: str):
    """
    修复XMind文件的META-INF结构

    Args:
        xmind_path: XMind文件路径
    """
    # 创建临时目录
    with tempfile.TemporaryDirectory() as temp_dir:
        # 解压XMind文件
        with zipfile.ZipFile(xmind_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)

        # 检查并创建META-INF目录
        meta_inf_dir = os.path.join(temp_dir, "META-INF")
        if not os.path.exists(meta_inf_dir):
            os.makedirs(meta_inf_dir)

        # 检查并创建manifest.xml文件
        manifest_path = os.path.join(meta_inf_dir, "manifest.xml")
        if not os.path.exists(manifest_path):
            with open(manifest_path, 'w', encoding='utf-8') as f:
                f.write('''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<manifest xmlns="urn:xmind:xmap:xmlns:manifest:1.0">
    <file-entry full-path="content.xml" media-type="text/xml"/>
    <file-entry full-path="META-INF/" media-type=""/>
    <file-entry full-path="META-INF/manifest.xml" media-type="text/xml"/>
    <file-entry full-path="meta.xml" media-type="text/xml"/>
    <file-entry full-path="styles.xml" media-type="text/xml"/>
    <file-entry full-path="comments.xml" media-type="text/xml"/>
    <file-entry full-path="Thumbnails/" media-type=""/>
    <file-entry full-path="Thumbnails/thumbnail.png" media-type="image/png"/>
</manifest>''')

        # 检查并创建meta.xml文件
        meta_path = os.path.join(temp_dir, "meta.xml")
        if not os.path.exists(meta_path):
            with open(meta_path, 'w', encoding='utf-8') as f:
                f.write('''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<meta xmlns="urn:xmind:xmap:xmlns:meta:2.0" version="2.0">
    <Author>XMind Python Generator</Author>
    <CreateTime>{}</CreateTime>
</meta>'''.format(int(time.time() * 1000)))

        # 重新压缩文件
        with zipfile.ZipFile(xmind_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, temp_dir)
                    zipf.write(file_path, arcname)

@mcp.tool(name="generate_xmind")
def safe_create_xmind(test_case_data: Dict, output_path: str):
    """
    安全创建XMind文件，处理各种异常情况

    Args:
        test_case_data: 测试用例JSON数据
        output_path: 输出XMind文件路径
    """
    try:
        return create_xmind_from_test_cases(test_case_data, output_path)
    except Exception as e:
        print(f"创建XMind文件时出错: {e}")
        return False


def main() -> None:
    # 启动MCP服务，使用标准输入输出作为传输方式
    mcp.run(transport='stdio')

