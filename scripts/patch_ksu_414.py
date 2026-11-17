import os
import sys

def log(msg):
    print(f"[+] {msg}", flush=True)

# 1. Patch drivers/kernelsu/pkg_observer.c for Linux 4.14 fsnotify API
pkg_path = 'drivers/kernelsu/pkg_observer.c'
if os.path.exists(pkg_path):
    with open(pkg_path, 'r', encoding='utf-8') as f:
        code = f.read()

    target = """static const struct fsnotify_ops ksu_ops = {
	.handle_inode_event = ksu_handle_inode_event,
};

static int add_mark_on_inode(struct inode *inode, u32 mask,
			     struct fsnotify_mark **out)
{
	struct fsnotify_mark *m;

	m = kzalloc(sizeof(*m), GFP_KERNEL);
	if (!m)
		return -ENOMEM;

	fsnotify_init_mark(m, g);
	m->mask = mask;

	if (fsnotify_add_inode_mark(m, inode, 0)) {
		fsnotify_put_mark(m);
		return -EINVAL;
	}
	*out = m;
	return 0;
}"""

    compat_code = """#if LINUX_VERSION_CODE < KERNEL_VERSION(5, 9, 0)
static int ksu_handle_event(struct fsnotify_group *group,
			    struct inode *to_tell,
			    struct fsnotify_mark *inode_mark,
			    struct fsnotify_mark *vfsmount_mark,
			    u32 mask, const void *data, int data_type,
			    const unsigned char *file_name, u32 cookie,
			    struct fsnotify_iter_info *iter_info)
{
	if (!file_name)
		return 0;
	if (mask & FS_ISDIR)
		return 0;
	if (!strcmp((const char *)file_name, "packages.list")) {
		pr_info("packages.list detected: %d\\n", mask);
		track_throne();
	}
	return 0;
}

static const struct fsnotify_ops ksu_ops = {
	.handle_event = ksu_handle_event,
};

static int add_mark_on_inode(struct inode *inode, u32 mask,
			     struct fsnotify_mark **out)
{
	struct fsnotify_mark *m;

	m = kzalloc(sizeof(*m), GFP_KERNEL);
	if (!m)
		return -ENOMEM;

	fsnotify_init_mark(m, g);
	m->mask = mask;

	if (fsnotify_add_mark(m, inode, NULL, 0)) {
		fsnotify_put_mark(m);
		return -EINVAL;
	}
	*out = m;
	return 0;
}
#else
static const struct fsnotify_ops ksu_ops = {
	.handle_inode_event = ksu_handle_inode_event,
};

static int add_mark_on_inode(struct inode *inode, u32 mask,
			     struct fsnotify_mark **out)
{
	struct fsnotify_mark *m;

	m = kzalloc(sizeof(*m), GFP_KERNEL);
	if (!m)
		return -ENOMEM;

	fsnotify_init_mark(m, g);
	m->mask = mask;

	if (fsnotify_add_inode_mark(m, inode, 0)) {
		fsnotify_put_mark(m);
		return -EINVAL;
	}
	*out = m;
	return 0;
}
#endif"""

    if target in code:
        code = code.replace(target, compat_code)
        with open(pkg_path, 'w', encoding='utf-8') as f:
            f.write(code)
        log('pkg_observer.c successfully patched for Linux 4.14')
    else:
        log('Note: Target block not found or already patched in pkg_observer.c')

