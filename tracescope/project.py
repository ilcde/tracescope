"""Validate and stage a portable source project separately from generated files."""
from pathlib import PurePosixPath

def validate_files(files,entry,source):
    if not isinstance(files,dict) or len(files)>64:raise ValueError('Project must contain at most 64 text files')
    result=dict(files);result[entry]=source
    total=0
    for name,text in result.items():
        if not isinstance(name,str) or not isinstance(text,str):raise ValueError('Project files must map relative paths to text')
        path=PurePosixPath(name)
        if not name or path.is_absolute() or '\\' in name or ':' in name or any(p in ('..','.git','.env') for p in path.parts) or '\x00' in name:raise ValueError('Unsafe project path')
        total+=len(text.encode('utf-8'))
        if len(text)>100000 or total>1000000:raise ValueError('Project source quota exceeded')
    return result
