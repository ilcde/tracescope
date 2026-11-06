"""Freestanding real CPU emulation. No operating system or invented instructions."""
import io, os, re, subprocess, sys, tempfile, time
from pathlib import Path
import unicorn as u, capstone as c, keystone as k
from unicorn import x86_const as x, arm_const as a, arm64_const as a64, riscv_const as r
from .protocol import Recorder, digest

PROFILES={
 'x86-16':(u.UC_ARCH_X86,u.UC_MODE_16,c.CS_ARCH_X86,c.CS_MODE_16,k.KS_ARCH_X86,k.KS_MODE_16,16,'x86 16-bit real mode (386+ instruction set)'),
 'x86-32':(u.UC_ARCH_X86,u.UC_MODE_32,c.CS_ARCH_X86,c.CS_MODE_32,k.KS_ARCH_X86,k.KS_MODE_32,32,'i386'),
 'x86-64':(u.UC_ARCH_X86,u.UC_MODE_64,c.CS_ARCH_X86,c.CS_MODE_64,k.KS_ARCH_X86,k.KS_MODE_64,64,'x86-64'),
 'arm32':(u.UC_ARCH_ARM,u.UC_MODE_ARM,c.CS_ARCH_ARM,c.CS_MODE_ARM,k.KS_ARCH_ARM,k.KS_MODE_ARM,32,'ARMv7 ARM'),
 'thumb':(u.UC_ARCH_ARM,u.UC_MODE_THUMB,c.CS_ARCH_ARM,c.CS_MODE_THUMB,k.KS_ARCH_ARM,k.KS_MODE_THUMB,32,'ARMv7 Thumb'),
 'arm64':(u.UC_ARCH_ARM64,u.UC_MODE_ARM,c.CS_ARCH_ARM64,c.CS_MODE_ARM,k.KS_ARCH_ARM64,k.KS_MODE_LITTLE_ENDIAN,64,'AArch64'),
 'rv32':(u.UC_ARCH_RISCV,u.UC_MODE_RISCV32,c.CS_ARCH_RISCV,c.CS_MODE_RISCV32,None,None,32,'RV32I'),
 'rv64':(u.UC_ARCH_RISCV,u.UC_MODE_RISCV64,c.CS_ARCH_RISCV,c.CS_MODE_RISCV64,None,None,64,'RV64I'),
}

def assemble(source,profile,syntax='intel'):
    if re.search(r'(?im)^\s*\.(?:incbin|include|file|include_next)\b',source):
        raise ValueError('External-file assembler directives are not supported')
    p=PROFILES[profile]
    if profile.startswith('rv'):
        import ziglang
        from elftools.elf.elffile import ELFFile
        zig=Path(ziglang.__file__).parent/('zig.exe' if os.name=='nt' else 'zig')
        with tempfile.TemporaryDirectory() as tmp:
            src=Path(tmp)/'main.s'; out=Path(tmp)/'main.elf'; src.write_text('.option norelax\n.option norvc\n.text\n.globl _start\n_start:\n'+source,encoding='utf-8')
            target='riscv32-freestanding' if profile=='rv32' else 'riscv64-freestanding'
            script=Path(tmp)/'link.ld';script.write_text('ENTRY(_start)\nSECTIONS { . = 0x1000; .text : { *(.text*) } }')
            env=os.environ.copy();env['ZIG_GLOBAL_CACHE_DIR']=str(Path(__file__).resolve().parent.parent/'.cache/zig')
            proc=subprocess.run([str(zig),'cc','-target',target,'-mcpu='+('generic_rv32' if profile=='rv32' else 'generic_rv64'),'-mabi='+('ilp32' if profile=='rv32' else 'lp64'),'-nostdlib','-T',str(script),str(src),'-o',str(out)],capture_output=True,text=True,env=env,timeout=30)
            if proc.returncode: raise ValueError(proc.stderr)
            with out.open('rb') as f: return ELFFile(f).get_section_by_name('.text').data()
    asm=k.Ks(p[4],p[5])
    # Keystone 0.9.2 changes literal radix when INTEL is explicitly re-set; preserve its decimal default.
    if profile.startswith('x86') and syntax=='att': asm.syntax=k.KS_OPT_SYNTAX_ATT
    result,_=asm.asm(source,addr=0x1000)
    return bytes(result)

