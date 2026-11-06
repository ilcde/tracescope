"""Process-tree resource controls. Explicitly NOT an isolation boundary."""
import os
if os.name=='nt':
    import ctypes as c
    from ctypes import wintypes as w
    class Basic(c.Structure):
        _fields_=[('processTime',c.c_int64),('jobTime',c.c_int64),('flags',w.DWORD),('minimum',c.c_size_t),('maximum',c.c_size_t),('active',w.DWORD),('affinity',c.c_size_t),('priority',w.DWORD),('scheduling',w.DWORD)]
    class IO(c.Structure):
        _fields_=[(n,c.c_uint64) for n in ('readOps','writeOps','otherOps','readBytes','writeBytes','otherBytes')]
    class Extended(c.Structure):
        _fields_=[('basic',Basic),('io',IO),('processMemory',c.c_size_t),('jobMemory',c.c_size_t),('peakProcessMemory',c.c_size_t),('peakJobMemory',c.c_size_t)]
    kernel=c.WinDLL('kernel32',use_last_error=True)
    kernel.CreateJobObjectW.argtypes=[c.c_void_p,w.LPCWSTR];kernel.CreateJobObjectW.restype=w.HANDLE
    kernel.SetInformationJobObject.argtypes=[w.HANDLE,c.c_int,c.c_void_p,w.DWORD];kernel.SetInformationJobObject.restype=w.BOOL
    kernel.AssignProcessToJobObject.argtypes=[w.HANDLE,w.HANDLE];kernel.AssignProcessToJobObject.restype=w.BOOL
    kernel.TerminateJobObject.argtypes=[w.HANDLE,w.UINT];kernel.TerminateJobObject.restype=w.BOOL
    kernel.CloseHandle.argtypes=[w.HANDLE];kernel.CloseHandle.restype=w.BOOL
    kernel.QueryInformationJobObject.argtypes=[w.HANDLE,c.c_int,c.c_void_p,w.DWORD,c.c_void_p];kernel.QueryInformationJobObject.restype=w.BOOL

class ProcessLimits:
    def __init__(self,process):
        self.handle=None;self.status='unavailable';self.error=None
        if os.name!='nt':return
        handle=kernel.CreateJobObjectW(None,None)
        if not handle:self.error='CreateJobObject failed';return
        info=Extended();info.basic.flags=0x2000|0x8|0x200|0x4 # kill on close, process count, total memory, job CPU
        info.basic.active=24;info.basic.jobTime=60*10_000_000;info.jobMemory=1024*1024*1024
        if not kernel.SetInformationJobObject(handle,9,c.byref(info),c.sizeof(info)) or not kernel.AssignProcessToJobObject(handle,int(process._handle)):
            self.error='Job assignment failed: '+str(c.get_last_error());kernel.CloseHandle(handle);return
        self.handle=handle;self.status='Windows Job: 1 GiB committed memory, 24 processes, 60 s job CPU; not sandboxed'
    def peak(self):
        if self.handle:
            info=Extended()
            if kernel.QueryInformationJobObject(self.handle,9,c.byref(info),c.sizeof(info),None):return info.peakJobMemory
        return None
    def terminate(self):
        if self.handle:kernel.TerminateJobObject(self.handle,1)
    def close(self):
        if self.handle:kernel.CloseHandle(self.handle);self.handle=None
