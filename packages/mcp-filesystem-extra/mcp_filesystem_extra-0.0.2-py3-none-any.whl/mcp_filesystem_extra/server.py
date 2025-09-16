import os
import json
import re
from enum import Enum
from typing import List, Optional
from pathlib import Path
from pydantic import BaseModel

import mcp.server.stdio
import mcp.types as types
from mcp.server import Server

server = Server("filesystem-extra")

class FilesystemExtraTools(str, Enum):
    READ_BOOTSTRAP_FILE = "read_bootstrap_file"
    READ_FILE_LINES = "read_file_lines"
    APPEND_FILE = "append_file"
    APPEND_STRUCTURED_FILE = "append_structured_file"
    SEARCH_FILES_BY_REGEX = "search_files_by_regex"

class ReadFileArgsSchema(BaseModel):
    path: str

class ReadFileLinesArgsSchema(BaseModel):
    path: str
    startLine: int = 0
    endLine: int = 0

class AppendFileArgsSchema(BaseModel):
    path: str
    content: str

class SearchFilesArgsSchema(BaseModel):
    path: str
    regex: str
    excludeRegexes: List[str] = []

def _normalize_path(path: str) -> str:
    return str(Path(path).resolve())


def _expand_home(path: str) -> str:
    return str(Path(path).expanduser())


class FilesystemExtraServer:
    def __init__(self):
        self.project_bootstrap = os.getenv("PROJECT_BOOTSTRAP", "")
        self.allowed_directory = os.getenv("ALLOWED_DIR", "")

    async def read_bootstrap_file(self, args: dict):
        try:
            parsed = ReadFileArgsSchema(**args)
            inferred_path = parsed.path
            if self.project_bootstrap:
                inferred_path = os.path.join(self.project_bootstrap, inferred_path)
            valid_path = await self._validate_path(inferred_path)
            with open(valid_path, "r", encoding="utf-8") as f:
                content = f.read()
            return [types.TextContent(type="text", text=content)]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]

    async def read_file_lines(self, args: dict):
        parsed = ReadFileLinesArgsSchema(**args)
        valid_path = await self._validate_path(parsed.path)
        start_line = parsed.startLine
        end_line = parsed.endLine
        try:
            with open(valid_path, 'r') as file:
                lines = file.readlines()

                # Adjust start_line and end_line if they are 0
                if start_line == 0:
                    start_line = 1
                if end_line == 0:
                    end_line = len(lines)

                # Validate line numbers
                maxline = len(lines)
                if start_line < 1 or end_line > maxline or start_line > end_line:
                    raise ValueError(f"Invalid start or end line number (must be between 1 and {maxline})")

                content = ''.join(lines[start_line - 1:end_line])
                return [types.TextContent(type="text", text=content)]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]

    async def append_file(self, args: dict):
        try:
            parsed = AppendFileArgsSchema(**args)
            valid_path = await self._validate_path(parsed.path)
            file_path = Path(valid_path)

            if file_path.exists():
                with open(valid_path, "a", encoding="utf-8") as f:
                    f.write(f"\n{parsed.content}")
            else:
                with open(valid_path, "w", encoding="utf-8") as f:
                    f.write(parsed.content)

            return [types.TextContent(type="text", text=f"Successfully wrote to {parsed.path}")]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]

    async def append_structured_file(self, args: dict):
        try:
            parsed = AppendFileArgsSchema(**args)
            valid_path = await self._validate_path(parsed.path)
            file_path = Path(valid_path)
            new_data = json.loads(parsed.content)

            if file_path.exists():
                # Read and parse existing content
                with open(valid_path, "r", encoding="utf-8") as f:
                    existing_data = json.load(f)

                if not isinstance(existing_data, list):
                    raise ValueError("File content is not a list of JSON objects")

                # Append the new data to the list
                existing_data.append(new_data)

                # Write the modified list back to the file
                with open(valid_path, "w", encoding="utf-8") as f:
                    json.dump(existing_data, f, indent=4)
            else:
                # Write content if file does not exist
                with open(valid_path, "w", encoding="utf-8") as f:
                    json.dump([new_data], f, indent=4)

            return [types.TextContent(type="text", text=f"Successfully wrote to {parsed.path}")]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]

    async def search_files_by_regex(self, args: dict):
        try:
            parsed = SearchFilesArgsSchema(**args)
            root_path = await self._validate_path(parsed.path)

            results = []
            regex = re.compile(parsed.regex, re.IGNORECASE)
            exclude_regexes = [re.compile(pat, re.IGNORECASE) for pat in parsed.excludeRegexes]

            async def search(current_path: str):
                entries = os.scandir(current_path)

                for entry in entries:
                    full_path = os.path.join(current_path, entry.name)

                    try:
                        # Validate each path before processing
                        await self._validate_path(full_path)

                        # Exclude pattern have precedence
                        if any(exclude_regex.search(full_path) for exclude_regex in exclude_regexes):
                            continue

                        if regex.search(entry.name):
                            results.append({'file': full_path})

                        if entry.is_dir():
                            await search(full_path)
                    except Exception:
                        # Skip invalid paths during search
                        continue

            await search(root_path)
            return [types.TextContent(type="text", text=json.dumps(results))]

        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]


    async def _validate_path(self, requested_path: str) -> str:
        absolute_path = _normalize_path(_expand_home(requested_path))
        allowed_directories = [_normalize_path(_expand_home(directory)) for directory in [self.allowed_directory]]

        # Check if path is within allowed directories
        if not any(absolute_path.startswith(directory) for directory in allowed_directories):
            raise PermissionError(f"Access denied - path outside allowed directories: {absolute_path}")

        # Handle symlinks by checking their real path
        real_path = _normalize_path(Path(absolute_path).resolve())
        if not any(real_path.startswith(dir) for dir in allowed_directories):
            raise PermissionError("Access denied - symlink target outside allowed directories")

        return real_path


