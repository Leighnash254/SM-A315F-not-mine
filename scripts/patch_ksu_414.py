import os
import sys

# 1. Patch drivers/kernelsu/pkg_observer.c
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
        print('pkg_observer.c successfully patched for Linux 4.14')
    else:
        print('Note: Target block not found or already patched in pkg_observer.c')

# 2. Patch drivers/kernelsu/core_hook.c for SuSFS 4.14 compatibility
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
        with open(hook_path, 'w', encoding='utf-8') as f:
            f.write(hook_code)
        print('core_hook.c successfully patched for SuSFS 4.14 compatibility')
    else:
        print('Note: Target hook not found or already patched in core_hook.c')

# 3. Append can_umount and path_umount to fs/namespace.c (runs AFTER susfs 4.14 patch has applied cleanly)
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
        print('fs/namespace.c successfully appended with can_umount & path_umount')
    else:
        print('Note: path_umount already present in fs/namespace.c')
