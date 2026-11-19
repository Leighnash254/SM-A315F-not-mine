import os
import sys
import shutil

def log(msg):
    print(f"[+] {msg}", flush=True)

# 1. Ensure uapi headers are present in drivers/kernelsu/include/uapi
uapi_dest = 'drivers/kernelsu/include/uapi'
uapi_src = '/tmp/KernelSU-Next/uapi'
if os.path.exists('/tmp/KernelSU-Next/uapi'):
    if os.path.exists(uapi_dest):
        if not os.path.isdir(uapi_dest) or os.path.islink(uapi_dest):
            os.remove(uapi_dest)
            shutil.copytree(uapi_src, uapi_dest)
            log('Replaced uapi symlink with real uapi header directory')
    else:
        shutil.copytree(uapi_src, uapi_dest)
        log('Copied uapi header directory to drivers/kernelsu/include/uapi')

# 2. Versioning & Tag Override (33355 & v3.4.2)
override_ver = os.environ.get('KSU_OVERRIDE_VERSION', '33355')
override_tag = os.environ.get('KSU_OVERRIDE_VERSION_TAG', 'v3.4.2')

for kh_path in ['drivers/kernelsu/include/ksu.h', 'drivers/kernelsu/ksu.h']:
    if os.path.exists(kh_path):
        with open(kh_path, 'r', encoding='utf-8') as f:
            kh = f.read()
        target_macro = '#define KERNEL_SU_VERSION KSU_VERSION\n#define KERNEL_SU_VERSION_TAG KSU_VERSION_TAG'
        replacement_macro = f'#undef KERNEL_SU_VERSION\n#define KERNEL_SU_VERSION {override_ver}\n#undef KERNEL_SU_VERSION_TAG\n#define KERNEL_SU_VERSION_TAG "{override_tag}"'
        if target_macro in kh:
            kh = kh.replace(target_macro, replacement_macro, 1)
            with open(kh_path, 'w', encoding='utf-8') as f:
                f.write(kh)
            log(f'Patched {kh_path} with Version: {override_ver}, Tag: {override_tag}')
        elif '#define KERNEL_SU_VERSION ' in kh:
            log(f'{kh_path} already configured for versioning')

# Also override in Kbuild if present
kbuild_path = 'drivers/kernelsu/Kbuild'
if os.path.exists(kbuild_path):
    with open(kbuild_path, 'r', encoding='utf-8') as f:
        kb = f.read()
    if 'KSU_VERSION_FALLBACK := 1' in kb:
        kb = kb.replace('KSU_VERSION_FALLBACK := 1', f'KSU_VERSION_FALLBACK := {override_ver}')
    if 'KSU_VERSION_TAG_FALLBACK := v0.0.1' in kb:
        kb = kb.replace('KSU_VERSION_TAG_FALLBACK := v0.0.1', f'KSU_VERSION_TAG_FALLBACK := {override_tag}')
    with open(kbuild_path, 'w', encoding='utf-8') as f:
        f.write(kb)
    log(f'Patched drivers/kernelsu/Kbuild fallback version to {override_ver} ({override_tag})')

# 3. Patch drivers/kernelsu/feature/kernel_umount.c for SuSFS compatibility glue
umount_c = 'drivers/kernelsu/feature/kernel_umount.c'
if os.path.exists(umount_c):
    with open(umount_c, 'r', encoding='utf-8') as f:
        ucode = f.read()

    if 'static void try_umount(const char *mnt, int flags)' in ucode:
        ucode = ucode.replace('static void try_umount(const char *mnt, int flags)', 'void try_umount(const char *mnt, int flags)')

    if 'susfs_is_current_ksu_domain' not in ucode:
        glue = """
/* SuSFS Compatibility Glue */
bool susfs_is_current_ksu_domain(void)
{
	return is_ksu_domain();
}

void ksu_try_umount(const char *mnt, bool check_mnt, int flags, uid_t uid)
{
	try_umount(mnt, flags);
}
"""
        ucode += glue
        with open(umount_c, 'w', encoding='utf-8') as f:
            f.write(ucode)
        log('Patched drivers/kernelsu/feature/kernel_umount.c with SuSFS glue')
    else:
        log('SuSFS glue already present in kernel_umount.c')