# 2. Patch drivers/kernelsu/core_hook.c for SuSFS 4.14 compatibility and ksu_try_umount
hook_path = 'drivers/kernelsu/core_hook.c'
if os.path.exists(hook_path):
    with open(hook_path, 'r', encoding='utf-8') as f:
        hook_code = f.read()

    target_hook = '#include <linux/susfs.h>'
    stubs = """#include <linux/susfs.h>

struct st_susfs_sus_map;

#ifndef CMD_SUSFS_ADD_SUS_PATH_LOOP
#define CMD_SUSFS_ADD_SUS_PATH_LOOP 0x55553
static inline int susfs_add_sus_path_loop(void *arg) { return -EOPNOTSUPP; }
#endif
#ifndef CMD_SUSFS_SET_ANDROID_DATA_ROOT_PATH
#define CMD_SUSFS_SET_ANDROID_DATA_ROOT_PATH 0x55551
#define CMD_SUSFS_SET_SDCARD_ROOT_PATH 0x55552
static inline int susfs_set_i_state_on_external_dir(void *arg, int cmd) { return -EOPNOTSUPP; }
#endif
#ifndef CMD_SUSFS_HIDE_SUS_MNTS_FOR_ALL_PROCS
#define CMD_SUSFS_HIDE_SUS_MNTS_FOR_ALL_PROCS 0x55561
#endif
#ifndef CMD_SUSFS_UMOUNT_FOR_ZYGOTE_ISO_SERVICE
#define CMD_SUSFS_UMOUNT_FOR_ZYGOTE_ISO_SERVICE 0x55562
#endif
#ifndef CMD_SUSFS_ADD_SUS_MAP
#define CMD_SUSFS_ADD_SUS_MAP 0x60020
static inline int susfs_add_sus_map(void *arg) { return -EOPNOTSUPP; }
#endif
#ifndef CMD_SUSFS_ENABLE_AVC_LOG_SPOOFING
#define CMD_SUSFS_ENABLE_AVC_LOG_SPOOFING 0x60010
static inline void susfs_set_avc_log_spoofing(bool val) {}
#endif

static inline bool susfs_is_current_proc_umounted(void) { return false; }
static inline void susfs_set_current_proc_umounted(void) {}
__attribute__((weak)) bool susfs_hide_sus_mnts_for_all_procs = false;
__attribute__((weak)) void susfs_reorder_mnt_id(void) {}
__attribute__((weak)) void susfs_run_sus_path_loop(uid_t uid) {}
__attribute__((weak)) int susfs_get_enabled_features(char __user *buf, size_t size) { return 0; }"""

    if target_hook in hook_code and 'susfs_reorder_mnt_id(void) {}' not in hook_code:
        hook_code = hook_code.replace(target_hook, stubs, 1)

    # Add ksu_try_umount bridge for susfs.c
    if 'void ksu_try_umount' not in hook_code:
        ksu_try_umount_impl = """
#ifdef CONFIG_KSU_SUSFS_TRY_UMOUNT
void ksu_try_umount(const char *mnt, bool check_mnt, int flags, uid_t uid)
{
	try_umount(mnt, check_mnt, flags, uid);
}
#endif
"""
        hook_code += ksu_try_umount_impl
        log('Added ksu_try_umount implementation to drivers/kernelsu/core_hook.c')

    with open(hook_path, 'w', encoding='utf-8') as f:
        f.write(hook_code)
    log('core_hook.c successfully patched')

# 3. Patch fs/notify/fdinfo.c for missing inotify_mark_user_mask in Linux 4.14
fdinfo_path = 'fs/notify/fdinfo.c'
if os.path.exists(fdinfo_path):
    with open(fdinfo_path, 'r', encoding='utf-8') as f:
        fdinfo_code = f.read()

    if 'static inline u32 inotify_mark_user_mask' not in fdinfo_code:
        inotify_helper = """
#ifndef inotify_mark_user_mask
static inline u32 inotify_mark_user_mask(struct fsnotify_mark *mark)
{
	return mark->mask & IN_ALL_EVENTS;
}
#endif
"""
        target_inc = '#include "inotify/inotify.h"'
        if target_inc in fdinfo_code:
            fdinfo_code = fdinfo_code.replace(target_inc, target_inc + "\n" + inotify_helper, 1)
        else:
            fdinfo_code = inotify_helper + "\n" + fdinfo_code
        with open(fdinfo_path, 'w', encoding='utf-8') as f:
            f.write(fdinfo_code)
        log('fs/notify/fdinfo.c successfully patched with inotify_mark_user_mask')