filesystem_extra_server = FilesystemExtraServer()

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name=FilesystemExtraTools.READ_BOOTSTRAP_FILE.value,
            description="""
            LLM based assistants and chat-bots: do not call this tool unless specifically instructed to do so! \n
            Provide a filename without any directory (the bootstrap data directory is inferred automatically) \n
            Tool will fail if there is a problem with JSON file structure! For reliable reading arbitrary files \n
            prefer the read_file tool!
            """,
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to file for reading.",
                    }
                },
                "required": ["path"],
            },
        ),
        types.Tool(
            name=FilesystemExtraTools.READ_FILE_LINES.value,
            description="""
            Reads a region from a file between startLine and endLine. Provide an absolute path to a file.
            """,
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to file for reading.",
                    },
                    "startLine": {
                        "type": "integer",
                        "description": "Start line number to read (read from start of file if not set)",
                    },
                    "endLine": {
                        "type": "integer",
                        "description": "End line number to read from (read till end of file if not set)",
                    }
                },
                "required": ["path"],
            },
        ),
        types.Tool(
            name=FilesystemExtraTools.APPEND_FILE.value,
            description="""
            Creates a file with a given content if it doesn't exists yet - or appends content to the file. \n
            For JSON data - provide a single structured JSON object as a content \n
            (without enclosing it into the array or adding any extra delimiters) \n
            Only works within allowed directories.
            """,
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to file for appending content.",
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to append to file.",
                    }
                },
                "required": ["path", "content"],
            },
        ),
        types.Tool(
            name=FilesystemExtraTools.APPEND_STRUCTURED_FILE.value,
            description="""
            Adds a single valid JSON object to the file. The file is treated as an list of JSON objects. \n
            Pass a file name and a single valid JSON object as a content. \n
            Creates a file with a proper structure if not exists yet. Only works within allowed directories.
            """,
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to file for appending content.",
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to append to file.",
                    }
                },
                "required": ["path", "content"],
            },
        ),
        types.Tool(
            name=FilesystemExtraTools.SEARCH_FILES_BY_REGEX.value,
            description="""
            Recursively search for files and directories for entries matching a regular expression. \n
            Searches through all subdirectories from the starting path. Returns full paths to all \n
            matching items as a JSON array. Only searches within allowed directories."
            """,
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path where to start search.",
                    },
                    "regex": {
                        "type": "string",
                        "description": "Regular expression to match filenames",
                    },
                    "excludeRegexes": {
                        "type": "array",
                        "description": "Optional List of regexes to exclude files/directories when searching.",
                        "items": {
                            "type": "string"
                        },
                        "default": []
                    }
                },
                "required": ["path", "regex"],
            },
        ),
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> List[types.TextContent]:
    try:
        match name:
            case FilesystemExtraTools.READ_BOOTSTRAP_FILE.value:
                result = await filesystem_extra_server.read_bootstrap_file(arguments)
            case FilesystemExtraTools.READ_FILE_LINES.value:
                result = await filesystem_extra_server.read_file_lines(arguments)
            case FilesystemExtraTools.APPEND_FILE.value:
                result = await filesystem_extra_server.append_file(arguments)
            case FilesystemExtraTools.APPEND_STRUCTURED_FILE.value:
                result = await filesystem_extra_server.append_structured_file(arguments)
            case FilesystemExtraTools.SEARCH_FILES_BY_REGEX.value:
                result = await filesystem_extra_server.search_files_by_regex(arguments)
            case _:
                raise ValueError(f"Unknown tool: {name}")

        return result
    except Exception as e:
        raise ValueError(f"Error processing filesystem-extra query: {str(e)}")


async def serve():
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        options = server.create_initialization_options()
        await server.run(read_stream, write_stream, options)