# 4. Patch throne_tracker.c for relaxed magic check (Android 16 / OneUI 8 subdirectories)
for tt_path in ['drivers/kernelsu/manager/throne_tracker.c', 'drivers/kernelsu/throne_tracker.c']:
    if os.path.exists(tt_path):
        with open(tt_path, 'r', encoding='utf-8') as f:
            tt_code = f.read()

        magic_check = """if (S_MAGIC_COMPAT(file) != data_app_magic) {
					pr_info("%s: skip: %s magic: 0x%lx expected: 0x%lx\\n", __func__, pos->dirpath, 
						S_MAGIC_COMPAT(file), data_app_magic);
					filp_close(file, NULL);
					goto skip_iterate;
				}"""

        magic_relaxed = """/* Relaxed magic check for Android 16 / OneUI 8 subdirectories */
				if (false && S_MAGIC_COMPAT(file) != data_app_magic) {
					pr_info("%s: skip: %s magic: 0x%lx expected: 0x%lx\\n", __func__, pos->dirpath, 
						S_MAGIC_COMPAT(file), data_app_magic);
					filp_close(file, NULL);
					goto skip_iterate;
				}"""

        if magic_check in tt_code:
            tt_code = tt_code.replace(magic_check, magic_relaxed, 1)
            with open(tt_path, 'w', encoding='utf-8') as f:
                f.write(tt_code)
            log(f'Relaxed filesystem magic check in {tt_path} for Android 16 / OneUI 8')

# 5. Ensure kernel/reboot.c contains ksu_handle_sys_reboot hook
reboot_path = 'kernel/reboot.c'
if os.path.exists(reboot_path):
    with open(reboot_path, 'r', encoding='utf-8') as f:
        reboot_code = f.read()
    if 'ksu_handle_sys_reboot' not in reboot_code:
        target = '/* We only trust the superuser with rebooting the system. */'
        hook_code = """#ifdef CONFIG_KSU
	extern int ksu_handle_sys_reboot(int magic1, int magic2, unsigned int cmd, void __user **arg);
	if (ksu_handle_sys_reboot(magic1, magic2, cmd, &arg))
		return 0;
#endif

	/* We only trust the superuser with rebooting the system. */"""
        if target in reboot_code:
            reboot_code = reboot_code.replace(target, hook_code, 1)
            with open(reboot_path, 'w', encoding='utf-8') as f:
                f.write(reboot_code)
            log('Added ksu_handle_sys_reboot hook to kernel/reboot.c')
    else:
        log('kernel/reboot.c already verified to have ksu_handle_sys_reboot hook')

# 6. Ensure fs/namespace.c contains can_umount and path_umount
ns_path = 'fs/namespace.c'
if os.path.exists(ns_path):
    with open(ns_path, 'r', encoding='utf-8') as f:
        ns_code = f.read()
    if 'int path_umount(struct path *path, int flags)' not in ns_code:
        target_ns = 'static bool is_mnt_ns_file(struct dentry *dentry)'
        ns_impl = """static int can_umount(const struct path *path, int flags)
{
	struct mount *mnt = real_mount(path->mnt);

	if (flags & ~(MNT_FORCE | MNT_DETACH | MNT_EXPIRE | UMOUNT_NOFOLLOW))
		return -EINVAL;
	if (!may_mount())
		return -EPERM;
	if (path->dentry != path->mnt->mnt_root)
		return -EINVAL;
	if (!check_mnt(mnt))
		return -EINVAL;
	if (mnt->mnt.mnt_flags & MNT_LOCKED)
		return -EINVAL;
	if (flags & MNT_FORCE && !capable(CAP_SYS_ADMIN))
		return -EPERM;
	return 0;
}

int path_umount(struct path *path, int flags)
{
	struct mount *mnt = real_mount(path->mnt);
	int ret;

	ret = can_umount(path, flags);
	if (!ret)
		ret = do_umount(mnt, flags);
	dput(path->dentry);
	mntput_no_expire(mnt);
	return ret;
}
EXPORT_SYMBOL(path_umount);

"""
        if target_ns in ns_code:
            ns_code = ns_code.replace(target_ns, ns_impl + target_ns, 1)
            with open(ns_path, 'w', encoding='utf-8') as f:
                f.write(ns_code)
            log('Added can_umount and path_umount to fs/namespace.c')
    else:
        log('fs/namespace.c already contains path_umount')

log('KernelSU-Next legacy patching completed successfully!')