def run(config,emit):
    profile=config.get('profile','x86-64'); p=PROFILES[profile]
    start=time.perf_counter_ns(); code=assemble(config['source'],profile,config.get('syntax','intel'))
    if len(code)>32768: raise ValueError('Machine code exceeds 32 KiB')
    compile_ms=(time.perf_counter_ns()-start)/1e6
    engine=u.Uc(p[0],p[1]); engine.mem_map(0,0x20000); engine.mem_write(0x1000,code)
    dis=c.Cs(p[2],p[3]); dis.detail=True
    if profile.startswith('x86') and config.get('syntax')=='att': dis.syntax=c.CS_OPT_SYNTAX_ATT
    width=p[6]
    if profile.startswith('x86'):
        names=['ax','bx','cx','dx','si','di','bp','sp','ip'] if width==16 else (['eax','ebx','ecx','edx','esi','edi','ebp','esp','eip'] if width==32 else ['rax','rbx','rcx','rdx','rsi','rdi','rbp','rsp','rip','r8','r9','r10','r11','r12','r13','r14','r15'])
        regs={name:getattr(x,'UC_X86_REG_'+name.upper()) for name in names}; regs['eflags']=x.UC_X86_REG_EFLAGS
        pc=regs['ip' if width==16 else 'eip' if width==32 else 'rip']; sp=regs['sp' if width==16 else 'esp' if width==32 else 'rsp']
    elif profile in ('arm32','thumb'):
        regs={f'r{i}':getattr(a,f'UC_ARM_REG_R{i}') for i in range(13)}; regs.update(sp=a.UC_ARM_REG_SP,lr=a.UC_ARM_REG_LR,pc=a.UC_ARM_REG_PC,cpsr=a.UC_ARM_REG_CPSR);pc=regs['pc'];sp=regs['sp']
    elif profile=='arm64':
        regs={f'x{i}':getattr(a64,f'UC_ARM64_REG_X{i}') for i in range(31)};regs.update(sp=a64.UC_ARM64_REG_SP,pc=a64.UC_ARM64_REG_PC,nzcv=a64.UC_ARM64_REG_NZCV);pc=regs['pc'];sp=regs['sp']
    else:
        regs={f'x{i}':getattr(r,f'UC_RISCV_REG_X{i}') for i in range(32)};regs['pc']=r.UC_RISCV_REG_PC;pc=regs['pc'];sp=regs['x2']
    engine.reg_write(sp,0xf000); engine.reg_write(pc,0x1000)
    source_lines=[i+1 for i,line in enumerate(config['source'].splitlines()) if line.strip() and not line.strip().endswith(':') and not line.strip().startswith(('#',';','.'))]
    instructions=[]
    for i,ins in enumerate(dis.disasm(code,0x1000)):
        instructions.append(dict(address=hex(ins.address),bytes=bytes(ins.bytes).hex(),mnemonic=ins.mnemonic,operands=ins.op_str,line=0,
                                 layer='machine code'))
    by_address={int(v['address'],16):v for v in instructions}
    emit({'buildHash':digest(code),'target':dict(isa=profile,width=width,endian='little',abi='freestanding',cpu=p[7],callingConvention='manual; no OS ABI'),
          'artifacts':[dict(kind='assembly',label=p[7]+' / Unicorn '+u.__version__,instructions=instructions,buildHash=digest(code))],
          'metrics':{'compileMs':compile_ms},'limitations':['Freestanding code only. No system calls, MMU, devices or cycle timing. Assembly source maps unavailable; instruction addresses are exact.']})
    recorder=Recorder(emit,config.get('maxEvents',2000)); writes=[]; reads=[]
    def mem(uc,access,address,size,value,data):
        if access==u.UC_MEM_WRITE:
            writes.append(dict(address=hex(address),size=size,before=bytes(uc.mem_read(address,size)).hex(),after=(value & ((1<<(8*size))-1)).to_bytes(size,'little').hex(),type=f'bytes[{size}]'))
        else: reads.append(dict(address=hex(address),size=size,value=bytes(uc.mem_read(address,size)).hex(),type=f'bytes[{size}]'))
    engine.hook_add(u.UC_HOOK_MEM_WRITE|u.UC_HOOK_MEM_READ,mem)
    def snapshot(): return {n:dict(type=f'bits{width}' if n not in ('eflags','cpsr','nzcv') else 'status bits',value=str(engine.reg_read(reg)),hex=hex(engine.reg_read(reg)),state='available',size=width//8) for n,reg in regs.items()}
    start=time.perf_counter_ns()
    while 0x1000<=engine.reg_read(pc)<0x1000+len(code):
        address=engine.reg_read(pc); before=snapshot(); writes.clear();reads.clear()
        engine.emu_start(address | (1 if profile=='thumb' else 0),0x1000+len(code),timeout=100000,count=1)
        after=snapshot()
        recorder.event('instruction',values=after,instruction=hex(address),phaseOverride='after',before=before,memory=list(writes),reads=list(reads),decoded=by_address.get(address),depth=1)
    emit({'metrics':{'executionMs':(time.perf_counter_ns()-start)/1e6,'instructionCount':recorder.seq,'measurement':'host emulation cost; not target cycles'}})
