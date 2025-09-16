from mlgame.utils.logger import logger
# 安全鎖：禁止所有 exec*（subprocess.run 最終會被擋）
def install_exec_killer():
    import sys
    logger.info(f"您的作業系統是: {sys.platform}")
    if sys.platform == "win32":
        return  # Windows 不適用 seccomp
    elif sys.platform == "darwin":
        return  # MacOS 不適用 seccomp
    
    logger.info("您的作業系統是 Linux，安裝 exec killer 以防止 execve 被使用")

    import pyseccomp as sc
    from pyseccomp import Arch
    import errno
    # 可選：先設 no_new_privs，避免繞過（多數容器已預設開）
    try:
        import ctypes
        libc = ctypes.CDLL(None)
        PR_SET_NO_NEW_PRIVS = 38
        libc.prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0)
    except Exception:
        pass

    try:
        if hasattr(sc, "SCMP_ACT_ALLOW"):  # A 類：libseccomp 綁定（python3-libseccomp）
            logger.info("libseccomp 綁定，禁止使用 execve")
            flt = sc.SyscallFilter(defaction=sc.SCMP_ACT_ALLOW)
            flt.add_rule(sc.SCMP_ACT_ERRNO, sc.ScmpSyscall("execve"))
            # flt.add_rule(sc.SCMP_ACT_ERRNO, sc.ScmpSyscall("execveat"))
            # （如需要可再加 posix_spawn/posix_spawnp，視 libc 而定）
            flt.load()
        else:  # B 類：pyseccomp 綁定（pip: pyseccomp）
            logger.info("pyseccomp 綁定，禁止使用 execve")
            flt = sc.SyscallFilter(defaction=sc.ALLOW)
            
            # flt.add_rule(sc.ERRNO(errno.EPERM), "execveat")
            flt.add_rule(sc.ERRNO(errno.EPERM), "execve")
            flt.load()
    except Exception as e:
        logger.exception(f"Exception: {e}")
        