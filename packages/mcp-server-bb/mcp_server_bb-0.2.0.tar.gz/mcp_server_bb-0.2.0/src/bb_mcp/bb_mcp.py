from __future__ import annotations

import asyncio
import base64
import os
from pathlib import Path

import dotenv

from mcp.server.fastmcp import FastMCP

from .config import settings
from .models import CalendarItem, DownloadResult
from .service import (
    BlackboardService,
    CourseLookupError,
    render_announcement,
    render_content_tree,
    render_course_summary,
    render_grade,
    render_todo,
)

mcp = FastMCP("BB-MCP")
dotenv.load_dotenv()
service = BlackboardService()


def _format_section(items: list[str], empty_message: str) -> str:
    return "\n---\n".join(items) if items else f"\n---\n{empty_message}"


def _format_course_not_found(error: CourseLookupError) -> str:
    if error.suggestions:
        suggestion_text = ", ".join(
            f"{course.code} ({course.title})" for course in error.suggestions[:3]
        )
        return f"\n---\nCourse '{error.query}' not found. Did you mean: {suggestion_text}?"
    return f"\n---\nCourse '{error.query}' not found."


@mcp.tool()
async def fetch_course_list() -> str:
    """Get user's enrolled course list from CUHKSZ."""
    courses = await service.get_courses()
    rendered = [render_course_summary(course) for course in courses]
    return _format_section(rendered, "No course found.")


@mcp.tool()
async def fetch_todo() -> str:
    """Get user's todo list from CUHKSZ."""
    items = await service.get_calendar()
    rendered = [_format_calendar(item) for item in items]
    return _format_section(rendered, "No todo items found. You are all set!")


def _format_calendar(item: CalendarItem) -> str:
    return render_todo(item)


@mcp.tool()
async def fetch_announcements(code: str, num: int | None = None) -> str:
    """Get user's announcements from CUHKSZ."""
    try:
        announcements = await service.get_announcements(code, num)
    except CourseLookupError as error:
        return _format_course_not_found(error)
    rendered = [render_announcement(announcement) for announcement in announcements]
    return _format_section(rendered, "No announcements found.")


@mcp.tool()
async def fetch_grades(code: str) -> str:
    """Get user's grades from CUHKSZ."""
    try:
        grades = await service.get_grades(code)
    except CourseLookupError as error:
        return _format_course_not_found(error)
    rendered = [render_grade(grade) for grade in grades]
    return _format_section(rendered, "No grades found.")


@mcp.tool()
async def fetch_content(code: str, verbose: bool = False) -> str:
    """Get course content from CUHKSZ."""
    try:
        folder = await service.get_content_tree(code)
    except CourseLookupError as error:
        return _format_course_not_found(error)
    if verbose:
        return folder.model_dump_json(indent=2)
    return "\n---\n" + render_content_tree(folder)


@mcp.tool()
async def find_content_detail(code: str, folder: str, content: str) -> str:
    """Find content in course."""
    try:
        node = await service.find_content(code, folder, content)
    except CourseLookupError as error:
        return _format_course_not_found(error)
    if node is None:
        return "\n---\nContent not found."
    return "\n---\n" + node.model_dump_json(indent=2)


@mcp.tool()
async def download_file(url: str, name: str, download_dir: str | os.PathLike[str] = ".") -> str:
    """Download file from url."""
    try:
        data, extension = await service.download_file(url, name)
        target_dir = Path(download_dir)
        target_dir.mkdir(parents=True, exist_ok=True)
        base_name = Path(name).stem
        file_name = base_name + extension if extension and not name.endswith(extension) else name
        file_path = target_dir / file_name
        await asyncio.to_thread(file_path.write_bytes, data)

        payload = DownloadResult(
            success=True,
            message="File downloaded successfully",
            file_data=base64.b64encode(data).decode("utf-8"),
            suggested_extension=extension or None,
            file_path=str(file_path),
        )
    except Exception as exc:  # noqa: BLE001
        payload = DownloadResult(success=False, message=str(exc), file_data=None, suggested_extension=None, file_path=None)
    return "\n---\n" + payload.model_dump_json(indent=2)


async def test():
    print("BB_BASE_URL:", settings.bb_base_url)
    while True:
        print("\n请选择要测试的功能：")
        print("1. 获取课程列表(fetch_course_list)")
        print("2. 获取待办(fetch_todo)")
        print("3. 获取公告(fetch_announcements)")
        print("4. 获取成绩(fetch_grades)")
        print("5. 获取内容(fetch_content)")
        print("6. 查找具体内容(find_content_detail)")
        print("7. 下载文件(download_file)")
        print("0. 退出")
        choice = input("输入选项编号: ").strip()
        if choice == "1":
            result = await fetch_course_list()
            print(result)
        elif choice == "2":
            result = await fetch_todo()
            print(result)
        elif choice == "3":
            code = input("课程代码: ").strip()
            num = input("数量(可选): ").strip()
            num_value = int(num) if num else None
            result = await fetch_announcements(code, num_value)
            print(result)
        elif choice == "4":
            code = input("课程代码: ").strip()
            result = await fetch_grades(code)
            print(result)
        elif choice == "5":
            code = input("课程代码: ").strip()
            verbose = input("是否返回详细信息? (y/n): ").strip().lower() == "y"
            result = await fetch_content(code, verbose)
            print(result)
        elif choice == "6":
            code = input("课程代码: ").strip()
            folder = input("文件夹名称: ").strip()
            content = input("内容名称: ").strip()
            result = await find_content_detail(code, folder, content)
            print(result)
        elif choice == "7":
            url = input("文件URL: ").strip()
            name = input("文件名称(含后缀，可选): ").strip() or "downloaded_file"
            download_dir = input("保存目录(默认为当前目录): ").strip() or "."
            result = await download_file(url, name, download_dir)
            print(result)
        elif choice == "0":
            print("退出测试。")
            break
        else:
            print("无效选项，请重新输入。")
    await service.close()


if __name__ == "__main__":
    asyncio.run(test())