# 4. Patch fs/namespace.c (ensure can_umount and path_umount exist)
ns_path = 'fs/namespace.c'
if os.path.exists(ns_path):
    with open(ns_path, 'r', encoding='utf-8') as f:
        ns_code = f.read()
    if 'int path_umount' not in ns_code:
        path_umount_impl = """
/* KernelSU path_umount backport for Linux 4.14 */
static int can_umount(const struct path *path, int flags)
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
        with open(ns_path, 'a', encoding='utf-8') as f:
            f.write(path_umount_impl)
        log('fs/namespace.c successfully appended with can_umount & path_umount')

# 5. Patch include/linux/idr.h
idr_path = 'include/linux/idr.h'
if os.path.exists(idr_path):
    with open(idr_path, 'r', encoding='utf-8') as f:
        idr_code = f.read()
    if 'ida_alloc' not in idr_code:
        target = "void ida_simple_remove(struct ida *ida, unsigned int id);"
        helpers = """
static inline int ida_alloc_range(struct ida *ida, unsigned int min, unsigned int max, gfp_t gfp)
{
	return ida_simple_get(ida, min, max, gfp);
}
static inline int ida_alloc_min(struct ida *ida, unsigned int min, gfp_t gfp)
{
	return ida_simple_get(ida, min, 0, gfp);
}
static inline int ida_alloc(struct ida *ida, gfp_t gfp)
{
	return ida_simple_get(ida, 0, 0, gfp);
}
static inline void ida_free(struct ida *ida, unsigned int id)
{
	ida_simple_remove(ida, id);
}
"""
        if target in idr_code:
            idr_code = idr_code.replace(target, target + "\n" + helpers, 1)
            with open(idr_path, 'w', encoding='utf-8') as f:
                f.write(idr_code)
            log('Injected ida_alloc helpers into include/linux/idr.h')

# 6. Patch include/linux/poll.h
poll_path = 'include/linux/poll.h'
if os.path.exists(poll_path):
    with open(poll_path, 'r', encoding='utf-8') as f:
        poll_code = f.read()
    if '__poll_t' not in poll_code:
        target = "#include <uapi/linux/poll.h>"
        helpers = """#include <uapi/linux/poll.h>

#ifndef __poll_t
#define __poll_t __poll_t
typedef unsigned int __poll_t;
#endif
"""
        if target in poll_code:
            poll_code = poll_code.replace(target, helpers, 1)
            with open(poll_path, 'w', encoding='utf-8') as f:
                f.write(poll_code)
            log('Injected __poll_t typedef into include/linux/poll.h')

# 7. Patch include/linux/timekeeping.h
tk_path = 'include/linux/timekeeping.h'
if os.path.exists(tk_path):
    with open(tk_path, 'r', encoding='utf-8') as f:
        tk_code = f.read()
    if 'ktime_get_boottime_ts64' not in tk_code:
        target = "static inline void get_monotonic_boottime64(struct timespec64 *ts)"
        helper = """static inline void ktime_get_boottime_ts64(struct timespec64 *ts)
{
	*ts = ktime_to_timespec64(ktime_get_boottime());
}

static inline void get_monotonic_boottime64(struct timespec64 *ts)"""
        if target in tk_code:
            tk_code = tk_code.replace(target, helper, 1)
            with open(tk_path, 'w', encoding='utf-8') as f:
                f.write(tk_code)
            log('Injected ktime_get_boottime_ts64 into include/linux/timekeeping.h')

# 8. Patch drivers/kernelsu/kernel_compat.h
compat_h = 'drivers/kernelsu/kernel_compat.h'
if os.path.exists(compat_h):
    with open(compat_h, 'r', encoding='utf-8') as f:
        c = f.read()
    if 'KSYM_NAME_LEN' not in c:
        extra = """
#include <linux/kallsyms.h>
#ifndef KSYM_NAME_LEN
#define KSYM_NAME_LEN 128
#endif
"""
        target = "#define __KSU_H_KERNEL_COMPAT"
        if target in c:
            c = c.replace(target, target + extra, 1)
            with open(compat_h, 'w', encoding='utf-8') as f:
                f.write(c)
            log('Added KSYM_NAME_LEN fallback to kernel_compat.h')
